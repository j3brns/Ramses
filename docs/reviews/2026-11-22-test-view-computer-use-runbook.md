# Adversarial review: Test View computer-use acceptance runbook

## Scope

Define a deployment-gated, observation-only acceptance procedure for the undeployed Ramses Test View blueprint.

## Failure modes

- An operator mistakes a written runbook for authority to import or modify a Home Assistant dashboard.
- A desktop-only check misses mobile clipping, accidental target control, or navigation failure.
- Baseline, candidate, or invalid gateway epoch data is presented as qualified timed or live-heating evidence.
- Screenshots or acceptance records place credentials, packet data, personal dashboard data, or live identifiers in Git.

## Evidence and tests

The runbook specifies preconditions, exact CSS viewports, observable UI-01 through UI-08 assertions, named evidence rows, negative checks, sanitised evidence handling, and stop conditions. Static tests assert that the contract links the runbook and that the runbook retains the test-only, deployment and timestamp boundaries. This change does not import a dashboard or interact with Home Assistant, MQTT, RF, credentials, or a browser.

## Decision

Use a written acceptance oracle before any Test View deployment. Treat a browser session as read-only observation, retain private sanitised evidence outside Git, and require an explicit release decision before control-capable UI work.

## Rollback

Revert this runbook, contract link, test and review. No deployed dashboard, Home Assistant state, broker, RF system, or credential is changed.
