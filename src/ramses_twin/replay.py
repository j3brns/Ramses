"""Pure decoding and ordered replay of bounded gateway-RX scenarios.

This module preserves capture order.  It deliberately does not treat a
gateway-provided timestamp as an authoritative clock: callers must establish
that separately before making elapsed-time or schedule-behaviour claims.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from datetime import datetime
import re
from typing import Any, Mapping

from ramses_twin.evidence import normalise_rx_event


_DEVICE_ID = re.compile(r"(?:--:------|[0-9]{2}:[0-9]{6})$")
_CODE = re.compile(r"[0-9A-F]{4}$")
_PAYLOAD = re.compile(r"[0-9A-F]*$")
_RSSI = re.compile(r"[0-9]{3}$")
_SEQUENCE = re.compile(r"(?:---|[0-9]{3})$")
_VERBS = frozenset({"I", "RP", "RQ", "W"})


@dataclass(frozen=True)
class ObservedFrame:
    """One syntactically valid frame in its observed scenario position."""

    ordinal: int
    topic: str
    gateway_ts: str
    receipt_ts: str | None
    gateway_time_quality: str
    signal: str
    verb: str
    source: str
    destination: str
    code: str
    payload: str


@dataclass(frozen=True)
class ReplayTrace:
    """A bounded ordered scenario, without inferred physical state changes."""

    name: str
    frames: tuple[ObservedFrame, ...]
    timestamps_reliable: bool

    @property
    def code_counts(self) -> dict[str, int]:
        """Return deterministic protocol-code counts for this exact replay."""
        return dict(sorted(Counter(frame.code for frame in self.frames).items()))


def decode_frame(event: Mapping[str, str], ordinal: int) -> ObservedFrame:
    """Decode frame structure only; semantic packet interpretation is separate."""
    if ordinal < 0:
        raise ValueError("ordinal must be non-negative")
    tokens = event["msg"].split()
    if len(tokens) != 9:
        raise ValueError("RAMSES frame must have nine fields")
    signal, verb, sequence, source, _via, destination, code, length, payload = tokens
    if not _RSSI.fullmatch(signal) or not _SEQUENCE.fullmatch(sequence):
        raise ValueError("RAMSES frame has an invalid signal or sequence field")
    if verb not in _VERBS:
        raise ValueError("unsupported RAMSES frame verb")
    if not _DEVICE_ID.fullmatch(source) or not _DEVICE_ID.fullmatch(destination):
        raise ValueError("RAMSES frame has an invalid device address")
    if not _CODE.fullmatch(code):
        raise ValueError("RAMSES frame code must be four uppercase hexadecimal characters")
    if not _PAYLOAD.fullmatch(payload) or len(payload) % 2:
        raise ValueError("RAMSES frame payload must contain complete hexadecimal bytes")
    try:
        declared_length = int(length, 10)
    except ValueError as error:
        raise ValueError("RAMSES frame length must be decimal") from error
    if len(payload) // 2 != declared_length:
        raise ValueError("RAMSES frame payload length does not match its declared length")
    return ObservedFrame(
        ordinal=ordinal,
        topic=event["topic"],
        gateway_ts=event["gateway_ts"],
        receipt_ts=event.get("receipt_ts"),
        gateway_time_quality=event["gateway_time_quality"],
        signal=signal,
        verb=verb,
        source=source,
        destination=destination,
        code=code,
        payload=payload,
    )


def replay_scenario(document: Mapping[str, Any]) -> ReplayTrace:
    """Validate and structurally replay a recorded RX scenario in list order."""
    if document.get("format") != 1 or document.get("kind") != "ordered-rx-scenario":
        raise ValueError("unsupported replay scenario format")
    name, events = document.get("name"), document.get("events")
    if not isinstance(name, str) or not isinstance(events, list) or not events:
        raise ValueError("replay scenario needs a name and at least one event")
    retention = document.get("retention")
    if not isinstance(retention, Mapping) or not isinstance(retention.get("event_limit"), int):
        raise ValueError("replay scenario needs a retention event limit")
    if len(events) > retention["event_limit"]:
        raise ValueError("replay scenario exceeds its recorded event limit")
    normalised = [normalise_rx_event(event) for event in events]
    frames = tuple(decode_frame(event, ordinal) for ordinal, event in enumerate(normalised))
    return ReplayTrace(
        name=name,
        frames=frames,
        timestamps_reliable=_timestamps_reliable(frames),
    )


def _timestamps_reliable(frames: tuple[ObservedFrame, ...]) -> bool:
    """Use only broker receipt time for elapsed-time or schedule assertions."""
    try:
        dates = [datetime.fromisoformat(frame.receipt_ts) for frame in frames if frame.receipt_ts]
    except ValueError:
        return False
    return (
        len(dates) == len(frames)
        and all(date.tzinfo is not None and date.year >= 2000 for date in dates)
        and all(previous < current for previous, current in zip(dates, dates[1:]))
    )
