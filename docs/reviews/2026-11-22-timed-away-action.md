# Adversarial review: timed Away action

## Scope

Review the new pure test-world whole-system Away rule. It has no persistence,
Home Assistant, MQTT, RF, dashboard, or physical-control path.

## Failure modes

- Away erases zone-local override state. Mitigation: it masks targets only;
  cancellation and expiry delegate back to the existing zone controller.
- An invalid duration leaves an action permanently active. Mitigation: require
  aware timestamps and a duration from one through 99 days.
- A zone outside the declared group silently receives an action. Mitigation:
  reject an unknown zone name.
- A model decision becomes a claim about physical equipment. Mitigation: keep
  the state in an in-memory programmer boundary and label it test-world only.

## Evidence and tests

Fixed-clock tests cover precedence over temporary and permanent zone targets,
explicit cancellation, expiry, frame construction, unknown zones, naive time,
and duration bounds. The manual supplies the user-facing 15 C and 1--99-day
behaviour; it does not establish RF or device internals.

## Decision

Model Away as a timed 15 C action over explicitly declared zones. It has higher
precedence than zone-local state while active, without mutating that state.

## Rollback

Revert the `Programmer` module, its tests, contract text, and this review
together. No external or live equipment state exists to clean up.
