---
type: concept
title: Programmer behaviour
source:
  - ATC928G3000 Evohome User Guide 32303496-001 C, pages 4-16
verification: manual-derived
contract: ../programmer-contract.md
---

# Programmer behaviour

The programmer owns user intent, not valve mechanics. It resolves schedule, override and whole-system modes into one effective target per zone, records why that target applies, and publishes only through the test transport.

The initial repertoire is: zone membership; weekly time/temperature schedules; temporary and permanent zone overrides; explicit return to schedule; whole-system quick actions; optional, explainable optimum start/stop; and fault/alert visibility. The system must retain enough durable state to recreate the effective target after a restart.

See the [Programmer Contract](../programmer-contract.md) for precedence and acceptance cases.
