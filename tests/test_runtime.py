import json
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
    restored.restore(datetime(2026, 11, 23, 6, 0, tzinfo=timezone.utc))
    assert restored.coordinators["kitchen"].thermal_model.loss_samples == 1


def test_runtime_override_command_checkpoints_and_expiry_is_pruned(tmp_path) -> None:
    now = datetime(2026, 11, 23, 6, 10, tzinfo=timezone.utc)
    store = JsonStateStore(tmp_path / "state.json")
    runtime = TwinRuntime(
        {"kitchen": ZoneCoordinator(ZoneController("12:900001", 1, scheduled_target=16.0), ThermalModel())}, store
    )
    assert runtime.apply_temporary_override("kitchen", 21.0, now + timedelta(minutes=5), now).endswith("010834")

    after_restart = TwinRuntime(
        {"kitchen": ZoneCoordinator(ZoneController("12:900001", 1, scheduled_target=16.0), ThermalModel())}, store
    )
    after_restart.restore(now + timedelta(minutes=5))
    second_restart = TwinRuntime(
        {"kitchen": ZoneCoordinator(ZoneController("12:900001", 1, scheduled_target=16.0), ThermalModel())}, store
    )
    second_restart.restore(now + timedelta(minutes=5))
    assert second_restart.recovery_frames(now + timedelta(minutes=5))["kitchen"].endswith("010640")


def test_runtime_rejects_same_name_state_for_reconfigured_zone(tmp_path) -> None:
    now = datetime(2026, 11, 23, 6, 0, tzinfo=timezone.utc)
    store = JsonStateStore(tmp_path / "state.json")
    original = TwinRuntime(
        {"kitchen": ZoneCoordinator(ZoneController("12:900001", 1, scheduled_target=16.0), ThermalModel())}, store
    )
    original.apply_temporary_override("kitchen", 21.0, now + timedelta(minutes=10), now)
    reconfigured = TwinRuntime(
        {"kitchen": ZoneCoordinator(ZoneController("12:900099", 2, scheduled_target=16.0), ThermalModel())}, store
    )
    reconfigured.restore(now)
    assert reconfigured.recovery_frames(now)["kitchen"].endswith("020640")


def test_runtime_checkpoints_due_optimiser_start(tmp_path) -> None:
    now = datetime(2026, 11, 23, 6, 10, tzinfo=timezone.utc)
    schedule = WeeklySchedule((SwitchPoint(0, 0, 16.0), SwitchPoint(0, 390, 21.0)))
    controller = ZoneController("12:900001", 1, schedule=schedule)
    model = ThermalModel(heat_rate=0.2, loss_rate=0.01, heat_samples=3, loss_samples=3)
    store = JsonStateStore(tmp_path / "state.json")
    runtime = TwinRuntime({"kitchen": ZoneCoordinator(controller, model)}, store)
    assert runtime.due_frame("kitchen", now, 16.0, 10.0) is not None
    restored = TwinRuntime(
        {"kitchen": ZoneCoordinator(ZoneController("12:900001", 1, schedule=schedule), ThermalModel())}, store
    )
    restored.restore(now)
    assert restored.recovery_frames(now)["kitchen"].endswith("010834")


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


def test_runtime_restores_permanent_override_across_restart(tmp_path) -> None:
    now = datetime(2026, 11, 23, 6, 0, tzinfo=timezone.utc)
    original = ZoneController("12:900001", 1, scheduled_target=16.0)
    original.set_permanent_override(21.0)
    store = JsonStateStore(tmp_path / "state.json")
    TwinRuntime({"kitchen": ZoneCoordinator(original, ThermalModel())}, store).checkpoint()

    restored_controller = ZoneController("12:900001", 1, scheduled_target=16.0)
    restored = TwinRuntime({"kitchen": ZoneCoordinator(restored_controller, ThermalModel())}, store)
    restored.restore(now)

    assert restored.recovery_frames(now)["kitchen"].endswith("010834")


def test_runtime_restores_active_temporary_and_discards_expired_override(tmp_path) -> None:
    now = datetime(2026, 11, 23, 6, 0, tzinfo=timezone.utc)
    active = ZoneController("12:900001", 1, scheduled_target=16.0)
    active.boost(21.0, now + timedelta(minutes=15))
    expired = ZoneController("12:900002", 2, scheduled_target=18.0)
    expired.boost(22.0, now + timedelta(minutes=5))
    store = JsonStateStore(tmp_path / "state.json")
    TwinRuntime(
        {"active": ZoneCoordinator(active, ThermalModel()), "expired": ZoneCoordinator(expired, ThermalModel())}, store
    ).checkpoint()

    active_after = ZoneController("12:900001", 1, scheduled_target=16.0)
    expired_after = ZoneController("12:900002", 2, scheduled_target=18.0)
    restored = TwinRuntime(
        {"active": ZoneCoordinator(active_after, ThermalModel()), "expired": ZoneCoordinator(expired_after, ThermalModel())}, store
    )
    restored.restore(now + timedelta(minutes=5))

    frames = restored.recovery_frames(now + timedelta(minutes=5))
    assert frames["active"].endswith("010834")
    assert frames["expired"].endswith("020708")


def test_runtime_restores_timed_boost_and_ignores_retired_zone_state(tmp_path) -> None:
    now = datetime(2026, 11, 23, 6, 0, tzinfo=timezone.utc)
    original = ZoneController("12:900001", 1, scheduled_target=16.0)
    original.timed_boost(2.0, now + timedelta(minutes=30), now)
    store = JsonStateStore(tmp_path / "state.json")
    runtime = TwinRuntime({"kitchen": ZoneCoordinator(original, ThermalModel())}, store)
    runtime.checkpoint()
    document = json.loads(store.path.read_text(encoding="utf-8"))
    document["overrides"]["retired-zone"] = document["overrides"]["kitchen"]
    store.path.write_text(json.dumps(document), encoding="utf-8")

    after = ZoneController("12:900001", 1, scheduled_target=16.0)
    restored = TwinRuntime({"kitchen": ZoneCoordinator(after, ThermalModel())}, store)
    restored.restore(now)
    assert restored.recovery_frames(now)["kitchen"].endswith("010708")


def test_runtime_ignores_invalid_override_for_configured_zone(tmp_path) -> None:
    now = datetime(2026, 11, 23, 6, 0, tzinfo=timezone.utc)
    controller = ZoneController("12:900001", 1, scheduled_target=16.0)
    controller.set_permanent_override(21.0)
    store = JsonStateStore(tmp_path / "state.json")
    TwinRuntime({"kitchen": ZoneCoordinator(controller, ThermalModel())}, store).checkpoint()
    document = json.loads(store.path.read_text(encoding="utf-8"))
    document["overrides"]["kitchen"] = {"wrong": "shape"}
    store.path.write_text(json.dumps(document), encoding="utf-8")

    restored = TwinRuntime(
        {"kitchen": ZoneCoordinator(ZoneController("12:900001", 1, scheduled_target=16.0), ThermalModel())}, store
    )
    restored.restore(now)
    assert restored.recovery_frames(now)["kitchen"].endswith("010640")


def test_runtime_reads_legacy_thermal_only_state(tmp_path) -> None:
    store = JsonStateStore(tmp_path / "state.json")
    model = ThermalModel(loss_samples=1, loss_rate=0.2)
    store.path.write_text(
        json.dumps({"format": 1, "zones": {"kitchen": model.to_state()}}), encoding="utf-8"
    )
    restored = TwinRuntime(
        {"kitchen": ZoneCoordinator(ZoneController("12:900001", 1, scheduled_target=16.0), ThermalModel())}, store
    )
    restored.restore(datetime(2026, 11, 23, 6, 0, tzinfo=timezone.utc))
    assert restored.coordinators["kitchen"].thermal_model.loss_samples == 1
