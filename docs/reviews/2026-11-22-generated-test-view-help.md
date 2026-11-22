# Adversarial review: generated Test View Help

## Scope

Generate the Ramses Test Help Markdown card from the canonical user guide in
the undeployed Lovelace blueprint. The change has no Home Assistant deployment,
broker, MQTT, RF, or live-heating path.

## Failure modes

- Help drifts from the canonical guide. Mitigation: the renderer replaces one
  delimited region and `--check` fails when the committed output is stale.
- A duplicate or missing insertion region silently damages the blueprint.
  Mitigation: the renderer rejects both conditions and has deterministic tests.
- The Help panel is mistaken for a live control UI. Mitigation: generated copy
  names the test-only boundary and the existing blueprint is constrained to
  test entities and isolated transport.
- A hand-maintained dashboard copy becomes the source of truth. Mitigation:
  `docs/user-guide.md` remains the input; the blueprint is derived output.

## Evidence and tests

The renderer check, derivation test, and marker-rejection test prove output
freshness and fail-closed generation. The existing Lovelace contract tests
continue to reject live entity/topic references.

## Decision

Use one generated Markdown region in the version-controlled, undeployed Test
View blueprint. Generate it locally before review or release; deployment and
computer-use acceptance remain separate gates.

## Rollback

Revert the renderer, generated region, tests, and review together. No deployed
dashboard, Home Assistant configuration, MQTT traffic, RF traffic, or heating
state is affected.
