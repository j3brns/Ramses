"""Household programmer for the isolated four-zone test world."""

from collections.abc import Mapping
from dataclasses import dataclass
from datetime import datetime

from ramses_twin.coordinator import ZoneCoordinator
from ramses_twin.ha_adapter import TestAdapterDescriptor, TestClimateCommand, apply_test_temporary_override
from ramses_twin.model import WeeklySchedule, ZoneController
from ramses_twin.runtime import TwinRuntime
from ramses_twin.store import JsonStateStore
from ramses_twin.thermal import ThermalModel


@dataclass(frozen=True)
class HouseholdZone:
    label: str
    controller_suffix: str
    test_controller_id: str
    zone_index: int
    valves: tuple[str, ...]


HOUSEHOLD_ZONES = {
    "kitchen": HouseholdZone("Kitchen", "487", "12:900001", 1, ("027", "030", "049")),
    "ejmb_rdgb": HouseholdZone("EJMB + RDGB", "487", "12:900001", 2, ("389", "048")),
    "lounge": HouseholdZone("Lounge", "751", "12:900002", 1, ("472", "387")),
    "cmq_jgb": HouseholdZone("CMQ JGB", "751", "12:900002", 2, ("040",)),
}


def build_household_runtime(schedules: Mapping[str, WeeklySchedule], store: JsonStateStore) -> TwinRuntime:
    """Fit each supplied programme to its own zone on a virtual controller."""
    if set(schedules) != set(HOUSEHOLD_ZONES):
        raise ValueError("supply one programme for each of the four household zones")
    return TwinRuntime({
        key: ZoneCoordinator(
            ZoneController(zone.test_controller_id, zone.zone_index, schedule=schedules[key]),
            ThermalModel(),
        ) for key, zone in HOUSEHOLD_ZONES.items()
    }, store)


def boost_until_next(
    descriptor: TestAdapterDescriptor, runtime: TwinRuntime, target_temperature: float, now: datetime,
) -> TestClimateCommand:
    """Expire at the next different programmed temperature in this zone."""
    schedule = runtime.coordinators[descriptor.zone_id].controller.schedule
    if schedule is None or len({point.target for point in schedule.switchpoints}) < 2:
        raise ValueError("the zone needs a future programmed temperature change")
    return apply_test_temporary_override(
        descriptor, runtime, target_temperature, schedule.next_change_after(now), now,
    )


def cancel_boost(runtime: TwinRuntime, zone_id: str, now: datetime) -> str:
    """Restore and checkpoint the selected zone's current programme."""
    if now.tzinfo is None or now.utcoffset() is None:
        raise ValueError("command time must be timezone-aware")
    controller = runtime.coordinators[zone_id].controller
    controller.return_to_schedule()
    runtime.checkpoint()
    return controller.setpoint_frame(now)
