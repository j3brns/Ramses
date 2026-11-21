# ADR 0005: replacement target and retained devices

- Status: accepted
- Date: 2026-11-21

## Context

The project's end state needs to be explicit. A digital twin framed only as an experiment risks becoming an indefinite companion to the legacy heating controllers, while the intended outcome is a replacement system. At the same time, replacing hardware is not authorised by the existence of a model, decoded packets, or a Home Assistant dashboard.

## Decision

The strategic objective is to replace the existing physical heating-control hardware with a Home Assistant-centred control system. The installed RAMSES-II TRVs are retained devices and form part of the compatibility boundary. The hot-water-cylinder temperature gauge is an in-scope planned Sunnydays telemetry/UI addition; its eventual physical sensing and wiring arrangement is not decided by this ADR.

The current delivery phase remains software-only: passive evidence, a digital twin, `RAMSES/TEST/...` transport, simulator tests and Home Assistant Test View. It must not transmit RF, change bindings, reflash/configure the live gateway, operate the BDR91/boiler, or replace any live control hardware.

Any physical cutover requires a new ADR and an explicitly approved, staged, reversible plan. That future ADR must identify each hardware item to be removed/replaced, retained-device compatibility, fallback, failure mode, test evidence and homeowner operating procedure.

## Consequences

- The Programmer Contract and digital twin are implementation evidence for the replacement target, not a substitute for cutover approval.
- The model must work with retained TRVs, and the Sunnydays plan must include cylinder-temperature visibility without prematurely deciding its physical implementation.
- A successful simulator does not itself establish RF authority or boiler-control authority.
- Documentation must keep the strategic replacement target and present test-only operating status visibly distinct.
