---
type: knowledge-index
title: Ramses Programmer Contract repertoire
okf_version: "0.3"
status: active
---

# Ramses Programmer Contract repertoire

This is a small, version-controlled Open Knowledge Format (OKF) bundle. It stores the distilled knowledge that agents, maintainers, documentation, and the eventual Home Assistant help panel share. It is deliberately plain Markdown with YAML frontmatter: no Google Cloud account, database, or new runtime is required.

## Concepts

- [Skills and capabilities](skills-and-capabilities.md) — portable maintenance capability contracts.
- [Programmer behaviour](programmer-behaviour.md) — manual-derived user-visible rules and acceptance examples.
- [Lovelace help and UI assurance](lovelace-help-and-ui-assurance.md) — documentation rendering and computer-use evaluation requirements.

- [Baseline RX observations](baseline-rx-observations.md) â€” bounded message-code and topology evidence, not a timing model.
- [Kitchen schedule-capture selector](kitchen-schedule-capture.md) â€” candidate controller-target changes with receipt-time requirements.
- [Scenario qualification](../scenario-qualification.md) â€” prevents candidate RX from becoming named behaviour evidence without corroboration.
- [Passive capture client recovery](passive-capture-runbook.md) â€” credential-free local operation, bounded capture, and broker-restart recovery.

- [Temporal Kitchen capture](temporal-kitchen-capture.md) â€” bounded time-window selection when ordinary RX traffic is too dense.
- [Replay readiness](replay-readiness.md) â€” deterministic evidence coverage, without promoting a baseline to behaviour.

## Source policy

Every concept identifies its source, scope and verification state. Manual sources are paraphrased; copied prose, images, serial numbers, credentials, HA configuration and live packet logs are excluded. The canonical rendered user guide remains ordinary Markdown under `docs/`.

## Maintenance policy

Update this bundle with a contract, UI, model or source change. Link each changed behavioural rule to deterministic tests and, when UI exists, to a computer-use acceptance scenario. The bundle may be consumed by an HA help panel, but the panel is a rendering, never the source of truth.
