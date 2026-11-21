import json
from datetime import datetime, timezone
from pathlib import Path

import pytest

from ramses_twin.model import ZoneController
from ramses_twin.mqtt import rx_envelope, topics


@pytest.mark.integration
def test_observed_zones_can_be_represented_by_the_virtual_contract() -> None:
    observed = json.loads(Path("data/observed/topology.json").read_text(encoding="utf-8"))
    now = datetime(2026, 11, 21, tzinfo=timezone.utc)
    assert topics()["rx"].startswith("RAMSES/TEST/")
    for entry in observed["zones"]:
        zone = ZoneController("12:900001", int(entry["zone"], 16), 18.0)
        message = rx_envelope(zone.setpoint_frame(now), now)
        assert "2309 003" in message["msg"]
        assert message["msg"].endswith(f"{int(entry['zone'], 16):02X}0708")


@pytest.mark.integration
def test_observed_samples_follow_the_ingest_contract() -> None:
    observed = json.loads(Path("data/observed/samples.json").read_text(encoding="utf-8"))
    allowed_codes = {"1F09", "2309", "3150", "30C9", "1060", "3EF0"}
    assert observed["format"] == 1
    assert observed["snapshot"] is True
    assert observed["retention"]["per_code_limit"] == 16
    assert observed["retention"]["discarded"] >= 0
    assert observed["samples"]
    counts = {}
    for sample in observed["samples"]:
        assert sample["code"] in allowed_codes
        assert sample["source"] is None or len(sample["source"]) == 3
        assert set(sample) <= {"code", "source", "destination", "values"}
        assert all(value is None or isinstance(value, (bool, int, float, str)) for value in sample["values"].values())
        counts[sample["code"]] = counts.get(sample["code"], 0) + 1
    assert all(count <= observed["retention"]["per_code_limit"] for count in counts.values())
