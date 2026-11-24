"""Score relay pulse widths from a contiguous grouped HA /api/history/period JSON export.

Each pulse begins at an observed transition and ends at the next. Unknown states
break the sequence. The demand reading is the latest through one second after
the start, accommodating HA's asynchronous entity updates: this is conditional
replay, not a forecast issued before the edge. Unreported outages and changes
in demand during a pulse can affect MAE. Each UTC day is scored using only
pulses completed before that day. A 60-second floor is an experimental challenger.
"""

import argparse
from bisect import bisect_left, bisect_right
from datetime import datetime, timedelta, timezone
import json
from math import isfinite
from pathlib import Path
from statistics import mean, median


def transitions(group):
    events = []
    for row in group:
        stamp = datetime.fromisoformat(row["last_changed"])
        if stamp.utcoffset() is None:
            raise ValueError("history timestamps require UTC offsets")
        stamp = stamp.astimezone(timezone.utc)
        if events and stamp < events[-1][0]:
            raise ValueError("expected chronological entity history")
        if not events or row["state"] != events[-1][1]:
            events.append((stamp, row["state"]))
    return events


def score(history, active_id, demand_id):
    groups = {group[0]["entity_id"]: group for group in history if group}
    active = transitions(groups[active_id])
    demand = transitions(groups[demand_id])
    stamps = [stamp for stamp, _ in demand]
    pulses = []
    for (_, previous), (start, state), (end, following) in zip(active, active[1:], active[2:]):
        if (previous, state, following) not in {("on", "off", "on"), ("off", "on", "off")}:
            continue
        i = min(bisect_right(stamps, start + timedelta(seconds=1)), bisect_left(stamps, end)) - 1
        if i < 0:
            continue
        try:
            pct = float(demand[i][1])
        except ValueError:
            continue
        if isfinite(pct) and 0 <= pct <= 100:
            fraction = (pct if state == "on" else 100 - pct) / 100
            pulses.append((start, end, state, fraction, (end - start).total_seconds()))
    results = []
    for day, state in sorted({(start.date(), state) for start, _, state, _, _ in pulses}):
        train = [(f, width) for _, end, s, f, width in pulses if end.date() < day and s == state]
        test = [(f, width) for start, _, s, f, width in pulses if start.date() == day and s == state]
        ratios = [width / f for f, width in train if f > 0]
        if not ratios:
            continue
        period = median(ratios)
        constant = median(width for _, width in train)
        results.append(dict(day=day.isoformat(), state=state, train=len(train), test=len(test),
                            period_seconds=period, floor_active=sum(period*f < 60 for f, _ in test),
                            mae_constant=mean(abs(width-constant) for _, width in test),
                            mae_duty=mean(abs(width-period*f) for f, width in test),
                            mae_floor60=mean(abs(width-max(60, period*f)) for f, width in test)))
    return results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("history", type=Path)
    parser.add_argument("--active", required=True, help="binary relay entity ID")
    parser.add_argument("--demand", required=True, help="numeric 0-100 percent demand entity ID")
    args = parser.parse_args()
    print(json.dumps(score(json.loads(args.history.read_text(encoding="utf-8-sig")),
                           args.active, args.demand), indent=2))
