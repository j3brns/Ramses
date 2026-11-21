"""Conservative selection of observed Kitchen controller setpoint changes."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Any, Mapping

from ramses_twin.replay import ObservedFrame, replay_scenario


KITCHEN_CONTROLLER_ID = "12:216487"
KITCHEN_ZONE_INDEX = 1


@dataclass(frozen=True)
class KitchenSetpointTransition:
    """A receipt-timestamped controller target change, not a schedule claim."""

    zone_index: int
    previous_target: float
    target: float
    previous_ordinal: int
    ordinal: int
    previous_receipt_ts: str
    receipt_ts: str

    def as_dict(self) -> dict[str, object]:
        """Return a deterministic JSON-ready representation."""
        return asdict(self)


def kitchen_setpoint_transitions(
    scenario: Mapping[str, Any],
    *,
    controller_id: str = KITCHEN_CONTROLLER_ID,
    zone_index: int = KITCHEN_ZONE_INDEX,
) -> tuple[KitchenSetpointTransition, ...]:
    """Return observed controller target changes for one Kitchen zone.

    The selector deliberately returns *candidates*, not schedule changes. A
    controller-originated ``2309`` target change can also result from a manual
    action. Caller evidence must establish the cause separately.
    """
    if not 0 <= zone_index <= 255:
        raise ValueError("zone_index must fit in one byte")
    trace = replay_scenario(scenario)
    previous: tuple[ObservedFrame, float, datetime] | None = None
    transitions: list[KitchenSetpointTransition] = []

    for frame in trace.frames:
        decoded = _controller_setpoint(frame, controller_id)
        if decoded is None:
            continue
        frame_zone, target = decoded
        if frame_zone != zone_index:
            continue
        receipt = _receipt_time(frame)
        if receipt is None:
            # Do not join two timestamped targets across an eligible frame whose
            # ordering cannot be established. That would manufacture chronology.
            previous = None
            continue
        if previous is not None:
            previous_frame, previous_target, previous_receipt = previous
            if receipt <= previous_receipt:
                raise ValueError("Kitchen controller receipt times must increase")
            if target != previous_target:
                transitions.append(
                    KitchenSetpointTransition(
                        zone_index=zone_index,
                        previous_target=previous_target,
                        target=target,
                        previous_ordinal=previous_frame.ordinal,
                        ordinal=frame.ordinal,
                        previous_receipt_ts=previous_frame.receipt_ts or "",
                        receipt_ts=frame.receipt_ts or "",
                    )
                )
        previous = (frame, target, receipt)
    return tuple(transitions)


def _controller_setpoint(frame: ObservedFrame, controller_id: str) -> tuple[int, float] | None:
    if frame.source != controller_id or frame.verb != "I" or frame.code != "2309":
        return None
    if len(frame.payload) != 6:
        raise ValueError("controller 2309 payload must contain a zone and centi-degree target")
    zone_index = int(frame.payload[:2], 16)
    target = int(frame.payload[2:], 16) / 100
    # Match the virtual-controller contract: impossible targets are not
    # evidence of a usable schedule transition.
    if not 5.0 <= target <= 35.0:
        raise ValueError("controller 2309 target must be between 5 and 35 C")
    return zone_index, target


def _receipt_time(frame: ObservedFrame) -> datetime | None:
    if not frame.receipt_ts:
        return None
    try:
        timestamp = datetime.fromisoformat(frame.receipt_ts)
    except ValueError as error:
        raise ValueError("Kitchen controller receipt time must be ISO-8601") from error
    if timestamp.tzinfo is None or timestamp.year < 2000:
        raise ValueError("Kitchen controller receipt time must be a current timezone-aware timestamp")
    return timestamp
