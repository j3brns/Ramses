"""Transparent virtual BDR relay response for the software-only test world.

The model represents the test-world boiler-enable boundary. It does not encode
or operate a physical BDR91 relay.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ramses_twin.trv import TrvReport


@dataclass(frozen=True)
class BdrReport:
    """One deterministic aggregate-demand result for a virtual relay."""

    device_id: str
    demand: float
    relay_on: bool
    contributing_devices: tuple[str, ...]
    observed_at: datetime


@dataclass
class VirtualBdr:
    """Aggregate virtual valve demand into an explicit test-only relay state.

    The maximum demand wins. This preserves the hottest zone's request as a
    simple, inspectable modulation value while ``relay_on`` represents the
    binary boiler-enable side. Neither rule claims physical BDR91 behaviour.
    """

    device_id: str
    on_threshold: float = 0.01

    def __post_init__(self) -> None:
        if not 0.0 <= self.on_threshold <= 1.0:
            raise ValueError("relay threshold must be between zero and one")

    def respond(self, reports: tuple[TrvReport, ...], now: datetime) -> BdrReport:
        """Return a bounded relay response from current virtual TRV reports."""
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("report time must be timezone-aware")
        for report in reports:
            if not 0.0 <= report.heat_demand <= 1.0:
                raise ValueError("TRV heat demand must be between zero and one")

        demand = max((report.heat_demand for report in reports), default=0.0)
        contributors = tuple(sorted(report.device_id for report in reports if report.heat_demand > 0.0))
        return BdrReport(
            device_id=self.device_id,
            demand=demand,
            relay_on=demand >= self.on_threshold,
            contributing_devices=contributors,
            observed_at=now,
        )
