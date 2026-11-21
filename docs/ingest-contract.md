# Observation ingestion contract

## Purpose

Turn a passive Home Assistant `ramses_cc` packet-cache snapshot into versioned, sanitised evidence for the digital twin. This boundary must not publish MQTT, transmit RF, bind devices, or alter Home Assistant configuration.

## Transport

The supported transport is a local, read-only SSH command:

```powershell
ssh ha "sudo -n cat /homeassistant/.storage/ramses_cc" |
  py scripts/refresh_observations.py --input -
```

An HA API adapter may be added later only if it produces the same source schema. Its token belongs in local secret storage and must never be committed or logged.

## Source schema

The ingester accepts one JSON cache export containing `data.client_state.packets`, a map of packets with `code`, `src`, `dst`, and decoded `payload` fields. The source is a cache snapshot, not a chronological packet capture, so it carries no asserted observation timestamp.

## Output schema

The refresh creates two tracked derived fixtures:

- `data/observed/topology.json`: controller-zone membership from `2309` and `3150` records.
- `data/observed/samples.json`: examples of `1F09`, `2309`, `3150`, `30C9`, `1060`, and `3EF0` with a fixed allow-list of decoded values.

Both use format `1`, retain only the final three device-ID digits, omit raw frames and cache keys, and contain no credentials, IP addresses, topics, or timestamps. Decoded values may be numbers, booleans, strings, or `null` when a device reports an unknown value (for example, battery percentage).

## Acceptance rules

1. The extractor consumes stdin or an explicit local export; it never writes raw input.
2. Fixtures are deterministic for identical cache input.
3. A topology refresh updates the target-system assessment when membership changes.
4. CI checks the fixture schema and virtual-controller representation.
5. The secret scan and `scripts/check.ps1` pass before commit.
