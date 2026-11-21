import pytest

from ramses_twin.evidence import normalise_rx_event, scenario_document


def test_normalise_rx_event_preserves_an_ordered_gateway_message() -> None:
    event = normalise_rx_event(
        {
            "topic": "RAMSES/GATEWAY/18:016440/rx",
            "payload": {"msg": " I --- 04:000001 12:000001 3150 002 0100", "ts": "2026-11-21T07:00:00+00:00"},
        }
    )
    assert event["topic"].endswith("/rx")
    assert event["msg"].endswith("0100")
    assert event["gateway_ts"] == event["ts"]
    assert event["gateway_time_quality"] == "unverified"


def test_normalise_rx_event_separates_broker_receipt_from_invalid_gateway_epoch() -> None:
    event = normalise_rx_event(
        {
            "tst": "2026-11-21T15:33:21.275299+0000",
            "topic": "RAMSES/GATEWAY/18:016440/rx",
            "payload": {"msg": " I --- 04:000001 12:000001 3150 002 0100", "ts": "1970-01-01T18:10:26+00:00"},
        }
    )

    assert event["receipt_ts"] == "2026-11-21T15:33:21.275299+0000"
    assert event["gateway_ts"] == "1970-01-01T18:10:26+00:00"
    assert event["gateway_time_quality"] == "epoch-invalid"


def test_recorder_rejects_tx_and_invalid_scenario_names() -> None:
    with pytest.raises(ValueError, match="RX topic"):
        normalise_rx_event({"topic": "RAMSES/GATEWAY/18:016440/tx", "msg": "frame", "ts": "now"})
    with pytest.raises(ValueError, match="scenario name"):
        scenario_document("Kitchen boost", [], 10)
