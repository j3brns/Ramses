# ADR 0002: Sanitised evidence refresh

## Status

Accepted.

## Decision

Refresh derived topology evidence locally from the live packet cache, sanitise it to last-three-digit labels, review and commit it. GitHub Actions validates the checked-in evidence; it does not access the home network.

## Consequences

- The repository remains useful and reproducible without live credentials.
- Raw production captures stay outside Git.
- Data refresh is a deliberate, reviewable change rather than an opaque CI side effect.
