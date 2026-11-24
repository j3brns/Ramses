"""Estimate thermostat 226's demand from temperature error using grouped HA history.

Pipe full recorder history JSON (including attributes) and pass an ISO cutoff.
"""

import json
import math
import sys
from bisect import bisect_right
from datetime import datetime, timedelta
from statistics import mean, median

THERMOSTAT = "sensor.thm_22_013226_temperature"
RELAY = "sensor.bdr_13_193642_relay_demand"


def pairs(history):
    """Pair each demand report with the last available temperature and setpoint."""
    series = {THERMOSTAT: {}, RELAY: {}}
    for group in history:
        for row in group:
            entity = row["entity_id"]
            if entity in series:
                time = datetime.fromisoformat(row["last_updated"])
                if time.tzinfo is None:
                    raise ValueError("recorder timestamps need UTC offsets")
                series[entity][time] = row
    times = sorted(series[THERMOSTAT])
    previous = None
    for time, demand in sorted(series[RELAY].items()):
        index = bisect_right(times, time) - 1
        if index < 0 or time - times[index] > timedelta(minutes=30):
            previous = None
            continue
        thermostat = series[THERMOSTAT][times[index]]
        try:
            error = float(thermostat["attributes"]["setpoint"]) - float(thermostat["state"])
            value = float(demand["state"])
        except (KeyError, ValueError, TypeError):
            previous = None
            continue
        if not math.isfinite(error) or not 0 <= value <= 100:
            previous = None
            continue
        observation = (round(error, 4), value)
        if observation != previous:
            yield time, *observation
        previous = observation


def fit(history, cutoff):
    training, validation = [], []
    for time, error, demand in pairs(history):
        (training if time < cutoff else validation).append((error, demand))
    if not training or not validation:
        raise ValueError("need valid pairs on both sides of cutoff")

    def predict(error, bias, gain):
        return min(100, max(0, bias + gain * error))

    def loss(params):
        return sum((predict(x, *params) - y) ** 2 for x, y in training)

    bias, gain = min(((b, g) for b in range(101) for g in range(101)), key=loss)
    baseline = median(y for _, y in training)
    return {"intercept": bias, "gain": gain, "training_pairs": len(training),
            "validation_pairs": len(validation),
            "training_mae": mean(abs(predict(x, bias, gain) - y) for x, y in training),
            "validation_mae": mean(abs(predict(x, bias, gain) - y) for x, y in validation),
            "baseline_validation_mae": mean(abs(baseline - y) for _, y in validation)}


if __name__ == "__main__":
    print(json.dumps(fit(json.load(sys.stdin), datetime.fromisoformat(sys.argv[1])), indent=2))
