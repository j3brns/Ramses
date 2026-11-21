# Adversarial review: live RX feeder

## Scope

Add an offline NDJSON feeder that validates and bounds passive live gateway RX envelopes before scenario recording.

## Failure modes

- The collector opens a broker connection, publishes MQTT, or accepts TX traffic.
- A capture becomes an append-only log or writes raw input without a cap.
- A malformed, foreign-root, or empty event enters scenario evidence.
- A partial file replaces an existing local capture.

## Evidence and tests

The feeder has no networking dependency or credentials. It delegates topic/payload validation to the existing RX normaliser, retains ordered events up to a declared limit, reports discards, and atomically replaces an explicit output file. Tests cover order preservation, cap/discard accounting, TX rejection, foreign-root rejection and invalid payload rejection.

## Decision

Use the feeder only between a locally authenticated subscriber and the ordered scenario recorder. Keep broker connection/authentication outside the repository and keep scenario ownership in `record_scenario.py`.

## Rollback

Revert the feeder, tests and documentation. No broker, RF, Home Assistant or live-heating state is affected.
