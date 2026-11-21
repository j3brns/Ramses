---
title: Skills inventory and maintenance contract
status: active
reviewed: 2026-11-21
---

# Skills inventory and maintenance contract

This is the project-level contract for capabilities used to build and maintain Ramses. It describes required outcomes rather than assuming every future coding agent has the same tool or plugin installation.

## Required capability contracts

| Capability | When it is required | Minimum contract | Evidence to retain |
| --- | --- | --- | --- |
| Python development and `pytest` | Any domain-model, adapter, parser or state change | Deterministic tests with a fixed clock; no access to a live MQTT broker | Test name and command in the change/PR |
| Repository and release governance | Every committed change | Follow `AGENTS.md`, run `scripts/check.ps1`, use small scoped commits and update release documentation | CI run and commit/PR link |
| Computer Use | Any Home Assistant/Lovelace UI acceptance work | Inspect and operate Test View only; test desktop and mobile widths; never change live heating | Sanitised screenshot or scenario ID, expected and observed result |
| Documentation and Programmer Contract | Any user-visible, behavioural or architectural change | Update Markdown source, the relevant contract and the repertoire concept; preserve provenance and verification state | Source link/page range and linked test IDs |
| Test MQTT isolation | Any MQTT or entity-control work | Use and enforce `RAMSES/TEST/...`; reject the live root in code and tests | Negative test for a non-test topic |

## Context capabilities: use when relevant

- **Home Assistant/Lovelace research:** verify card, dashboard, helper and integration behaviour against current official HA documentation before implementation. Native HA UI is preferred over bespoke front ends. Sunnydays is a visual reference only.
- **Open Knowledge Format (OKF):** use the light-weight Markdown/YAML conventions in `docs/repertoire/`; no Google Cloud service, graph database, or hosted knowledge product is required. The repository itself is the canonical bundle.
- **Protocol research:** use RAMSES RF/ramses_cc documentation and bounded observed evidence. Do not infer live timing or bindings merely from an unordered cache.
- **Adversarial review:** required for model, collector, scenario, transport, CI and deployment changes as defined in `AGENTS.md`; it is recommended for material contract changes.

## Optional capabilities

These can improve work but are not prerequisites: Mermaid for diagrams, static documentation rendering, and a local OKF viewer. They must consume the canonical Markdown rather than become a second source of truth.

## Operating model for future agents

1. Read `AGENTS.md`, the active Programmer Contract and relevant repertoire concepts.
2. Claim one leaf task in `tk`; split independent, non-overlapping leaves before implementation.
3. Select the capability contracts above that apply to the change. If a named tool/skill is unavailable, meet the contract with an equivalent local method and record that choice.
4. Implement, test and document the change together.
5. Add the prescribed adversarial review, run the local gate, then push for CI.

## Dependency rule

The project depends on capability contracts, not on a particular agent framework, cloud account, or private skill. A future agent must not claim a feature needs a skill merely because it was convenient during a previous session. Conversely, a UI change is incomplete without computer-use acceptance evidence, even if it looks correct in source or YAML.
