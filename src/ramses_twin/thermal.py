"""Small, explainable per-zone thermal response model.

This learns the building response, not Honeywell's proprietary optimiser.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


MIN_TRAINING_SAMPLES = 3


@dataclass(frozen=True)
class Observation:
    """One aligned zone observation used to learn a temperature slope."""

    at: datetime
    room_temp: float
    outdoor_temp: float
    valve_demand: float
    boiler_on: bool

    def __post_init__(self) -> None:
        if self.at.tzinfo is None or self.at.utcoffset() is None:
            raise ValueError("observation time must be timezone-aware")
        if not 0.0 <= self.valve_demand <= 1.0:
            raise ValueError("valve demand must be between 0 and 1")


@dataclass(frozen=True)
class TrainingResult:
    kind: str
    accepted: bool
    estimate: float | None = None


@dataclass
class ThermalModel:
    """Learns heating gain and passive heat loss as degrees per minute."""

    heat_rate: float | None = None
    loss_rate: float | None = None
    heat_samples: int = 0
    loss_samples: int = 0
    alpha: float = 0.25

    @property
    def ready(self) -> bool:
        return (
            self.heat_rate is not None
            and self.loss_rate is not None
            and self.heat_samples >= MIN_TRAINING_SAMPLES
            and self.loss_samples >= MIN_TRAINING_SAMPLES
        )

    @staticmethod
    def _ewma(previous: float | None, value: float, alpha: float) -> float:
        return value if previous is None else alpha * value + (1 - alpha) * previous

    def learn(self, previous: Observation, current: Observation) -> TrainingResult:
        """Learn from one clean cooling or heating interval.

        Cooling intervals estimate loss. Heating intervals estimate gain after
        adjusting for the current loss estimate. Ambiguous or long intervals
        are intentionally ignored.
        """
        minutes = (current.at - previous.at).total_seconds() / 60
        if not 1 <= minutes <= 30:
            return TrainingResult("ignored", False)
        slope = (current.room_temp - previous.room_temp) / minutes
        temperature_gap = previous.room_temp - previous.outdoor_temp

        if previous.valve_demand <= 0.05 and not previous.boiler_on and temperature_gap >= 1 and slope <= 0:
            estimate = -slope / temperature_gap
            self.loss_rate = self._ewma(self.loss_rate, estimate, self.alpha)
            self.loss_samples += 1
            return TrainingResult("loss", True, estimate)

        if previous.valve_demand >= 0.2 and previous.boiler_on and self.loss_rate is not None:
            estimate = (slope + self.loss_rate * temperature_gap) / previous.valve_demand
            if estimate > 0:
                self.heat_rate = self._ewma(self.heat_rate, estimate, self.alpha)
                self.heat_samples += 1
                return TrainingResult("heat", True, estimate)

        return TrainingResult("ignored", False)

    def minutes_to_target(
        self,
        room_temp: float,
        target_temp: float,
        outdoor_temp: float,
        demand: float = 1.0,
        max_minutes: int = 90,
    ) -> int | None:
        """Simulate minute steps until target is reached, or return ``None``."""
        if not self.ready:
            return None
        if target_temp <= room_temp:
            return 0
        if not 0 < demand <= 1:
            raise ValueError("prediction demand must be between 0 and 1")
        assert self.heat_rate is not None and self.loss_rate is not None
        temperature = room_temp
        for minute in range(1, max_minutes + 1):
            temperature += self.heat_rate * demand - self.loss_rate * (temperature - outdoor_temp)
            if temperature >= target_temp:
                return minute
        return None

    def to_state(self) -> dict[str, float | int | None]:
        return {
            "heat_rate": self.heat_rate,
            "loss_rate": self.loss_rate,
            "heat_samples": self.heat_samples,
            "loss_samples": self.loss_samples,
            "alpha": self.alpha,
        }

    @classmethod
    def from_state(cls, state: dict[str, float | int | None]) -> "ThermalModel":
        return cls(
            heat_rate=state["heat_rate"],  # type: ignore[arg-type]
            loss_rate=state["loss_rate"],  # type: ignore[arg-type]
            heat_samples=state["heat_samples"],  # type: ignore[arg-type]
            loss_samples=state["loss_samples"],  # type: ignore[arg-type]
            alpha=state["alpha"],  # type: ignore[arg-type]
        )
