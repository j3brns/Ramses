from datetime import datetime, timezone

import pytest

from ramses_twin.bdr import VirtualBdr
from ramses_twin.trv import VirtualTrv


def _report(device_id: str, temperature: float, target: float):
    valve = VirtualTrv(device_id, "12:900001", 1, temperature=temperature, target=target)
    return valve.report(datetime(2026, 11, 21, 12, 0, tzinfo=timezone.utc))


def test_bdr_uses_highest_virtual_demand_and_lists_contributors() -> None:
    bdr = VirtualBdr("13:900642")
    result = bdr.respond(
        (_report("04:900030", 19.0, 20.0), _report("04:900027", 18.0, 22.0)),
        datetime(2026, 11, 21, 12, 5, tzinfo=timezone.utc),
    )

    assert result.demand == 1.0
    assert result.relay_on
    assert result.contributing_devices == ("04:900027", "04:900030")


def test_bdr_is_off_without_demand_and_uses_configured_threshold() -> None:
    now = datetime(2026, 11, 21, tzinfo=timezone.utc)
    assert not VirtualBdr("13:900642").respond((), now).relay_on

    bdr = VirtualBdr("13:900642", on_threshold=0.5)
    result = bdr.respond((_report("04:900027", 19.0, 20.0),), now)
    assert result.demand == 0.25
    assert not result.relay_on


def test_bdr_rejects_invalid_threshold_demand_and_naive_time() -> None:
    with pytest.raises(ValueError, match="threshold"):
        VirtualBdr("13:900642", on_threshold=1.1)

    bdr = VirtualBdr("13:900642")
    with pytest.raises(ValueError, match="timezone-aware"):
        bdr.respond((), datetime(2026, 11, 21))
