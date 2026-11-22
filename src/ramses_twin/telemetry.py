"""Bounded validation of evidence before thermal-model training.

This module deliberately validates observations; it does not collect them,
connect to MQTT, or train a thermal model.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Sequence


MAX_ALIGNMENT_SAMPLES = 500
TelemetryStatus = Literal[
    "accepted", "incomplete", "receipt-time-invalid", "gateway-epoch-invalid"
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
