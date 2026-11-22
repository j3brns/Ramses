# Adversarial review: passive capture runbook

## Scope

Document the local passive MQTT client lifecycle: health verification,
receive-only subscription, bounded replacement capture, stopping, and broker
restart recovery. The runbook does not configure the broker, client account,
gateway, Home Assistant, or radio.

## Failure modes

- A credential, host, or certificate reference is copied into repository
  documentation or command history.
- A broad, transmit, retained, or test topic is subscribed accidentally.
- A quiet broker is mistaken for confirmed device traffic.
- A partial or post-restart capture is appended to an earlier time window.
- Client reconnection is misrepresented as heating-system recovery.

## Evidence and tests

The runbook uses the existing RX-only feeder and recorder contracts. The
feeder has deterministic tests for RX filtering, ordered retention, and the
event cap; replay tests require complete, timezone-aware, strictly increasing
broker receipt timestamps for timing reliability. Ignored local captures and
secret scanning protect repository retention and credential boundaries.

## Decision

Keep broker authentication entirely in an ignored local subscriber profile or
secret store. Require visible `CONNACK` and `SUBACK` before capture, replace
each local window rather than append, and restart with a new capture after
connection loss. Keep client recovery and heating-behaviour qualification
separate.

## Rollback

Remove the runbook, its index entry, and this review. No executable capture
path or live configuration changes with this documentation.
