# Test contracts

## Zone state contract

- A scheduled target is the active target unless an unexpired temporary override exists.
- A temporary override applies only to its own zone.
- At expiry, the zone immediately returns to its scheduled target.
- A weekly schedule uses timezone-aware local wall-clock switch points; a boost-until-next-switch expires at the first later switch point.

## Packet contract

- Setpoint frames use `2309` with a one-byte zone index and centi-degree temperature.
- Test-world publications use the ramses_esp envelope: `{"msg": "<frame>", "ts": "<ISO-8601>"}`.
- Test-world topics must begin `RAMSES/TEST/`.

## Virtual TRV contract

- A virtual TRV accepts a setpoint only for its bound zone.
- Local override becomes the effective target until explicitly cleared by the test-world controller.
- An open window forces virtual heat demand to zero.
- Demand follows the declared clamped proportional response; it is not claimed to be Honeywell's internal algorithm.

## Restart contract

- On startup or MQTT reconnect, recompute the active target from schedule and override state.
- Reissue the active target; do not wait for the next timetable boundary.

## Optimiser contract

- Train heat gain only when a zone has demand and the boiler is available; train heat loss only during passive cooling.
- Require three clean observations of each kind before planning an early start.
- Cap a predicted lead to 90 minutes and decline when a target cannot be reached within that cap.
- The optimiser proposes an earlier use of an existing scheduled target; it does not create a new RF command type.
- Persist only learned per-zone coefficients; do not retain an unbounded observation history in the runtime state store.

## Non-negotiable boundary

No unit, contract, integration, CI, or local-check test may publish to `RAMSES/GATEWAY` or transmit RF.
