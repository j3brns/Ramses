# Adversarial review: Lovelace UI contract

## Scope

Define the test-only Ramses dashboard layout, canonical Help delivery and computer-use acceptance criteria.

## Failure modes

- A test card can address or resemble a live heating entity.
- The dashboard hides target origin, expiry, next change or stale state, leaving people unable to understand heating behaviour.
- Sunnydays visual inspiration becomes copied configuration or overrides native Home Assistant semantics.
- Markdown Help drifts from the canonical user guide.
- A layout that works on desktop is unusable or unsafe on a phone.

## Evidence and tests

The contract uses native Sections, Tile, Thermostat, Markdown and Subview patterns. It defines desktop/mobile computer-use checks UI-01 through UI-07, requires test-only entities/topics, and defines `user-guide.md` as Help source. No dashboard or Home Assistant state is changed by this documentation slice.

## Decision

Start with a separate Ramses Test dashboard and native Home Assistant cards. Use Sunnydays only as a visual reference. Add custom cards only after a native-card limitation is demonstrated. Render Help from canonical Markdown, not a second manually maintained copy.

## Rollback

Revert the contract and linked documentation. No runtime, Home Assistant, MQTT, RF or live-heating state is affected.
