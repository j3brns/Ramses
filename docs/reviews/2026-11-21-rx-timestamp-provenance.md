# Adversarial review: RX timestamp provenance

## Scope

Preserve broker receipt time separately from gateway payload time in passive RX scenario evidence.

## Failure modes

- A gateway without a synchronised clock supplies a 1970 timestamp that is treated as real elapsed time.
- Broker receipt time is silently discarded, leaving a replay unable to explain its temporal basis.
- Adding provenance makes a capture path publish MQTT or alter the live gateway.

## Evidence and tests

The observed baseline contains gateway timestamps in 1970 while Mosquitto `%J` provides a current `tst` receipt timestamp. Deterministic tests prove the normaliser retains both fields and labels the epoch fallback `epoch-invalid`; feeder and evidence tests pass. The change has no MQTT client, broker, RF or Home Assistant dependency.

## Decision

Keep the legacy `ts` as a gateway-time alias for compatibility, add explicit `gateway_ts` and optional `receipt_ts`, and prohibit epoch-invalid gateway time from supporting wall-clock claims. Other gateway times remain `unverified` until independently calibrated.

## Rollback

Revert the provenance fields, contract wording and tests. No live state is affected.
