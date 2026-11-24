"""Read HA history JSON on stdin. Fit off time before the supplied ISO date."""

import json
import sys
from bisect import bisect_right
from datetime import datetime, timedelta
from statistics import mean, median


def fit(history, cutoff):
    series = {}
    for group in history:
        if group:
            series[group[0]["entity_id"]] = sorted(
                (datetime.fromisoformat(row["last_changed"]), row["state"]) for row in group
            )
    states = series["binary_sensor.bdr_13_193642_active"]
    demands = series["sensor.bdr_13_193642_relay_demand"]
    times = [time for time, _ in demands]
    train, test = [], []
    for previous, (start, state), (end, following) in zip(states, states[1:], states[2:]):
        if (previous[1], state, following) != ("on", "off", "on"):
            continue
        index = bisect_right(times, start + timedelta(seconds=1)) - 1
        if index < 0:
            continue
        try:
            fraction = 1 - float(demands[index][1]) / 100
        except ValueError:
            continue
        if 0 < fraction < 1:
            if end < cutoff:
                train.append((fraction, (end-start).total_seconds()))
            elif start >= cutoff:
                test.append((fraction, (end-start).total_seconds()))
    if not train or not test:
        raise ValueError("Need complete demand-labelled cycles on both sides of cutoff")
    period = median(seconds / fraction for fraction, seconds in train)
    baseline = median(seconds for _, seconds in train)
    return dict(train=len(train), test=len(test), period_seconds=period,
                test_mae=mean(abs(seconds-period*fraction) for fraction, seconds in test),
                baseline_mae=mean(abs(seconds-baseline) for _, seconds in test))


if __name__ == "__main__":
    print(json.dumps(fit(json.load(sys.stdin), datetime.fromisoformat(sys.argv[1])), indent=2))
