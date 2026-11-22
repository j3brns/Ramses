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


def test_timed_boost_is_capped_relative_to_schedule_and_expires() -> None:
    schedule = WeeklySchedule((
        SwitchPoint(0, 6 * 60, 16.0),
        SwitchPoint(0, 9 * 60, 20.0),
    ))
    started = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    zone = ZoneController("12:900001", 1, schedule=schedule)

    zone.timed_boost(3.0, started + timedelta(hours=3), started)
    assert zone.target_at(started) == 19.0
    # The boost remains a relative action at the schedule edge, rather than
    # silently retaining the old 19 C target.
    assert zone.target_at(datetime(2026, 11, 23, 9, 30, tzinfo=timezone.utc)) == 23.0
    assert zone.target_at(started + timedelta(hours=3)) == 20.0


def test_timed_boost_replaces_other_zone_overrides_and_validates_bounds() -> None:
    started = datetime(2026, 11, 23, 7, 0, tzinfo=timezone.utc)
    zone = ZoneController("12:900001", 1, scheduled_target=16.0)
    zone.set_permanent_override(22.0)
    zone.timed_boost(2.0, started + timedelta(hours=1), started)
    assert zone.target_at(started) == 18.0

    for delta in (0.0, 3.1):
        try:
            zone.timed_boost(delta, started + timedelta(hours=1), started)
        except ValueError:
            pass
        else:
            raise AssertionError("out-of-range boost delta was accepted")
    try:
        zone.timed_boost(1.0, started, started)
    except ValueError:
        pass
    else:
        raise AssertionError("non-future boost expiry was accepted")


def test_timed_boost_rejects_naive_times_across_dst_offset() -> None:
    started = datetime(2026, 3, 29, 1, 30, tzinfo=timezone(timedelta(hours=0), "GMT"))
    expires = datetime(2026, 3, 29, 3, 30, tzinfo=timezone(timedelta(hours=1), "BST"))
    zone = ZoneController("12:900001", 1, scheduled_target=34.0)
    zone.timed_boost(3.0, expires, started)
    # The requested delta is legal, but the absolute test-world target stays bounded.
    assert zone.target_at(started) == 35.0
    try:
        zone.timed_boost(1.0, expires, datetime(2026, 3, 29, 1, 30))
    except ValueError:
        pass
    else:
        raise AssertionError("naive boost start was accepted")


def test_next_change_skips_same_target_day_start_marker() -> None:
    schedule = WeeklySchedule((
        SwitchPoint(0, 0, 16.0),
        SwitchPoint(0, 6 * 60, 20.0),
        SwitchPoint(1, 0, 20.0),
        SwitchPoint(1, 9 * 60, 16.0),
    ))
    monday_evening = datetime(2026, 11, 23, 23, 0, tzinfo=timezone.utc)

    assert schedule.next_change_after(monday_evening) == datetime(
        2026, 11, 24, 9, 0, tzinfo=timezone.utc
    )


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
