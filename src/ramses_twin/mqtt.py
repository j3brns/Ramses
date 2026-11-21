"""MQTT envelope used by the software-only RAMSES/TEST gateway."""

from __future__ import annotations

from datetime import datetime, timezone


def rx_envelope(frame: str, when: datetime | None = None) -> dict[str, str]:
    """Return the same message shape as a ramses_esp RX publication."""
    timestamp = when or datetime.now(timezone.utc)
    return {"msg": frame, "ts": timestamp.isoformat()}


def topics(gateway_id: str = "18:990001") -> dict[str, str]:
    root = f"RAMSES/TEST/{gateway_id}"
    return {"rx": f"{root}/rx", "tx": f"{root}/tx"}
