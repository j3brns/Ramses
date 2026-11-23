# Adversarial review: temporal capture launcher

## Scope

Review the workstation launcher for one bounded, passive Home Assistant MQTT
subscriber used to acquire a Kitchen schedule candidate.

## Failure modes

- A second subscriber silently duplicates capture traffic or creates competing
  retention files.
- A stale or hostile PID file kills an unrelated Home Assistant process.
- A byte limit is mistaken for a duration limit, or either bound is absent.
- A capture is appended, half-written, or copied into Git with broker access
  credentials.

## Evidence and tests

The runner uses `timeout` and line-safe `awk` byte accounting independently.
It subscribes only to `RAMSES/GATEWAY/+/rx` with `mosquitto_sub`; the local
options file remains on Home Assistant. It starts via `setsid`, records its
PID, atomically replaces output after exit, and refuses unexpected PID/process
relationships. Static tests assert the receive-only topic/client, both bounds,
known-runner guard, and absence of embedded passwords.

## Decision

Use one named, isolated runner. Refuse ambiguity by default. Allow explicit
replacement only after the PID and process group identify the exact runner.

## Rollback

Remove the launcher, its static tests, repertoire instructions and this review.
No Home Assistant, broker, RF, or credential state is modified by rollback.
