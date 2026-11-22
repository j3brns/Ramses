# Adversarial review: permanent zone override

## Scope

Review the new pure test-world permanent zone-override precedence rule.

## Failure modes

- A schedule edge silently displaces a user's explicit permanent choice.
- A hidden temporary override reappears after a permanent choice is cancelled.
- Naive or DST-sensitive clocks cause return-to-schedule to expose the wrong target.
- The state helper is mistaken for a persistence, Home Assistant, MQTT, or RF control path.

## Evidence and tests

Fixed-clock tests prove that a permanent target survives a scheduled switch,
that return-to-schedule reveals the current scheduled target, that temporary
and permanent zone choices replace one another, and that cancellation works
across the Europe/London spring DST boundary. The implementation is a small
domain object with no adapter or transport dependency.

## Decision

Keep mutual replacement between temporary and permanent zone choices. It
prevents latent user intent from unexpectedly returning later. Treat this as a
test-world project decision, not evidence of CM67z or physical-TRV behaviour.

## Rollback

Revert the model methods, fixed-clock tests, contract text, and this review as
one change. No external system state exists to clean up.
