# Adversarial review: agents operating contract

## Scope

Replace the project agent rules with a concise, intent-led operating contract and align the repository and task-coordination documents.

## Failure modes

- A rule states an action but not the property it protects, causing agents to follow it mechanically or ignore it when context changes.
- Local rules contradict the actual verification gate, evidence model, task ownership or release practice.
- Parallel agents write the same files, leaving an unreviewable mixture of decisions.
- A direct push is mistaken for approval before CI has verified the shared release.

## Evidence and tests

An independent read-only review compared `AGENTS.md`, `scripts/check.ps1`, evidence/ingest contracts, repository contract and task coordination. It identified the integration-test, snapshot-chronology, review-ownership and direct-push ambiguities addressed here. The normal repository gate validates review structure and all tests.

## Decision

Use short rules that state action and reason together. Treat test-world integration as required by the local gate, reserve broker/live integration for explicit approval, permit read-only review across task boundaries, and make direct-push release readiness conditional on both independent review and CI.

## Rollback

Restore the previous governance documents. No runtime, MQTT, RF, Home Assistant or heating state is affected.
