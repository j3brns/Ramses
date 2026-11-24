# Test programmer deployment

The household simulation uses native HA helpers. Scripts store only a zone's
absolute boost expiry. The cards combine that value with the current schedule
block to display the effective target. The Python simulator and the native
programmer implement this behaviour independently.

Generate the configuration with `py scripts/test_programmer_ui.py`. Its
`schedules`, `expiries`, `scripts` and `view` keys contain complete HA
objects. On a fresh instance, create the **Ramses Test** storage dashboard
from `target-system/ramses-test-dashboard.yaml` first.

1. Using an authenticated HA WebSocket session, send `schedule/create` for
   each schedules value and `input_number/create` for each expiries value.
   Spread the value's fields into the command. Each returned ID must match
   its key in the generator output. For an existing installation, preserve
   resident timetables and deadlines. Resolve any ID collision first.
2. POST each scripts value to `/api/config/script/config/<key>` on the same
   HA instance. Each script targets exactly one generated input_number.
3. Read `lovelace/config` with `url_path: ramses-test`. Preserve existing
   views and append the generated view once, or replace only the previously
   generated `programmer` view. Save with `lovelace/config/save`, the same
   url_path and merged config. Refresh the Help card from the canonical
   Markdown in `docs/user-guide.md`.
4. Open **Ramses Test → Programmer**. Boost each zone in turn, verify the
   displayed deadline equals its timetable's next event, then cancel it.
   Other zones retain their target and deadline. Test helpers under Settings
   → Devices & services → Helpers support editing the example timetables.

On 24 November 2026 all four boost and cancel actions passed on HA 2026.11.1.
The desktop HA window displayed the four zones, their targets, next switches
and action buttons. Mobile appearance and reboot recovery on the deployed
instance still require separate checks.
