---
title: Ramses Test programmer guide
status: draft — test system only
source_contract: programmer-contract.md
---

# Ramses Test programmer guide

This guide describes the planned **Ramses Test** dashboard. It is a software-only test system. It does not control the live heating installation or publish to the live MQTT root.

## Read a zone

Each zone shows its current temperature, effective target, the source of that target, and what changes next. The source is one of **Schedule**, **Temporary override**, **Permanent override**, a whole-system action, or **Optimisation**. The dashboard also shows alerts such as an unavailable test device.

## Change a temperature

From a zone thermostat card, select a target. Choose either a temporary end time or **Make permanent**. A temporary override automatically returns to the schedule at its expiry. A permanent override remains active until **Return to schedule** is selected.

Until the test-only climate control path has passed its safety and computer-use tests, these controls are explanatory mock-ups and cannot publish a command.

## Use the schedule

The weekly schedule sets the normal target for each zone. The dashboard shows the current schedule value and the next switch. Editing a schedule changes future scheduled targets; it does not silently cancel a currently active override.

## Whole-system actions

The planned actions are Eco/Boost, Away, Day Off, Heating Off/frost protection and Custom. Their exact targets, duration and precedence are stated in the [Programmer Contract](programmer-contract.md). Each action must display its expiry and provide a clear cancel/return path.

## Optimisation

Optimum start is optional. When enough test evidence has trained the model, it may start applying an already scheduled warmer target early so that a room reaches its target at the scheduled time. It never changes the saved schedule, and the dashboard identifies when it is active.

## Help and safety

The Ramses Test dashboard will provide this guide through a Help subview. The Markdown source in this file remains canonical; the Help card is a generated rendering. If a UI appears to affect a live entity, stop: the test dashboard must use only `RAMSES/TEST/...` entities and topics.

## Read evidence status

Evidence status shows what the test system has actually observed. **Baseline** means bounded ordered receive traffic. **Candidate** means a rule found an event that still needs corroboration. **Qualified** means the named capture and replay checks passed. A gateway timestamp near 1970 is invalid for elapsed-time claims; use the displayed broker receipt time to assess capture freshness. Evidence status is read-only and never exposes a live packet stream.
