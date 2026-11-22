"""Validation and serialisation for bounded, ordered RF scenario evidence."""

from __future__ import annotations

import re
from typing import Any


_GATEWAY_ID = re.compile(r"[0-9]{2}:[0-9]{6}")


def normalise_rx_event(event: dict[str, Any], topic_root: str = "RAMSES/GATEWAY") -> dict[str, str]:
    """Validate one gateway RX envelope and preserve its time provenance.

    ``payload.ts`` belongs to the gateway, whereas Mosquitto's ``tst`` (as
    emitted by ``mosquitto_sub -F %J``) is the broker receipt time.  They are
    deliberately retained as distinct values: an unsynchronised gateway clock
    must not become evidence of elapsed wall-clock time.
    """
    topic = event.get("topic")
    if not _is_rx_topic(topic, topic_root):
        raise ValueError("event must come from an RX topic below the configured gateway root")
    payload = event.get("payload", event)
    if not isinstance(payload, dict):
        raise ValueError("event payload must be a JSON object")
    message, timestamp = payload.get("msg"), payload.get("ts")
    if not isinstance(message, str) or not message.strip():
        raise ValueError("event payload requires a non-empty msg")
    if not isinstance(timestamp, str) or not timestamp:
        raise ValueError("event payload requires a timestamp")
    result = {
        "topic": topic,
        "msg": message,
        # ``ts`` is retained as a backwards-compatible alias for the gateway
        # timestamp. New consumers should inspect the explicit provenance keys.
        "ts": timestamp,
        "gateway_ts": timestamp,
        "gateway_time_quality": _gateway_time_quality(timestamp),
    }
    # A raw ``mosquitto_sub -F %J`` envelope uses ``tst``.  A portable
    # scenario has already been normalised and carries the same broker clock
    # under ``receipt_ts``.  Preserve either form so replay does not silently
    # discard the only trustworthy chronology source.
    receipt_timestamp = event.get("tst", event.get("receipt_ts"))
    if isinstance(receipt_timestamp, str) and receipt_timestamp:
        result["receipt_ts"] = receipt_timestamp
    return result


def _is_rx_topic(topic: object, topic_root: str) -> bool:
    """Accept one concrete gateway RX topic, never a wildcard or nested path."""
    if not isinstance(topic, str) or not isinstance(topic_root, str) or not topic_root:
        return False
    prefix = f"{topic_root}/"
    if not topic.startswith(prefix):
        return False
    suffix = topic[len(prefix) :].split("/")
    return len(suffix) == 2 and _GATEWAY_ID.fullmatch(suffix[0]) is not None and suffix[1] == "rx"


def _gateway_time_quality(timestamp: str) -> str:
    """Classify only the known epoch fallback; all other gateway clocks remain unverified."""
    if timestamp.startswith("1970-01-01T"):
        return "epoch-invalid"
    return "unverified"


def scenario_document(name: str, events: list[dict[str, str]], max_events: int) -> dict[str, Any]:
    """Return the portable scenario contract written by the recorder."""
    if not name or any(character not in "abcdefghijklmnopqrstuvwxyz0123456789-_" for character in name):
        raise ValueError("scenario name must use lower-case letters, numbers, hyphens, or underscores")
    if max_events < 1:
        raise ValueError("max_events must be positive")
    return {
        "format": 1,
        "kind": "ordered-rx-scenario",
        "name": name,
        "retention": {"event_limit": max_events, "discarded": 0},
        "events": events,
    }
