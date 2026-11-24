---
title: Ramses Test programmer guide
status: draft — test system only
source_contract: programmer-contract.md
---

# Ramses Test programmer guide

Open **Ramses Test → Programmer** to try the household programme in Home Assistant. Kitchen, EJMB + RDGB, Lounge and CMQ JGB each have a separate test timetable. The example starts at 07:00 with a target of 20°C and returns to 16°C at 22:00 every day. These are sample settings.

Tap **Boost to 22°C** on one zone. The card shows its target and the end of the boost. The zone follows its schedule again at the next scheduled switch, or immediately when you tap **Return to schedule**. The other zones keep their own targets. The control stores the deadline in a Home Assistant helper. It changes only the simulated programme.

## Read a zone

Each zone shows its current temperature, effective target, the source of that target, and what changes next. The source is one of **Schedule**, **Temporary override**, **Permanent override**, a whole-system action, or **Optimisation**. The dashboard also shows alerts such as an unavailable test device.

## Change a temperature when the test path is enabled

When the test-only climate control path has passed its safety and computer-use tests, a zone thermostat card will allow a target to be selected. A temporary override will return to the schedule at its expiry. A permanent override will remain active until **Return to schedule** is selected.

The Programmer buttons work with native Home Assistant test helpers. The separate thermostat card on the Ramses Test overview is a diagnostic display.

## Use the schedule

The weekly schedule sets the normal target for each zone. The dashboard shows the current schedule value and the next switch. Editing a schedule changes future scheduled targets; it does not silently cancel a currently active override.

## Whole-system actions

The planned actions are Eco/Boost, Away, Day Off, Heating Off/frost protection and Custom. Their exact targets, duration and precedence are stated in the [Programmer Contract](programmer-contract.md). Each action must display its expiry and provide a clear cancel/return path.

## Optimisation

Optimum start is optional. When enough test evidence has trained the model, it may start applying an already scheduled warmer target early so that a room reaches its target at the scheduled time. It never changes the saved schedule, and the dashboard identifies when it is active.

## Help and safety

The Ramses Test dashboard will provide this guide through a Help subview. The Markdown source in this file remains canonical; the Help card is a generated rendering. See the [dashboard contract](lovelace-ui-contract.md) for the planned layout and the [computer-use acceptance runbook](test-view-computer-use-runbook.md) for the separately authorised test-only deployment procedure. If a UI appears to affect a live entity, stop: the test dashboard must use only `RAMSES/TEST/...` entities and topics.

## Read evidence status

Evidence status shows what the test system has actually observed. **Baseline** means bounded ordered receive traffic. **Candidate** means a rule found an event that still needs corroboration. **Qualified** means the named capture and replay checks passed. A gateway timestamp near 1970 is invalid for elapsed-time claims; use the displayed broker receipt time to assess capture freshness. Evidence status is read-only and never exposes a live packet stream.
