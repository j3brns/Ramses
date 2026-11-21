# ADR 0002: Sanitised evidence refresh

## Status

Accepted.

## Decision

Refresh evidence locally from the live packet cache, review and commit it. Keep sanitised topology/sample fixtures and a bounded raw RAMSES-II packet corpus. GitHub Actions validates the checked-in evidence; it does not access the home network.

## Consequences

- The repository remains useful and reproducible without live credentials.
- Home Assistant configuration and credentials stay outside Git; a bounded RAMSES-II packet corpus is intentionally versioned for protocol verification.
- Data refresh is a deliberate, reviewable change rather than an opaque CI side effect.
