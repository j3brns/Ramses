from datetime import datetime, timedelta, timezone

import pytest

from ramses_twin.ha_adapter import TestAdapterDescriptor
from ramses_twin.household import HOUSEHOLD_ZONES, boost_until_next, build_household_runtime, cancel_boost
from ramses_twin.model import WeeklySchedule, SwitchPoint
from ramses_twin.store import JsonStateStore


def test_cmq_boost_isolated_recovers_expires_and_cancels(tmp_path):
    now = datetime(2026, 11, 23, 7, tzinfo=timezone.utc)
    schedules = {
        zone: WeeklySchedule((SwitchPoint(0, 360, 16), SwitchPoint(0, 480, 19+i)))
        for i, zone in enumerate(HOUSEHOLD_ZONES)
    }
    # Make expiry observable as a change away from the temporary 22 C.
    schedules["cmq_jgb"] = schedules["kitchen"]
    store = JsonStateStore(tmp_path / "state.json")
    runtime = build_household_runtime(schedules, store)
    before = runtime.recovery_frames(now)
    descriptor = TestAdapterDescriptor("18:990001", "cmq_jgb")
    command = boost_until_next(descriptor, runtime, 22, now)
    assert command.expires_at == now + timedelta(hours=1)
    assert command.payload["msg"].endswith("12:900002 2309 003 020898")
    assert HOUSEHOLD_ZONES["cmq_jgb"].valves == ("040",)
    assert command.topic == "RAMSES/TEST/18:990001/tx"
    restarted = build_household_runtime(schedules, store)
    restarted.restore(now + timedelta(minutes=1))
    frames = restarted.recovery_frames(now)
    assert [zone for zone in before if before[zone] != frames[zone]] == ["cmq_jgb"]
    assert restarted.coordinators["cmq_jgb"].controller.target_at(command.expires_at) == 19
    restarted.restore(now + timedelta(days=1))
    assert restarted.coordinators["cmq_jgb"].controller.override_target is None
    restarted.restore(now)
    boost_until_next(descriptor, restarted, 22, now)
    assert cancel_boost(restarted, "cmq_jgb", now) == before["cmq_jgb"]
    restarted.restore(now)
    assert restarted.recovery_frames(now) == before


def test_rejects_incomplete_programmes_and_unknown_expiry(tmp_path):
    store = JsonStateStore(tmp_path / "state.json")
    with pytest.raises(ValueError, match="four household zones"):
        build_household_runtime({}, store)
    flat = WeeklySchedule((SwitchPoint(0, 0, 16),))
    runtime = build_household_runtime(dict.fromkeys(HOUSEHOLD_ZONES, flat), store)
    with pytest.raises(ValueError, match="future programmed"):
        boost_until_next(TestAdapterDescriptor("18:990001", "cmq_jgb"), runtime, 22,
                         datetime(2026, 11, 23, tzinfo=timezone.utc))
