"""Small, deterministic CM67z-zone state model.

This package never transmits RF. It only models scheduler decisions and the
frames that a later transport adapter may publish to RAMSES/TEST.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


def setpoint_payload(zone_index: int, temperature: float) -> str:
    """Encode the observed 2309 payload: zone byte + temperature in centi-degrees."""
    if not 0 <= zone_index <= 255:
        raise ValueError("zone index must fit in one byte")
    if not 5.0 <= temperature <= 35.0:
        raise ValueError("temperature must be between 5 and 35 C")
    return f"{zone_index:02X}{round(temperature * 100):04X}"


@dataclass
class ZoneController:
    """One CM67z zone with a scheduled target and optional temporary boost."""

    controller_id: str
    zone_index: int
    scheduled_target: float
    override_target: float | None = None
    override_until: datetime | None = None

    def target_at(self, now: datetime) -> float:
        if self.override_target is not None and self.override_until and now < self.override_until:
            return self.override_target
        self.clear_expired_override(now)
        return self.scheduled_target

    def boost(self, target: float, until: datetime) -> None:
        if until.tzinfo is None:
            raise ValueError("override expiry must be timezone-aware")
        self.override_target = target
        self.override_until = until

    def clear_expired_override(self, now: datetime) -> None:
        if self.override_until and now >= self.override_until:
            self.override_target = None
            self.override_until = None

    def setpoint_frame(self, now: datetime) -> str:
        target = self.target_at(now)
        payload = setpoint_payload(self.zone_index, target)
        return f" I --- --:------ --:------ {self.controller_id} 2309 003 {payload}"
