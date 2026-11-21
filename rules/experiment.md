# Experiment protocol

## Phases

1. Collect passive normal schedule and manual-boost traces.
2. Implement equivalent state transitions in the software simulator.
3. Test virtual packets and Home Assistant entities on `RAMSES/TEST`.
4. Compare virtual and observed traces.
5. Write a separate RF-test ADR before any live transmission.

## Acceptance criteria

- Scheduled setpoint frames encode the correct controller ID, zone index, and temperature.
- A boost applies only to its zone and returns to the next scheduled target.
- Restart/reconnect recomputes and republishes the current target.
- No simulator topic uses `RAMSES/GATEWAY`.
- All tests pass with a fixed clock.
