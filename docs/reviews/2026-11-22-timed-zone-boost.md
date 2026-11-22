# Adversarial review: timed zone Boost

## Scope

Review the new pure test-world timed per-zone Boost state rule. The change has
no Home Assistant, MQTT, RF, dashboard, persistence, or physical-control path.

## Failure modes

- A user can request an unbounded or cooling Boost. Mitigation: accept only
  a positive delta no greater than 3 C.
- Boost remains attached to a stale pre-schedule target. Mitigation: calculate
  the active target from the current scheduled target and retained delta.
- A prior temporary or permanent override returns unexpectedly. Mitigation:
  each new timed Boost clears both forms of zone override.
- A near-limit setpoint exceeds the model range. Mitigation: cap the resulting
  test-world target at 35 C.
- Naive, expired, or DST-ambiguous timing creates a lingering boost. Mitigation:
  require aware start and expiry times, and require expiry after the start.
- The state helper is treated as a physical controller. Mitigation: retain no
  transport dependency and document the test-world boundary.

## Evidence and tests

Fixed-clock tests cover a 3 C Boost across a schedule edge, expiry back to the
scheduled target, replacement of a permanent override, invalid deltas and
expiry, a DST-offset interval, and the 35 C absolute cap.

## Decision

Model timed zone Boost as a relative scheduled-target delta. This is a clear,
deterministic project decision that matches the public manual’s user-visible
limit without asserting undocumented device or RF semantics.

## Rollback

Revert the zone state fields and method, fixed-clock tests, contract text, and
this review together. No external or live equipment state exists to clean up.
