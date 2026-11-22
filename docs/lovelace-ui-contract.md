---
title: Ramses Test dashboard contract
status: planned
scope: test dashboard only
canonical_help: user-guide.md
reference: Sunnydays visual language; native Home Assistant dashboard semantics
---

# Ramses Test dashboard contract

## Purpose

The dashboard lets a person understand a test zone, its effective target, and what changes next. It is the human proof surface for the Programmer Contract. It is not a live-heating control surface.

## Boundary

- Dashboard: a dedicated **Ramses Test** dashboard. Do not modify Sunnydays while proving this flow.
- Entities: test integration entities only. IDs and transport must resolve to `RAMSES/TEST/...`; a live entity or `RAMSES/GATEWAY/...` topic is a release-blocking defect.
- Controls: until the test-only climate path passes its contract and computer-use acceptance, target-changing actions are disabled or explicitly labelled as mock controls.
- Source: `docs/user-guide.md` is canonical. The Help subview is generated from it or links to it; hand-maintained duplicate instructions are forbidden.

## Layout and interaction

Use a native **Sections** view. It is the default responsive Home Assistant layout and supports a compact grid on wide screens and a usable single-column flow on a phone.

| Surface | Native element | Required content | Action |
| --- | --- | --- | --- |
| Zone overview | Tile card | Zone name, current temperature, effective target, freshness/status | Navigate to zone detail; no hidden live control |
| Zone detail | Thermostat card | Current temperature, target, active mode/source | Test-only target action once enabled; otherwise disabled/explained |
| Programme status | Tile/Entities card | Schedule target, next switch, override expiry | Navigate to schedule/help; no silent cancellation |
| System status | Tile/Heading card | Test-world state, optimiser readiness, relay/demand diagnostics | Read-only diagnostics |
| Evidence status | Entities/Markdown card | Broker receipt-time health, bounded event count, baseline/candidate/qualified scenario states | Read-only provenance; no live packet stream |
| Help | Subview + Markdown card | Generated canonical guide, source/version and back navigation | Read-only |

Sunnydays is the visual reference: calm hierarchy, compact room grouping, legible temperatures and restrained status. Ramses Test keeps native card semantics, names and state colours. It does not imitate Sunnydays card code or make a test entity look live.

The version-controlled native-card blueprint is [`../target-system/ramses-test-dashboard.yaml`](../target-system/ramses-test-dashboard.yaml). It is deliberately not loaded by Home Assistant: a separate Test View deployment and computer-use evidence are required before it becomes an HA dashboard. Its current cards name the required test entities, including diagnostic/override entities that the future adapter must expose before deployment.

The deployment-gated [computer-use acceptance runbook](test-view-computer-use-runbook.md) supplies the observable desktop/mobile procedure, screenshot discipline, evidence oracle and negative cases. Reading it does not authorise a deployment or a browser session.

Evidence status is an audit surface, not a packet console. It must show the latest **broker receipt** time separately from the gateway time-validity state, because a gateway epoch timestamp cannot support elapsed-time claims. Its scenario states are constrained to **Baseline**, **Candidate**, and **Qualified**: a baseline is ordered RX traffic, a candidate awaits corroboration, and qualified means the named evidence/replay contract passed. No card may imply that a baseline has proved a schedule, override, restart, thermal, or live-heating behaviour.

## Explainability requirements

Every visible zone must answer, without opening another card:

1. What temperature is measured now?
2. What effective target applies now?
3. Why does it apply: schedule, temporary override, permanent override, whole-system action, or optimisation?
4. What changes next, and when?
5. Is the information stale, unavailable, or test-only?

An override view must show its expiry and a visible **Return to schedule** path. A schedule edit must not imply that it silently cancels an active override.

## Help subview contract

The Help view is a dashboard subview with a defined `back_path` to Ramses Test. It is reachable through a visible Help navigation action. It shows a Markdown rendering of the canonical guide and identifies it as test-only. The render/export step must fail CI when it is stale; until that exporter exists, the Help card remains a planned artefact rather than a manually copied guide.

## Computer-use acceptance

Run these checks only against Ramses Test at desktop and mobile widths. Store sanitised screenshots and scenario IDs with the UI evidence.

| ID | Given | Verify |
| --- | --- | --- |
| UI-01 | A scheduled zone | Current temp, target, source and next switch are visible without opening a detail view. |
| UI-02 | A temporary override | Override target, expiry and Return to schedule are visible; no live entity is addressed. |
| UI-03 | An expired override | The view reports the scheduled target with no duplicate or stale override. |
| UI-04 | An unavailable/stale test entity | The error is clear and does not resemble a live-heating fault. |
| UI-05 | The Help action | The Help subview opens, identifies its source/test boundary, and returns via `back_path`. |
| UI-06 | Mobile width | Cards remain readable, targets are not accidentally changed, and vertical flow needs no horizontal scroll. |
| UI-07 | Desktop width | Sections retain Sunnydays-like grouping and hierarchy without large empty gaps or clipped status. |
| UI-08 | Evidence status | Receipt-time health, event count and all four scenario states are readable; the copy distinguishes baseline, candidate and qualified evidence without claiming a live or timed result. |

## Done

The UI slice is ready only when its entities are proven test-only, the generated Help content matches `user-guide.md`, UI-01 through UI-08 pass by computer use, and the related schedule/override scenarios pass their deterministic model tests.
