"""Report whether the three observed-behaviour replay prerequisites exist.

This module deliberately reports readiness rather than trying to infer a
behaviour from packet shape.  A baseline capture is useful for decoder tests,
but it cannot make a schedule, override, or restart claim by itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from ramses_twin.qualification import validate_qualification


REQUIRED_BEHAVIOURS = (
    "schedule-change",
    "override-expiry",
    "restart-reconnect",
)


@dataclass(frozen=True)
class ReplayReadiness:
    """Immutable, conservative status of replay evidence coverage."""

    qualified: tuple[str, ...]
    missing: tuple[str, ...]
    rejected: dict[str, str]

    @property
    def ready(self) -> bool:
        return not self.missing

    def as_dict(self) -> dict[str, object]:
        return {
            "required": list(REQUIRED_BEHAVIOURS),
            "qualified": list(self.qualified),
            "missing": list(self.missing),
            "rejected": dict(sorted(self.rejected.items())),
            "ready": self.ready,
        }


def replay_readiness(
    scenarios: Mapping[str, Mapping[str, Any]],
    manifests: Mapping[str, Mapping[str, Any]],
) -> ReplayReadiness:
    """Return coverage of required replay behaviours without promoting data.

    ``scenarios`` and ``manifests`` are keyed by scenario name.  An absent,
    invalid, baseline, or candidate manifest is rejected for readiness.  Only
    the existing qualification validator can admit a named behaviour.
    """
    qualified: set[str] = set()
    rejected: dict[str, str] = {}

    for name, scenario in scenarios.items():
        manifest = manifests.get(name)
        if manifest is None:
            rejected[name] = "missing qualification manifest"
            continue
        try:
            qualification = validate_qualification(scenario, manifest)
        except ValueError as error:
            rejected[name] = str(error)
            continue
        if qualification.status != "qualified" or qualification.behaviour is None:
            rejected[name] = f"status is {qualification.status}, not qualified"
            continue
        qualified.add(qualification.behaviour)

    accepted = tuple(behaviour for behaviour in REQUIRED_BEHAVIOURS if behaviour in qualified)
    missing = tuple(behaviour for behaviour in REQUIRED_BEHAVIOURS if behaviour not in qualified)
    return ReplayReadiness(accepted, missing, rejected)
