# Ordered scenario recording

The packet cache discovers topology and current state. It cannot prove behaviour over time. Record a bounded `/rx` sequence for each behaviour the simulator claims to reproduce.

## Contract

An ordered scenario contains only gateway receive envelopes:

```json
{"topic":"RAMSES/GATEWAY/18:016440/rx","payload":{"msg":" I --- ...","ts":"2026-11-21T07:00:00+00:00"}}
```

The recorder rejects `/tx` input. `/tx` represents our proposed command; `/rx` is radio evidence of what actually happened.

## Required first scenarios

1. Kitchen scheduled setpoint change.
2. One local TRV override through the next scheduled switch.
3. Controller restart/reconnect while a zone is active.

Capture a short window only. The default cap is 500 events; the recorder writes one replacement fixture at `data/scenarios/<name>.json` and records discarded events.

## Invocation

Pipe a locally authenticated MQTT subscriber through the bounded feeder, then into the recorder. Neither repository script contains broker credentials or opens a connection. The feeder rejects every non-RX topic and prints its retained/discarded count to stderr:

```powershell
<local MQTT subscriber producing NDJSON> |
  py scripts/feed_live_rx.py --max-events 500 |
  py scripts/record_scenario.py kitchen-schedule-change
```

The feeder accepts only JSON lines shaped as `{"topic":"RAMSES/GATEWAY/<gateway-id>/rx","payload":{"msg":"...","ts":"..."}}`. It can also replace one explicit local NDJSON file with `--output <path>`; it never appends a log. Review the raw packets, commit the scenario, and add a replay test before claiming that behaviour is modelled.
