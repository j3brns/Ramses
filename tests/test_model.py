from datetime import datetime, timedelta, timezone

from ramses_twin.model import ZoneController, setpoint_payload
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
