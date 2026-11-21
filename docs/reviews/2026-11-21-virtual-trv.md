# Adversarial review

## Scope

Adds the test-world virtual TRV state machine: target receipt, local override, temperature, window state, battery flag, and declared proportional heat demand.

## Failure modes

- A proportional demand law could be mistaken for the real Honeywell valve algorithm.
- A foreign-zone setpoint could alter a valve if binding is not enforced.
- Early frame encoding could falsely claim protocol fidelity without a dedicated transport contract.

## Evidence and tests

- Unit tests prove bound-zone acceptance, foreign-zone rejection, window closure, local override, demand limits, and timezone-aware reporting.
- The current raw corpus shows TRV temperature, demand, setpoint, and window state messages but does not reveal the internal PID algorithm.

## Decision

Accept an explicit, configurable proportional response for simulation only. Keep demand-frame encoding out of the state model until the transport task verifies it against observed frames.

## Rollback

Remove `trv.py`, its tests, ADR, and contract section in one revert. The timer and thermal models do not depend on it yet.
