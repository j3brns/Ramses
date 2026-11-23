---
scope: logical-ha-system-diagram
date: 2026-11-23
status: accepted
---

# Logical Home Assistant system diagram review

## Scope

Add an editable, source-linked logical diagram and concise household context to
the canonical system architecture document.

## Failure modes considered

- A diagram could imply that Home Assistant currently has authority over the
  boiler, TRVs or live RF network.
- It could expose a network address, credential, device configuration or radio
  command path.
- Third-party product imagery could be copied into the repository without
  provenance or permission.

## Evidence

- The diagram source passed the Mermaid static validator and produced a
  structural SVG preview. This is source/structure validation, not browser
  renderer acceptance.
- The existing architecture, README and user-provided household description
  establish the named logical components and test-world boundary.

## Decision

Describe interfaces, observation and future authority as separate roles. Mark
direct zone/boiler tasking as evidence-gated. Keep product imagery out of the
repository; the hardware inventory links to sources instead.

## Rollback

Remove the Household context section and `docs/diagrams/logical-ha-system.*`.
No executable, Home Assistant, MQTT, RF or heating state changes.
