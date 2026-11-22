"""Tests for finite, candidate-only passive Kitchen capture."""

from __future__ import annotations

from datetime import timedelta

import pytest

from ramses_twin.temporal_capture import select_temporal_kitchen_window


def _event(message: str, second: int) -> dict[str, object]:
    return {
        "topic": "RAMSES/GATEWAY/18:016440/rx",
        "tst": f"2026-11-22T07:00:{second:02}+00:00",
        "payload": {"msg": message, "ts": "1970-01-01T00:00:00+00:00"},
    }


def _ordinary(second: int) -> dict[str, object]:
    return _event("060 I --- 04:118027 --:------ 12:216487 3150 002 014A", second)


def _target(value: str, second: int) -> dict[str, object]:
    return _event(f"060 I --- 12:216487 --:------ 12:216487 2309 003 {value}", second)


def test_temporal_capture_retains_only_candidate_context() -> None:
    result = select_temporal_kitchen_window(
        [_ordinary(0), _target("010708", 1), _ordinary(2), _target("010834", 3), _ordinary(4), _ordinary(5)],
        duration=timedelta(minutes=10),
        max_events=100,
        before=2,
        after=2,
    )

    assert result.stop_reason == "candidate"
    assert result.scenario is not None
    assert result.transition is not None
    assert (result.transition.previous_target, result.transition.target) == (18.0, 21.0)
    assert len(result.scenario["events"]) == 5
    assert result.scenario["retention"]["mode"] == "temporal-candidate-window"


def test_temporal_capture_rejects_trv_to_thermostat_report() -> None:
    result = select_temporal_kitchen_window(
        [
            _event("060 I --- 04:118027 --:------ 12:216487 2309 003 010708", 0),
            _event("060 I --- 04:118027 --:------ 12:216487 2309 003 010834", 1),
        ],
        duration=timedelta(minutes=10),
        max_events=100,
    )

    assert result.scenario is None
    assert result.stop_reason == "input-exhausted"


def test_temporal_capture_enforces_duration_and_event_bounds() -> None:
    result = select_temporal_kitchen_window(
        [_ordinary(0), _ordinary(2), _ordinary(3)],
        duration=timedelta(seconds=1),
        max_events=2,
    )

    assert result.scenario is None
    assert result.observed == 2
    assert result.discarded == 2
    assert result.stop_reason == "event-cap"


@pytest.mark.parametrize("duration", [timedelta(0), timedelta(seconds=-1)])
def test_temporal_capture_requires_positive_duration(duration: timedelta) -> None:
    with pytest.raises(ValueError, match="duration"):
        select_temporal_kitchen_window([], duration=duration, max_events=1)
