"""Isolated MQTT boundary used by the software-only RAMSES/TEST gateway.

This module intentionally has no MQTT-client dependency. A later adapter can
connect its publish callback to a broker, but this transport validates the
topic boundary before it hands a frame to model code.
"""

from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from dataclasses import dataclass
from datetime import datetime, timezone


TEST_ROOT = "RAMSES/TEST/"


class TopicViolation(ValueError):
    """Raised when a message attempts to cross the test-world boundary."""


def _require_gateway_id(gateway_id: str) -> None:
    if not gateway_id or any(char in gateway_id for char in "/+#") or gateway_id.strip() != gateway_id:
        raise ValueError("gateway id must be a non-empty MQTT topic segment")


def _require_test_topic(topic: str) -> None:
    if not topic.startswith(TEST_ROOT):
        raise TopicViolation("test transport rejects non-RAMSES/TEST topics")


def rx_envelope(frame: str, when: datetime | None = None) -> dict[str, str]:
    """Return the ramses_esp-compatible envelope for a test publication."""
    timestamp = when or datetime.now(timezone.utc)
    return {"msg": frame, "ts": timestamp.isoformat()}


def tx_envelope(frame: str, when: datetime | None = None) -> dict[str, str]:
    """Return a structured test TX command envelope."""
    return rx_envelope(frame, when)


def topics(gateway_id: str = "18:990001") -> dict[str, str]:
    """Return the only two topics a test gateway may use."""
    _require_gateway_id(gateway_id)
    root = f"{TEST_ROOT}{gateway_id}"
    return {"rx": f"{root}/rx", "tx": f"{root}/tx"}


def _frame_from(envelope: Mapping[str, str]) -> str:
    if set(envelope) != {"msg", "ts"}:
        raise ValueError("test MQTT envelope must contain only msg and ts")
    frame = envelope["msg"]
    if not isinstance(frame, str) or not frame.strip():
        raise ValueError("test MQTT envelope msg must be a non-empty string")
    timestamp = envelope["ts"]
    if not isinstance(timestamp, str):
        raise ValueError("test MQTT envelope ts must be an ISO-8601 string")
    try:
        parsed = datetime.fromisoformat(timestamp)
    except ValueError as error:
        raise ValueError("test MQTT envelope ts must be ISO-8601") from error
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("test MQTT envelope ts must include a timezone")
    return frame


def _response_frame(frame: object) -> str:
    if not isinstance(frame, str) or not frame.strip():
        raise ValueError("virtual gateway responses must be non-empty frame strings")
    return frame


@dataclass(frozen=True)
class PublishedFrame:
    """One broker-neutral test-world publication for assertions or adapters."""

    topic: str
    payload: dict[str, str]


TxHandler = Callable[[str, datetime], Iterable[str]]


@dataclass
class TestMqttTransport:
    """Consume one test TX topic and publish only matching test RX frames.

    ``handler`` is virtual-gateway/model code. It receives a frame and a
    timestamp, then returns zero or more response frames. The transport owns
    the namespace check; neither handler nor caller can redirect a response to
    a live topic.
    """

    __test__ = False

    gateway_id: str
    handler: TxHandler
    def __post_init__(self) -> None:
        _require_gateway_id(self.gateway_id)

    @property
    def topic_map(self) -> dict[str, str]:
        return topics(self.gateway_id)

    def consume_tx(self, topic: str, envelope: Mapping[str, str], when: datetime) -> tuple[PublishedFrame, ...]:
        """Process one command and return its isolated RX publications."""
        _require_test_topic(topic)
        if topic != self.topic_map["tx"]:
            raise TopicViolation("test transport accepts commands only on its own tx topic")
        if when.tzinfo is None or when.utcoffset() is None:
            raise ValueError("transport time must be timezone-aware")
        frame = _frame_from(envelope)
        responses = tuple(_response_frame(response) for response in self.handler(frame, when))
        publications = tuple(
            PublishedFrame(self.topic_map["rx"], rx_envelope(response, when))
            for response in responses
        )
        return publications
