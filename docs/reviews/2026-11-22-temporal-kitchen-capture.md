# Adversarial review: temporal Kitchen capture

## Scope

Review a passive, finite observation-period selector intended to find a rare
controller-originated Kitchen target change without retaining an RF log.

## Failure modes

- A high-rate TRV stream consumes an event cap before a scheduled broadcast.
- A duration-only capture grows without a byte or event limit.
- A TRV `2309` addressed to the thermostat is mistaken for controller authority.
- A candidate is written without enough following context to replay it.

## Evidence and tests

The selector requires valid broker receipt time, a positive finite duration and
an event cap. Its command wrapper rejects an oversized source file. It holds
only a small pre-transition ring and returns no scenario until post-context is
complete. Tests cover a candidate, TRV-direction rejection, caps and invalid
duration.

## Decision

Use explicit byte, event and receipt-time limits. Keep controller-source rules
unchanged. Non-candidate traffic is not output and cannot become a repository
log.

## Rollback

Revert the temporal selector, its command wrapper, tests and documentation as
one change. No live broker, Home Assistant, radio or credential state changes.
