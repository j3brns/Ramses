---
title: Ramses Test View computer-use acceptance runbook
status: planned — deployment-gated
owner: tk-bce5.9
canonical_contract: lovelace-ui-contract.md
---

# Ramses Test View computer-use acceptance runbook

Use this runbook only to assess a separately authorised deployment of the version-controlled [`ramses-test-dashboard.yaml`](../target-system/ramses-test-dashboard.yaml) blueprint. This document does not authorise importing the blueprint, opening a browser, changing Home Assistant, obtaining credentials, subscribing to MQTT, or sending RF.

The aim is to establish that the Test View is understandable and honest about its evidence. It does not establish that the live heating system works.

## Deployment boundary

The blueprint remains an undeployed reference until a release owner explicitly authorises a **Ramses Test-only** dashboard deployment. That deployment must be isolated from live entities and transport: every resolved entity has the `ramses_test` namespace and every relevant topic is under `RAMSES/TEST/...`.

Do not use this runbook against Sunnydays, a live dashboard, a live gateway, or a dashboard that contains a `RAMSES/GATEWAY/...` topic. If any of those conditions is observed, stop the session, retain a sanitised screenshot of the defect if permitted, and mark the acceptance run **blocked**. Do not try to correct the configuration from the browser.

## Preconditions

An acceptance owner confirms all of the following before any computer-use session starts:

1. The deployed dashboard was imported from a reviewed revision of the blueprint, and the commit ID is recorded in the acceptance record.
2. The tested URL/title identifies **Ramses Test**, not Sunnydays or a live dashboard.
3. The test fixtures are deterministic and read-only for the session. They cover the scheduled, temporary-override, expired-override, unavailable/stale, and evidence-status states below.
4. The displayed entity/topic inventory has been checked outside the browser: it contains test entities only and no `RAMSES/GATEWAY/...` route.
5. The operator is authorised for the Test View only. Credentials, tokens, MQTT payloads, RF frames, and unsanitised screenshots are not recorded in this repository.
6. The session has a scenario ID, an evidence location outside Git for permitted screenshots, the browser/HA versions, viewport sizes, and a named observer.

If a precondition is absent, record **not run** rather than inferring a result.

## Shared observation rules

- Use observation and navigation only. Do not set a target, edit a schedule, invoke a service, publish a message, or operate a physical controller.
- Take one sanitised screenshot before and after each scenario. Remove account names, addresses, tokens, and unrelated dashboard data.
- Record the rendered card labels and states, not packet contents. The evidence-status surface is not a packet console.
- A failure is a failed acceptance assertion, not a reason to repair the deployment in the session. File a defect with the scenario ID and screenshot reference.

## Desktop acceptance

Use a desktop viewport of at least 1280 × 800 CSS pixels. Capture the full Test View, then execute these scenarios using prepared test fixtures.

| Scenario | Given fixture | Observable assertions | Required record |
| --- | --- | --- | --- |
| UI-01 — scheduled zone | Kitchen has a scheduled target and later next switch | Kitchen shows measured temperature, effective target, source, next change, and the programme card without opening detail. | Screenshot, visible values, pass/fail. |
| UI-02 — temporary override | A test-only temporary override is active | Override target, expiry, and a visible Return to schedule path are shown. The view remains clearly test-only. | Screenshot, expiry text, pass/fail. |
| UI-03 — expired override | The same override fixture is expired | Scheduled target is shown; no duplicate or stale override survives. | Screenshot, target/source, pass/fail. |
| UI-04 — unavailable/stale | One test-only diagnostic entity is unavailable or stale | The state is comprehensible and does not read as a live-heating alarm. | Screenshot, displayed error, pass/fail. |
| UI-05 — Help | Help navigation is available | Help opens, identifies test-only/canonical-guide status, and its back action returns to Ramses Test. | Before/Help/after screenshots, pass/fail. |
| UI-07 — desktop layout | Default Test View state | Sections preserve compact Sunnydays-like hierarchy; labels are legible; no clipped cards, unnecessary gaps, or misleading controls. | Full screenshot, pass/fail. |
| UI-08 — evidence status | Evidence fixture supplied below | Receipt health, event count and all four named scenario states are visible and distinguish Baseline, Candidate, and Qualified. | Evidence-panel screenshot, state table, pass/fail. |

## Mobile acceptance

Repeat UI-01, UI-02, UI-04, UI-05 and UI-08 at 390 × 844 CSS pixels, with browser zoom at 100%.

For UI-06, scroll through the whole Test View and assert:

1. Cards form a readable vertical flow with no horizontal page scroll.
2. Text, temperatures, expiry and evidence states are readable without overlap or clipping.
3. Navigation to Help and back remains possible without accidentally changing a target.
4. A thermostat/control affordance, if rendered, is visibly disabled or labelled as test/mock until the separately contracted test-only climate path is accepted.

Store a top, middle/evidence, and Help screenshot. Record the actual viewport and whether device emulation or a physical test handset was used.

## Evidence-status oracle

Apply these meanings exactly; do not promote a status because it looks healthy:

| State | Meaning | Does not prove |
| --- | --- | --- |
| **Baseline** | Bounded ordered RX traffic exists. | A schedule change, override expiry, restart/reconnect, thermal response, or live behaviour. |
| **Candidate** | A rule selected an event that still needs corroboration. | That the event is a valid named scenario. |
| **Qualified** | The named scenario has passed its declared evidence and replay checks. | Broader controller, boiler, or physical-TRV fidelity. |

For the evidence panel, verify all named rows are present: **Baseline traffic**, **Kitchen schedule change**, **Local override expiry**, and **Restart or reconnect**. Verify that the latest **broker receipt time** is shown separately from **Gateway time valid for elapsed-time claims**. A gateway time at the 1970 epoch is diagnostic and invalid for elapsed-time claims; it must never make a scenario look fresh or qualified by itself.

Negative checks: no card says or implies “live packet stream”; no raw packet payload, live topic, or live entity is displayed; and no baseline-only fixture claims to have proved a timed scenario.

## Evidence record and decision

Store one sanitised acceptance record outside Git containing the commit ID, scenario ID, date/time, viewport, fixture IDs, assertions, screenshot references, observer, result, and any defect IDs. Commit only the durable contract, tests, and an adversarial review—not screenshots, account data, raw packets, or conversation text.

The release owner may mark the UI acceptance **passed** only when every applicable assertion passes and the deployment boundary remains intact. A blocked, not-run, or failed scenario prevents a control-capable Test View release. It does not prevent documentation-only work.

## Rollback and exit

End the session after evidence is collected. Do not mutate the dashboard or test fixtures from the UI. If a boundary defect is found, remove the Test View from release consideration through the normal change process; no live system rollback is needed because this runbook authorises no live action.
