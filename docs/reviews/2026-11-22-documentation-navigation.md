# Adversarial review: documentation navigation

## Scope

Repair concrete documentation-navigation gaps and stale UI acceptance/status references for agent onboarding and the household-facing Ramses Test path.

## Failure modes

- A reader follows a stale README status and assumes test transport or the Test View has a different delivery state.
- An agent cannot find the authoritative contract for behaviour, passive evidence, scenario qualification, or UI work.
- A household reader treats the planned Help/control wording as authority to deploy or control heating.
- A canonical contract retains UI-01 through UI-07 while the dashboard evidence contract requires UI-08.

## Evidence and tests

The README, documentation map and user guide now form explicit agent and household routes. Static tests assert their required links, the staged/deployed distinction, and the Help/deployment boundary. Canonical contract and repertoire UI references consistently require UI-01 through UI-08. No runtime, dashboard, Home Assistant, MQTT, RF, hardware, asset, or credential changes occur.

## Decision

Keep README as a concise navigation front door. Keep the user guide as canonical household Help while making control/deployment conditional. Keep behavioural, evidence and UI detail in their linked canonical documents rather than duplicating it in the README.

## Rollback

Revert the navigation, wording, reference, test and review changes. No live or test-world system state is affected.
