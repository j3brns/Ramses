"""Pure test-only climate-command contract tests."""

from datetime import datetime, timedelta, timezone

import pytest

from ramses_twin.coordinator import ZoneCoordinator
from ramses_twin.ha_adapter import TestAdapterDescriptor, apply_test_temporary_override
from ramses_twin.model import SwitchPoint, WeeklySchedule, ZoneController
from ramses_twin.thermal import ThermalModel


def _coordinator() -> ZoneCoordinator:
    schedule = WeeklySchedule(
        (
            SwitchPoint(weekday=0, minute_of_day=360, target=16.0),
            SwitchPoint(weekday=0, minute_of_day=480, target=21.0),
        )
    )
    return ZoneCoordinator(ZoneController("12:900001", 1, schedule=schedule), ThermalModel())


def test_temporary_climate_override_changes_only_virtual_zone_and_returns_test_tx() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    until = now + timedelta(hours=1)
    coordinator = _coordinator()
    command = apply_test_temporary_override(
        TestAdapterDescriptor("18:990001", "Kitchen"), coordinator, 22.0, until, now
    )

    assert command.entity_id == "climate.ramses_test_kitchen"
    assert command.topic == "RAMSES/TEST/18:990001/tx"
    assert command.payload["msg"].endswith("010898")
    assert command.payload["ts"] == now.isoformat()
    assert coordinator.controller.target_at(now) == 22.0
    assert coordinator.controller.target_at(until) == 21.0


@pytest.mark.parametrize(
    "target, until, now",
    [
        (22.0, datetime(2026, 11, 23, 8, 0), datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)),
        (22.0, datetime(2026, 11, 23, 6, 0, tzinfo=timezone.utc), datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)),
        (40.0, datetime(2026, 11, 23, 8, 0, tzinfo=timezone.utc), datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)),
    ],
)
def test_temporary_climate_override_rejects_invalid_input(
    target: float,
    until: datetime,
    now: datetime,
) -> None:
    coordinator = _coordinator()
    with pytest.raises(ValueError):
        apply_test_temporary_override(TestAdapterDescriptor("18:990001", "Kitchen"), coordinator, target, until, now)
    assert coordinator.controller.override_target is None
