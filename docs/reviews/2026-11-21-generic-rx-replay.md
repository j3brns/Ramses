# Adversarial review: generic RX replay

## Scope

Add a pure structural decoder and ordered replay trace for bounded gateway-RX scenarios.

## Failure modes

- A malformed frame reaches later semantic logic as if it were protocol evidence.
- Gateway frame order is lost, or a list position is mistaken for elapsed time.
- The 1970 gateway clock is used to claim controller timing or schedule fidelity.
- Packet-code counts are mistaken for physical state transitions.

## Evidence and tests

The decoder accepts the 111-event `baseline-rx-window` in recorded order, preserving ordinals and producing deterministic counts. Tests reject malformed field counts and payload lengths. The baseline marks the gateway clock `epoch-invalid`; no broker receipt timestamp exists in that older scenario, so timing remains unavailable.

## Decision

Use replay now for frame-structure, order and code-coverage work only. Named Kitchen schedule, local-override and restart scenarios remain required before replay asserts any controller or device behaviour.

## Rollback

Revert the pure replay module, tests, contract additions and this review. No broker, RF, Home Assistant or heating state is affected.
