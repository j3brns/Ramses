from datetime import datetime, timedelta, timezone

from scripts.fit_thermostat_demand import RELAY, THERMOSTAT, fit, pairs


def test_fit_uses_past_fresh_samples_and_freezes_coefficients_at_cutoff():
    start = datetime(2026, 1, 1, tzinfo=timezone.utc)

    def row(entity, minute, value):
        return {"entity_id": entity, "state": str(value), "attributes": {"setpoint": 20},
                "last_updated": (start + timedelta(minutes=minute)).isoformat()}

    temps = [row(THERMOSTAT, m, v) for m, v in [(1, 20), (3, 19), (6, 18)]]
    reports = [row(RELAY, m, v) for m, v in [(0, 99), (2, 10), (4, 30), (5, 30),
                                               (7, 70), (38, 95)]]
    history = [temps, reports]
    assert [(x, y) for _, x, y in pairs(history)] == [(0, 10), (1, 30), (2, 70)]
    result = fit(history, start + timedelta(minutes=6))
    assert (result["intercept"], result["gain"]) == (10, 20)
    assert (result["validation_mae"], result["baseline_validation_mae"]) == (20, 50)
