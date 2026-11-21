# Delivery breakdown

Each task has one observable output, a narrow test, and a review before push. No task may silently broaden into live RF control.

This file is the versioned delivery roadmap. The project-local `tk` queue manages live claims and dependencies for concurrent agents; see `task-coordination.md`. It is intentionally not a competing release record.

| Slice | Output | Done when | Status |
|---|---|---|---|
| 0. Governance | CI, secret scan, review gate | push is rejected without required checks/review | complete |
| 1. Evidence | topology, packet corpus, ordered scenarios | bounded live feeder plus schedule, override, and restart/reconnect scenarios | in progress |
| 2. Timer | weekly schedule and boost expiry | fixed-clock tests cover current/next target and expiry | complete |
| 3. Thermal model | per-zone gain/loss learner | trained/untrained and capped-prediction tests pass; aligned telemetry is available | complete core; evidence pending |
| 4. Virtual devices | TRV and BDR response model | TRV core plus resolved local-override semantics and BDR demand response | TRV semantics complete; BDR response pending |
| 5. Test transport | isolated MQTT runner | consume test TX, publish simulated RX, and reject non-`RAMSES/TEST` roots at runtime | complete |
| 6. HA adapter | packaging, schedule mapping, diagnostics, climate and cards | pure library import is proven; all entities and commands are test-only | import proof complete; remainder staged |
| 7. Calibration | decoder and replay harness | required scenario coverage and explicit replay tolerances pass | pending |
| 8. RF decision | separate ADR | all test-world slices and calibration complete; explicit go/no-go | blocked |

## Push protocol

1. Keep a change within one slice.
2. Add or update its deterministic test and relevant contract/ADR.
3. Add `docs/reviews/<date>-<topic>.md` when the change touches a reviewable path.
4. Run `scripts/check.ps1`, then commit. The Git hook checks staged review structure.
5. Push only after the local gate passes; CI repeats secret, compilation, tests, integration fixtures, and review-gate checks.

## Review corrections

- Do not start calibration from packet snapshots: it requires aligned telemetry and an ordered decoder/replay harness.
- The scenario recorder needs a credential-free live RX-to-NDJSON feeder before anyone can capture its required scenarios.
- The virtual local override ends on the next accepted bound-zone controller setpoint. This is a simulator rule; ordered evidence remains required before claiming physical-TRV fidelity.
- The simulator transport must refuse live roots at runtime, not merely by convention or tests.
- HA packaging/import proof, schedule mapping, diagnostics, climate control, and Lovelace cards are separate slices. Climate writes and cards remain test-only until the isolated transport is proven.
