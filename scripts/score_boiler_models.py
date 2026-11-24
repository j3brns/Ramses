"""Score competing explanations of relay 642 demand against one passive capture."""

import json
import sys
from collections import defaultdict
from datetime import datetime
from statistics import mean

from ramses_twin.evidence import normalise_rx_event


def score(lines):
    latest = {}
    previous = None
    previous_time = last_time = None
    scores = defaultdict(list)
    jointly_scored = defaultdict(list)
    valves = {"04:118027", "04:118030", "04:118049", "04:006472",
              "04:090387", "04:090389", "04:118048", "04:118040"}
    for line in lines:
        event = normalise_rx_event(json.loads(line))
        fields = event["msg"].split()
        if len(fields) != 9:
            continue
        _, verb, _, source, _, origin, code, length, payload = fields
        if code not in {"3150", "0008"} or length != "002" or len(payload) != 4:
            continue
        value = int(payload[2:], 16) / 2
        if value > 100:
            continue
        time = datetime.fromisoformat(event["receipt_ts"]).timestamp()
        if last_time is not None and time < last_time:
            raise ValueError("capture is out of order")
        last_time = time
        if verb == "I":
            device = origin if source == "--:------" else source
            latest[device, code] = time, value
            continue
        if (verb, source, code) != ("RP", "13:193642", "0008"):
            continue
        fresh = {key: v for key, (t, v) in latest.items() if 0 <= time - t <= 600}
        models = {label: fresh.get((device, "0008")) for label, device in
                  [("stat226", "22:013226"), ("kitchen", "12:216487"), ("lounge", "12:216751")]}
        if all((valve, "3150") in fresh for valve in valves):
            demands = [fresh[valve, "3150"] for valve in valves]
            models.update(max_valve=max(demands), mean_valve=mean(demands))
        models["previous_relay"] = previous if previous_time is not None and time-previous_time <= 600 else None
        for name, prediction in models.items():
            if prediction is not None:
                error = abs(value - prediction)
                scores[name].append(error)
                if len(models) == 6 and all(p is not None for p in models.values()):
                    jointly_scored[name].append(error)
        previous = value
        previous_time = time
    def metrics(groups):
        return {k: {"n": len(v), "exact": v.count(0), "mae_pct_points": round(mean(v), 2)}
                for k, v in groups.items()}
    return {"available": metrics(scores), "common_timestamps": metrics(jointly_scored)}


if __name__ == "__main__":
    print(json.dumps(score(sys.stdin), indent=2))
