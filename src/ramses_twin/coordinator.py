"""Zone coordination: timer and optimiser decide, the transport only carries frames."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from ramses_twin.model import ZoneController
from ramses_twin.optimiser import StartDecision, plan_optimum_start
from ramses_twin.thermal import ThermalModel


@dataclass
class ZoneCoordinator:
    """A software-only zone coordinator with no MQTT side effects."""

    controller: ZoneController
    thermal_model: ThermalModel

    def plan(self, now: datetime, room_temp: float, outdoor_temp: float) -> StartDecision | None:
        if self.controller.schedule is None:
            return None
        return plan_optimum_start(self.controller.schedule, self.thermal_model, now, room_temp, outdoor_temp)

    def apply_due_start(self, now: datetime, room_temp: float, outdoor_temp: float) -> str | None:
        """Apply one due early start and return its test-world setpoint frame."""
        decision = self.plan(now, room_temp, outdoor_temp)
        if decision is None or now < decision.start_at:
            return None
        if self.controller.override_target == decision.target and self.controller.override_until == decision.scheduled_at:
            return None
        self.controller.boost(decision.target, decision.scheduled_at)
        return self.controller.setpoint_frame(now)
