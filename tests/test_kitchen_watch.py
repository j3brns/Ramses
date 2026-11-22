"""Bounded Kitchen passive-watch selection tests."""

from __future__ import annotations

from ramses_twin.kitchen_watch import select_kitchen_watch_window


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


def test_watch_returns_bounded_context_for_eligible_transition() -> None:
    result = select_kitchen_watch_window(
        [_ordinary(0), _target("010708", 1), _ordinary(2), _target("010834", 3), _ordinary(4), _ordinary(5)],
        before=1,
        after=2,
    )

    assert result is not None
    assert (result.transition.previous_target, result.transition.target) == (18.0, 21.0)
    assert len(result.scenario["events"]) == 6
    assert result.scenario["retention"]["source_retained"] == 6
    assert any(event["msg"].endswith("2309 003 010708") for event in result.scenario["events"])


def test_watch_rejects_ordinary_traffic_and_partial_post_context() -> None:
    ordinary = select_kitchen_watch_window([_ordinary(0), _ordinary(1)])
    partial = select_kitchen_watch_window([_target("010708", 1), _target("010834", 2)], after=1)

    assert ordinary is None
    assert partial is None


def test_watch_caps_input_and_counts_discarded_events() -> None:
    result = select_kitchen_watch_window(
        [_target("010708", 0), _target("010834", 1), _ordinary(2), _ordinary(3)],
        max_events=3,
        before=0,
        after=1,
    )

    assert result is not None
    assert result.retained == 3
    assert result.discarded == 1
    assert result.scenario["retention"]["discarded"] == 1
