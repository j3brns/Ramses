# Adversarial review: passive capture pipeline

## Scope

Review passive capture from a local authenticated subscriber through the
bounded RX feeder, scenario recorder, normalisation, and replay. The review
covers credential boundaries, retention, timestamp provenance,
restart/reconnect evidence, and behavioural-claim boundaries.

## Failure modes

- Credentials could enter scripts, fixtures, or Git rather than remaining in
  the local subscriber or secret store.
- A replacement capture could become an unbounded log or preserve raw input.
- Gateway epoch time, duplicate receipt time, or reordered receipt time could
  be used to support elapsed-time claims.
- A restart/reconnect fixture could be omitted while the simulator nevertheless
  claims recovery behaviour.
- Ordered traffic or packet presence could be presented as proof of scheduler,
  override, optimiser, or physical-device behaviour.

## Evidence and tests

The feeder and recorder open no connection and contain no credential setting.
The feeder accepts RX only, caps retained events, reports discards, and the
recorder replaces one named fixture. Cache extraction replaces bounded,
sanitised fixtures; `.gitignore` excludes local captures, raw data, broker,
and Home Assistant configuration. Existing contracts require named scheduled,
override, and restart/reconnect scenarios before those claims are qualified.

Replay already rejected gateway epoch time for timing. A new deterministic
test proves duplicate broker receipt times now make `timestamps_reliable`
false; timing requires complete, timezone-aware, strictly increasing receipt
times.

## Decision

Keep the passive split: a local subscriber owns authentication; repository
tools consume only stdin or explicit local input. Keep retained scenarios
bounded and replacement-only. Treat traffic as baseline or candidate evidence
until the named scenario and replay contract qualify the specific claim.

## Rollback

Revert the strict receipt-order replay check, its test, contract wording, and
this review together. The conservative result then reverts to the prior
parseability-only timing classification; no collection or live-system change
is involved.
