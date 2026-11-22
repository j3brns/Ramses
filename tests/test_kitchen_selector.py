"""Kitchen transition selection tests using receipt-timestamped RX evidence."""

from __future__ import annotations

import pytest

from ramses_twin.kitchen import kitchen_setpoint_transitions


def _scenario(*events: dict[str, object]) -> dict[str, object]:
    return {
        "format": 1,
        "kind": "ordered-rx-scenario",
        "name": "kitchen-candidate",
        "retention": {"event_limit": 20, "discarded": 0},
        "events": list(events),
    }


def _event(payload: str, receipt: str, *, source: str = "12:216487") -> dict[str, object]:
    return {
        "topic": "RAMSES/GATEWAY/18:016440/rx",
        "tst": receipt,
        "payload": {
            "msg": f"060 I --- {source} --:------ {source} 2309 003 {payload}",
            "ts": "1970-01-01T00:00:00+00:00",
        },
    }


def test_selector_returns_a_controller_target_change_with_receipt_provenance() -> None:
    candidates = kitchen_setpoint_transitions(
        _scenario(
            _event("010708", "2026-11-21T06:59:59+00:00"),
            _event("010834", "2026-11-21T07:00:01+00:00"),
        )
    )

    assert len(candidates) == 1
    candidate = candidates[0]
    assert (candidate.previous_target, candidate.target) == (18.0, 21.0)
    assert (candidate.previous_ordinal, candidate.ordinal) == (0, 1)
    assert candidate.receipt_ts == "2026-11-21T07:00:01+00:00"


def test_selector_ignores_other_controller_zone_and_repeated_target() -> None:
    candidates = kitchen_setpoint_transitions(
        _scenario(
            _event("010708", "2026-11-21T06:59:59+00:00"),
            _event("010708", "2026-11-21T07:00:00+00:00"),
            _event("020834", "2026-11-21T07:00:01+00:00"),
            _event("010834", "2026-11-21T07:00:02+00:00", source="12:216751"),
        )
    )

    assert candidates == ()


def test_selector_ignores_a_trv_report_addressed_to_the_kitchen_controller() -> None:
    candidates = kitchen_setpoint_transitions(
        _scenario(
            _event("010708", "2026-11-21T06:59:59+00:00"),
            {
                "topic": "RAMSES/GATEWAY/18:016440/rx",
                "tst": "2026-11-21T07:00:00+00:00",
                "payload": {
                    "msg": "060 I --- 04:118027 --:------ 12:216487 2309 003 010834",
                    "ts": "1970-01-01T00:00:00+00:00",
                },
            },
        )
    )

    assert candidates == ()


def test_selector_requires_current_increasing_broker_receipt_times() -> None:
    with pytest.raises(ValueError, match="receipt times must increase"):
        kitchen_setpoint_transitions(
            _scenario(
                _event("010708", "2026-11-21T07:00:01+00:00"),
                _event("010834", "2026-11-21T07:00:00+00:00"),
            )
        )


def test_selector_rejects_target_outside_the_controller_contract() -> None:
    with pytest.raises(ValueError, match="target must be between 5 and 35 C"):
        kitchen_setpoint_transitions(
            _scenario(_event("010000", "2026-11-21T07:00:00+00:00"))
        )


def test_selector_does_not_bridge_an_untimestamped_controller_target() -> None:
    scenario = _scenario(
        _event("010708", "2026-11-21T06:59:59+00:00"),
        {
            "topic": "RAMSES/GATEWAY/18:016440/rx",
            "payload": {
                "msg": "060 I --- 12:216487 --:------ 12:216487 2309 003 010708",
                "ts": "1970-01-01T00:00:00+00:00",
            },
        },
        _event("010834", "2026-11-21T07:00:01+00:00"),
    )

    assert kitchen_setpoint_transitions(scenario) == ()
