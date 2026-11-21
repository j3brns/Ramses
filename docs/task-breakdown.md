# Delivery breakdown

Each task has one observable output, a narrow test, and a review before push. No task may silently broaden into live RF control.

This file is the current task authority. `tk` is not installed in this workspace, so we will not create a parallel task database. Re-evaluate it only if this Markdown backlog ceases to support shared ownership, dependencies, or evidence links.

| Slice | Output | Done when | Status |
|---|---|---|---|
| 0. Governance | CI, secret scan, review gate | push is rejected without required checks/review | in progress |
| 1. Evidence | topology, packet corpus, ordered scenarios | one recorded scenario proves each claimed timed behaviour | scenario capture pending |
| 2. Timer | weekly schedule and boost expiry | fixed-clock tests cover current/next target and expiry | complete |
| 3. Thermal model | per-zone gain/loss learner | trained/untrained and capped-prediction tests pass | complete core |
| 4. Virtual devices | TRV and BDR response model | a `/tx` setpoint leads to expected `/rx` state transitions | next |
| 5. Test transport | isolated MQTT runner | no code path uses `RAMSES/GATEWAY` for simulator output | pending |
| 6. HA adapter | test entities and schedule/telemetry mapping | restart, state persistence, and entity updates work in HA test instance | pending |
| 7. Calibration | recorded schedule/boost scenarios | model replay matches ordered observed evidence within stated tolerances | pending |
| 8. RF decision | separate ADR | explicit go/no-go; never implied by simulator completion | blocked by evidence and user approval |

## Push protocol

1. Keep a change within one slice.
2. Add or update its deterministic test and relevant contract/ADR.
3. Add `docs/reviews/<date>-<topic>.md` when the change touches a reviewable path.
4. Run `scripts/check.ps1`, then commit. The Git hook checks staged review structure.
5. Push only after the local gate passes; CI repeats secret, compilation, tests, integration fixtures, and review-gate checks.
