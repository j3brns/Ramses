# Adversarial review: Kitchen transition selector

## Scope

Add a pure local selector for candidate Kitchen controller setpoint changes in
an already recorded bounded RX scenario.

## Failure modes

- A TRV-originated `2309`, another controller, or another zone is labelled as
  a Kitchen controller transition.
- The gateway's 1970 clock or unordered receipt times are treated as evidence
  of a timed schedule edge.
- A controller setpoint change is presented as proof that the schedule caused
  it.

## Evidence and tests

Tests require controller `12:216487`, zone `01`, changing targets and ordered
current broker receipt timestamps. They reject out-of-order candidate receipt
time, out-of-contract targets, and break the candidate chain at an
untimestamped controller target. The selector does not access a broker, RF,
Home Assistant or a filesystem path beyond its explicit CLI input.

## Decision

Return only a `KitchenSetpointTransition` candidate. The bounded capture must
be deliberately bracketed around a known programmed edge before it satisfies
the named Kitchen schedule scenario contract.

## Rollback

Revert the selector, script, tests and documentation. No live-system state is
affected.
