"""Summarise the household programmers' received setpoints at an explicit UTC instant."""

import argparse
from collections import defaultdict, deque
from datetime import datetime, timedelta, timezone
import json
import struct
import sys

from ramses_twin.evidence import normalise_rx_event


ZONES = {("12:216487", 1): "Kitchen", ("12:216487", 2): "EJMB + RDGB",
         ("12:216751", 1): "Lounge", ("12:216751", 2): "CMQ JGB"}


def observed_programme(lines, as_of, fresh_for=timedelta(minutes=10)):
    if as_of.utcoffset() is None or fresh_for <= timedelta(0):
        raise ValueError("use an offset-aware timestamp and positive freshness interval")
    observations = {}
    recent = defaultdict(deque)
    last = None
    for line in lines:
        event = normalise_rx_event(json.loads(line))
        at = datetime.fromisoformat(event["receipt_ts"])
        if at.utcoffset() is None or (last is not None and at < last):
            raise ValueError("receipt timestamps must have offsets and be chronological")
        last = at
        if at > as_of:
            break
        fields = event["msg"].split()
        if len(fields) != 9 or fields[1] != "I":
            continue
        a, b, c, code, length, payload = fields[3:]
        if b != "--:------" or a not in ("--:------", c):
            continue
        if (code, length, len(payload)) not in {("2249", "007", 14), ("2309", "003", 6)}:
            continue
        raw = bytes.fromhex(payload)
        zone, current = struct.unpack(">Bh", raw[:3])
        if (c, zone) not in ZONES or not 500 <= current <= 3000:
            continue
        following = due = None
        if code == "2249":
            target, minutes = struct.unpack(">hH", raw[3:])
            if 500 <= target <= 3000 and minutes < 0xFFFF:
                following, due = target / 100, at + timedelta(minutes=minutes)
        history = recent[c, zone]
        while history and at - history[0][0] > fresh_for:
            history.popleft()
        if due is None or (history and history[-1][1:3] != (current, following)):
            history.clear()
        prior_due = next((entry[3] for entry in reversed(history)
                          if at - entry[0] >= timedelta(minutes=1)), None)
        agreement = None
        if due is not None:
            agreement = "single"
            if prior_due is not None:
                agreement = "corroborated" if abs(due-prior_due) <= timedelta(seconds=90) else "revised"
            history.append((at, current, following, due))
        observations[c, zone] = at, current / 100, following, due, agreement, prior_due
    result = {}
    for key, room in ZONES.items():
        record = observations.get(key)
        if record is None:
            result[room] = {"status": "unseen"}
            continue
        at, current, following, due, agreement, prior_due = record
        status = "stale" if as_of-at > fresh_for else "observed"
        if due is not None and as_of >= due:
            status = "elapsed"
        result[room] = {
            "status": status, "received_at": at.astimezone(timezone.utc).isoformat(),
            "reported_current_c": current, "reported_next_c": following,
            "estimated_change_at": due.astimezone(timezone.utc).isoformat() if due else None,
            "estimate_agreement": agreement,
            "previous_estimate_at": prior_due.astimezone(timezone.utc).isoformat() if prior_due else None,
        }
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", required=True, type=datetime.fromisoformat)
    args = parser.parse_args()
    print(json.dumps(observed_programme(sys.stdin, args.as_of), indent=2))
