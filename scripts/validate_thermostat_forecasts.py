"""Walk forward one day at a time over full, grouped HA recorder JSON on stdin.

Run: py -m scripts.validate_thermostat_forecasts 2026-11-22 < history.json
Each forecast uses the preceding measured demand and currently available temperature.
"""

import argparse
import json
import math
import sys
from bisect import bisect_left
from datetime import date, datetime, timedelta, timezone
from statistics import mean

from scripts.fit_thermostat_demand import RELAY, THERMOSTAT


def aligned(history):
    series = {THERMOSTAT: {}, RELAY: {}}
    for group in history:
        for row in group:
            table = series.get(row["entity_id"])
            if table is None:
                continue
            t = datetime.fromisoformat(row["last_updated"])
            if t.tzinfo is None:
                raise ValueError("timestamps need a UTC offset")
            table[t.astimezone(timezone.utc)] = row
    clock = sorted(series[THERMOSTAT])
    fresh = timedelta(minutes=30)
    previous = None
    for t, reading in sorted(series[RELAY].items()):
        i = bisect_left(clock, t) - 1
        if i < 0 or t - clock[i] > fresh:
            previous = None
            continue
        temperature = series[THERMOSTAT][clock[i]]
        try:
            error = float(temperature["attributes"]["setpoint"]) - float(temperature["state"])
            demand = float(reading["state"])
        except (KeyError, ValueError, TypeError):
            previous = None
            continue
        if not math.isfinite(error) or not 0 <= demand <= 100:
            previous = None
            continue
        if previous and t - previous[0] <= fresh:
            yield t.date(), previous[1], previous[2], error, demand
        previous = t, demand, error


def clip(value):
    return max(0, min(100, value))


def validate(history, first_day):
    rows = list(aligned(history))
    folds = []
    pooled = []
    for day in sorted({row[0] for row in rows if row[0] >= first_day}):
        train = [row for row in rows if row[0] < day]
        if not train:
            raise ValueError("need at least one earlier training day")
        test = [row for row in rows if row[0] == day]
        bias, gain = min(((b, g) for b in range(101) for g in range(101)),
                         key=lambda v: sum((clip(v[0] + v[1] * e) - y) ** 2
                                           for _, _, _, e, y in train))
        delta_gain = min(range(101), key=lambda g: sum(
            (clip(p + g * (e - e0)) - y) ** 2 for _, p, e0, e, y in train))
        errors = [(abs(p - y), abs(clip(bias + gain * e) - y),
                   abs(clip(p + delta_gain * (e - e0)) - y)) for _, p, e0, e, y in test]
        pooled.extend(errors)
        folds.append(dict(day=day.isoformat(), training=len(train), scored=len(test),
                          changes=sum(p != y for _, p, _, _, y in test), bias=bias,
                          gain=gain, delta_gain=delta_gain, mae=list(map(mean, zip(*errors)))))
    if not pooled:
        raise ValueError("no held-out aligned observations")
    return dict(models=["persistence", "clipped_error", "previous_plus_error_change"],
                folds=folds, pooled_mae=list(map(mean, zip(*pooled))))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("first_day", type=date.fromisoformat)
    print(json.dumps(validate(json.load(sys.stdin), parser.parse_args().first_day), indent=2))
