# Adversarial review: RF validation gate

## Scope

Review the proposed decision gate for any future RF validation experiment.

## Failure modes

- A simulator pass or decoded packet is treated as authority to transmit.
- An experiment uses an undocumented sender identity, binding, or target zone.
- A one-zone test accidentally becomes a boiler-control or multi-zone change.
- A failed experiment has no immediate, verified way to restore the legacy
  controller.
- A missing evidence field is hidden by a vague "ready" label.

## Evidence and tests

The Programmer, MQTT, scenario-qualification, replay, and dashboard contracts
already keep the executable test world under `RAMSES/TEST` and live radio
receive-only. The ADR maps their missing physical-evidence requirements into
explicit gate fields. No test claims live validation, and this documentation
change has no live side effect.

## Decision

Keep the ADR proposed. Require an explicit later ADR to select either no-go or
one named reversible experiment only after every gate field is evidenced and
owner approval is recorded.

## Rollback

Revert the ADR and review together if the gate is superseded. No RF, Home
Assistant, broker, gateway, or hardware state needs restoration.
