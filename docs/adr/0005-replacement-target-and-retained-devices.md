# ADR 0005: replacement target and retained devices

- Status: accepted
- Date: 2026-11-21

## Context

The project's end state needs to be explicit. A digital twin framed only as an experiment risks becoming an indefinite companion to the legacy heating controllers, while the intended outcome is a replacement system. At the same time, replacing hardware is not authorised by the existence of a model, decoded packets, or a Home Assistant dashboard.

## Decision

The strategic objective is to replace the existing physical heating-control hardware with a Home Assistant-centred control system. The installed RAMSES-II TRVs and the hot-water-cylinder temperature gauge are retained devices and form part of the compatibility boundary.

The current delivery phase remains software-only: passive evidence, a digital twin, `RAMSES/TEST/...` transport, simulator tests and Home Assistant Test View. It must not transmit RF, change bindings, reflash/configure the live gateway, operate the BDR91/boiler, or replace any live control hardware.

Any physical cutover requires a new ADR and an explicitly approved, staged, reversible plan. That future ADR must identify each hardware item to be removed/replaced, retained-device compatibility, fallback, failure mode, test evidence and homeowner operating procedure.

## Consequences

- The Programmer Contract and digital twin are implementation evidence for the replacement target, not a substitute for cutover approval.
- The model must learn to work with retained TRVs and the retained cylinder gauge rather than treating every field device as disposable.
- A successful simulator does not itself establish RF authority or boiler-control authority.
- Documentation must keep the strategic replacement target and present test-only operating status visibly distinct.
