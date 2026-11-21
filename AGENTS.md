# Ramses operating contract

## Mission

Build a Home Assistant replacement for the heating controls only after the test world proves it. Retain the TRVs, add cylinder-temperature visibility, and keep live authority outside development.

## Non-negotiable boundaries

- Use only `RAMSES/TEST/...` in model code, tests and fixtures so a defect cannot address live equipment.
- Never transmit RF, alter bindings, reflash or configure the live gateway, change live heating, or store credentials so the experiment stays reversible and shareable.
- Keep captures bounded and sanitised so evidence remains reviewable and Git never becomes a log archive.

## Evidence and decisions

- Treat cache snapshots as topology/state evidence. Claim timed behaviour only from bounded ordered `/rx` scenarios and replay tests, because snapshots have no chronology.
- Keep the target map current with packet evidence. Update the relevant contract, architecture, objective, rule or ADR when scope, authority or behaviour changes, so documentation and implementation do not diverge.
- Use public manuals as behavioural sources, with source/page range. Separate observed facts and HA design choices, so fidelity is not overclaimed.
- Keep reviews to scope, failure modes, evidence, decision and rollback. Exclude prompts, dialogue and transient preferences so reviews remain durable engineering records. Store deliberate asset prompts with asset provenance instead.
- Keep `docs/repertoire/` as the canonical human/agent knowledge bundle and render UI help from it, so a dashboard card never becomes the sole documentation.

## Parallel delivery

- Claim a ready `tk` task and partition overlapping writes before editing, so parallel agents do not overwrite evidence or decisions. Read-only reviewers may inspect shared files without owning them.
- Delegate independent research, review and test leaves by default. One integrator owns the final contract, tests, review and merge, so parallel findings converge into one accountable change.
- Record dependencies before parallel work starts and log evidence before closing a task, so the queue explains both progress and blockers.

## Verification and release

- Add deterministic fixed-clock tests for behavioural, state, encoding and transport changes, so failures reproduce.
- Run `scripts/check.ps1`, inspect the diff/status, then make one scoped commit, so every change is reproducible and reversible. Test-world integration is required by this gate; broker or live integration is forbidden unless separately approved.
- Use an adversarial review for behavioural, boundary, data, scenario, transport, CI or deployment changes, and for documentation that changes contract or safety meaning, so release decisions can be challenged later.
- Install and enforce the repository hooks; do not bypass the review gate, so local work cannot silently omit required evidence.
- Use a pull request for multi-author or multi-commit behavioural/architectural work when the branch workflow is available. For an owner-authorised single-integrator direct push, require the local gate and independent review first, then require CI to pass before calling the shared release ready.
