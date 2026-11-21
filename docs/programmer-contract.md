---
title: Programmer Contract
status: baseline
reference_model: ATC928G3000 Evohome controller
reference_user_guide: 32303496-001 C (2020)
verification: manual-derived; implementation pending
source_url: https://automatikcentret.dk/files/data/doc/products/ATC928G3000/evohome-userguide_EN.pdf
source_checked: 2026-11-21
---

# Programmer Contract

This contract defines the user-visible behaviour Home Assistant will provide for the Ramses test system. Home Assistant is the implementation; the Evohome ATC928G3000 user guide is the behavioural fidelity reference. It is not a claim to clone Evohome firmware or its undocumented RF behaviour.

## Product behaviour to preserve

| Capability | Contract | Reference |
| --- | --- | --- |
| Zones | A zone is one room or a deliberate group of rooms; its target is independently visible and controllable. | User guide pp. 4–5 |
| Weekly programme | Each zone has a weekly sequence of time/temperature switch points. A user can inspect and edit a zone's schedule. | pp. 9–10 |
| Temporary override | A user may set a zone target until a chosen end time. On expiry it resumes the schedule. | p. 11 |
| Permanent override | A user may make a zone target permanent, and explicitly cancel it to resume the schedule. | p. 11 |
| Quick actions | Eco/Boost adjusts zones by up to 3 °C (timed 1–24 h); Away sets zones to 15 °C (timed 1–99 days); Day Off applies Saturday's schedule (timed 1–99 days); Custom applies a custom schedule; Heating Off is a frost-protect/off mode. All have explicit cancellation. | pp. 12–15 |
| Optimisation | Optimum start/stop is optional and visibly indicated. It advances or reduces use of scheduled targets; it does not change the saved schedule. | pp. 6–7 |
| Explainability | The user can see active target, origin/mode, expiry or next event, and alerts. | pp. 2, 11, 16 |

## Evidence and implementation status

`manual-derived` means the guide describes a user-visible capability. It does
not establish an HA data model, RF message, timing tolerance, persistence
behaviour, or a CM67z implementation detail. `HA decision` means this project
must specify and test the detail before it is offered. `Not implemented` is not
a promise that a dashboard control exists.

| Capability | Guide evidence | Project status |
| --- | --- | --- |
| Zones | pp. 4-5 | Core schedule model; UI pending |
| Weekly programme | pp. 9-10 | Core model and pure HA mapping; UI pending |
| Temporary override | p. 11 | Virtual test seam only |
| Permanent override | p. 11 | Not implemented |
| Eco/Boost | p. 12 | Not implemented |
| Away | p. 13 | Not implemented |
| Day Off | p. 14 | Not implemented |
| Heating Off / Custom | pp. 12, 15-16 | Not implemented |
| Optimisation | pp. 6-7 | Test-world proposal only |
| Explainability | pp. 2, 11, 16 | UI contract defined; UI pending |

## HA decisions still requiring implementation

Proposed precedence is `Heating Off`/frost-protect > active timed whole-system
action > active permanent whole-system action > active zone override > scheduled
target. A cancelled or expired state would reveal the next lower state
immediately. This is an HA decision inferred from the guide's modes, not a
claimed Evohome state machine. It must not become a control feature without a
dedicated state model and deterministic tests.

## Virtual TRV local override

A virtual TRV local override is separate from the programmer's zone override. In the test model, it stays active until the virtual TRV accepts its next bound-zone controller setpoint; that accepted setpoint clears the local override and becomes the effective target. A foreign-zone frame does neither. This is an explicit simulator coordination rule, chosen so the controller can restore one authoritative zone target at a known event. The public guide and current passive packet corpus do not establish the physical TRV's internal expiry behaviour.

## Acceptance examples

1. Given a Kitchen schedule changes from 18 °C to 21 °C at 06:30, at 06:30 the active target is 21 °C and the UI shows the next change.
2. Given a Lounge temporary override of 22 °C until 18:00, the active target remains 22 °C until 18:00, then returns to the schedule without a manual action.
3. Given a permanent override, a later schedule edge does not supersede it; **Return to schedule** cancels it and applies the current scheduled target.
4. Given a timed Away action, each affected zone is 15 °C and shows the mode and expiry. Cancelling Away returns every zone to its previously applicable state.
5. Given trained optimum start for a rising scheduled target, the UI identifies it as optimisation; the stored schedule remains unchanged.
6. Given an HA restart or MQTT reconnection, the active target is recomputed from durable schedule and override state before test-world publication resumes.
7. Given Heating Off, the UI identifies frost-protect/off rather than asserting zero heat, and tests its configured resulting target separately.
8. Given an override ending on a schedule edge, or expiry across DST, one documented state transition occurs with no duplicate setpoint publication.
9. Given a schedule edit while an override is active, the UI preserves and explains the active override; cancellation applies the newly current schedule target.

## Verification map

| Contract slice | Present evidence | Required before control-capable release |
| --- | --- | --- |
| Weekly schedule and temporary expiry | `tests/test_timer.py`; `tests/test_model.py`; `tests/test_ha_climate.py` | Test View and computer-use acceptance |
| HA schedule mapping | `tests/test_ha_schedule.py` | Rendered test-only cards and UI-01â€“UI-07 |
| Permanent override and Quick Actions | Manual-derived only | State model, deterministic tests, UI acceptance and adversarial review |
| Optimisation | Manual-derived indication; test-world model contract | Bounded observation/replay evidence, accuracy criteria and UI acceptance |
| Restart/reconnect | Project rule, not guide evidence | Ordered evidence plus replay contract |

## Deliberate exclusions

- Live RF transmission, controller impersonation, binding changes, and boiler control.
- Evohome cloud, Wi-Fi setup, hot-water support, and proprietary internal algorithms.
- Copying the guide's prose or graphics. This is a concise, traceable abstraction.

## Source and maintenance

- ATC928G3000 Evohome User Guide, document `32303496-001 C`, 2020: [public copy](https://automatikcentret.dk/files/data/doc/products/ATC928G3000/evohome-userguide_EN.pdf). This is evidence of user-facing behaviour only; it does not prove CM67z RF timing, binding, or firmware internals.
- The corresponding concept records and provenance live in [the repertoire index](repertoire/index.md).
- A source revision or contradiction requires a contract review, linked acceptance-test update, and release documentation update.
