"""Pure, test-world whole-system programmer actions.

This module resolves an action over a declared collection of zone controllers.
It has no persistence, transport, Home Assistant, or RF side effects.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from ramses_twin.model import ZoneController, setpoint_payload


AWAY_TARGET = 15.0
SATURDAY = 5


def _require_aware(value: datetime, label: str) -> None:
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{label} must be timezone-aware")


@dataclass
class Programmer:
    """Resolve test-world whole-system state over a fixed set of zones.

    A timed whole-system action has higher precedence than every zone-local
    override, but it does not erase zone state.  Away and Day Off replace each
    other, so there is never an ambiguous pair of active whole-system actions.
    On cancellation or expiry each zone immediately resumes its independently
    applicable target.
    """

    zones: dict[str, ZoneController]
    away_until: datetime | None = None
    day_off_until: datetime | None = None

    def __post_init__(self) -> None:
        if not self.zones:
            raise ValueError("a programmer needs at least one named zone")
        if any(not name.strip() for name in self.zones):
            raise ValueError("zone names must be non-empty")

    def start_away(self, until: datetime, now: datetime) -> None:
        """Apply 15 C to every declared zone until the explicit expiry."""
        _require_aware(now, "Away time")
        _require_aware(until, "Away expiry")
        duration = until - now
        if not timedelta(days=1) <= duration <= timedelta(days=99):
            raise ValueError("Away duration must be between 1 and 99 days")
        self.day_off_until = None
        self.away_until = until

    def cancel_away(self) -> None:
        """Return all zones immediately to their independent state."""
        self.away_until = None

    def start_day_off(self, until: datetime, now: datetime) -> None:
        """Apply each weekly zone's Saturday programme until ``until``.

        Day Off needs a weekly programme for every declared zone.  Fixed
        targets have no Saturday programme, so rejecting them keeps this model
        decision explicit rather than inventing one.
        """
        _require_aware(now, "Day Off time")
        _require_aware(until, "Day Off expiry")
        duration = until - now
        if not timedelta(days=1) <= duration <= timedelta(days=99):
            raise ValueError("Day Off duration must be between 1 and 99 days")
        if any(zone.schedule is None for zone in self.zones.values()):
            raise ValueError("Day Off requires a weekly schedule for every zone")
        self.away_until = None
        self.day_off_until = until

    def cancel_day_off(self) -> None:
        """Return all zones immediately to their independent state."""
        self.day_off_until = None

    def away_active(self, now: datetime) -> bool:
        _require_aware(now, "programmer time")
        if self.away_until is not None and now >= self.away_until:
            self.away_until = None
        return self.away_until is not None

    def day_off_active(self, now: datetime) -> bool:
        _require_aware(now, "programmer time")
        if self.day_off_until is not None and now >= self.day_off_until:
            self.day_off_until = None
        return self.day_off_until is not None

    def target_at(self, zone_name: str, now: datetime) -> float:
        """Return the effective target for one declared zone at ``now``."""
        try:
            zone = self.zones[zone_name]
        except KeyError as error:
            raise KeyError(f"unknown zone: {zone_name}") from error
        if self.away_active(now):
            return AWAY_TARGET
        if self.day_off_active(now):
            assert zone.schedule is not None  # start_day_off validates this.
            return zone.schedule.target_for_weekday_at(SATURDAY, now)
        return zone.target_at(now)

    def setpoint_frame(self, zone_name: str, now: datetime) -> str:
        """Return one test-world frame using whole-system precedence."""
        zone = self.zones[zone_name]
        payload = setpoint_payload(zone.zone_index, self.target_at(zone_name, now))
        return f" I --- --:------ --:------ {zone.controller_id} 2309 003 {payload}"
