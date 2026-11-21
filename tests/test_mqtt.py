from datetime import datetime, timezone

import pytest

from ramses_twin.mqtt import TestMqttTransport, TopicViolation, topics, tx_envelope


def test_transport_accepts_own_test_tx_and_publishes_only_its_test_rx() -> None:
    seen: list[str] = []

    def virtual_gateway(frame: str, when: datetime) -> tuple[str, ...]:
        seen.append(frame)
        assert when == datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
        return (" I --- 12:00:00 12:900001 2309 003 0107D0",)

    transport = TestMqttTransport("18:990001", virtual_gateway)
    now = datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc)
    publications = transport.consume_tx(
        topics("18:990001")["tx"],
        tx_envelope(" W --- 12:00:00 18:990001 2309 003 0107D0", now),
        now,
    )

    assert seen == [" W --- 12:00:00 18:990001 2309 003 0107D0"]
    assert len(publications) == 1
    assert publications[0].topic == "RAMSES/TEST/18:990001/rx"
    assert publications[0].payload["msg"].endswith("0107D0")


@pytest.mark.parametrize(
    "topic",
    [
        "RAMSES/GATEWAY/18:016440/tx",
        "RAMSES/TEST/18:990001/rx",
        "RAMSES/TEST/another-gateway/tx",
    ],
)
def test_transport_rejects_live_and_other_test_topics(topic: str) -> None:
    transport = TestMqttTransport("18:990001", lambda frame, when: ())
    now = datetime(2026, 11, 21, tzinfo=timezone.utc)

    with pytest.raises(TopicViolation):
        transport.consume_tx(topic, tx_envelope("frame", now), now)


@pytest.mark.parametrize("gateway_id", ["18:990001/../../GATEWAY", "18:+", "18:#"])
def test_transport_rejects_unsafe_gateway_ids(gateway_id: str) -> None:
    with pytest.raises(ValueError):
        topics(gateway_id)


@pytest.mark.parametrize(
    "envelope",
    [
        {"msg": "frame"},
        {"msg": "frame", "ts": "not-a-time"},
        {"msg": "frame", "ts": "2026-11-21T12:00:00"},
    ],
)
def test_transport_rejects_malformed_envelopes(envelope: dict[str, str]) -> None:

    transport = TestMqttTransport("18:990001", lambda frame, when: ())
    now = datetime(2026, 11, 21, tzinfo=timezone.utc)
    with pytest.raises(ValueError):
        transport.consume_tx(transport.topic_map["tx"], envelope, now)


@pytest.mark.parametrize("response", [None, b"frame", ""])
def test_transport_rejects_malformed_virtual_gateway_response(response: object) -> None:
    transport = TestMqttTransport("18:990001", lambda frame, when: (response,))
    now = datetime(2026, 11, 21, tzinfo=timezone.utc)

    with pytest.raises(ValueError):
        transport.consume_tx(transport.topic_map["tx"], tx_envelope("frame", now), now)
