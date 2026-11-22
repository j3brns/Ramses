from datetime import datetime, timedelta, timezone

from ramses_twin.model import SwitchPoint, WeeklySchedule, ZoneController, setpoint_payload
from ramses_twin.mqtt import rx_envelope, topics


def test_setpoint_payload_matches_observed_kitchen_frame() -> None:
    assert setpoint_payload(1, 10.0) == "0103E8"


def test_boost_expires_back_to_schedule() -> None:
    now = datetime(2026, 11, 21, 6, 0, tzinfo=timezone.utc)
    zone = ZoneController("12:900001", 1, scheduled_target=16.0)
    zone.boost(21.0, now + timedelta(hours=1))
    assert zone.target_at(now) == 21.0
    assert zone.target_at(now + timedelta(hours=1)) == 16.0


def test_frame_and_gateway_envelope_follow_test_contract() -> None:
    now = datetime(2026, 11, 21, 6, 0, tzinfo=timezone.utc)
    zone = ZoneController("12:900001", 2, scheduled_target=18.0)
    message = rx_envelope(zone.setpoint_frame(now), now)
    assert message["msg"].endswith("2309 003 020708")
    assert message["ts"] == "2026-11-21T06:00:00+00:00"
    assert topics()["rx"] == "RAMSES/TEST/18:990001/rx"


def test_permanent_override_survives_schedule_edge_until_returned() -> None:
    schedule = WeeklySchedule((
        SwitchPoint(0, 6 * 60, 16.0),
        SwitchPoint(0, 9 * 60, 20.0),
    ))
    zone = ZoneController("12:900001", 1, schedule=schedule)
    zone.set_permanent_override(22.0)

    assert zone.target_at(datetime(2026, 11, 23, 8, 0, tzinfo=timezone.utc)) == 22.0
    assert zone.target_at(datetime(2026, 11, 23, 10, 0, tzinfo=timezone.utc)) == 22.0

    zone.return_to_schedule()
    assert zone.target_at(datetime(2026, 11, 23, 10, 0, tzinfo=timezone.utc)) == 20.0


def test_permanent_override_replaces_temporary_override_and_a_new_boost_replaces_it() -> None:
    now = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    zone = ZoneController("12:900001", 1, scheduled_target=16.0)
    zone.boost(21.0, now + timedelta(hours=1))
    zone.set_permanent_override(22.0)
    assert zone.target_at(now + timedelta(hours=2)) == 22.0

    zone.boost(19.0, now + timedelta(hours=3))
    assert zone.target_at(now) == 19.0


def test_return_to_schedule_is_timezone_aware_across_dst_boundary() -> None:
    schedule = WeeklySchedule((
        SwitchPoint(6, 0, 16.0),
        SwitchPoint(6, 3 * 60, 20.0),
    ))
    zone = ZoneController("12:900001", 1, schedule=schedule)
    zone.set_permanent_override(22.0)
    after_dst_change = datetime(2026, 3, 29, 2, 30, tzinfo=timezone(timedelta(hours=1), "BST"))

    assert zone.target_at(after_dst_change) == 22.0
    zone.return_to_schedule()
    assert zone.target_at(after_dst_change) == 16.0
