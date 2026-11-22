"""Bounded selection of a Kitchen transition window from passive RX input."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from ramses_twin.evidence import normalise_rx_event, scenario_document
from ramses_twin.kitchen import KitchenSetpointTransition, kitchen_setpoint_transitions


@dataclass(frozen=True)
class KitchenWatchResult:
    """One bounded candidate window, without asserting why it changed."""

    transition: KitchenSetpointTransition
    scenario: dict[str, Any]
    retained: int
    discarded: int


def select_kitchen_watch_window(
    raw_events: Iterable[Mapping[str, Any]],
    *,
    max_events: int = 500,
    before: int = 12,
    after: int = 12,
    name: str = "kitchen-candidate-window",
) -> KitchenWatchResult | None:
    """Return a context window around the first eligible observed transition.

    This function consumes already-observed RX envelopes only. It caps input,
    requires post-transition context, and returns ``None`` for ordinary traffic.
    A returned candidate is not evidence that the transition was scheduled.
    """
    if max_events < 1:
        raise ValueError("max_events must be positive")
    if before < 0 or after < 0:
        raise ValueError("context sizes must not be negative")

    retained: list[dict[str, str]] = []
    discarded = 0
    for event in raw_events:
        normalised = normalise_rx_event(dict(event))
        if len(retained) < max_events:
            retained.append(normalised)
        else:
            discarded += 1
    if not retained:
        return None

    source = scenario_document("kitchen-watch-source", retained, max_events)
    source["retention"]["discarded"] = discarded
    candidates = kitchen_setpoint_transitions(source)
    if not candidates:
        return None
    for transition in candidates:
        start = max(0, transition.previous_ordinal - before)
        end = transition.ordinal + after + 1
        if end > len(retained):
            continue
        # The span may include unrelated RX traffic between the two target
        # frames, so its storage limit must match the actual bounded slice.
        scenario = scenario_document(name, retained[start:end], end - start)
        scenario["retention"] = {
            "event_limit": end - start,
            "discarded": discarded,
            "source_retained": len(retained),
            "context_before": before,
            "context_after": after,
        }
        return KitchenWatchResult(transition, scenario, len(retained), discarded)
    return None
