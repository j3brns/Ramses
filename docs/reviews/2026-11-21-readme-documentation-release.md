# Adversarial review: README documentation release

## Scope

Expand the top-level README from a compact project stub into the documentation entry point for the Ramses experiment.

The release also corrects the strategic objective: replacement of physical heating-control hardware is the target, while the installed TRVs are retained. Cylinder temperature is an in-scope planned Sunnydays addition, not a prematurely specified retained physical-control component. Present work stays software-only.

## Failure modes

- A polished overview can conceal that the work is experimental, test-only, or incomplete.
- Repeating detailed contracts in the README can create contradictory sources of truth.
- An incomplete run command can suggest that a broker, gateway, Home Assistant, or RF device is needed for local verification.
- A long document map can make discovery worse if it lacks clear question-to-document routing.
- A contributor could mistake the visible topology for permission to control corresponding devices.
- The new replacement objective could be read as permission to start physical work before a cutover decision.

## Evidence and tests

The README links only to repository-local canonical documents and describes each at its existing scope. It names the test namespace and live boundary consistently with `AGENTS.md`, the transport contract and current architecture. Its commands match `pyproject.toml` and `scripts/check.ps1`. The verification gate validates the review structure and all code/fixture tests.

## Decision

Use the README as the brief, navigable front door: purpose, status, safety, topology, architecture, present capability, verification, documentation routing and contribution protocol. Make the strategic target visible, but put its phase boundary and future cutover requirements in ADR 0005. Keep behavioural details in the Programmer Contract and user guide, rather than duplicating them.

## Rollback

Revert this documentation-only commit. No runtime, MQTT, RF, Home Assistant or target-system state is affected.
