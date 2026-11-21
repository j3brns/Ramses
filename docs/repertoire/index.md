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

## Source policy

Every concept identifies its source, scope and verification state. Manual sources are paraphrased; copied prose, images, serial numbers, credentials, HA configuration and live packet logs are excluded. The canonical rendered user guide remains ordinary Markdown under `docs/`.

## Maintenance policy

Update this bundle with a contract, UI, model or source change. Link each changed behavioural rule to deterministic tests and, when UI exists, to a computer-use acceptance scenario. The bundle may be consumed by an HA help panel, but the panel is a rendering, never the source of truth.
