# Scenario qualification contract

An ordered receive scenario is not automatically evidence of a named heating
behaviour. Attach one local, version-controlled qualification manifest before
documentation, a dashboard, or model code calls it a schedule, override, or
restart scenario.

## Manifest

```json
{
  "format": 1,
  "kind": "scenario-qualification",
  "scenario": "kitchen-schedule-change",
  "status": "qualified",
  "receipt_time_health": "healthy",
  "behaviour": "schedule-change",
  "corroboration": [{"source": "programmed-schedule", "reference": "Kitchen weekday 07:00"}],
  "replay_test": "tests/test_programmer_contract.py::test_kitchen_schedule_change"
}
```

The manifest is local metadata beside a reviewed scenario; it contains no
credentials, broker connection details, or raw capture. Validate it with
`ramses_twin.qualification.validate_qualification`. Code that needs to assert
a behaviour must use `require_qualified` for that exact behaviour.

## States

| State | Permitted information | Prohibited claim |
| --- | --- | --- |
| Baseline | Ordered RX traffic and receipt-time health | Any schedule, override, or restart behaviour |
| Candidate | A bounded hypothesis such as `schedule-change` | That the hypothesis happened for the stated reason |
| Qualified | Exact behaviour, healthy broker receipt chronology, corroboration, and a named replay test | Any behaviour other than the one named in the manifest |

Supported qualified behaviours are `schedule-change`, `override-expiry`, and
`restart-reconnect`. A qualified manifest must have strictly increasing,
timezone-aware broker receipt timestamps from a current year. Gateway time,
including a 1970 epoch, is not a substitute.

Corroboration identifies independent evidence, for example a known programmed
switch point or a documented restart action. It is deliberately required even
when packet shapes look convincing: the same packets can follow a manual
change or resynchronisation.
