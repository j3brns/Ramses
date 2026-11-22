# Adversarial review: Test View evidence status

## Scope

Add a static, test-only Ramses Test dashboard contract for capture provenance and scenario qualification.

## Failure modes

- A baseline capture is displayed as proof of a schedule, override, restart, thermal, or live-heating behaviour.
- Gateway epoch time is displayed as fresh elapsed-time evidence.
- A status card references a live entity, topic, packet stream, or control path.

## Evidence and tests

Static blueprint tests require all evidence entities to use the `ramses_test` namespace and reject live gateway transport. The contract and guide define receipt time, bounded count and the Baseline/Candidate/Qualified distinction. This change does not deploy a dashboard, connect to MQTT, or alter Home Assistant.

## Decision

Keep evidence status read-only and declarative. A future adapter must provide the named test entities before deployment and must not qualify a scenario without its named evidence and replay checks.

## Rollback

Revert the blueprint, documentation, tests and this review. No dashboard deployment, broker, RF, Home Assistant, or heating state is affected.
