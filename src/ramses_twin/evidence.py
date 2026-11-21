"""Validation and serialisation for bounded, ordered RF scenario evidence."""

from __future__ import annotations

from typing import Any


def normalise_rx_event(event: dict[str, Any], topic_root: str = "RAMSES/GATEWAY") -> dict[str, str]:
    """Validate one gateway RX envelope and preserve its time provenance.

    ``payload.ts`` belongs to the gateway, whereas Mosquitto's ``tst`` (as
    emitted by ``mosquitto_sub -F %J``) is the broker receipt time.  They are
    deliberately retained as distinct values: an unsynchronised gateway clock
    must not become evidence of elapsed wall-clock time.
    """
    topic = event.get("topic")
    if not isinstance(topic, str) or not topic.startswith(f"{topic_root}/") or not topic.endswith("/rx"):
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
    receipt_timestamp = event.get("tst")
    if isinstance(receipt_timestamp, str) and receipt_timestamp:
        result["receipt_ts"] = receipt_timestamp
    return result


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
