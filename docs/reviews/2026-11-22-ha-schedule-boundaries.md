# Adversarial review: HA schedule boundaries

## Scope

Harden the pure conversion from Home Assistant Schedule helper blocks to the
test-world weekly timetable. This change has no Home Assistant runtime, MQTT,
RF, dashboard, credential, or heating-equipment path.

## Failure modes

- Overlapping same-day blocks can create more than one target for a wall-clock
  interval. Mitigation: parse and sort blocks by start time, then reject every
  overlap before switchpoints are created.
- Input order can hide an overlap. Mitigation: validation operates on sorted
  intervals, not the source sequence.
- The end of Sunday can leak an active target into Monday. Mitigation: retain
  explicit off switchpoints and test the Sunday-to-Monday next change.
- An explicit day-start off marker is necessary for a sparse, repeating weekly
  schedule, but may repeat the already-active off target. Mitigation: the
  weekly scheduler ignores no-op switchpoints when finding the next change.
- The rejection rule is mistaken for validation of the live HA helper.
  Mitigation: it validates only the pure adapter input; no HA API is called.

## Evidence and tests

`tests/test_ha_schedule.py` fixes the clock at the weekly boundary and proves
an overlapping, out-of-order pair is rejected. Existing tests continue to
cover minute alignment, day names, cross-midnight blocks, active data and
timezone-aware `next_event` input.

## Decision

Treat same-day overlap as ambiguous adapter input. Adjacent blocks remain
valid because one target ends exactly where the next begins.

## Rollback

Revert the parser validation, its two deterministic tests, the contract line,
and this review together. No external state exists to restore.
