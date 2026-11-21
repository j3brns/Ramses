# System objectives

## Primary objective

Develop a software-only digital twin of the observed CM67z/HR80 RAMSES-II system before any live RF control is considered.

## Success criteria

- Reproduce the observed controller-to-valve packet contract in `RAMSES/TEST`.
- Model schedules, temporary boosts, expiry at the next schedule change, and restart recovery.
- Give Home Assistant test entities that behave consistently with the simulated RF world.
- Compare each simulated scenario against bounded, ordered observed `/rx` traces.

## Non-objectives

- Transmitting RF or replacing a live CM67z.
- Altering BDR91/boiler behaviour in the first phase.
- Building a general-purpose RAMSES protocol library.
