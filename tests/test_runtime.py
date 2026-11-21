from datetime import datetime, timedelta, timezone

from ramses_twin.coordinator import ZoneCoordinator
from ramses_twin.model import SwitchPoint, WeeklySchedule, ZoneController
from ramses_twin.runtime import TwinRuntime
from ramses_twin.store import JsonStateStore
from ramses_twin.thermal import Observation, ThermalModel


def test_runtime_learns_and_restores_zone_model(tmp_path) -> None:
    schedule = WeeklySchedule((SwitchPoint(0, 360, 16.0),))
    controller = ZoneController("12:900001", 1, schedule=schedule)
    store = JsonStateStore(tmp_path / "state.json")
    runtime = TwinRuntime({"kitchen": ZoneCoordinator(controller, ThermalModel())}, store)
    base = datetime(2026, 11, 23, 6, 0, tzinfo=timezone.utc)
    runtime.observe("kitchen", Observation(base, 20.0, 10.0, 0.0, False))
    result = runtime.observe("kitchen", Observation(base + timedelta(minutes=10), 19.8, 10.0, 0.0, False))
    assert result is not None and result.accepted
    restored = TwinRuntime({"kitchen": ZoneCoordinator(controller, ThermalModel())}, store)
    restored.restore()
    assert restored.coordinators["kitchen"].thermal_model.loss_samples == 1
