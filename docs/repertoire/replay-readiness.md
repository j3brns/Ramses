---
type: evidence-readiness
source: qualification-manifest
status: active
---

# Replay readiness

The replay harness is structurally usable with the bounded baseline fixture,
but it is **not behaviour-ready** until the three required observations are
qualified:

1. `schedule-change`
2. `override-expiry`
3. `restart-reconnect`

Run the deterministic report locally:

```powershell
$env:PYTHONPATH = 'src'
py scripts/report_replay_readiness.py
```

It scans `data/scenarios/` for ordered scenarios and qualification manifests.
A scenario qualifies only through `validate_qualification`; baseline and
candidate scenarios remain visible as rejected inputs, not evidence of a
behaviour. Use `--require-ready` only in a release gate that actually requires
all three behaviours. It exits non-zero while any are absent.

The report is a readiness view, not a collector. It does not contact Home
Assistant or MQTT, publish an RF frame, retain raw logs, or infer a behaviour
from a packet code.
