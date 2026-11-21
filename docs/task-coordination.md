# Task coordination with tk

This repository uses the project-local `tk` binary from Tacks 0.2.4 for concurrent task claims, blockers, and progress notes. It is installed by `scripts/install_tk.ps1` and invoked through `scripts/tk.ps1`.

```powershell
.\scripts\tk.ps1 ready --json
.\scripts\tk.ps1 update <task-id> --claim
.\scripts\tk.ps1 comment <task-id> "What changed; evidence; next action"
.\scripts\tk.ps1 close <task-id> -c "Commit <sha>; CI passed"
```

## Authority split

- `tk` is local operational coordination: claim one ready task before editing, record blockers, and close it only after its acceptance evidence exists.
- `docs/task-breakdown.md`, ADRs, contracts, tests, reviews, and Git commits are the versioned source of truth. A `tk` task cannot approve a release or replace an adversarial review.
- `.tacks/` is deliberately ignored: its SQLite database prevents two concurrent local agents from claiming the same work, but contains no unique project evidence.

## Parallel work rules

1. Work only a claimed task.
2. One task owns one code area; split or sequence work if files would overlap.
3. Add dependencies before parallel work starts; a blocked task is not an invitation to guess.
4. Each agent records its finding, test result, and commit in the task before closing it.
5. Reconcile `tk` status with the Git roadmap at each release review.
