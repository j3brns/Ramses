"""Show the relay's advertised, revisable actuator deadline (passive RX NDJSON)."""

import json
import struct
import sys
from datetime import datetime, timedelta

from ramses_twin.evidence import normalise_rx_event


def countdown(event):
    observation = normalise_rx_event(event)
    fields = observation["msg"].split()
    if len(fields) != 9 or fields[1] != "RP" or fields[3] != "13:193642":
        return None
    if fields[6:8] != ["3EF1", "007"] or len(fields[8]) != 14:
        return None
    _, cycle, actuator, modulation, _ = struct.unpack(">BhhBB", bytes.fromhex(fields[8]))
    if not 0 <= actuator < 0x7FFF or modulation not in (0, 200):
        return None
    now = datetime.fromisoformat(observation["receipt_ts"])
    if now.utcoffset() is None:
        raise ValueError("broker receipt time requires a UTC offset")
    return {"at": now.isoformat(), "active": modulation == 200,
            "cycle_seconds": cycle if 0 <= cycle < 0x7FFF else None,
            "actuator_seconds": actuator, "deadline": (now+timedelta(seconds=actuator)).isoformat()}


if __name__ == "__main__":
    for line in sys.stdin:
        record = countdown(json.loads(line))
        if record:
            print(json.dumps(record), flush=True)
