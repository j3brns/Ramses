# Test contracts

The source of user-visible scheduler semantics is the [Programmer Contract](programmer-contract.md). These are executable implementation contracts; where evidence is incomplete, they must be labelled rather than silently treated as product behaviour.

## Zone state contract

- A scheduled target is the active target unless an unexpired temporary override exists.
- A temporary override applies only to its own zone.
- At expiry, the zone immediately returns to its scheduled target.
- A weekly schedule uses timezone-aware local wall-clock switch points; a boost-until-next-switch expires at the first later switch point.
- A permanent zone override replaces a temporary zone override and survives a schedule edge; a later temporary override replaces it. **Return to schedule** clears either and immediately exposes the current schedule target.
- This permanent-override rule is pure test-world state only: it has no UI, persistence or live-control seam. Whole-house quick actions remain unimplemented.

## Home Assistant Schedule helper contract

- The adapter consumes HA Get schedule blocks as the weekly source and requires `data.target_temperature` for every active block.
- The current helper state plus active additional data provides the active target; `next_event` provides the next switchpoint and must be timezone-aware.
- A helper that is `off` has no active target. The weekly adapter requires an explicit frost/off target for gaps, so it never silently invents a temperature.
- The adapter rejects malformed, non-minute-aligned, cross-midnight, timezone-naive or out-of-range input rather than issuing an ambiguous target.

## Packet contract

- Setpoint frames use `2309` with a one-byte zone index and centi-degree temperature.
- Test-world publications use the ramses_esp envelope: `{"msg": "<frame>", "ts": "<ISO-8601-with-timezone>"}`.
- Test-world topics must begin `RAMSES/TEST/`.

## Test climate command contract

- A temporary target requires an explicit, timezone-aware expiry later than its command time.
- The climate seam validates the bounded target, changes only virtual-controller state, and returns a test `tx` envelope; it does not publish, call Home Assistant, or create a permanent override.
- Expiry returns through the existing schedule/override contract.

## Virtual TRV contract

- A virtual TRV accepts a setpoint only for its bound zone.
- Local override becomes the effective target until the next accepted bound-zone controller setpoint; that setpoint explicitly returns the virtual TRV to coordinated control.
- An open window forces virtual heat demand to zero.
- Demand follows the declared clamped proportional response; it is not claimed to be Honeywell's internal algorithm.
- This local-override rule is a simulator decision, not a claimed physical-TRV behaviour. Calibration and RF decisions still require ordered observed scenarios before asserting physical fidelity.

## Virtual BDR contract

- The virtual BDR aggregates current virtual-TRV demand using the maximum demand; it exposes that value and its contributing virtual devices.
- It reports relay on when demand is at or above its declared threshold, and off when no demand reaches that threshold.
- This is an explicit test-world coordination model. It does not claim the BDR91's physical relay timing, modulation, or boiler-control behaviour.

## Restart contract

- On startup or MQTT reconnect, recompute the active target from schedule and override state.
- Reissue the active target; do not wait for the next timetable boundary.
- `TwinRuntime.recovery_frames(now)` is the pure test-world seam: it requires an
  explicit timezone-aware time and returns one current setpoint frame per
  configured zone in stable zone-ID order. A later test-only adapter owns
  publication and durable schedule/override reconstruction.

## Optimiser contract

- Train heat gain only when a zone has demand and the boiler is available; train heat loss only during passive cooling.
- Require three clean observations of each kind before planning an early start.
- Cap a predicted lead to 90 minutes and decline when a target cannot be reached within that cap.
- The optimiser proposes an earlier use of an existing scheduled target; it does not create a new RF command type.
- Persist only learned per-zone coefficients; do not retain an unbounded observation history in the runtime state store.
- Training evidence aligns reference temperature, outdoor temperature, valve demand, boiler availability, and timestamps; isolated packet snapshots are insufficient.
- An optimiser candidate sample requires complete bounded inputs and strictly increasing timezone-aware broker receipt timestamps. Gateway time is diagnostic only: a 1970 epoch value is labelled but cannot supply chronology. Candidate validation constructs no intervals, trains no coefficient, and makes no thermal-fidelity claim.

## Scenario and replay contract

- Required evidence covers a scheduled rise, a local override through its expiry, and restart/reconnect while a zone is active.
- A replay harness decodes ordered frames before asserting state transitions; it must not infer temporal behaviour from an unordered cache.
- Each replay test states its permitted timing tolerance. Packet order and named state transitions are exact unless the fixture declares a retry/duplicate allowance.
- Structural replay preserves RX list order and validates the RAMSES frame envelope before semantic interpretation. It may count packet codes, but cannot infer physical state changes without a named scenario contract.
- Only strictly increasing, timezone-aware broker receipt timestamps can support elapsed-time assertions. Gateway timestamps marked `epoch-invalid` or `unverified` remain diagnostic metadata.

## Dashboard contract

- The Ramses Test dashboard uses only test entities and `RAMSES/TEST/...` transport; a live entity/topic is a release-blocking defect.
- Its canonical requirements and computer-use acceptance IDs are in [the Lovelace UI contract](lovelace-ui-contract.md).
- UI-01 through UI-08 must pass at desktop and mobile widths before a control-capable Test View release; the deployment-gated procedure is in `test-view-computer-use-runbook.md`.
- The Help subview renders or links to `user-guide.md`; the Markdown source remains canonical.

## Non-negotiable boundary

No unit, contract, integration, CI, or local-check test may publish to `RAMSES/GATEWAY` or transmit RF.
The test transport must reject any non-`RAMSES/TEST` topic at runtime.
