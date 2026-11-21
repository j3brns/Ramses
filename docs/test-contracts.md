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

## Restart contract

- On startup or MQTT reconnect, recompute the active target from schedule and override state.
- Reissue the active target; do not wait for the next timetable boundary.

## Non-negotiable boundary

No unit, contract, integration, CI, or local-check test may publish to `RAMSES/GATEWAY` or transmit RF.
