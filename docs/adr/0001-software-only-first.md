# ADR 0001: Software-only test world first

## Status

Accepted.

## Decision

Build and test the virtual CM67z system against `RAMSES/TEST/...` MQTT topics before any RF transmission, binding, or live-controller replacement.

## Consequences

- The initial work cannot affect live heating.
- The simulator must reproduce the gateway frame contract, not merely dashboard states.
- A future real-RF cutover requires a new ADR and an explicit user decision.
