# Adversarial review: logical Home Assistant context

## Scope

Review the README addition that describes the household Home Assistant system
at a logical level.

## Failure modes

- Context is mistaken for deployable configuration or a source of credentials.
- A dashboard or interaction surface is described as live heating authority.
- The digital twin is described as a firmware, RF, or binding replacement.
- A future control transfer is presented as completed.

## Evidence and tests

The wording is limited to user-provided component roles. The documentation
navigation test requires the logical-system, Sonoff, mobile-app and digital-twin
statements to remain present. No HA, MQTT, RF, dashboard, or hardware state was
read or changed.

## Decision

Keep the section as concise architectural context. It intentionally omits
addresses, credentials, YAML, entity IDs, and operating configuration.

## Rollback

Revert this README and test change together if the household architecture
changes. No operational system state requires restoration.
