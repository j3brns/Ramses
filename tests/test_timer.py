from datetime import datetime, timezone

import pytest

from ramses_twin.model import SwitchPoint, WeeklySchedule, ZoneController


def schedule() -> WeeklySchedule:
    return WeeklySchedule(
        (
            SwitchPoint(0, 6 * 60 + 30, 20.0),  # Monday 06:30
            SwitchPoint(0, 9 * 60, 16.0),       # Monday 09:00
            SwitchPoint(0, 17 * 60, 21.0),      # Monday 17:00
            SwitchPoint(0, 22 * 60 + 30, 12.0), # Monday 22:30
        )
    )


def test_weekly_schedule_selects_active_and_next_target() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)  # Monday
    timetable = schedule()
    assert timetable.target_at(now) == 20.0
    assert timetable.next_change_after(now) == datetime(2026, 11, 23, 9, 0, tzinfo=timezone.utc)
    assert timetable.target_at(datetime(2026, 11, 24, 8, 0, tzinfo=timezone.utc)) == 12.0


def test_boost_until_next_switch_returns_to_timetable() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    zone = ZoneController("12:900001", 1, schedule=schedule())
    assert zone.boost_until_next_switch(22.0, now) == datetime(2026, 11, 23, 9, 0, tzinfo=timezone.utc)
    assert zone.target_at(now) == 22.0
    assert zone.target_at(datetime(2026, 11, 23, 9, 0, tzinfo=timezone.utc)) == 16.0


def test_timer_rejects_naive_clock_and_duplicate_switches() -> None:
    timetable = schedule()
    with pytest.raises(ValueError, match="timezone-aware"):
        timetable.target_at(datetime(2026, 11, 23, 7, 0))
    with pytest.raises(ValueError, match="duplicate"):
        WeeklySchedule((SwitchPoint(0, 420, 20.0), SwitchPoint(0, 420, 16.0)))
