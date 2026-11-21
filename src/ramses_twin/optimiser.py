"""Conservative optimum-start planning above the normal zone timer contract."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta

from ramses_twin.model import WeeklySchedule
from ramses_twin.thermal import ThermalModel


@dataclass(frozen=True)
class StartDecision:
    target: float
    scheduled_at: datetime
    start_at: datetime
    lead_minutes: int
    reason: str


def plan_optimum_start(
    schedule: WeeklySchedule,
    model: ThermalModel,
    now: datetime,
    room_temp: float,
    outdoor_temp: float,
    max_lead_minutes: int = 90,
) -> StartDecision | None:
    """Plan the next upward schedule transition, or decline conservatively."""
    current_target = schedule.target_at(now)
    scheduled_at = schedule.next_change_after(now)
    next_target = schedule.target_at(scheduled_at)
    if next_target <= current_target:
        return None
    lead_minutes = model.minutes_to_target(room_temp, next_target, outdoor_temp, max_minutes=max_lead_minutes)
    if lead_minutes is None:
        return None
    return StartDecision(
        target=next_target,
        scheduled_at=scheduled_at,
        start_at=max(now, scheduled_at - timedelta(minutes=lead_minutes)),
        lead_minutes=lead_minutes,
        reason="learned-zone-response",
    )
