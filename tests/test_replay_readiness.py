from __future__ import annotations

from ramses_twin.replay_readiness import REQUIRED_BEHAVIOURS, replay_readiness


def _scenario(name: str) -> dict[str, object]:
    return {
        "format": 1,
        "kind": "ordered-rx-scenario",
        "name": name,
        "retention": {"event_limit": 1, "discarded": 0},
        "events": [
            {
                "topic": "RAMSES/GATEWAY/18:016440/rx",
                "receipt_ts": "2026-11-22T08:00:00+00:00",
                "payload": {
                    "msg": "066 I --- 01:000001 --:------ 02:000002 2309 003 010700",
                    "ts": "1970-01-01T00:00:00+00:00",
                },
            }
        ],
    }


def _manifest(name: str, behaviour: str) -> dict[str, object]:
    return {
        "format": 1,
        "kind": "scenario-qualification",
        "scenario": name,
        "status": "qualified",
        "receipt_time_health": "healthy",
        "behaviour": behaviour,
        "corroboration": [{"source": "test", "reference": name}],
        "replay_test": "tests/test_replay_readiness.py",
    }


def test_readiness_does_not_promote_an_unqualified_baseline() -> None:
    report = replay_readiness({"baseline": _scenario("baseline")}, {})

    assert report.qualified == ()
    assert report.missing == REQUIRED_BEHAVIOURS
    assert report.rejected == {"baseline": "missing qualification manifest"}
    assert report.ready is False


def test_readiness_requires_each_exact_qualified_behaviour() -> None:
    scenarios = {behaviour: _scenario(behaviour) for behaviour in REQUIRED_BEHAVIOURS}
    manifests = {behaviour: _manifest(behaviour, behaviour) for behaviour in REQUIRED_BEHAVIOURS}

    report = replay_readiness(scenarios, manifests)

    assert report.qualified == REQUIRED_BEHAVIOURS
    assert report.missing == ()
    assert report.rejected == {}
    assert report.ready is True


def test_candidate_or_invalid_manifest_is_not_replay_ready() -> None:
    scenario = _scenario("candidate")
    manifest = _manifest("candidate", "schedule-change")
    manifest["status"] = "candidate"
    manifest.pop("behaviour")
    manifest["hypothesis"] = "schedule-change"
    report = replay_readiness({"candidate": scenario}, {"candidate": manifest})

    assert "candidate" in report.rejected
    assert report.qualified == ()
    assert report.missing == REQUIRED_BEHAVIOURS
