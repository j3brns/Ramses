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


def test_recorder_rejects_tx_and_invalid_scenario_names() -> None:
    with pytest.raises(ValueError, match="RX topic"):
        normalise_rx_event({"topic": "RAMSES/GATEWAY/18:016440/tx", "msg": "frame", "ts": "now"})
    with pytest.raises(ValueError, match="scenario name"):
        scenario_document("Kitchen boost", [], 10)
