"""In-process runtime that an HA adapter can call without duplicating model logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta

from ramses_twin.coordinator import ZoneCoordinator
from ramses_twin.model import ZoneController
from ramses_twin.store import JsonStateStore
from ramses_twin.thermal import Observation, TrainingResult


@dataclass
class TwinRuntime:
    coordinators: dict[str, ZoneCoordinator]
    store: JsonStateStore
    _last_observation: dict[str, Observation] = field(default_factory=dict)

    def restore(self, now: datetime) -> None:
        """Restore and prune bounded state against one explicit recovery clock."""
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("restore time must be timezone-aware")
        state = self.store.load()
        for zone_id, model in state.models.items():
            if zone_id in self.coordinators:
                self.coordinators[zone_id].thermal_model = model
        for zone_id, override in state.overrides.items():
            if zone_id not in self.coordinators:
                continue
            try:
                self._restore_override(self.coordinators[zone_id].controller, override)
            except ValueError:
                # A corrupt single zone must not stop independent zones from
                # recovering. It is discarded deterministically on checkpoint.
                continue
        for coordinator in self.coordinators.values():
            coordinator.controller.clear_expired_override(now)
        # Persist the cleaned, configured-world projection so malformed,
        # retired and expired records cannot reappear after a second restart.
        self.checkpoint()

    @staticmethod
    def _restore_override(controller: ZoneController, state: dict[str, object]) -> None:
        expected = {
            "controller_id",
            "zone_index",
            "override_target",
            "override_until",
            "boost_delta",
            "boost_until",
            "permanent_override_target",
        }
        if set(state) != expected:
            raise ValueError("invalid zone override fields")
        if state["controller_id"] != controller.controller_id or state["zone_index"] != controller.zone_index:
            raise ValueError("override identity does not match configured zone")

        def number(name: str) -> float | None:
            value = state[name]
            if value is None:
                return None
            if isinstance(value, bool) or not isinstance(value, (int, float)):
                raise ValueError("invalid numeric override state")
            return float(value)

        def timestamp(name: str) -> datetime | None:
            value = state[name]
            if value is None or not isinstance(value, str):
                if value is None:
                    return None
                raise ValueError("invalid override timestamp")
            try:
                parsed = datetime.fromisoformat(value)
            except ValueError as error:
                raise ValueError("invalid override timestamp") from error
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("override timestamp must be timezone-aware")
            return parsed

        override_target, override_until = number("override_target"), timestamp("override_until")
        boost_delta, boost_until = number("boost_delta"), timestamp("boost_until")
        permanent = number("permanent_override_target")
        active = sum(value is not None for value in (override_target, boost_delta, permanent))
        if active > 1 or (override_target is None) != (override_until is None) or (boost_delta is None) != (boost_until is None):
            raise ValueError("inconsistent zone override state")
        controller.return_to_schedule()
        if permanent is not None:
            controller.set_permanent_override(permanent)
        elif override_target is not None:
            assert override_until is not None
            controller.boost(override_target, override_until)
        elif boost_delta is not None:
            assert boost_until is not None
            # Use a time immediately before expiry to reuse normal validation.
            controller.timed_boost(boost_delta, boost_until, boost_until.replace(microsecond=0) - timedelta(microseconds=1))

    def checkpoint(self) -> None:
        """Atomically persist recovery state; never retain raw observations."""
        self.store.save(
            {key: item.thermal_model for key, item in self.coordinators.items()},
            {
                zone_id: {
                    "controller_id": controller.controller_id,
                    "zone_index": controller.zone_index,
                    "override_target": controller.override_target,
                    "override_until": controller.override_until.isoformat() if controller.override_until else None,
                    "boost_delta": controller.boost_delta,
                    "boost_until": controller.boost_until.isoformat() if controller.boost_until else None,
                    "permanent_override_target": controller.permanent_override_target,
                }
                for zone_id, coordinator in self.coordinators.items()
                for controller in (coordinator.controller,)
            },
        )

    def apply_temporary_override(self, zone_id: str, target: float, until: datetime, now: datetime) -> str:
        """Set and atomically checkpoint one test-world temporary override."""
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("command time must be timezone-aware")
        if until.tzinfo is None or until.utcoffset() is None or until <= now:
            raise ValueError("override expiry must be later than command time")
        controller = self.coordinators[zone_id].controller
        controller.boost(target, until)
        self.checkpoint()
        return controller.setpoint_frame(now)

    def recovery_frames(self, now: datetime) -> dict[str, str]:
        """Recompute every configured target for a test-only recovery publication."""
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("recovery time must be timezone-aware")
        return {
            zone_id: self.coordinators[zone_id].controller.setpoint_frame(now)
            for zone_id in sorted(self.coordinators)
        }

    def observe(self, zone_id: str, observation: Observation) -> TrainingResult | None:
        coordinator = self.coordinators[zone_id]
        previous = self._last_observation.get(zone_id)
        self._last_observation[zone_id] = observation
        if previous is None:
            return None
        result = coordinator.thermal_model.learn(previous, observation)
        if result.accepted:
            self.checkpoint()
        return result

    def due_frame(self, zone_id: str, now: datetime, room_temp: float, outdoor_temp: float) -> str | None:
        frame = self.coordinators[zone_id].apply_due_start(now, room_temp, outdoor_temp)
        if frame is not None:
            self.checkpoint()
        return frame
