"""Validate evidence status without promoting an observed candidate to fact."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Mapping

from ramses_twin.replay import replay_scenario


_STATUSES = frozenset({"baseline", "candidate", "qualified"})
_BEHAVIOURS = frozenset({"schedule-change", "override-expiry", "restart-reconnect"})


@dataclass(frozen=True)
class ScenarioQualification:
    """Validated scenario status; only qualified evidence exposes behaviour."""

    scenario: str
    status: str
    receipt_time_health: str
    behaviour: str | None
    hypothesis: str | None
    corroboration: tuple[dict[str, str], ...]
    replay_test: str | None


def receipt_time_health(scenario: Mapping[str, Any]) -> str:
    """Return the broker-receipt chronology health for an ordered scenario."""
    trace = replay_scenario(scenario)
    timestamps: list[datetime] = []
    for frame in trace.frames:
        if not frame.receipt_ts:
            return "missing"
        try:
            timestamp = datetime.fromisoformat(frame.receipt_ts)
        except ValueError:
            return "invalid"
        if timestamp.tzinfo is None or timestamp.year < 2000:
            return "invalid"
        timestamps.append(timestamp)
    if any(later <= earlier for earlier, later in zip(timestamps, timestamps[1:])):
        return "non-monotonic"
    return "healthy"


def validate_qualification(
    scenario: Mapping[str, Any], manifest: Mapping[str, Any]
) -> ScenarioQualification:
    """Validate explicit qualification metadata against the supplied scenario.

    A candidate may state a hypothesis, but it never exposes a behaviour.
    Qualified evidence additionally requires healthy broker chronology,
    corroboration, and a named replay test.
    """
    scenario_name = scenario.get("name")
    if not isinstance(scenario_name, str) or not scenario_name:
        raise ValueError("scenario needs a name")
    if manifest.get("format") != 1 or manifest.get("kind") != "scenario-qualification":
        raise ValueError("unsupported scenario qualification format")
    if manifest.get("scenario") != scenario_name:
        raise ValueError("qualification scenario must match scenario name")
    status = manifest.get("status")
    if status not in _STATUSES:
        raise ValueError("qualification status must be baseline, candidate, or qualified")
    actual_health = receipt_time_health(scenario)
    if manifest.get("receipt_time_health") != actual_health:
        raise ValueError("qualification receipt_time_health must match scenario")

    hypothesis = _optional_behaviour(manifest.get("hypothesis"), "hypothesis")
    behaviour = _optional_behaviour(manifest.get("behaviour"), "behaviour")
    corroboration = _corroboration(manifest.get("corroboration"))
    replay_test = manifest.get("replay_test")
    if replay_test is not None and (not isinstance(replay_test, str) or not replay_test):
        raise ValueError("replay_test must be a non-empty string")

    if status == "baseline":
        if any(value is not None for value in (hypothesis, behaviour, replay_test)) or corroboration:
            raise ValueError("baseline must not assert behaviour or corroboration")
        return ScenarioQualification(scenario_name, status, actual_health, None, None, (), None)
    if status == "candidate":
        if hypothesis is None:
            raise ValueError("candidate requires a bounded behaviour hypothesis")
        if any(value is not None for value in (behaviour, replay_test)) or corroboration:
            raise ValueError("candidate must not assert qualified behaviour")
        return ScenarioQualification(scenario_name, status, actual_health, None, hypothesis, (), None)

    if behaviour is None or hypothesis is not None:
        raise ValueError("qualified evidence requires behaviour, not a hypothesis")
    if actual_health != "healthy":
        raise ValueError("qualified evidence requires healthy broker receipt chronology")
    if not corroboration or replay_test is None:
        raise ValueError("qualified evidence requires corroboration and a replay test")
    return ScenarioQualification(scenario_name, status, actual_health, behaviour, None, corroboration, replay_test)


def require_qualified(
    scenario: Mapping[str, Any], manifest: Mapping[str, Any], behaviour: str
) -> ScenarioQualification:
    """Return qualified evidence for ``behaviour`` or reject the claim."""
    if behaviour not in _BEHAVIOURS:
        raise ValueError("unknown qualified behaviour")
    qualification = validate_qualification(scenario, manifest)
    if qualification.status != "qualified" or qualification.behaviour != behaviour:
        raise ValueError("scenario is not qualified for the requested behaviour")
    return qualification


def _optional_behaviour(value: object, field: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or value not in _BEHAVIOURS:
        raise ValueError(f"{field} must name a supported behaviour")
    return value


def _corroboration(value: object) -> tuple[dict[str, str], ...]:
    if value is None:
        return ()
    if not isinstance(value, list):
        raise ValueError("corroboration must be a list")
    result: list[dict[str, str]] = []
    for item in value:
        if not isinstance(item, Mapping):
            raise ValueError("corroboration entries must be objects")
        source, reference = item.get("source"), item.get("reference")
        if not isinstance(source, str) or not source or not isinstance(reference, str) or not reference:
            raise ValueError("corroboration requires source and reference")
        result.append({"source": source, "reference": reference})
    return tuple(result)
