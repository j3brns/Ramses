from datetime import datetime, timezone

import pytest

from ramses_twin.trv import VirtualTrv


def test_bound_setpoint_drives_explainable_proportional_demand() -> None:
    valve = VirtualTrv("04:900027", "12:900487", 1, temperature=18.0)
    assert valve.receive_setpoint(1, 20.0)
    assert valve.heat_demand == 0.5
    valve.set_temperature(20.0)
    assert valve.heat_demand == 0.0


def test_window_and_local_override_change_effective_target_and_demand() -> None:
    valve = VirtualTrv("04:900027", "12:900487", 1, temperature=18.0, target=20.0)
    valve.set_local_override(22.0)
    assert valve.heat_demand == 1.0
    valve.window_open = True
    assert valve.heat_demand == 0.0
    report = valve.report(datetime(2026, 11, 21, tzinfo=timezone.utc))
    assert report.target == 22.0
    assert report.window_open


def test_foreign_zone_is_ignored_and_naive_reports_are_rejected() -> None:
    valve = VirtualTrv("04:900027", "12:900487", 1, temperature=18.0, target=20.0)
    assert not valve.receive_setpoint(2, 22.0)
    assert valve.target == 20.0
    with pytest.raises(ValueError, match="timezone-aware"):
        valve.report(datetime(2026, 11, 21))
