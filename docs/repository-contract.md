# Repository contract

## Local loop

1. Make one scoped change.
2. Run `scripts/check.ps1`.
3. Inspect `git diff` and `git status`.
4. Commit with its test/fixture/documentation update.

For observed data, refresh the sanitised fixture locally, review the derived topology and target-system map, then run the same gate. Hosted CI validates committed evidence; it never connects to the private Home Assistant or MQTT network.

## Review and push

1. Push a branch to GitHub.
2. Open a pull request for behavioural or architectural changes.
3. Require the CI verify job and review checklist to pass.
4. Merge only after the documentation and tests agree with the code.

### Review-record boundary

Adversarial reviews are durable project records. They contain only the scope, failure modes, evidence, decision and rollback for the change. They do not reproduce prompts, conversation, transient writing direction, personal preference, or rejected alternatives. Keep deliberately versioned visual-generation prompts with the asset provenance instead.

## Reset and rollback

- Prefer a new revert commit for shared/pushed history.
- Use `git restore` only for uncommitted local work.
- Do not rewrite published history for experiment data or decisions.
- If a simulator release is wrong, tag the last known-good commit and revert the faulty change.

## Documentation contract

Every material change updates the relevant one of: `system-objectives.md`, `system-architecture.md`, `change-management.md`, `contract.md`, `target-system/`, `rules/`, or an ADR.
