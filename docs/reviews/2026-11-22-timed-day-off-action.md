# Adversarial review: timed Day Off action

## Scope

Review the new pure test-world whole-system Day Off rule. It has no persistence,
Home Assistant, MQTT, RF, dashboard, or physical-control path.

## Failure modes

- Day Off invents a programme for a fixed-target zone. Mitigation: reject the
  action unless every declared zone has a weekly schedule.
- Early Saturday loses the target carried from Friday. Mitigation: evaluate the
  existing repeating weekly schedule at Saturday's local wall time.
- Day Off and Away create ambiguous simultaneous whole-system actions.
  Mitigation: starting either clears the other.
- Day Off erases an underlying zone override. Mitigation: it masks only the
  effective target; cancellation and expiry delegate back to each zone.
- A malformed interval remains active indefinitely. Mitigation: require aware
  timestamps and a duration from one through 99 days.

## Evidence and tests

Fixed-clock tests cover Saturday carry-in and daytime switch points, precedence
over temporary and permanent zone state, explicit cancellation, expiry, mutual
replacement with Away, fixed-target rejection, naive times, and duration bounds.
The manual supplies the user-facing Saturday schedule and 1--99-day behaviour;
it does not establish RF or device internals.

## Decision

Model Day Off as a timed Saturday-programme action over explicitly declared
weekly zones. It is mutually exclusive with Away and remains an in-memory,
test-world-only decision.

## Rollback

Revert the weekday helper, programmer fields and methods, fixed-clock tests,
contract text, and this review together. No external or live equipment state
exists to clean up.
