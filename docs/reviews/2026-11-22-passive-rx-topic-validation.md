# Adversarial review: passive RX topic validation

## Scope

Review the passive evidence boundary's MQTT-topic acceptance before a bounded
capture is normalised, replayed, or retained.

## Failure modes

- A nested path or wildcard can be accepted because it has the expected prefix
  and suffix, while not naming one concrete gateway receive channel.
- A malformed gateway identifier can be stored as apparent radio evidence.
- A syntactically valid frame on an invalid topic can make a replay look more
  authoritative than its transport provenance permits.

## Evidence and tests

The normaliser now accepts exactly `RAMSES/GATEWAY/<NN:NNNNNN>/rx` for the
configured root. Deterministic tests reject TX, nested, wildcard and malformed
gateway paths. Existing replay and qualification rules still decide chronology
and behavioural claims; this change only narrows the input boundary.

## Decision

Keep one concrete gateway RX topic as an invariant. Reject malformed transport
provenance before data enters a scenario so later validation cannot repair an
ambiguous origin.

## Rollback

Revert the strict topic helper, its tests, and this review together. No broker,
Home Assistant, radio, or fixture state is changed.
