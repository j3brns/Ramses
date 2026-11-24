"""Exercise native HA programmer boundaries and cross-zone isolation."""

from runpy import run_path


def test_four_zone_actions_only_change_their_own_persistent_deadline():
    config = run_path("scripts/test_programmer_ui.py")["build"]()
    sections = config["view"]["sections"][1:]
    assert [s["cards"][0]["heading"] for s in sections] == [
        "Kitchen", "EJMB + RDGB", "Lounge", "CMQ JGB"
    ]
    for section in sections:
        _, status, controls, tile = section["cards"]
        schedule = tile["entity"].removeprefix("schedule.")
        slug = schedule.removesuffix("_test_timetable")
        expiry = f"{slug}_boost_expiry"
        assert schedule in config["schedules"] and expiry in config["expiries"]
        assert "input_number." + expiry in status["content"]
        for action, card in zip(("boost", "cancel"), controls["cards"], strict=True):
            script = card["tap_action"]["perform_action"].removeprefix("script.")
            assert script == f"{slug}_{action}"
            steps = config["scripts"][script]["sequence"]
            calls = [s for s in steps if "action" in s]
            assert len(calls) == 1
            assert calls[0]["action"] == "input_number.set_value"
            assert calls[0]["target"]["entity_id"] == "input_number." + expiry
            if action == "boost":
                assert schedule in steps[0]["variables"]["deadline"]
                assert "next_event" in steps[0]["variables"]["deadline"]
                assert steps[1]["condition"] == "template"
            else:
                assert calls[0]["data"]["value"] == 0
