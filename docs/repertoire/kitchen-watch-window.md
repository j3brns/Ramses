# Kitchen passive watch window

Use this local utility to select one bounded, reviewable context window from
already captured gateway-RX NDJSON. It does not connect to a broker, read
credentials, transmit RF, or alter Home Assistant.

```powershell
$env:PYTHONPATH = 'src'
Get-Content .\capture.ndjson |
  py .\scripts\select_kitchen_watch_window.py --output .\candidate.json
Remove-Item Env:PYTHONPATH
```

The input must be raw Mosquitto JSON envelopes, including the broker receipt
time (`tst`). The utility retains at most 500 input events by default and
replaces the requested output only when it finds a complete candidate window.
It does not append logs. An ordinary capture prints `output_written: false`.

Selection is deliberately narrow: only an `I 2309` target change transmitted
by controller `12:216487` for zone `01` is eligible. The two targets must have
valid, increasing broker receipt timestamps. Gateway timestamps are retained
but are not used for chronology.

A candidate means only “an observed controller setpoint changed.” It is not
called scheduled until an operator corroborates it against a known programmed
schedule edge and records that corroboration with the scenario. A manual
change, reconnect, or controller resynchronisation can look identical here.

Keep candidate files outside version control until they have been reviewed,
sanitised, and explicitly promoted as scenario evidence.
