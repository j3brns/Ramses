# System objectives

## Primary objective

Develop a software-only digital twin of the observed CM67z/HR80 RAMSES-II system before any live RF control is considered.

## Success criteria

- Reproduce the observed controller-to-valve packet contract in `RAMSES/TEST`.
- Model schedules, temporary boosts, expiry at the next schedule change, and restart recovery.
- Give Home Assistant test entities that behave consistently with the simulated RF world.
- Make the Programmer Contract and user guide available both as versioned Markdown and as read-only help content inside Home Assistant.
- Evaluate the Test View with computer-use tests for functional correctness and usability, using Sunnydays as the visual reference.
- Compare each simulated scenario against bounded, ordered observed `/rx` traces.
- Learn an explainable, per-zone optimum-start policy from completed heat-up and cooling intervals; fall back to ordinary schedule timing until it is trained.

## Non-objectives

- Transmitting RF or replacing a live CM67z.
- Altering BDR91/boiler behaviour in the first phase.
- Building a general-purpose RAMSES protocol library.
