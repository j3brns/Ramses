"""Telemetry-evidence validation before thermal training."""

from datetime import timedelta

from ramses_twin.telemetry import (
    MAX_ALIGNMENT_SAMPLES,
    ObservedReading,
    TelemetrySample,
    TelemetrySnapshot,
    assess_telemetry,
    assess_snapshot,
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


def reading(value: float | bool | None, observed_at: str = "2026-11-22T08:00:00+00:00") -> ObservedReading:
    return ObservedReading(value=value, observed_at=observed_at)


def snapshot(**changes: object) -> TelemetrySnapshot:
    values: dict[str, object] = {
        "receipt_ts": "2026-11-22T08:01:00+00:00",
        "gateway_ts": "1970-01-01T08:01:00+00:00",
        "reference_temp": reading(20.0),
        "outdoor_temp": reading(8.0),
        "valve_demand": reading(0.5),
        "boiler_available": reading(True),
    }
    values.update(changes)
    return TelemetrySnapshot(**values)  # type: ignore[arg-type]


def test_snapshot_normalises_only_fresh_tightly_aligned_observations() -> None:
    assessment = assess_snapshot(snapshot())
    assert assessment.status == "accepted"
    assert assessment.sample == sample(
        receipt_ts="2026-11-22T08:01:00+00:00",
        gateway_ts="1970-01-01T08:01:00+00:00",
    )


def test_snapshot_rejects_old_or_future_source_readings() -> None:
    old = snapshot(outdoor_temp=reading(8.0, "2026-11-22T07:45:59+00:00"))
    future = snapshot(valve_demand=reading(0.5, "2026-11-22T08:01:01+00:00"))
    assert assess_snapshot(old).status == "stale"
    assert assess_snapshot(future).status == "stale"


def test_snapshot_rejects_time_skew_and_missing_values() -> None:
    skewed = snapshot(boiler_available=reading(True, "2026-11-22T07:57:59+00:00"))
    incomplete = snapshot(reference_temp=reading(None))
    assert assess_snapshot(skewed).status == "time-skewed"
    assert assess_snapshot(incomplete).status == "incomplete"


def test_snapshot_rejects_invalid_receipt_and_bad_value_types() -> None:
    assert assess_snapshot(snapshot(receipt_ts="not-a-time")).status == "receipt-time-invalid"
    assert assess_snapshot(snapshot(boiler_available=reading(1.0))).status == "incomplete"


def test_snapshot_rejects_negative_freshness_limits() -> None:
    for limits in ({"max_age": timedelta(seconds=-1)}, {"max_skew": timedelta(seconds=-1)}):
        try:
            assess_snapshot(snapshot(), **limits)
        except ValueError as error:
            assert "non-negative" in str(error)
        else:
            raise AssertionError("expected invalid freshness limits to fail")
