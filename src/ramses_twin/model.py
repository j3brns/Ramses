"""Small, deterministic CM67z-zone state model.

This package never transmits RF. It only models scheduler decisions and the
frames that a later transport adapter may publish to RAMSES/TEST.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, time, timedelta


def setpoint_payload(zone_index: int, temperature: float) -> str:
    """Encode the observed 2309 payload: zone byte + temperature in centi-degrees."""
    if not 0 <= zone_index <= 255:
        raise ValueError("zone index must fit in one byte")
    if not 5.0 <= temperature <= 35.0:
        raise ValueError("temperature must be between 5 and 35 C")
    return f"{zone_index:02X}{round(temperature * 100):04X}"


def _validate_temperature(temperature: float) -> None:
    if not 5.0 <= temperature <= 35.0:
        raise ValueError("temperature must be between 5 and 35 C")


@dataclass(frozen=True, order=True)
class SwitchPoint:
    """One weekly wall-clock setpoint change, where Monday is day zero."""

    weekday: int
    minute_of_day: int
    target: float

    def __post_init__(self) -> None:
        if not 0 <= self.weekday <= 6:
            raise ValueError("weekday must be between Monday (0) and Sunday (6)")
        if not 0 <= self.minute_of_day < 24 * 60:
            raise ValueError("minute_of_day must be between 0 and 1439")
        _validate_temperature(self.target)


@dataclass(frozen=True)
class WeeklySchedule:
    """A repeating local-time schedule with at least one weekly switch point."""

    switchpoints: tuple[SwitchPoint, ...]

    def __post_init__(self) -> None:
        if not self.switchpoints:
            raise ValueError("a weekly schedule needs at least one switch point")
        keys = [(point.weekday, point.minute_of_day) for point in self.switchpoints]
        if len(keys) != len(set(keys)):
            raise ValueError("a weekly schedule cannot have duplicate switch points")

    @staticmethod
    def _require_aware(now: datetime) -> None:
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("schedule time must be timezone-aware")

    @staticmethod
    def _at_local_time(now: datetime, days_from_now: int, point: SwitchPoint) -> datetime:
        date = (now + timedelta(days=days_from_now)).date()
        return datetime.combine(date, time(point.minute_of_day // 60, point.minute_of_day % 60), now.tzinfo)

    def target_at(self, now: datetime) -> float:
        """Return the last local weekly target that has taken effect by ``now``."""
        self._require_aware(now)
        candidates = []
        for days_back in range(7):
            weekday = (now.weekday() - days_back) % 7
            for point in self.switchpoints:
                if point.weekday != weekday:
                    continue
                candidate = self._at_local_time(now, -days_back, point)
                if candidate <= now:
                    candidates.append((candidate, point.target))
        if not candidates:  # A schedule repeats weekly, so this is defensive only.
            raise RuntimeError("no active schedule switch point")
        return max(candidates, key=lambda item: item[0])[1]

    def next_change_after(self, now: datetime) -> datetime:
        """Return the first scheduled switch strictly after ``now``."""
        self._require_aware(now)
        candidates = []
        for days_forward in range(8):
            weekday = (now.weekday() + days_forward) % 7
            for point in self.switchpoints:
                if point.weekday != weekday:
                    continue
                candidate = self._at_local_time(now, days_forward, point)
                if candidate > now:
                    candidates.append(candidate)
        if not candidates:  # A repeating weekly schedule always has a next point.
            raise RuntimeError("no next schedule switch point")
        return min(candidates)


@dataclass
class ZoneController:
    """One CM67z zone with a scheduled target and optional temporary boost."""

    controller_id: str
    zone_index: int
    scheduled_target: float | None = None
    schedule: WeeklySchedule | None = None
    override_target: float | None = None
    override_until: datetime | None = None

    def __post_init__(self) -> None:
        if self.schedule is None and self.scheduled_target is None:
            raise ValueError("a zone requires either a fixed target or a weekly schedule")
        if self.scheduled_target is not None:
            _validate_temperature(self.scheduled_target)

    def scheduled_target_at(self, now: datetime) -> float:
        if self.schedule is not None:
            return self.schedule.target_at(now)
        assert self.scheduled_target is not None
        return self.scheduled_target

    def target_at(self, now: datetime) -> float:
        if self.override_target is not None and self.override_until and now < self.override_until:
            return self.override_target
        self.clear_expired_override(now)
        return self.scheduled_target_at(now)

    def boost(self, target: float, until: datetime) -> None:
        if until.tzinfo is None:
            raise ValueError("override expiry must be timezone-aware")
        _validate_temperature(target)
        self.override_target = target
        self.override_until = until

    def boost_until_next_switch(self, target: float, now: datetime) -> datetime:
        """Apply the standard temporary override and return its exact expiry."""
        if self.schedule is None:
            raise ValueError("a boost-until-next-switch needs a weekly schedule")
        until = self.schedule.next_change_after(now)
        self.boost(target, until)
        return until

    def clear_expired_override(self, now: datetime) -> None:
        if self.override_until and now >= self.override_until:
            self.override_target = None
            self.override_until = None

    def setpoint_frame(self, now: datetime) -> str:
        target = self.target_at(now)
        payload = setpoint_payload(self.zone_index, target)
        return f" I --- --:------ --:------ {self.controller_id} 2309 003 {payload}"
