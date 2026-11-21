---
type: candidate-selector
source: ordered-rx-scenario
status: evidence-preparation
---

# Kitchen schedule-capture selector

The selector finds a candidate controller setpoint transition for Kitchen
controller `12:216487`, zone `01`. It requires two controller-originated
`2309` frames with different centi-degree targets and increasing, valid broker
receipt timestamps. Targets must be within the existing controller contract of
5–35°C.

It does **not** call the transition a scheduled change. The same packet shape
may follow a manual controller action. Promote a candidate to the required
Kitchen schedule scenario only when the bounded capture is intentionally
bracketed around a known programmed transition and the review records that
context.

Use it after recording a bounded scenario:

```powershell
$env:PYTHONPATH = 'src'
py scripts/select_kitchen_transitions.py data/scenarios/kitchen-schedule-change.json
```

An eligible controller target without a receipt timestamp breaks the candidate
chain; the selector never joins timestamps across it. It rejects epoch-invalid
or non-increasing receipt time. Gateway `ts` remains diagnostic metadata only.
