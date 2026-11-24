# Adversarial review: runtime override recovery

## Scope

Review bounded persistence and recovery of zone-local temporary, permanent and
timed-Boost state in the test-world runtime.

## Failure modes

- A restart silently loses an active override and produces an unexpected scheduled target.
- Expired or malformed stored state becomes an active override.
- A retired zone prevents a surviving zone from recovering.
- A schema change discards existing learned thermal coefficients.
- Persistence turns into an unbounded observation or broker-log archive.

## Evidence and tests

`JsonStateStore` writes atomically and retains only thermal coefficients plus
the seven JSON-safe fields required to reconstruct one zone-local override and
bind it to its controller ID and zone index.
Format 1 thermal-only state remains readable; format 2 adds a separate
override map. Fixed-clock tests cover permanent, active temporary, expired
temporary, timed-Boost, malformed/retired-zone records and the format-1
migration. The standard local gate executes these tests alongside the
transport-isolation tests.

## Decision

Persist bounded zone-local recovery state through `TwinRuntime.checkpoint()`.
The test climate command and optimiser due-start paths route through that
checkpoint before returning their test-only frame.
At `restore(now)`, accept only complete, internally consistent, timezone-aware
records for configured zones; ignore invalid or retired-zone records and clear
any expiry at the supplied clock. This is test-world state only. It does not
add a broker client, Home Assistant runtime, RF transmission or live control.

## Rollback

Revert this change to return to thermal-coefficient-only format-1 persistence.
The stored file is local, contains no credentials or raw observations, and no
Home Assistant, broker, RF or heating state changes as part of rollback.
