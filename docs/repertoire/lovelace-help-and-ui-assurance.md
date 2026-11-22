---
type: concept
title: Lovelace help and UI assurance
source:
  - Project decision: Sunnydays is the visual reference
verification: contract-defined; implementation pending
---

# Lovelace help and UI assurance

Home Assistant Test View is the proving ground. Sunnydays supplies the visual language; it does not replace native HA semantics or tests. The canonical layout, entity, Help and computer-use requirements are in the [Ramses Test dashboard contract](../lovelace-ui-contract.md).

## Documentation delivery

The user guide is authored in Markdown under `docs/`. A read-only Help card or sub-dashboard renders or links to the same versioned material. Each control explains its current state, effect, expiry and return-to-schedule action.

## Computer-use acceptance

Before a UI release, exercise Test View at desktop and mobile widths. Verify schedule presentation, temporary/permanent override, expiry, return-to-schedule, disabled/live-test boundaries, readable status and error copy. Retain sanitised screenshots and scenario identifiers as evidence; never use UI automation to change live heating. The dashboard contract assigns these checks IDs UI-01 through UI-08; the [acceptance runbook](../test-view-computer-use-runbook.md) gives the deployment-gated procedure.
