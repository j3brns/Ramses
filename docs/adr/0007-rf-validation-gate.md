# ADR 0007: RF validation gate

- Status: proposed; no RF decision
- Date: 2026-11-23

## Context

The software-only test world, passive evidence pipeline, and Test View make it
possible to prepare for an RF validation experiment. They do not provide RF
authority. In particular, a decoded frame, a simulator pass, or a dashboard
control does not prove that a retained TRV will accept a controller command,
that a binding is correct, or that the BDR91/boiler interlock is safe to
operate.

The current live boundary is receive-only. This ADR records the evidence and
operational gate that any future, separately approved RF decision must pass.
It does not authorise RF transmission, a binding change, controller identity
use, gateway configuration, BDR91 actuation, or removal of a physical
controller.

## Decision

Do not make an RF go/no-go decision until all required fields below are filled
with reviewed, versioned evidence and a new ADR explicitly accepts a staged
experiment.

| Gate | Required evidence | Current state |
| --- | --- | --- |
| Ordered scenarios | Qualified schedule-change, override-expiry, and restart-reconnect scenarios with healthy broker receipt chronology and named replay tests | Unfilled |
| Replay | Observed scenarios replay against the intended test-world contract within their declared tolerances | Unfilled |
| Topology | Reviewed zone/controller/TRV map, including the exact retained devices for the proposed one-zone experiment | Partially observed; not approved |
| Test View | UI-01 through UI-08 pass at desktop and mobile widths against `RAMSES/TEST` only | Undeployed / unfilled |
| Command contract | Exact proposed frame, sender identity, receiver, timing, acknowledgement expectation, and cancellation/expiry behaviour are independently evidenced | Unfilled |
| Reversibility | Physical controller to retire, battery-removal/restore procedure, operator, abort threshold, and verified fallback are documented | Unfilled |
| Authority | Explicit owner approval names one zone, time window, and permitted operation | Unfilled |

The required future ADR must select exactly one outcome:

1. **No-go**: retain receive-only operation and record the failed gate.
2. **Limited experiment**: authorise one reversible operation in one named zone
   for a bounded period, with an immediate rollback procedure.
3. **Cutover preparation**: only after successful limited experiments; it is
   still not a general release or boiler-control authorisation.

## Consequences

- `RAMSES/TEST/...` remains the only executable transport in this repository.
- A missing scenario, acknowledgement, UI acceptance, command definition, or
  rollback path is a no-go, not a reason to infer a safe command.
- RF observation continues only as bounded, passive `/rx` evidence.
- The evidence fields make the future decision auditable without copying
  credentials, raw log archives, or operational prompts into Git.

## Rollback

This ADR changes no live state. Revert it if the decision-gate structure proves
wrong. A future limited experiment must have its own physical rollback: stop
test transmission, restore the retired controller's batteries, and confirm the
legacy controller resumes responsibility before leaving the site.
