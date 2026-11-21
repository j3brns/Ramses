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

Ordered radio evidence uses the separate, credential-free `scripts/feed_live_rx.py` filter. A locally authenticated subscriber supplies NDJSON; the filter accepts passive `RAMSES/GATEWAY/<gateway-id>/rx` envelopes only, caps them, and hands them to `scripts/record_scenario.py`. It does not connect to MQTT, publish, or append a log.

## Source schema

The ingester accepts one JSON cache export containing `data.client_state.packets`, a map of packets with `code`, `src`, `dst`, and decoded `payload` fields. The source is a cache snapshot, not a chronological packet capture, so it carries no asserted observation timestamp.

## Output schema

The refresh creates three tracked fixtures:

- `data/observed/topology.json`: controller-zone membership from `2309` and `3150` records.
- `data/observed/samples.json`: examples of `1F09`, `2309`, `3150`, `30C9`, `1060`, and `3EF0` with a fixed allow-list of decoded values.
- `data/observed/packets.json`: exact RAMSES-II frames and decoded packet fields for independent protocol-contract tests.

`topology.json` and `samples.json` retain only final three device-ID digits. `packets.json` intentionally retains full RAMSES-II device IDs and raw frames. No fixture contains Home Assistant configuration, credentials, IP addresses, topics, or timestamps. Decoded values may be numbers, booleans, strings, or `null` when a device reports an unknown value (for example, battery percentage).

`samples.json` is bounded to 16 examples per packet code (96 maximum across the six supported codes). `packets.json` is bounded to 32 packets per packet code. Excess examples are deterministically discarded and counted in each `retention` object. Each refresh replaces the previous fixtures; no Home Assistant log or historical capture is retained by this repository.

## Acceptance rules

1. The extractor consumes stdin or an explicit local export; it never writes raw input.
2. Fixtures are deterministic for identical cache input.
3. A topology refresh updates the target-system assessment when membership changes.
4. CI checks the fixture schema and virtual-controller representation.
5. The secret scan and `scripts/check.ps1` pass before commit.
6. Purging live Home Assistant, MQTT, or board logs is a separate operational change: identify the exact files and retention policy before deletion.
