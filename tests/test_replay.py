"""Real-RX structural replay tests; no physical timing is inferred."""

import json
from pathlib import Path

import pytest

from ramses_twin.replay import decode_frame, replay_scenario


def _baseline() -> dict[str, object]:
    return json.loads(Path("data/scenarios/baseline-rx-window.json").read_text(encoding="utf-8"))


def test_replay_preserves_all_baseline_event_order_and_protocol_counts() -> None:
    trace = replay_scenario(_baseline())

    assert trace.name == "baseline-rx-window"
    assert len(trace.frames) == 111
    assert [frame.code for frame in trace.frames[:3]] == ["3EF0", "0008", "0008"]
    assert trace.frames[-1].ordinal == 110
    assert trace.code_counts["2309"] == 13
    assert trace.code_counts["3150"] == 11


def test_replay_rejects_epoch_clock_for_timing_claims_but_keeps_order() -> None:
    trace = replay_scenario(_baseline())

    assert trace.timestamps_reliable is False
    assert trace.frames[0].gateway_ts.startswith("1970-")
    assert trace.frames[0].gateway_time_quality == "epoch-invalid"
    assert trace.frames[0].ordinal < trace.frames[1].ordinal


def test_replay_requires_strictly_increasing_broker_receipt_times_for_timing_claims() -> None:
    scenario = {
        "format": 1,
        "kind": "ordered-rx-scenario",
        "name": "receipt-order",
        "retention": {"event_limit": 2, "discarded": 0},
        "events": [
            {
                "topic": "RAMSES/GATEWAY/18:016440/rx",
                "receipt_ts": "2026-11-22T08:00:01+00:00",
                "payload": {"msg": "066 I --- 01:000001 --:------ 02:000002 2309 003 010700", "ts": "1970-01-01T00:00:00+00:00"},
            },
            {
                "topic": "RAMSES/GATEWAY/18:016440/rx",
                "receipt_ts": "2026-11-22T08:00:01+00:00",
                "payload": {"msg": "066 I --- 01:000001 --:------ 02:000002 2309 003 010700", "ts": "1970-01-01T00:00:00+00:00"},
            },
        ],
    }

    assert replay_scenario(scenario).timestamps_reliable is False


@pytest.mark.parametrize(
    "message, reason",
    [
        ("066 I --- 01:000001 02:000002 2309 003 0107", "nine fields"),
        ("066 I --- 01:000001 --:------ 02:000002 2309 003 0107", "declared length"),
    ],
)
def test_decoder_rejects_malformed_frame_structure(message: str, reason: str) -> None:
    with pytest.raises(ValueError, match=reason):
        decode_frame(
            {"topic": "RAMSES/GATEWAY/18:016440/rx", "msg": message, "ts": "2026-11-21T12:00:00+00:00"},
            0,
        )
