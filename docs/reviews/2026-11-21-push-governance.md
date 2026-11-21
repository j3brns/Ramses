# Adversarial review

## Scope

Adds a commit-time and CI-time requirement for a structured adversarial review whenever model, collector, scenario, transport, CI, or deployment files change.

## Failure modes

- A review note can be superficial: the automated gate proves structure, not judgement.
- A contributor can bypass a local Git hook with `--no-verify`; CI catches only the pushed commit's diff.
- The gate could become friction for trivial code changes if the scope is made too broad.

## Evidence and tests

- Unit tests exercise the reviewability decision and required-heading validation.
- The hook validates staged content before a normal commit.
- GitHub Actions runs the same check against the pushed commit.

## Decision

Accept. Require a concise review note for consequential implementation changes, keeping documentation-only edits outside the gate unless they alter a test or deployment contract.

## Rollback

Remove the hook, CI invocation, and review-gate script in one revert commit. Existing review records remain useful evidence.
