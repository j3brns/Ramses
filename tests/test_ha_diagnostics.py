"""Contract tests for the pure, read-only HA test-zone diagnostics projection."""

from datetime import datetime, timezone

import pytest

from ramses_twin.coordinator import ZoneCoordinator
from ramses_twin import ha_adapter
from ramses_twin.model import SwitchPoint, WeeklySchedule, ZoneController
from ramses_twin.thermal import ThermalModel


def _coordinator(model: ThermalModel | None = None) -> ZoneCoordinator:
    schedule = WeeklySchedule(
        (
            SwitchPoint(weekday=0, minute_of_day=360, target=16.0),
            SwitchPoint(weekday=0, minute_of_day=480, target=21.0),
        )
    )
    return ZoneCoordinator(
        controller=ZoneController("12:900001", zone_index=1, schedule=schedule),
        thermal_model=model or ThermalModel(),
    )


def test_diagnostics_have_test_only_entity_names_and_do_not_apply_a_control() -> None:
    descriptor = ha_adapter.TestAdapterDescriptor("18:999999", "kitchen")
    assert descriptor.diagnostic_entity_ids == {
        "effective_target": "sensor.ramses_test_kitchen_effective_target",
        "next_change": "sensor.ramses_test_kitchen_next_change",
        "optimiser_ready": "binary_sensor.ramses_test_kitchen_optimiser_ready",
        "planned_start": "sensor.ramses_test_kitchen_planned_start",
    }

    coordinator = _coordinator()
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    state = ha_adapter.read_test_zone_diagnostics(coordinator, now, room_temp=18.0, outdoor_temp=5.0)

    assert state.effective_target == 16.0
    assert state.next_change == datetime(2026, 11, 23, 8, 0, tzinfo=timezone.utc)
    assert state.optimiser_ready is False
    assert state.planned_start is None
    assert coordinator.controller.override_target is None
    assert coordinator.controller.override_until is None


def test_diagnostics_reports_a_planned_start_only_when_the_model_is_ready() -> None:
    model = ThermalModel(
        heat_rate=0.2,
        loss_rate=0.01,
        heat_samples=3,
        loss_samples=3,
    )
    coordinator = _coordinator(model)
    now = datetime(2026, 11, 23, 7, 30, tzinfo=timezone.utc)

    state = ha_adapter.read_test_zone_diagnostics(coordinator, now, room_temp=18.0, outdoor_temp=5.0)

    assert state.optimiser_ready is True
    assert state.next_change == datetime(2026, 11, 23, 8, 0, tzinfo=timezone.utc)
    assert state.planned_start is not None
    assert state.planned_start <= state.next_change
    assert coordinator.controller.override_target is None
    assert coordinator.controller.override_until is None


def test_diagnostics_rejects_a_naive_clock() -> None:
    with pytest.raises(ValueError, match="timezone-aware"):
        ha_adapter.read_test_zone_diagnostics(_coordinator(), datetime(2026, 11, 23, 7, 0), 18.0, 5.0)
