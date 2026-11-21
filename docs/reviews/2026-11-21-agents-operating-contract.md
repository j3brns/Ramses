# Adversarial review: agents operating contract

## Scope

Replace the project agent rules with a concise, intent-led operating contract, then scope distinct local guidance to model code, canonical documentation and evidence data.

## Failure modes

- A rule states an action but not the property it protects, causing agents to follow it mechanically or ignore it when context changes.
- Local rules contradict the actual verification gate, evidence model, task ownership or release practice.
- Parallel agents write the same files, leaving an unreviewable mixture of decisions.
- A direct push is mistaken for approval before CI has verified the shared release.
- A large root instruction file injects unrelated context into every task, or nested files repeat root rules and create conflicting guidance.

## Evidence and tests

Independent read-only reviews compared `AGENTS.md`, `scripts/check.ps1`, evidence/ingest contracts, repository contract and task coordination. They identified the integration-test, snapshot-chronology, observed-RX/test-traffic, review-ownership, direct-push and guidance-scope ambiguities addressed here. The nested files contain only rules that differ for their subtree; the root routes agents to canonical sources. The normal repository gate validates review structure and all tests.

## Decision

Use short rules that state action and reason together. Treat test-world integration as required by the local gate, reserve broker/live integration for explicit approval, distinguish passive observed RX evidence from executable test traffic, permit read-only review across task boundaries, and make direct-push release readiness conditional on both independent review and CI. Keep the root as a routing/safety switchboard; put only genuine subtree differences in nested guidance.

## Rollback

Restore the previous governance documents. No runtime, MQTT, RF, Home Assistant or heating state is affected.
