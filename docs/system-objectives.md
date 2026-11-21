# System objectives

## Primary objective

Replace the existing physical heating-control hardware with a Home Assistant–centred, RAMSES-II-compatible control system, while retaining the installed TRVs and the hot-water-cylinder temperature gauge. The required first phase is a software-only digital twin of the observed CM67z/HR80 RAMSES-II system; no live RF control is considered until that phase has met its evidence and cutover criteria.

## Success criteria

- Reproduce the observed controller-to-valve packet contract in `RAMSES/TEST`.
- Model schedules, temporary boosts, expiry at the next schedule change, and restart recovery.
- Give Home Assistant test entities that behave consistently with the simulated RF world.
- Make the Programmer Contract and user guide available both as versioned Markdown and as read-only help content inside Home Assistant.
- Evaluate the Test View with computer-use tests for functional correctness and usability, using Sunnydays as the visual reference.
- Compare each simulated scenario against bounded, ordered observed `/rx` traces.
- Learn an explainable, per-zone optimum-start policy from completed heat-up and cooling intervals; fall back to ordinary schedule timing until it is trained.
- Produce a staged, reversible replacement plan for the current controller/programmer and associated heating-control hardware, while preserving the retained TRVs and cylinder temperature gauge as explicitly mapped devices.

## Non-objectives

- Transmitting RF or replacing live hardware in the first phase.
- Altering BDR91/boiler behaviour before a separately approved cutover phase.
- Building a general-purpose RAMSES protocol library.
