import json
from datetime import datetime, timedelta, timezone

from scripts.predict_relay_edges import forecasts
from scripts.fit_relay_timing import fit


def event(seconds, device, code, value):
    when = (datetime(2026, 11, 24, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat()
    return json.dumps({"topic": "RAMSES/GATEWAY/18:016440/rx", "tst": when,
                       "payload": {"ts": when, "msg": f"060 I --- {device} --:------ {device} "
                                   f"{code} {len(value)//2:03} {value}"}})


def test_forecast_is_frozen_before_outcome():
    packets = [event(0, "13:193642", "3EF0", "00C8FF"),
               event(1, "22:013226", "0008", "009C"),
               event(2, "13:193642", "3EF0", "0000FF"),
               event(5, "22:013226", "0008", "0064"),
               event(134, "13:193642", "3EF0", "00C8FF")]
    forecast, result = forecasts(packets)
    assert forecast["demand"] == 78
    assert result["error_seconds"] == -0.44
    assert result["error_600s_seconds"] == 0
    assert list(forecasts(packets[:3]))[-1]["event"] == "pending_at_end"


def test_busy_gateway_does_not_hide_relay_silence():
    packets = [event(0, "13:193642", "3EF0", "00C8FF"),
               event(1, "22:013226", "0008", "009C"),
               event(2, "13:193642", "3EF0", "0000FF"),
               event(400, "22:013226", "0008", "009C"),
               event(700, "13:193642", "3EF0", "00C8FF")]
    assert [record["event"] for record in forecasts(packets)] == ["forecast", "expired"]


def test_timing_fit_learns_from_earlier_cycles():
    start = datetime(2026, 11, 24, tzinfo=timezone.utc)
    def series(entity, events):
        return [{"entity_id": entity, "state": state,
                 "last_changed": (start + timedelta(seconds=second)).isoformat()}
                for second, state in events]
    history = [series("binary_sensor.bdr_13_193642_active",
                      [(0, "on"), (1, "off"), (121, "on"), (601, "off"), (901, "on")]),
               series("sensor.bdr_13_193642_relay_demand", [(0, "80"), (600, "50")])]
    result = fit(history, start + timedelta(seconds=500))
    assert result["train"] == result["test"] == 1
    assert abs(result["test_mae"]) < 1e-9
    assert result["baseline_mae"] == 180
