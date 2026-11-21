# Adversarial review: Test View thermostat and schedule cards

## Scope

Add a version-controlled native-Lovelace blueprint for Ramses Test zone
thermostat, schedule, diagnostics and Help cards.

## Failure modes

- A copied card names a live entity or live MQTT root, making a test screen
  appear safe while addressing real heating.
- A dashboard configuration is mistaken for a deployed dashboard before
  computer-use acceptance proves its desktop and mobile behaviour.
- The Help card becomes a hand-maintained second copy of the user guide.

## Evidence and tests

The blueprint contains only `*.ramses_test_*` entities, identifies
`RAMSES/TEST/...`, and contains native Sections, Thermostat, Entities, Tile,
Markdown and Help-subview patterns. Static tests reject non-test entity IDs or
the live gateway root. Home Assistant documents Sections as its grid/grouping
view and Thermostat cards as controls for climate entities; those native
patterns are used rather than custom dashboard code.

## Decision

Keep the blueprint un-deployed until its referenced integration entities
exist, canonical Help export is implemented, and UI-01 through UI-07 are
observed by computer use. Treat the Markdown guide as canonical meanwhile.

## Rollback

Delete the reference blueprint and its static contract tests. No Home
Assistant, broker, RF or heating state is changed by this slice.
