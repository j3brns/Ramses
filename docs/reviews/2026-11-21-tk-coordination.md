# Adversarial review

## Scope

Adopts a project-local, checksum-verified `tk` task CLI and defines its boundary with Git-tracked delivery evidence.

## Failure modes

- Two agents can still conflict if tasks are split by intent but edit the same file.
- The local SQLite queue can be lost or become stale because it is not committed.
- A downloaded executable could be wrong or tampered with without version and checksum verification.

## Evidence and tests

- Installed `tk` 0.2.4 from the released Windows archive after SHA-256 verification.
- Initial epics, tasks, and dependency edges exist in the local queue.
- Installation and use instructions pin the version and checksum.

## Decision

Accept for local coordination only. Require one claimed task per agent and retain Git commits, tests, ADRs, and adversarial reviews as the release record.

## Rollback

Remove the wrapper and installer, delete the ignored `.tacks/` and `.tools/` directories locally, and continue with the Markdown roadmap alone.
