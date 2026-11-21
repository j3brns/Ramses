from datetime import datetime, timezone

import pytest

from ramses_twin.ha_adapter import schedule_snapshot_from_ha, weekly_schedule_from_ha_blocks


def test_ha_blocks_create_weekly_targets_and_explicit_off_periods() -> None:
    schedule = weekly_schedule_from_ha_blocks(
        {
            "monday": [
                {"from": "06:30:00", "to": "08:00:00", "data": {"target_temperature": 20.5}},
                {"from": "08:00:00", "to": "22:00:00", "data": {"target_temperature": 18}},
            ]
        },
        off_target=12.0,
    )
    utc = timezone.utc

    assert schedule.target_at(datetime(2026, 11, 23, 6, 29, tzinfo=utc)) == 12.0
    assert schedule.target_at(datetime(2026, 11, 23, 6, 30, tzinfo=utc)) == 20.5
    assert schedule.target_at(datetime(2026, 11, 23, 8, 0, tzinfo=utc)) == 18.0
    assert schedule.target_at(datetime(2026, 11, 23, 22, 0, tzinfo=utc)) == 12.0


def test_ha_schedule_snapshot_reads_active_data_and_dst_aware_next_event() -> None:
    snapshot = schedule_snapshot_from_ha(
        "on",
        {"target_temperature": 21, "next_event": "2026-03-29T02:00:00+01:00"},
    )

    assert snapshot.active_target == 21.0
    assert snapshot.next_event.utcoffset().total_seconds() == 3600

    off = schedule_snapshot_from_ha("off", {"next_event": "2026-03-29T03:00:00+01:00"})
    assert off.active_target is None


@pytest.mark.parametrize(
    "schedule",
    [
        {"monday": [{"from": "06:00", "to": "07:00", "data": {}}]},
        {"monday": [{"from": "07:00", "to": "06:00", "data": {"target_temperature": 20}}]},
        {"monday": [{"from": "06:00:01", "to": "07:00", "data": {"target_temperature": 20}}]},
        {"funday": [{"from": "06:00", "to": "07:00", "data": {"target_temperature": 20}}]},
        [],
    ],
)
def test_ha_blocks_reject_invalid_schedule_data(schedule: dict[str, list[dict[str, object]]]) -> None:
    with pytest.raises(ValueError):
        weekly_schedule_from_ha_blocks(schedule, off_target=12.0)


@pytest.mark.parametrize(
    "state, attributes",
    [
        ("on", {"target_temperature": 20, "next_event": "2026-03-29T02:00:00"}),
        ("on", {"target_temperature": 20, "next_event": "not-a-date"}),
        ("on", {"next_event": "2026-03-29T02:00:00+01:00"}),
        ("unknown", {"next_event": "2026-03-29T02:00:00+01:00"}),
    ],
)
def test_ha_snapshot_rejects_invalid_or_ambiguous_state(state: str, attributes: dict[str, object]) -> None:
    with pytest.raises(ValueError):
        schedule_snapshot_from_ha(state, attributes)
