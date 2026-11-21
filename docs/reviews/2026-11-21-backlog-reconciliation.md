# Adversarial review

## Scope

Reconciles the delivery backlog after independent reviews of dependencies, safety/evidence, and the Home Assistant/dashboard path.

## Failure modes

- Work can look parallel while its missing evidence or transport prerequisites make it unverifiable.
- A virtual TRV can disagree with timer override semantics and produce a convincing but invalid twin.
- A test transport protected only by convention can accidentally target live MQTT.
- An HA dashboard can expose a control before its test-only boundary is proven.

## Evidence and tests

- Three independent backlog reviews identified the same missing capture/replay and runtime-isolation prerequisites.
- The local `tk` dependency graph now records feeder, telemetry, restart, override-contract, decoder/replay, and HA sub-slices.
- Contracts and roadmap now make those prerequisites explicit.

## Decision

Accept the revised order: transport and feeder/HA packaging can proceed in parallel; calibration waits for scenarios, telemetry, override decision, and decoder; RF waits for every test-world slice.

## Rollback

Revert this documentation commit and remove its local `tk` tasks/dependencies if the project changes to a different test architecture. Do not discard the review findings.
