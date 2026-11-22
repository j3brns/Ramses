# Adversarial review: timed Eco action

## Scope

Review the new pure test-world whole-system Eco rule. It has no persistence,
Home Assistant, MQTT, RF, dashboard, or physical-control path.

## Failure modes

- Eco erases zone-local state. Mitigation: it masks each zone's effective
  target only; cancellation and expiry delegate back to the zone controller.
- A low target falls outside the zone model's legal range. Mitigation: clamp
  the 3 C reduction at the existing 5 C model floor.
- More than one whole-system action produces unclear precedence. Mitigation:
  starting Eco clears Away and Day Off; starting either of those clears Eco.
- A model decision becomes a claim about physical equipment. Mitigation: the
  implementation is explicitly in-memory and test-world only.

## Evidence and tests

The public Evohome guide, p. 12, describes reducing all room temperatures by
3 C and a one--24-hour timed action. Fixed-clock tests cover masking and
restoration of zone state, schedule-edge behaviour, clamping, expiry,
whole-system replacement, naive time, and duration bounds. It does not
establish RF or device internals.

## Decision

Model Eco as a timed 3 C reduction of every declared zone's current
lower-precedence target, clamped to 5 C. It remains purely in-memory.

## Rollback

Revert the `Programmer` changes, their tests, contract text, and this review
together. No external or live equipment state exists to clean up.
