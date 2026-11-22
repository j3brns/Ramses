"""In-process runtime that an HA adapter can call without duplicating model logic."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime

from ramses_twin.coordinator import ZoneCoordinator
from ramses_twin.store import JsonStateStore
from ramses_twin.thermal import Observation, TrainingResult


@dataclass
class TwinRuntime:
    coordinators: dict[str, ZoneCoordinator]
    store: JsonStateStore
    _last_observation: dict[str, Observation] = field(default_factory=dict)

    def restore(self) -> None:
        for zone_id, model in self.store.load_models().items():
            if zone_id in self.coordinators:
                self.coordinators[zone_id].thermal_model = model

    def recovery_frames(self, now: datetime) -> dict[str, str]:
        """Recompute every configured target for a test-only recovery publication."""
        if now.tzinfo is None or now.utcoffset() is None:
            raise ValueError("recovery time must be timezone-aware")
        return {
            zone_id: self.coordinators[zone_id].controller.setpoint_frame(now)
            for zone_id in sorted(self.coordinators)
        }

    def observe(self, zone_id: str, observation: Observation) -> TrainingResult | None:
        coordinator = self.coordinators[zone_id]
        previous = self._last_observation.get(zone_id)
        self._last_observation[zone_id] = observation
        if previous is None:
            return None
        result = coordinator.thermal_model.learn(previous, observation)
        if result.accepted:
            self.store.save_models({key: item.thermal_model for key, item in self.coordinators.items()})
        return result

    def due_frame(self, zone_id: str, now: datetime, room_temp: float, outdoor_temp: float) -> str | None:
        return self.coordinators[zone_id].apply_due_start(now, room_temp, outdoor_temp)
