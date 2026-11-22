"""Scenario evidence qualification must block accidental behavioural claims."""

import pytest

from ramses_twin.qualification import require_qualified, validate_qualification


def _scenario(*receipt_times: str | None) -> dict[str, object]:
    events = []
    for receipt in receipt_times:
        event: dict[str, str] = {
            "topic": "RAMSES/GATEWAY/18:016440/rx",
            "msg": "060 I --- 12:216487 --:------ 12:216487 2309 003 010708",
            "ts": "1970-01-01T00:00:00+00:00",
        }
        if receipt is not None:
            event["receipt_ts"] = receipt
        events.append(event)
    return {
        "format": 1,
        "kind": "ordered-rx-scenario",
        "name": "kitchen-window",
        "retention": {"event_limit": 10, "discarded": 0},
        "events": events,
    }


def _manifest(status: str, health: str, **extra: object) -> dict[str, object]:
    return {
        "format": 1,
        "kind": "scenario-qualification",
        "scenario": "kitchen-window",
        "status": status,
        "receipt_time_health": health,
        **extra,
    }


def test_baseline_and_candidate_do_not_expose_qualified_behaviour() -> None:
    scenario = _scenario("2026-11-22T07:00:00+00:00")
    baseline = validate_qualification(scenario, _manifest("baseline", "healthy"))
    candidate = validate_qualification(
        scenario, _manifest("candidate", "healthy", hypothesis="schedule-change")
    )

    assert baseline.behaviour is None
    assert candidate.behaviour is None
    assert candidate.hypothesis == "schedule-change"
    with pytest.raises(ValueError, match="not qualified"):
        require_qualified(scenario, _manifest("candidate", "healthy", hypothesis="schedule-change"), "schedule-change")


def test_qualified_behaviour_requires_corroboration_replay_and_healthy_receipts() -> None:
    scenario = _scenario(
        "2026-11-22T07:00:00+00:00", "2026-11-22T07:00:01+00:00"
    )
    manifest = _manifest(
        "qualified",
        "healthy",
        behaviour="schedule-change",
        corroboration=[{"source": "programmed-schedule", "reference": "Kitchen weekday 07:00"}],
        replay_test="tests/test_programmer_contract.py::test_kitchen_schedule_change",
    )

    assert require_qualified(scenario, manifest, "schedule-change").behaviour == "schedule-change"
    with pytest.raises(ValueError, match="corroboration"):
        validate_qualification(scenario, _manifest("qualified", "healthy", behaviour="schedule-change", replay_test="test_id"))
    with pytest.raises(ValueError, match="healthy broker"):
        validate_qualification(
            _scenario(None),
            _manifest(
                "qualified",
                "missing",
                behaviour="schedule-change",
                corroboration=[{"source": "schedule", "reference": "07:00"}],
                replay_test="test_id",
            ),
        )


def test_manifest_cannot_lie_about_scenario_or_receipt_health() -> None:
    scenario = _scenario("2026-11-22T07:00:01+00:00", "2026-11-22T07:00:00+00:00")
    with pytest.raises(ValueError, match="receipt_time_health"):
        validate_qualification(scenario, _manifest("candidate", "healthy", hypothesis="schedule-change"))
    with pytest.raises(ValueError, match="scenario must match"):
        validate_qualification(
            _scenario("2026-11-22T07:00:00+00:00"),
            {**_manifest("baseline", "healthy"), "scenario": "other"},
        )
