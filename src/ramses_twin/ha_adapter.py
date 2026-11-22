"""Pure-Python descriptor for the future Home Assistant Test adapter.

This module deliberately does not import Home Assistant, an MQTT client, or an
RF gateway. A Home Assistant integration may consume this descriptor later;
unit tests and the digital twin can import it today.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime

from ramses_twin.coordinator import ZoneCoordinator
from ramses_twin.model import SwitchPoint, WeeklySchedule
from ramses_twin.mqtt import topics, tx_envelope


TEST_ENTITY_PREFIX = "ramses_test"
_WEEKDAYS = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}


def _entity_fragment(value: str) -> str:
    fragment = value.strip().lower().replace("-", "_").replace(" ", "_")
    if not fragment or not all(character.isalnum() or character == "_" for character in fragment):
        raise ValueError("zone id must produce a safe Home Assistant entity fragment")
    return fragment


@dataclass(frozen=True)
class TestAdapterDescriptor:
    """Test-only names and transport settings for one future HA zone adapter."""

    __test__ = False

    gateway_id: str
    zone_id: str

    @property
    def climate_entity_id(self) -> str:
        return f"climate.{TEST_ENTITY_PREFIX}_{_entity_fragment(self.zone_id)}"

    @property
    def mqtt_topics(self) -> dict[str, str]:
        """Return only the already-validated test-world topics."""
        return topics(self.gateway_id)

    @property
    def diagnostic_entity_ids(self) -> dict[str, str]:
        """Return read-only, test-only identifiers for one zone's state."""
        fragment = _entity_fragment(self.zone_id)
        return {
            "effective_target": f"sensor.{TEST_ENTITY_PREFIX}_{fragment}_effective_target",
            "next_change": f"sensor.{TEST_ENTITY_PREFIX}_{fragment}_next_change",
            "optimiser_ready": f"binary_sensor.{TEST_ENTITY_PREFIX}_{fragment}_optimiser_ready",
            "planned_start": f"sensor.{TEST_ENTITY_PREFIX}_{fragment}_planned_start",
        }


@dataclass(frozen=True)
class TestZoneDiagnostics:
    """Read-only state that a later HA adapter may expose for one test zone."""

    __test__ = False

    effective_target: float
    next_change: datetime | None
    optimiser_ready: bool
    planned_start: datetime | None


@dataclass(frozen=True)
class TestClimateCommand:
    """A test-world temporary target command ready for isolated transport.

    The command is data only. Publishing it remains the responsibility of an
    adapter outside this pure module.
    """

    __test__ = False

    entity_id: str
    target_temperature: float
    expires_at: datetime
    topic: str
    payload: dict[str, str]


def read_test_zone_diagnostics(
    coordinator: ZoneCoordinator,
    now: datetime,
    room_temp: float,
    outdoor_temp: float,
) -> TestZoneDiagnostics:
    """Project zone state into diagnostics without changing model state.

    The optimiser may propose a future start only when it is trained. This
    function never applies that proposal, sends a frame, or accesses HA/MQTT.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("diagnostic time must be timezone-aware")
    controller = coordinator.controller
    next_change = controller.schedule.next_change_after(now) if controller.schedule else None
    planned = coordinator.plan(now, room_temp, outdoor_temp)
    return TestZoneDiagnostics(
        effective_target=controller.target_at(now),
        next_change=next_change,
        optimiser_ready=coordinator.thermal_model.ready,
        planned_start=planned.start_at if planned is not None else None,
    )


def apply_test_temporary_override(
    descriptor: TestAdapterDescriptor,
    coordinator: ZoneCoordinator,
    target_temperature: object,
    expires_at: datetime,
    now: datetime,
) -> TestClimateCommand:
    """Apply a virtual temporary target and return its test-only TX command.

    This is the narrow write seam for a future climate entity. It changes the
    virtual controller only; it opens no broker connection and cannot select a
    live topic. The normal controller expiry path returns the zone to schedule.
    """
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("command time must be timezone-aware")
    if expires_at.tzinfo is None or expires_at.utcoffset() is None:
        raise ValueError("override expiry must be timezone-aware")
    if expires_at <= now:
        raise ValueError("override expiry must be later than command time")
    target = _temperature(target_temperature, "target_temperature")
    coordinator.controller.boost(target, expires_at)
    frame = coordinator.controller.setpoint_frame(now)
    return TestClimateCommand(
        entity_id=descriptor.climate_entity_id,
        target_temperature=target,
        expires_at=expires_at,
        topic=descriptor.mqtt_topics["tx"],
        payload=tx_envelope(frame, now),
    )


def _temperature(value: object, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a numeric temperature")
    target = float(value)
    if not 5.0 <= target <= 35.0:
        raise ValueError(f"{label} must be between 5 and 35 C")
    return target


def _minute_of_day(value: object, label: str) -> int:
    if not isinstance(value, str):
        raise ValueError(f"{label} must be HH:MM or HH:MM:SS")
    parts = value.split(":")
    if len(parts) not in {2, 3}:
        raise ValueError(f"{label} must be HH:MM or HH:MM:SS")
    try:
        hour, minute = (int(part) for part in parts[:2])
        second = int(parts[2]) if len(parts) == 3 else 0
    except ValueError as error:
        raise ValueError(f"{label} must be HH:MM or HH:MM:SS") from error
    if not 0 <= hour <= 23 or not 0 <= minute <= 59 or second != 0:
        raise ValueError(f"{label} must be minute-aligned and within one day")
    return hour * 60 + minute


def _block_target(block: Mapping[str, object]) -> float:
    data = block.get("data")
    if not isinstance(data, Mapping) or "target_temperature" not in data:
        raise ValueError("each active schedule block needs data.target_temperature")
    return _temperature(data["target_temperature"], "data.target_temperature")


def weekly_schedule_from_ha_blocks(
    schedule: Mapping[str, Sequence[Mapping[str, object]]],
    *,
    off_target: float,
) -> WeeklySchedule:
    """Convert HA Get schedule blocks into the pure weekly timetable.

    HA schedules are active inside blocks and off outside them. The pure model
    has a target at all times, so callers must name the frost/off target rather
    than letting this adapter invent one. Blocks must be minute-aligned and may
    not cross midnight; the HA schedule itself guarantees no same-day overlap.
    """
    if not isinstance(schedule, Mapping):
        raise ValueError("Home Assistant schedule must be a mapping of days to blocks")
    off = _temperature(off_target, "off_target")
    events: dict[tuple[int, int], float] = {}
    for day, blocks in schedule.items():
        try:
            weekday = _WEEKDAYS[day.lower()]
        except (AttributeError, KeyError) as error:
            raise ValueError(f"unknown Home Assistant schedule day: {day!r}") from error
        if not isinstance(blocks, Sequence) or isinstance(blocks, (str, bytes)):
            raise ValueError(f"schedule blocks for {day} must be a sequence")
        parsed_blocks: list[tuple[int, int, float]] = []
        for block in blocks:
            if not isinstance(block, Mapping):
                raise ValueError(f"schedule block for {day} must be a mapping")
            start = _minute_of_day(block.get("from"), "block.from")
            end = _minute_of_day(block.get("to"), "block.to")
            if end <= start:
                raise ValueError("schedule blocks must end later on the same day")
            parsed_blocks.append((start, end, _block_target(block)))

        parsed_blocks.sort(key=lambda item: item[0])
        for previous, current in zip(parsed_blocks, parsed_blocks[1:]):
            if current[0] < previous[1]:
                raise ValueError("schedule blocks must not overlap")

        # Make the inactive period before the first block explicit. This also
        # supplies a valid prior-week target to the repeating pure model.
        events[(weekday, 0)] = off
        for start, end, target in parsed_blocks:
            # An adjacent block start intentionally overwrites a preceding end.
            events[(weekday, end)] = off
            events[(weekday, start)] = target
    if not events:
        raise ValueError("Home Assistant schedule must contain at least one block")
    return WeeklySchedule(tuple(SwitchPoint(day, minute, target) for (day, minute), target in events.items()))


@dataclass(frozen=True)
class HaScheduleSnapshot:
    """Current HA Schedule helper state, independent of a Home Assistant runtime."""

    active_target: float | None
    next_event: datetime


def schedule_snapshot_from_ha(state: object, attributes: Mapping[str, object]) -> HaScheduleSnapshot:
    """Read active additional data and next_event from an HA Schedule entity."""
    if state not in {"on", "off"}:
        raise ValueError("Home Assistant schedule state must be on or off")
    next_event_value = attributes.get("next_event")
    if isinstance(next_event_value, datetime):
        next_event = next_event_value
    elif isinstance(next_event_value, str):
        try:
            next_event = datetime.fromisoformat(next_event_value)
        except ValueError as error:
            raise ValueError("next_event must be ISO-8601") from error
    else:
        raise ValueError("next_event must be a datetime or ISO-8601 string")
    if next_event.tzinfo is None or next_event.utcoffset() is None:
        raise ValueError("next_event must include a timezone")
    active_target = None if state == "off" else _temperature(attributes.get("target_temperature"), "target_temperature")
    return HaScheduleSnapshot(active_target, next_event)


__all__ = [
    "HaScheduleSnapshot",
    "TEST_ENTITY_PREFIX",
    "TestAdapterDescriptor",
    "TestClimateCommand",
    "TestZoneDiagnostics",
    "schedule_snapshot_from_ha",
    "apply_test_temporary_override",
    "read_test_zone_diagnostics",
    "weekly_schedule_from_ha_blocks",
]
