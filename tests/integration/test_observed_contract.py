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
