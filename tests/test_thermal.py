from datetime import datetime, timedelta, timezone

from ramses_twin.thermal import MIN_TRAINING_SAMPLES, Observation, ThermalModel


def observation(minutes: int, room: float, outside: float, demand: float, boiler: bool) -> Observation:
    return Observation(datetime(2026, 11, 23, 6, 0, tzinfo=timezone.utc) + timedelta(minutes=minutes), room, outside, demand, boiler)


def test_model_learns_loss_then_heating_rate_and_predicts() -> None:
    model = ThermalModel()
    # A 10 C inside/outside gap cooling at 0.02 C/minute implies 0.002 loss rate.
    for offset in range(MIN_TRAINING_SAMPLES):
        result = model.learn(observation(offset * 10, 20.0, 10.0, 0.0, False), observation((offset + 1) * 10, 19.8, 10.0, 0.0, False))
        assert result.kind == "loss"
    # With 0.8 demand, 0.02 C/minute rise and 0.002 loss at a 10 C gap: heat rate is 0.05.
    for offset in range(MIN_TRAINING_SAMPLES):
        result = model.learn(observation(100 + offset * 10, 20.0, 10.0, 0.8, True), observation(110 + offset * 10, 20.2, 10.0, 0.8, True))
        assert result.kind == "heat"
    assert model.ready
    assert model.minutes_to_target(20.0, 21.0, 10.0) is not None
    assert model.to_state() == ThermalModel.from_state(model.to_state()).to_state()


def test_model_declines_ambiguous_or_untrained_intervals() -> None:
    model = ThermalModel()
    assert not model.learn(observation(0, 20, 10, 0.5, False), observation(10, 20, 10, 0.5, False)).accepted
    assert model.minutes_to_target(20, 21, 10) is None
