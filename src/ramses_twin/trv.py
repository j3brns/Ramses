"""Transparent virtual radiator-valve behaviour for the test world.

This is a declared proportional response model, not an emulation of
Honeywell's undisclosed valve-control algorithm.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


def _validate_temperature(value: float) -> None:
    if not 5.0 <= value <= 35.0:
        raise ValueError("temperature must be between 5 and 35 C")


@dataclass(frozen=True)
class TrvReport:
    device_id: str
    controller_id: str
    zone_index: int
    temperature: float
    target: float
    heat_demand: float
    window_open: bool
    battery_low: bool
    observed_at: datetime


@dataclass
class VirtualTrv:
    """One bound virtual TRV with an explainable demand response."""

    device_id: str
    controller_id: str
    zone_index: int
    temperature: float
    target: float = 5.0
    window_open: bool = False
    battery_low: bool = False
    local_override: float | None = None
    proportional_band: float = 4.0

    def __post_init__(self) -> None:
        _validate_temperature(self.temperature)
        _validate_temperature(self.target)
        if not 0 <= self.zone_index <= 255:
            raise ValueError("zone index must fit in one byte")
        if self.proportional_band <= 0:
            raise ValueError("proportional band must be positive")

    @property
    def effective_target(self) -> float:
        return self.local_override if self.local_override is not None else self.target

    @property
    def heat_demand(self) -> float:
        """Return the declared test-world response, clamped to zero through one."""
        if self.window_open:
            return 0.0
        return max(0.0, min(1.0, (self.effective_target - self.temperature) / self.proportional_band))

    def receive_setpoint(self, zone_index: int, target: float) -> bool:
        """Apply a bound-zone target; unrelated zone packets are ignored."""
        _validate_temperature(target)
        if zone_index != self.zone_index:
            return False
        self.target = target
        return True

    def set_temperature(self, temperature: float) -> None:
        _validate_temperature(temperature)
        self.temperature = temperature

    def set_local_override(self, target: float | None) -> None:
        if target is not None:
            _validate_temperature(target)
        self.local_override = target

    def report(self, now: datetime) -> TrvReport:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("report time must be timezone-aware")
        return TrvReport(
            device_id=self.device_id,
            controller_id=self.controller_id,
            zone_index=self.zone_index,
            temperature=self.temperature,
            target=self.effective_target,
            heat_demand=self.heat_demand,
            window_open=self.window_open,
            battery_low=self.battery_low,
            observed_at=now,
        )
