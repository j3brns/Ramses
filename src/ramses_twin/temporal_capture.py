"""Select a short candidate window from a bounded period of passive RX data."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Iterable, Mapping

from ramses_twin.evidence import normalise_rx_event, scenario_document
from ramses_twin.kitchen import KitchenSetpointTransition, kitchen_setpoint_transitions


@dataclass(frozen=True)
class TemporalCaptureResult:
    """A finite passive observation period's candidate-only result."""

    scenario: dict[str, Any] | None
    transition: KitchenSetpointTransition | None
    observed: int
    discarded: int
    stop_reason: str


def select_temporal_kitchen_window(
    raw_events: Iterable[Mapping[str, Any]],
    *,
    duration: timedelta,
    max_events: int,
    before: int = 12,
    after: int = 12,
) -> TemporalCaptureResult:
    """Return one short candidate from a finite receipt-time interval.

    The interval begins at the first valid broker receipt timestamp. At most
    ``max_events`` raw envelopes are examined. Before a candidate, only a
    ``before``-event ring buffer exists in memory. A candidate is emitted only
    after ``after`` following events arrive. Ordinary traffic is never retained
    in the result.
    """
    if duration <= timedelta(0):
        raise ValueError("duration must be positive")
    if max_events < 1:
        raise ValueError("max_events must be positive")
    if before < 0 or after < 0:
        raise ValueError("context sizes must not be negative")

    ring: deque[dict[str, str]] = deque(maxlen=before)
    candidate_events: list[dict[str, str]] | None = None
    candidate: KitchenSetpointTransition | None = None
    window_start: datetime | None = None
    observed = discarded = 0
    stop_reason = "input-exhausted"

    for raw in raw_events:
        if observed >= max_events:
            discarded += 1
            stop_reason = "event-cap"
            continue
        observed += 1
        event = normalise_rx_event(dict(raw))
        receipt = _receipt_time(event)
        if receipt is None:
            discarded += 1
            continue
        if window_start is None:
            window_start = receipt
        if receipt - window_start > duration:
            discarded += 1
            stop_reason = "duration-cap"
            continue

        if candidate_events is not None:
            candidate_events.append(event)
            if len(candidate_events) >= _candidate_size(before, after):
                return _result(candidate_events, candidate, observed, discarded, "candidate")
            continue

        trial_events = [*ring, event]
        transition = _final_transition(trial_events)
        ring.append(event)
        if transition is None:
            continue
        candidate = transition
        candidate_events = trial_events
        if after == 0:
            return _result(candidate_events, candidate, observed, discarded, "candidate")

    return TemporalCaptureResult(None, None, observed, discarded, stop_reason)


def _final_transition(events: list[dict[str, str]]) -> KitchenSetpointTransition | None:
    scenario = scenario_document("temporal-probe", events, len(events) or 1)
    candidates = kitchen_setpoint_transitions(scenario)
    if not candidates:
        return None
    transition = candidates[-1]
    return transition if transition.ordinal == len(events) - 1 else None


def _candidate_size(before: int, after: int) -> int:
    return before + 1 + after


def _result(
    events: list[dict[str, str]],
    transition: KitchenSetpointTransition | None,
    observed: int,
    discarded: int,
    stop_reason: str,
) -> TemporalCaptureResult:
    scenario = scenario_document("kitchen-temporal-candidate", events, len(events))
    scenario["retention"] = {
        "event_limit": len(events),
        "discarded": discarded,
        "observed": observed,
        "mode": "temporal-candidate-window",
    }
    return TemporalCaptureResult(scenario, transition, observed, discarded, stop_reason)


def _receipt_time(event: Mapping[str, str]) -> datetime | None:
    value = event.get("receipt_ts")
    if value is None:
        return None
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError as error:
        raise ValueError("broker receipt time must be ISO-8601") from error
    if timestamp.tzinfo is None or timestamp.year < 2000:
        raise ValueError("broker receipt time must be current and timezone-aware")
    return timestamp
