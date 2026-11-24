from datetime import date, datetime, timedelta, timezone

from scripts.validate_thermostat_forecasts import RELAY, THERMOSTAT, aligned, validate


def test_future_same_timestamp_and_stale_reports_cannot_supply_predictors():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def row(entity, m, value):
        return dict(entity_id=entity, state=str(value), attributes={"setpoint": 20},
                    last_updated=(start + timedelta(minutes=m)).isoformat())

    temperatures = [row(THERMOSTAT, m, v) for m, v in
                    [(0, 20), (2, 19), (1440, 20), (1442, 19)]]
    relay = [row(RELAY, m, v) for m, v in [(1, 10), (2, 10), (3, 30),
                                             (40, 99), (1441, 10), (1443, 30)]]
    history = [temperatures, relay]
    rows = list(aligned(history))
    assert [r[1:] for r in rows] == [(10, 0, 0, 10), (10, 0, 1, 30), (10, 0, 1, 30)]
    result = validate(history, date(2026, 1, 2))
    assert result["folds"][0]["delta_gain"] == 20
    assert result["pooled_mae"] == [20, 0, 0]
