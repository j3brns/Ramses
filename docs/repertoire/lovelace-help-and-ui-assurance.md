---
type: concept
title: Lovelace help and UI assurance
source:
  - Project decision: Sunnydays is the visual reference
verification: planned
---

# Lovelace help and UI assurance

Home Assistant Test View is the proving ground. Sunnydays supplies the visual language; it does not replace native HA semantics or tests.

## Documentation delivery

The user guide is authored in Markdown under `docs/`. A read-only Help card or sub-dashboard renders or links to the same versioned material. Each control explains its current state, effect, expiry and return-to-schedule action.

## Computer-use acceptance

Before a UI release, exercise Test View at desktop and mobile widths. Verify schedule presentation, temporary/permanent override, expiry, return-to-schedule, disabled/live-test boundaries, readable status and error copy. Retain sanitised screenshots and scenario identifiers as evidence; never use UI automation to change live heating.
