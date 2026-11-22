# Adversarial review: Kitchen selector directionality

## Scope

Review the passive Kitchen `2309` candidate selector after bounded live RX
windows contained TRV reports addressed to `12:216487`, but no eligible
controller-originated target transition.

## Failure modes

- A TRV report addressed to the Kitchen controller is treated as a controller
  command because it shares the same destination and packet code.
- Repeated device reports with different targets are promoted as an apparent
  programme change.
- A negative capture is mistaken for a selector defect and the selector is
  broadened until it finds a result.

## Evidence and tests

The bounded corpus includes `I 2309` frames from Kitchen TRVs to
`12:216487`. The derived packet corpus independently identifies those devices
as TRV sources and `12:216487` as their destination. The selector already
requires the controller as the RAMSES frame source; the added deterministic
test locks that directionality in. No captured controller-originated target
transition was present, so no scenario was retained or promoted.

## Decision

Keep the source-based controller rule. Do not reinterpret a destination as
command authority or infer a schedule change from a TRV report. Continue
bounded passive observation for a real controller-originated transition and
require independent schedule-edge corroboration before qualification.

## Rollback

Revert the directionality test and repertoire clarification together. No live
system, broker, radio, or Home Assistant state was changed.
