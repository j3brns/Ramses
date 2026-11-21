from datetime import datetime, timezone

from ramses_twin.coordinator import ZoneCoordinator
from ramses_twin.model import SwitchPoint, WeeklySchedule, ZoneController
from ramses_twin.optimiser import plan_optimum_start
from ramses_twin.thermal import ThermalModel


def model() -> ThermalModel:
    return ThermalModel(heat_rate=0.06, loss_rate=0.002, heat_samples=3, loss_samples=3)


def schedule() -> WeeklySchedule:
    return WeeklySchedule((SwitchPoint(0, 6 * 60, 16.0), SwitchPoint(0, 7 * 60, 20.0), SwitchPoint(0, 9 * 60, 16.0)))


def test_optimiser_plans_only_the_next_upward_transition() -> None:
    now = datetime(2026, 11, 23, 6, 30, tzinfo=timezone.utc)
    decision = plan_optimum_start(schedule(), model(), now, room_temp=18.0, outdoor_temp=5.0)
    assert decision is not None
    assert decision.target == 20.0
    assert decision.scheduled_at == datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    assert now <= decision.start_at <= decision.scheduled_at


def test_coordinator_emits_one_early_test_frame_only_when_due() -> None:
    now = datetime(2026, 11, 23, 6, 59, tzinfo=timezone.utc)
    coordinator = ZoneCoordinator(ZoneController("12:900001", 1, schedule=schedule()), model())
    frame = coordinator.apply_due_start(now, room_temp=18.0, outdoor_temp=5.0)
    assert frame is not None and "2309 003" in frame
    assert coordinator.apply_due_start(now, room_temp=18.0, outdoor_temp=5.0) is None
