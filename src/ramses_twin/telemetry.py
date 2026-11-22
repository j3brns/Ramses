"""Bounded validation of evidence before thermal-model training.

This module deliberately validates observations; it does not collect them,
connect to MQTT, or train a thermal model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Literal, Sequence


MAX_ALIGNMENT_SAMPLES = 500
TelemetryStatus = Literal[
    "accepted", "incomplete", "receipt-time-invalid", "gateway-epoch-invalid"
]
SnapshotStatus = Literal[
    "accepted", "incomplete", "receipt-time-invalid", "stale", "time-skewed"
]


@dataclass(frozen=True)
class TelemetrySample:
    """One externally aligned observation for a prospective zone interval."""

    receipt_ts: str | None
    gateway_ts: str | None
    reference_temp: float | None
    outdoor_temp: float | None
    valve_demand: float | None
    boiler_available: bool | None


@dataclass(frozen=True)
class TelemetryAssessment:
    """Validation result retained alongside the original sample."""

    sample: TelemetrySample
    status: TelemetryStatus


@dataclass(frozen=True)
class ObservedReading:
    """One value plus the time Home Assistant says it last changed.

    This is deliberately a value object. Fetching Home Assistant state belongs
    outside the model, so this module cannot make a live observation appear
    coherent merely by reading it.
    """

    value: float | bool | None
    observed_at: str | None


@dataclass(frozen=True)
class TelemetrySnapshot:
    """Read-only inputs required to form one prospective optimiser sample."""

    receipt_ts: str | None
    gateway_ts: str | None
    reference_temp: ObservedReading
    outdoor_temp: ObservedReading
    valve_demand: ObservedReading
    boiler_available: ObservedReading


@dataclass(frozen=True)
class SnapshotAssessment:
    """A normalised sample with an explicit claim limit."""

    sample: TelemetrySample | None
    status: SnapshotStatus


def assess_telemetry(samples: Sequence[TelemetrySample]) -> tuple[TelemetryAssessment, ...]:
    """Classify bounded candidate samples without treating gateway time as truth.

    A valid broker receipt time is required to align an interval. Gateway time
    remains diagnostic only: an epoch value is labelled, but does not discard
    an otherwise usable broker-timestamped sample.
    """
    if len(samples) > MAX_ALIGNMENT_SAMPLES:
        raise ValueError(f"telemetry samples must not exceed {MAX_ALIGNMENT_SAMPLES}")

    assessments: list[TelemetryAssessment] = []
    previous_receipt: datetime | None = None
    for sample in samples:
        if not _complete(sample):
            assessments.append(TelemetryAssessment(sample, "incomplete"))
            continue
        receipt = _timestamp(sample.receipt_ts)
        if receipt is None or (previous_receipt is not None and receipt <= previous_receipt):
            assessments.append(TelemetryAssessment(sample, "receipt-time-invalid"))
            continue
        previous_receipt = receipt
        if _is_epoch(sample.gateway_ts):
            assessments.append(TelemetryAssessment(sample, "gateway-epoch-invalid"))
        else:
            assessments.append(TelemetryAssessment(sample, "accepted"))
    return tuple(assessments)


def aligned_candidates(samples: Sequence[TelemetrySample]) -> tuple[TelemetrySample, ...]:
    """Return evidence eligible for later interval construction, never training.

    The caller still needs ordered intervals and the optimiser's separate
    three-clean-samples-per-kind threshold before it may plan an early start.
    """
    return tuple(
        assessment.sample
        for assessment in assess_telemetry(samples)
        if assessment.status in {"accepted", "gateway-epoch-invalid"}
    )


def assess_snapshot(
    snapshot: TelemetrySnapshot,
    *,
    max_age: timedelta = timedelta(minutes=15),
    max_skew: timedelta = timedelta(minutes=2),
) -> SnapshotAssessment:
    """Normalise one externally collected snapshot without inferring an interval.

    All source readings must be recent relative to broker receipt and close to
    each other. This prevents a fresh room temperature plus an old weather or
    valve value being presented as a single physical observation. Passing this
    check only makes a sample eligible for later evidence validation; it does
    not train the optimiser or establish thermal fidelity.
    """
    if max_age < timedelta(0) or max_skew < timedelta(0):
        raise ValueError("max_age and max_skew must be non-negative")

    receipt = _timestamp(snapshot.receipt_ts)
    if receipt is None:
        return SnapshotAssessment(None, "receipt-time-invalid")

    readings = (
        snapshot.reference_temp,
        snapshot.outdoor_temp,
        snapshot.valve_demand,
        snapshot.boiler_available,
    )
    observed = tuple(_timestamp(reading.observed_at) for reading in readings)
    if any(timestamp is None or reading.value is None for reading, timestamp in zip(readings, observed)):
        return SnapshotAssessment(None, "incomplete")

    times = tuple(timestamp for timestamp in observed if timestamp is not None)
    if any(timestamp > receipt or receipt - timestamp > max_age for timestamp in times):
        return SnapshotAssessment(None, "stale")
    if max(times) - min(times) > max_skew:
        return SnapshotAssessment(None, "time-skewed")

    sample = TelemetrySample(
        receipt_ts=snapshot.receipt_ts,
        gateway_ts=snapshot.gateway_ts,
        reference_temp=_number(snapshot.reference_temp.value),
        outdoor_temp=_number(snapshot.outdoor_temp.value),
        valve_demand=_number(snapshot.valve_demand.value),
        boiler_available=snapshot.boiler_available.value if isinstance(snapshot.boiler_available.value, bool) else None,
    )
    if not _complete(sample):
        return SnapshotAssessment(None, "incomplete")
    return SnapshotAssessment(sample, "accepted")


def _complete(sample: TelemetrySample) -> bool:
    values = (sample.reference_temp, sample.outdoor_temp, sample.valve_demand)
    if any(value is None or isinstance(value, bool) or not isinstance(value, (int, float)) for value in values):
        return False
    if not -50.0 <= float(sample.reference_temp) <= 60.0:
        return False
    if not -50.0 <= float(sample.outdoor_temp) <= 60.0:
        return False
    if not 0.0 <= float(sample.valve_demand) <= 1.0:
        return False
    return isinstance(sample.boiler_available, bool)


def _timestamp(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        timestamp = datetime.fromisoformat(value)
    except ValueError:
        return None
    if timestamp.tzinfo is None or timestamp.utcoffset() is None:
        return None
    return timestamp


def _is_epoch(value: str | None) -> bool:
    timestamp = _timestamp(value)
    return timestamp is not None and timestamp.year == 1970


def _number(value: float | bool | None) -> float | None:
    """Keep bools out of numeric telemetry despite Python's bool/int overlap."""
    return float(value) if isinstance(value, (int, float)) and not isinstance(value, bool) else None
