from scripts.read_relay_countdowns import countdown


def test_relay_actuator_and_cycle_have_independent_deadlines():
    event = {"topic": "RAMSES/GATEWAY/18:016440/rx", "tst": "2026-11-24T23:46:08+00:00",
             "payload": {"msg": "065 RP --- 13:193642 22:013226 --:------ 3EF1 007 00024700D900FF",
                         "ts": "1970-01-03T07:00:00+00:00"}}
    assert countdown(event) == {"at": event["tst"], "active": False, "cycle_seconds": 583,
                                "actuator_seconds": 217, "deadline": "2026-11-24T23:49:45+00:00"}
    header = event["payload"]["msg"].rsplit(" ", 1)[0]
    for timer in ("FFFF", "7FFF"):
        event["payload"]["msg"] = header + " 000247" + timer + "00FF"
        assert countdown(event) is None
        event["payload"]["msg"] = header + " 00" + timer + "000000FF"
        assert countdown(event)["cycle_seconds"] is None
        assert countdown(event)["actuator_seconds"] == 0
