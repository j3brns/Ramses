# Adversarial review: replay readiness

## Scope

Review the boundary between structural replay and a claim that the model can
replay observed controller behaviour.

## Failure modes

- A bounded baseline fixture is treated as evidence of a schedule, override,
  or restart.
- A candidate packet shape is promoted without corroboration.
- A malformed or mismatched manifest appears to satisfy release coverage.
- A future readiness gate accidentally contacts a live broker.

## Evidence and tests

`replay_readiness` delegates qualification to the existing validator and only
accepts its explicit qualified behaviour. Tests cover a baseline without a
manifest, complete exact coverage, and a candidate manifest. The report reads
local JSON only.

## Decision

Expose the current evidence gap as deterministic output. Do not make a model,
dashboard, or RF readiness claim until every required behaviour is separately
qualified.

## Rollback

Revert the readiness module, report script, tests, repertoire note and this
review together. They have no Home Assistant, MQTT, RF, gateway, credential or
data-collection side effect.
