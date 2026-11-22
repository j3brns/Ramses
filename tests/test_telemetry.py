"""Telemetry-evidence validation before thermal training."""

from ramses_twin.telemetry import (
    MAX_ALIGNMENT_SAMPLES,
    TelemetrySample,
    assess_telemetry,
    aligned_candidates,
)


def sample(**changes: object) -> TelemetrySample:
    values: dict[str, object] = {
        "receipt_ts": "2026-11-22T08:00:00+00:00",
        "gateway_ts": "1970-01-01T08:00:00+00:00",
        "reference_temp": 20.0,
        "outdoor_temp": 8.0,
        "valve_demand": 0.5,
        "boiler_available": True,
    }
    values.update(changes)
    return TelemetrySample(**values)  # type: ignore[arg-type]


def test_epoch_gateway_time_is_labelled_but_broker_time_keeps_candidate_usable() -> None:
    assessments = assess_telemetry((sample(),))
    assert assessments[0].status == "gateway-epoch-invalid"
    assert aligned_candidates((sample(),)) == (sample(),)


def test_incomplete_and_out_of_range_values_are_not_aligned_candidates() -> None:
    assessments = assess_telemetry((sample(reference_temp=None), sample(valve_demand=1.1)))
    assert [item.status for item in assessments] == ["incomplete", "incomplete"]
    assert aligned_candidates((sample(reference_temp=None),)) == ()


def test_missing_or_non_increasing_receipt_time_breaks_alignment() -> None:
    later = sample(receipt_ts="2026-11-22T08:10:00+00:00", gateway_ts=None)
    repeated = sample(receipt_ts="2026-11-22T08:10:00+00:00", gateway_ts=None)
    assessments = assess_telemetry((sample(receipt_ts=None), later, repeated))
    assert [item.status for item in assessments] == ["receipt-time-invalid", "accepted", "receipt-time-invalid"]


def test_unverified_non_epoch_gateway_time_is_diagnostic_only() -> None:
    assessment = assess_telemetry((sample(gateway_ts="2026-11-22T08:00:00+00:00"),))[0]
    assert assessment.status == "accepted"


def test_telemetry_input_is_bounded() -> None:
    samples = tuple(sample() for _ in range(MAX_ALIGNMENT_SAMPLES + 1))
    try:
        assess_telemetry(samples)
    except ValueError as error:
        assert "must not exceed" in str(error)
    else:
        raise AssertionError("expected bounded telemetry validation")
