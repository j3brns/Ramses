from datetime import datetime, timedelta, timezone

import pytest

from ramses_twin.model import SwitchPoint, WeeklySchedule, ZoneController
from ramses_twin.programmer import AWAY_TARGET, ECO_REDUCTION, Programmer


def _programmer() -> tuple[Programmer, ZoneController, ZoneController]:
    kitchen = ZoneController("12:900001", 1, scheduled_target=18.0)
    lounge = ZoneController("12:900002", 2, scheduled_target=19.0)
    return Programmer({"kitchen": kitchen, "lounge": lounge}), kitchen, lounge


def test_away_precedes_each_zone_override_without_erasing_it() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    programmer, kitchen, lounge = _programmer()
    kitchen.set_permanent_override(22.0)
    lounge.boost(21.0, now + timedelta(hours=2))

    programmer.start_away(now + timedelta(days=2), now)
    assert programmer.target_at("kitchen", now) == AWAY_TARGET
    assert programmer.target_at("lounge", now) == AWAY_TARGET

    programmer.cancel_away()
    assert programmer.target_at("kitchen", now) == 22.0
    assert programmer.target_at("lounge", now) == 21.0


def test_away_expiry_returns_to_each_zone_current_target_and_frame() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    programmer, kitchen, _ = _programmer()
    kitchen.set_permanent_override(22.0)
    programmer.start_away(now + timedelta(days=2), now)

    assert programmer.setpoint_frame("kitchen", now).endswith("2309 003 0105DC")
    assert programmer.target_at("kitchen", now + timedelta(days=2)) == 22.0
    assert programmer.away_until is None


def test_away_requires_aware_future_times_and_known_zone() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    programmer, _, _ = _programmer()

    with pytest.raises(ValueError, match="timezone-aware"):
        programmer.start_away(now.replace(tzinfo=None) + timedelta(hours=1), now)
    with pytest.raises(ValueError, match="between 1 and 99"):
        programmer.start_away(now, now)
    with pytest.raises(ValueError, match="between 1 and 99"):
        programmer.start_away(now + timedelta(days=100), now)
    with pytest.raises(KeyError, match="unknown zone"):
        programmer.target_at("bedroom", now)


def _scheduled_programmer() -> tuple[Programmer, ZoneController, ZoneController]:
    schedule = WeeklySchedule(
        (
            SwitchPoint(4, 18 * 60, 17.0),  # Friday carry-in for early Saturday
            SwitchPoint(5, 8 * 60, 20.0),
            SwitchPoint(5, 22 * 60, 16.0),
        )
    )
    kitchen = ZoneController("12:900001", 1, schedule=schedule)
    lounge = ZoneController("12:900002", 2, schedule=schedule)
    return Programmer({"kitchen": kitchen, "lounge": lounge}), kitchen, lounge


def test_day_off_uses_saturday_programme_and_preserves_zone_state() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)  # Monday
    programmer, kitchen, lounge = _scheduled_programmer()
    kitchen.set_permanent_override(22.0)
    lounge.boost(21.0, now + timedelta(hours=2))

    programmer.start_day_off(now + timedelta(days=2), now)
    assert programmer.target_at("kitchen", now) == 17.0
    assert programmer.target_at("lounge", now.replace(hour=9)) == 20.0

    programmer.cancel_day_off()
    assert programmer.target_at("kitchen", now) == 22.0
    assert programmer.target_at("lounge", now) == 21.0


def test_day_off_replaces_away_and_expiry_reveals_current_zone_target() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    programmer, kitchen, _ = _scheduled_programmer()
    kitchen.set_permanent_override(22.0)
    programmer.start_away(now + timedelta(days=2), now)
    programmer.start_day_off(now + timedelta(days=1), now)

    assert programmer.away_until is None
    assert programmer.target_at("kitchen", now) == 17.0
    assert programmer.target_at("kitchen", now + timedelta(days=1)) == 22.0
    assert programmer.day_off_until is None


def test_day_off_requires_schedules_and_aware_valid_duration() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    fixed, _, _ = _programmer()
    scheduled, _, _ = _scheduled_programmer()

    with pytest.raises(ValueError, match="weekly schedule"):
        fixed.start_day_off(now + timedelta(days=1), now)
    with pytest.raises(ValueError, match="timezone-aware"):
        scheduled.start_day_off(now.replace(tzinfo=None) + timedelta(days=1), now)
    with pytest.raises(ValueError, match="between 1 and 99"):
        scheduled.start_day_off(now, now)


def test_eco_reduces_each_current_zone_target_without_erasing_zone_state() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    programmer, kitchen, lounge = _programmer()
    kitchen.set_permanent_override(22.0)
    lounge.boost(18.0, now + timedelta(hours=3))

    programmer.start_eco(now + timedelta(hours=2), now)
    assert programmer.target_at("kitchen", now) == 22.0 - ECO_REDUCTION
    assert programmer.target_at("lounge", now) == 18.0 - ECO_REDUCTION

    programmer.cancel_eco()
    assert programmer.target_at("kitchen", now) == 22.0
    assert programmer.target_at("lounge", now) == 18.0


def test_eco_follows_schedule_edges_clamps_and_replaces_whole_system_actions() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    schedule = WeeklySchedule((
        SwitchPoint(0, 6 * 60, 7.0),
        SwitchPoint(0, 9 * 60, 20.0),
    ))
    kitchen = ZoneController("12:900001", 1, schedule=schedule)
    lounge = ZoneController("12:900002", 2, schedule=schedule)
    programmer = Programmer({"kitchen": kitchen, "lounge": lounge})
    monday_early = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    programmer.start_away(monday_early + timedelta(days=2), monday_early)
    programmer.start_eco(monday_early + timedelta(hours=4), monday_early)

    assert programmer.away_until is None
    assert programmer.target_at("kitchen", monday_early) == 5.0
    assert programmer.target_at("kitchen", monday_early.replace(hour=10)) == 17.0
    assert programmer.target_at("kitchen", monday_early + timedelta(hours=4)) == 20.0
    assert programmer.eco_until is None


def test_eco_requires_aware_one_to_24_hour_duration() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    programmer, _, _ = _programmer()

    with pytest.raises(ValueError, match="timezone-aware"):
        programmer.start_eco(now.replace(tzinfo=None) + timedelta(hours=1), now)
    with pytest.raises(ValueError, match="between 1 and 24"):
        programmer.start_eco(now + timedelta(minutes=59), now)
    with pytest.raises(ValueError, match="between 1 and 24"):
        programmer.start_eco(now + timedelta(hours=25), now)
