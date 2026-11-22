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


def test_recovery_recomputes_and_reissues_current_targets(tmp_path) -> None:
    schedule = WeeklySchedule((SwitchPoint(0, 360, 16.0), SwitchPoint(0, 420, 21.0)))
    kitchen = ZoneController("12:900001", 1, schedule=schedule)
    lounge = ZoneController("12:900002", 2, scheduled_target=18.0)
    now = datetime(2026, 11, 23, 6, 30, tzinfo=timezone.utc)
    kitchen.boost(20.0, now + timedelta(minutes=5))
    runtime = TwinRuntime(
        {
            "lounge": ZoneCoordinator(lounge, ThermalModel()),
            "kitchen": ZoneCoordinator(kitchen, ThermalModel()),
        },
        JsonStateStore(tmp_path / "state.json"),
    )

    assert runtime.recovery_frames(now) == {
        "kitchen": " I --- --:------ --:------ 12:900001 2309 003 0107D0",
        "lounge": " I --- --:------ --:------ 12:900002 2309 003 020708",
    }
    assert runtime.recovery_frames(now + timedelta(minutes=5))["kitchen"].endswith("010640")


def test_recovery_requires_timezone_aware_time(tmp_path) -> None:
    runtime = TwinRuntime(
        {"kitchen": ZoneCoordinator(ZoneController("12:900001", 1, scheduled_target=16.0), ThermalModel())},
        JsonStateStore(tmp_path / "state.json"),
    )

    try:
        runtime.recovery_frames(datetime(2026, 11, 23, 6, 0))
    except ValueError as error:
        assert str(error) == "recovery time must be timezone-aware"
    else:
        raise AssertionError("naive recovery time must be rejected")
