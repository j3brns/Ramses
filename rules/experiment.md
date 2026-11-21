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

## Work and push discipline

1. Break work into the slices in `docs/task-breakdown.md`; each slice has one observable output and a narrow deterministic test.
2. Keep a commit within one slice. A later slice may depend on an earlier one, but must not smuggle its unfinished work into the same change.
3. Changes to model, collector, scenario evidence, transport, CI, or deployment must include `docs/reviews/<date>-<topic>.md` using the adversarial-review headings.
4. The review must state a concrete failure mode, evidence/test, decision, and rollback; a checklist without those facts is not a review.
5. Run `scripts/check.ps1` before push. The installed Git hook checks staged review material; CI checks the pushed commit again.
6. Do not bypass the hook with `--no-verify`. If an emergency exception is necessary, record it in the review and immediately add the missing gate in the follow-up commit.

## Task tracking

`docs/task-breakdown.md` is the repository task authority until a shared task tool is deliberately adopted. A task tool must support versioned, reviewable task state and link each task to its evidence and commit; do not maintain duplicate backlogs.
