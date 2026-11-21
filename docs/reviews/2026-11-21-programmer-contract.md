# Adversarial review: Programmer Contract baseline

## Scope

Manual-derived Programmer Contract and the initial OKF-style repertoire.

## Failure modes

- Presenting an HA precedence choice as documented Evohome behaviour.
- Treating Heating Off as a literal zero-demand state rather than frost protection.
- Collapsing materially different Quick Action duration and target rules.
- Claiming restart persistence or optimiser internals from a user guide.
- Allowing a dashboard rendering to become the sole documentation source.

## Evidence and tests

The ATC928G3000 User Guide `32303496-001 C`, pp. 2 and 4–16, documents zones, schedules, zone override/cancellation, Quick Actions, optimisation indicators, and settings. The Programmer Contract now separates its documented behaviour from HA-specific precedence/restart guarantees and adds acceptance cases for schedule-edge expiry, DST, cancellation, Heating Off and schedule edits during an override.

## Decision

Adopt the guide as the behavioural baseline and record the distilled repertoire in versioned Markdown. Implement unresolved precedence, recovery and optimiser details only as explicit HA decisions with deterministic tests.

## Rollback

Remove the baseline contract and retain the existing test RF transport contract; no live RF or Home Assistant configuration has changed.
