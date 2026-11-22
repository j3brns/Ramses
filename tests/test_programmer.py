from datetime import datetime, timedelta, timezone

import pytest

from ramses_twin.model import ZoneController
from ramses_twin.programmer import AWAY_TARGET, Programmer


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
