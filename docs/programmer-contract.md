---
title: Programmer Contract
status: baseline
reference_model: ATC928G3000 Evohome controller
reference_user_guide: 32303496-001 C (2020)
verification: manual-derived; implementation pending
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

## State precedence

From highest to lowest priority: `Heating Off`/frost-protect, active timed whole-system action, active permanent whole-system action, active zone override, scheduled target. A cancelled or expired state is removed and the next lower state takes effect immediately. This precedence is an HA implementation decision inferred from the guide's modes, not a claimed Evohome state machine; its detailed behaviour is tested before it is exposed as control.

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

## Deliberate exclusions

- Live RF transmission, controller impersonation, binding changes, and boiler control.
- Evohome cloud, Wi-Fi setup, hot-water support, and proprietary internal algorithms.
- Copying the guide's prose or graphics. This is a concise, traceable abstraction.

## Source and maintenance

- ATC928G3000 Evohome User Guide, document `32303496-001 C`, 2020: [public copy](https://automatikcentret.dk/files/data/doc/products/ATC928G3000/evohome-userguide_EN.pdf). This is evidence of user-facing behaviour only; it does not prove CM67z RF timing, binding, or firmware internals.
- The corresponding concept records and provenance live in [the repertoire index](repertoire/index.md).
- A source revision or contradiction requires a contract review, linked acceptance-test update, and release documentation update.
