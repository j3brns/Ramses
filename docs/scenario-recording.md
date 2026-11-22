# Ordered scenario recording

The packet cache discovers topology and current state. It cannot prove behaviour over time. Record a bounded `/rx` sequence for each behaviour the simulator claims to reproduce.

## Contract

An ordered scenario contains only gateway receive envelopes. Preserve the MQTT
subscriber's broker receipt field (`tst` from `mosquitto_sub -F %J`) when it is
available:

```json
{"tst":"2026-11-21T07:00:00+00:00","topic":"RAMSES/GATEWAY/18:016440/rx","payload":{"msg":" I --- ...","ts":"1970-01-01T00:00:00+00:00"}}
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

The feeder accepts only JSON lines shaped as `{"topic":"RAMSES/GATEWAY/<gateway-id>/rx","payload":{"msg":"...","ts":"..."}}`; it preserves an optional top-level `tst` as `receipt_ts`. Gateway `payload.ts` is retained as `gateway_ts` and is only `unverified` unless independently calibrated. A `1970-01-01...` gateway timestamp is marked `epoch-invalid` and cannot support wall-clock or elapsed-time claims. It can also replace one explicit local NDJSON file with `--output <path>`; it never appends a log. Review the raw packets, commit the scenario, and add a replay test before claiming that behaviour is modelled.

An ordered capture starts as baseline or candidate evidence. Before calling it a
schedule, override, or restart scenario, add and validate its explicit
[qualification manifest](scenario-qualification.md). A candidate hypothesis is
not a qualified behaviour claim.

## Windows-safe file retrieval

Do not redirect `ssh ... cat` output into a PowerShell file: Windows PowerShell
can create UTF-16 text and make valid NDJSON unreadable by the selector. Fetch a
completed, bounded capture as ASCII base64 and write decoded bytes instead:

```powershell
.\scripts\fetch_rx_capture.ps1 `
  -SshHost ha `
  -RemotePath /home/hassio/kitchen_schedule_watch.ndjson `
  -Destination "$env:TEMP\kitchen_schedule_watch.ndjson" `
  -Force
```

The helper is receive-only: it invokes `ssh` and remote `base64`, has no MQTT
credentials, and cannot publish, transmit RF, bind a device, or alter Home
Assistant. It rejects oversized files before it writes them. Its output remains
an untracked local input until the normal scenario review and qualification
steps decide whether a bounded fixture belongs in the repository.

## Dense traffic

If a 500-event window is filled by ordinary TRV traffic before a rare
controller broadcast, use the temporal selector on an already bounded local
capture. It enforces independent byte, event and broker-receipt-time limits,
keeps only a small pre-transition ring, and writes nothing unless it has both
a controller-originated target change and its required following context. See
[Temporal Kitchen capture](repertoire/temporal-kitchen-capture.md). It does
not relax device-direction checks or qualify a candidate as a scheduled change.
