"""Replay or follow gateway RX NDJSON, emitting forecasts as soon as an off edge arrives."""

import json
import sys
from datetime import datetime, timedelta, timezone

from ramses_twin.evidence import normalise_rx_event


def forecasts(lines):
    demand = state = previous = prediction = last_relay = None
    for line in lines:
        event = normalise_rx_event(json.loads(line))
        now = datetime.fromisoformat(event["receipt_ts"])
        if now.utcoffset() is None:
            raise ValueError("broker receipt time requires a UTC offset")
        if previous is not None and now < previous:
            raise ValueError("capture is out of order")
        if previous and (now - previous).total_seconds() > 600:
            if prediction:
                yield {"event": "expired", "reason": "capture gap", "at": now.isoformat()}
            demand = state = prediction = None
        previous = now
        if last_relay and (now - last_relay).total_seconds() > 620:
            if prediction:
                yield {"event": "expired", "reason": "relay silence", "at": now.isoformat()}
            state = prediction = last_relay = None
        fields = event["msg"].split()
        if len(fields) != 9 or fields[1] != "I":
            continue
        source, code, payload = fields[3], fields[6], fields[8]
        if source == "22:013226" and code == "0008" and len(payload) == 4 and payload.startswith("00"):
            value = int(payload[2:], 16) / 2
            demand = (now, value) if value <= 100 else None
        if source != "13:193642" or code != "3EF0" or payload not in ("0000FF", "00C8FF"):
            continue
        active = payload == "00C8FF"
        last_relay = now
        if prediction and (now-prediction).total_seconds() > 602:
            yield {"event": "expired", "reason": "missed cycle", "at": now.isoformat()}
            prediction = None
        if state is True and not active:
            if demand and 0 < demand[1] < 100 and (now-demand[0]).total_seconds() <= 600:
                prediction = now + timedelta(seconds=602 * (1 - demand[1]/100))
                ten_minutes = now + timedelta(seconds=600 * (1 - demand[1]/100))
                yield {"event": "forecast", "at": now.isoformat(), "demand": demand[1],
                       "expected_on": prediction.isoformat(), "expected_on_600s": ten_minutes.isoformat()}
            else:
                yield {"event": "unscored", "at": now.isoformat(), "reason": "stale or endpoint demand"}
        elif active and prediction:
            yield {"event": "result", "at": now.isoformat(),
                   "error_seconds": round((now-prediction).total_seconds(), 3),
                   "error_600s_seconds": round((now-ten_minutes).total_seconds(), 3)}
            prediction = None
        state = active
    if prediction:
        yield {"event": "pending_at_end", "expected_on": prediction.isoformat()}


if __name__ == "__main__":
    for record in forecasts(sys.stdin):
        print(json.dumps(dict(record, processed_at=datetime.now(timezone.utc).isoformat())), flush=True)
