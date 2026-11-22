# Documentation map

## Start here

- **Agent onboarding:** read [`../AGENTS.md`](../AGENTS.md), then use the route map below. Start behavioural work with `programmer-contract.md`, evidence work with `ingest-contract.md` and `scenario-recording.md`, and UI work with `lovelace-ui-contract.md`. The canonical source always outranks a generated/dashboard rendering.
- **Household/Test View path:** read `user-guide.md` for the planned everyday experience. It is the canonical Help source. The Test View blueprint is not deployed; `lovelace-ui-contract.md` and `test-view-computer-use-runbook.md` define its test-only deployment and acceptance boundary.

## Canonical routes

- `programmer-contract.md` — user-visible programmer behaviour and implementation status.
- `user-guide.md` — canonical household-facing Ramses Test Help source; dashboard Help is a rendering, not a competing guide.
- `test-view-computer-use-runbook.md` — deployment-gated desktop/mobile UI observation procedure, evidence semantics and screenshot discipline.
- `ingest-contract.md` and `scenario-recording.md` — bounded passive capture; `scenario-qualification.md` — when a candidate can become a named behaviour claim.

- `lovelace-ui-contract.md` - test-only dashboard structure, Help subview and computer-use acceptance.

- `../target-system/ramses-test-dashboard.yaml` - native Sections/Test View blueprint; not an active Home Assistant dashboard.

- `hardware-foundation.md` — Elecram/ramses_esp gateway hardware, upstream attribution and the physical boundary.

- `contract.md` — MQTT/RF gateway boundary for the test world.
- `system-objectives.md` — goals and non-goals.
- `system-architecture.md` — component and transport design.
- `change-management.md` — evidence and review rules.
- `repository-contract.md` — local loop, review, push and rollback agreement.
- `adr/` — irreversible or consequential architectural decisions.
- `../target-system/` — observed live topology and replacement target.
- `../rules/` — experiment protocol and acceptance criteria.
- `../data/` — capture manifests and derived, sanitised data.
