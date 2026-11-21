# Adversarial review: HA pure-library import

## Scope

Add a pure-Python descriptor for the future Home Assistant Test adapter and prove that it imports without a Home Assistant runtime.

## Failure modes

- A model/test import pulls in Home Assistant, a broker client, or a radio dependency.
- An adapter descriptor can name a live MQTT root or an unsafe entity identifier.
- A minimal import proof is mistaken for a functioning Home Assistant integration or climate-control path.

## Evidence and tests

The descriptor imports only Python standard-library modules and the existing isolated topic helper. Tests remove any `homeassistant` module entry before import, confirm it remains absent, assert stable test-only entity/topic output, and reject unsafe entity fragments and gateway IDs.

## Decision

Keep the HA-facing seam as a pure descriptor until the isolated transport, schedule mapping, diagnostics and climate-control tasks are separately implemented. Use the `ramses_test` entity prefix and validated `RAMSES/TEST/...` topics as the only exposed identifiers.

## Rollback

Revert the descriptor, tests and documentation. No Home Assistant runtime, MQTT client, RF or live-heating state is affected.
