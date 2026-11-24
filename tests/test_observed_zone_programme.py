import json
from datetime import datetime

from scripts.observed_zone_programme import observed_programme


def test_only_programmer_announcements_qualify_and_countdown_does_not_auto_roll():
    def event(clock, frame):
        return json.dumps({"tst": "2026-11-24T" + clock + "+00:00",
                           "topic": "RAMSES/GATEWAY/18:016440/rx",
                           "payload": {"ts": "1970-01-03T00:00:00Z", "msg": frame}})

    sample = [
        event("22:57:05", "075 I 100 --:------ --:------ 12:216751 2249 007 02070804B00004"),
        event("22:57:06", "075 I 101 --:------ --:------ 12:216751 2309 003 010898"),
        event("22:58:00", "075 I --- 04:118040 --:------ 12:216751 2309 003 0204B0"),
        event("23:01:30", "075 I 102 --:------ --:------ 12:216751 2249 007 0204B0070801D6"),
    ]

    def at(clock):
        return observed_programme(sample, datetime.fromisoformat("2026-11-24T" + clock + "+00:00"))

    assert at("22:58:01")["CMQ JGB"] == {
        "status": "observed", "reported_current_c": 18.0, "reported_next_c": 12.0,
        "estimate_agreement": "single", "previous_estimate_at": None,
        "received_at": "2026-11-24T22:57:05+00:00", "estimated_change_at": "2026-11-24T23:01:05+00:00"}
    assert at("22:58:01")["Lounge"]["reported_next_c"] is None
    assert at("22:58:01")["Kitchen"] == {"status": "unseen"}
    assert at("23:01:06")["CMQ JGB"]["status"] == "elapsed"
    assert at("23:01:31")["CMQ JGB"]["reported_current_c"] == 12.0
    assert at("23:12:00")["CMQ JGB"]["status"] == "stale"


def test_revised_candidate_is_visible_and_can_later_be_corroborated():
    def event(clock, minutes):
        return json.dumps({"tst": f"2026-11-24T{clock}Z", "topic": "RAMSES/GATEWAY/18:016440/rx",
                           "payload": {"ts": "1970-01-03T00:00:00Z", "msg":
                               f"075 I 100 --:------ --:------ 12:216487 2249 007 0204B006A4{minutes:04X}"}})

    rows = [event("22:21:03", 515), event("22:21:04", 515), event("22:25:23", 767),
            event("22:29:43", 506), event("22:34:03", 502)]
    def summary(clock):
        return observed_programme(rows, datetime.fromisoformat(f"2026-11-24T{clock}Z"))["EJMB + RDGB"]

    assert summary("22:21:04")["estimate_agreement"] == "single"
    revised = summary("22:25:23")
    assert revised["estimate_agreement"] == "revised"
    assert revised["estimated_change_at"] == "2026-11-25T11:12:23+00:00"
    assert revised["previous_estimate_at"] == "2026-11-25T06:56:04+00:00"
    assert summary("22:29:43")["estimate_agreement"] == "revised"
    assert summary("22:34:03")["estimate_agreement"] == "corroborated"
