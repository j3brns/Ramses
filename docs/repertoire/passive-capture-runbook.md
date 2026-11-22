---
type: operational-runbook
title: Passive capture client recovery
scope: local-read-only-client
---

# Passive capture client recovery

Use this runbook to operate the **local** MQTT subscriber that supplies
passive evidence. The repository scripts do not authenticate or connect to a
broker. Keep the subscriber's host, account, password and any certificate in
an ignored local profile or operating-system secret store; do not put them in
a command history, capture, fixture or Git.

## Prepare the local command

Create a local shell alias or function called `ramses-rx`. It must run
`mosquitto_sub` with private connection arguments held outside this repository,
and these fixed receive-only arguments:

```text
-R -F %J -t RAMSES/GATEWAY/+/rx
```

`-R` excludes retained messages. `%J` emits the JSON envelope whose `tst`
field is the broker receipt timestamp. The topic ends in `/rx`; never change
it to `#`, `/tx`, or a test topic. The feeder is a second guard: it rejects
non-RX input before writing evidence.

## Verify broker health and receive-only subscription

Run a short diagnostic subscription from a local PowerShell session:

```powershell
ramses-rx -d -W 15 2>&1 | Select-String 'CONNACK|SUBACK|Error'
```

Proceed only after the diagnostic shows successful `CONNACK` and `SUBACK` for
the `/rx` topic. A timeout with successful connection/subscription means the
broker is healthy but quiet; it is not evidence that the board or a heating
device has transmitted. Any authentication, connection or subscription error
is a local operational failure: stop and repair the private client setup,
without changing repository scripts or recording a scenario.

## Capture a bounded local window

Choose a lowercase scenario name and a new ignored local output under
`captures/`. `feed_live_rx.py` retains at most 500 events and atomically
**replaces** the named output. It never appends.

```powershell
$name = 'kitchen-schedule-change'
ramses-rx -W 300 |
  py scripts/feed_live_rx.py --max-events 500 --output ".\\captures\\$name.ndjson"
```

Check the final `retained=<n> discarded=<n>` line. `retained=0` is a valid
quiet window, not a usable scenario. Inspect the first local envelope before
continuing: it must have a `topic` ending `/rx`, `receipt_ts`, `gateway_ts`,
and `gateway_time_quality`. A gateway time near 1970 is expected diagnostic
metadata on this installation; it is never timing evidence.

For a candidate that you intend to review, replace the tracked fixture from
the bounded local file:

```powershell
Get-Content ".\\captures\\$name.ndjson" |
  py scripts/record_scenario.py $name --max-events 500
```

The resulting scenario is baseline or candidate evidence only. Add its replay
test and qualification manifest before calling it a schedule, override, or
restart/reconnect behaviour. Receipt timestamps must be complete,
timezone-aware, and strictly increasing before an elapsed-time claim is valid.

## Replace or rotate local output

Use one name per observation window. Reusing a name replaces its ignored local
file atomically; it does not join two time windows. To preserve a window, copy
the reviewed scenario into the tracked `data/scenarios/` route through
`record_scenario.py`; do not retain a local log. Delete unwanted files only
inside the explicit `captures/` directory.

## Stop and recover after a broker restart

Stop the subscriber with `Ctrl+C`. If the feeder did not print its final
retained/discarded count, treat the local output as incomplete and do not
promote it. After a broker restart or connection loss:

1. Run the short `CONNACK`/`SUBACK` check again.
2. Start a fresh bounded capture with a new local name; never append or merge
   the pre-restart output.
3. Review its receipt-time health before promotion.

This proves the **capture client** reconnected. It does not prove the
controller, gateway, Home Assistant, schedule, or heating system recovered.
To make a restart/reconnect behavioural claim, deliberately capture the named
scenario, record independent corroboration, and qualify it under the
[scenario qualification contract](../scenario-qualification.md).
