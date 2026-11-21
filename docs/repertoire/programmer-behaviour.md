---
type: concept
title: Programmer behaviour
source:
  - ATC928G3000 Evohome User Guide 32303496-001 C, pages 2, 4-16
verification: manual-derived
contract: ../programmer-contract.md
implementation: partial-test-world-only
---

# Programmer behaviour

The programmer owns user intent, not valve mechanics. It resolves schedule, override and whole-system modes into one effective target per zone, records why that target applies, and publishes only through the test transport.

The manual-derived repertoire is: zone membership; weekly time/temperature
schedules; temporary and permanent zone overrides; explicit return to schedule;
whole-system quick actions; optional, explainable optimum start/stop; and
fault/alert visibility. The implementation status and page-level source map are
in the contract, so this concept does not turn unbuilt features into claims.

The system retaining durable state after restart is a project requirement, not a
claim derived from the guide.

See the [Programmer Contract](../programmer-contract.md) for precedence and acceptance cases.
