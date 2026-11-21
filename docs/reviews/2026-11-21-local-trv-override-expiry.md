# Adversarial review: local TRV override expiry

## Scope

Define the event that ends a virtual TRV local override in the software-only test model.

## Failure modes

- A local override can persist indefinitely, so the controller and valve disagree about the zone target.
- A foreign-zone frame can cancel an unrelated valve's override.
- A simple simulator rule is presented as undocumented physical TRV behaviour.
- Calibration treats model output as RF evidence.

## Evidence and tests

The programmer contract distinguishes user-visible zone overrides from valve-local state, but the public guide and passive corpus do not establish physical local-override expiry. Fixed-input tests prove that a foreign-zone setpoint preserves the override and that the next accepted bound-zone setpoint clears it and supplies the effective target.

## Decision

In the virtual model, the next accepted setpoint for the bound zone is the explicit controller event that clears local override. It restores a single coordinated target without introducing a second timer. This is a simulator coordination decision only; future ordered scenarios may require a revised physical-fidelity model.

## Rollback

Restore the former independent local-override state and mark the expiry rule unresolved. No MQTT, RF, Home Assistant or live-heating state is affected.
