import json
from pathlib import Path
import subprocess
import sys


def test_rolling_replay_breaks_at_outages_and_scores_unseen_day(tmp_path):
    def group(name, events):
        return [dict(entity_id=name, last_changed="2026-11-" + timestamp + "Z", state=state)
                for timestamp, state in events]

    active = group("b", [
        ("20T10:00:00", "on"), ("20T10:01:00", "off"), ("20T10:02:00", "on"),
        ("20T10:03:00", "off"), ("20T10:03:05", "unavailable"),
        ("21T09:00:00", "on"), ("21T10:00:00", "off"), ("21T10:01:00", "on"),
    ])
    demand = group("d", [("20T10:00:00", "90"), ("21T10:00:00.200", "95")])
    path = tmp_path / "history.json"
    path.write_text(json.dumps([active, demand]), encoding="utf-8")
    tool = Path(__file__).resolve().parents[1] / "scripts" / "score_relay_history.py"
    result = subprocess.check_output([sys.executable, str(tool), str(path),
                                      "--active", "b", "--demand", "d"], text=True)
    assert json.loads(result) == [
        {"day": "2026-11-21", "state": "off", "train": 1, "test": 1, "period_seconds": 600.0,
         "floor_active": 1, "mae_constant": 0.0, "mae_duty": 30.0, "mae_floor60": 0.0}
    ]
