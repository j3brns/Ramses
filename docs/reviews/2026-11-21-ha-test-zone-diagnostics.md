# Adversarial review: read-only HA test-zone diagnostics

## Scope

Adds a pure projection of one simulated zone's effective target, next scheduled
change, optimiser readiness, and optional planned start. The projection has
test-only entity names and neither changes controller state nor transmits data.

## Failure modes

- A dashboard could mistake an untrained optimiser for an actionable plan.
- A diagnostic read could accidentally apply a planned start or an override.
- A later adapter could expose names that collide with live Home Assistant
  entities.

## Evidence and tests

`tests/test_ha_diagnostics.py` proves the entity names use the `ramses_test`
prefix, an untrained model has no planned start, a trained model reports a
future plan, reads leave the controller override untouched, and a naive clock
is rejected.

## Decision

Expose diagnostics only as a pure, test-world projection. Any Home Assistant
entity implementation remains a separate, isolated transport slice.

## Rollback

Remove the projection and its descriptor identifiers. It has no persisted
state, wire effect, or dependency on a live Home Assistant instance.
