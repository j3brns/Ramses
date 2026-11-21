# Adversarial review: HA Schedule helper mapping

## Scope

Map Home Assistant Schedule helper blocks, active additional data and `next_event` into pure, test-only weekly-timer input.

## Failure modes

- Treating the current entity state as the full weekly programme.
- Inventing a target for inactive schedule gaps.
- Applying timezone-naive or sub-minute/DST-ambiguous event data.
- Importing a Home Assistant runtime, broker client or live configuration into the pure model.

## Evidence and tests

Home Assistant documents that schedule blocks carry active additional data and that `next_event` is the next state-change datetime. The mapper accepts the block response separately from the current entity snapshot, requires explicit `target_temperature` data and explicit off/frost target, and validates timezone-bearing events. Tests cover active/off snapshots, a DST-offset event, adjacent blocks, gaps and invalid input.

## Decision

Use HA Get schedule blocks as the full timetable source. Use the active entity attributes only as the current projection. Keep the adapter pure Python and test-world only.

## Rollback

Revert the mapper, tests and contract updates. No Home Assistant, broker, RF or heating state is changed.
