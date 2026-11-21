# Adversarial review: test-only climate path

## Scope

Add a pure temporary-target command seam for a future Home Assistant test climate entity.

## Failure modes

- A climate command selects a live topic, opens a broker connection, or reaches RF/boiler control.
- A malformed, expired or out-of-range target mutates virtual state.
- A temporary command is mistaken for a permanent override or bypasses the existing expiry rule.

## Evidence and tests

The command accepts a validated test descriptor, explicit timezone-aware command/expiry times and a bounded temperature. It returns only the descriptor's validated `RAMSES/TEST/.../tx` topic and envelope. Tests prove the temporary target applies to the virtual controller, expires to schedule, and rejects invalid input without mutation.

## Decision

Keep the first climate path pure and temporary-only. A later adapter may publish the returned command through the already isolated test transport; permanent overrides and live Home Assistant entities require separate contract and integration work.

## Rollback

Revert the pure adapter function, tests and contract note. No broker, RF, Home Assistant or heating state is affected.
