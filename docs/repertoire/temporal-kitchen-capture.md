---
type: capture-pattern
scope: passive-rx
status: testable-preparation
---

# Temporal Kitchen capture

The first 500 radio messages are not necessarily a useful observation period:
frequent TRV reports can crowd out a rare programmed target broadcast. The
temporal selector accepts one *already bounded* local RX file and scans a
broker-receipt-time interval for a controller-originated Kitchen `2309` target
change.

It has three independent bounds: input-file bytes, raw-event count and elapsed
broker-receipt time. Before a candidate it keeps only a small ring buffer; it
writes a scenario only after the required post-transition context arrives.
Ordinary traffic and a non-candidate period are discarded rather than promoted
to a repository log.

```powershell
$env:PYTHONPATH = 'src'
py scripts/select_temporal_kitchen_watch.py `
  --input "$env:TEMP\kitchen-rx.ndjson" `
  --output "$env:TEMP\kitchen-candidate.json" `
  --duration-seconds 21600 --max-events 10000 --max-bytes 2097152
```

Source authority remains unchanged: a TRV `2309` addressed to `12:216487` is
a device report, not a controller setpoint. The selector does not infer a
programmed change from it. A returned candidate still needs the normal
qualification manifest and known schedule-edge corroboration.

The helper has no MQTT client, credentials, Home Assistant, RF or filesystem
write outside its explicit local output path. It never appends a capture.

## Starting one bounded listener

Use the launcher only from the development workstation. It starts one passive
subscriber on Home Assistant using the pre-existing, local-only Mosquitto
options file; that file is never read into this repository or printed. The
remote runner is process-group isolated, writes to a temporary file, and only
replaces its bounded capture when it exits. Its duration and byte limit are
independent.

```powershell
.\scripts\start_temporal_rx_capture.ps1 -SshHost ha
```

Check rather than duplicate a running capture:

```powershell
.\scripts\start_temporal_rx_capture.ps1 -SshHost ha -Status
```

`-ReplaceKnownRun` is an explicit recovery action. It will stop only a runner
whose PID file and process command both match this launcher's private runner
path and isolated process group. Any malformed PID file, unrelated process or
non-isolated process group is refused. After it exits, fetch the bounded file
with `fetch_rx_capture.ps1`, then run the temporal selector above. A negative
selection is discarded; it is not a repository fixture.
