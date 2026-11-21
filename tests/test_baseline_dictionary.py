"""Keep the observed-message dictionary tied to its bounded scenario."""

import json
from collections import Counter
from pathlib import Path


def test_baseline_message_dictionary_has_expected_bounded_coverage() -> None:
    scenario = json.loads(Path("data/scenarios/baseline-rx-window.json").read_text())
    codes = Counter(event["msg"].split()[6] for event in scenario["events"])

    assert len(scenario["events"]) == 111
    assert scenario["retention"] == {"event_limit": 500, "discarded": 0}
    assert codes == {
        "0008": 23, "000A": 2, "1060": 24, "1F09": 4, "1F41": 1,
        "2249": 2, "2309": 13, "2349": 1, "30C9": 21, "3150": 11,
        "31DA": 1, "3B00": 3, "3EF0": 1, "3EF1": 4,
    }


def test_baseline_gateway_timestamps_are_not_usable_wall_clock_evidence() -> None:
    scenario = json.loads(Path("data/scenarios/baseline-rx-window.json").read_text())
    assert all(event["ts"].startswith("1970-") for event in scenario["events"])
