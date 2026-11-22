---
type: concept
title: Observational telemetry snapshot normalisation
verification: project-defined
implementation: test-world evidence preparation
---

# Observational telemetry snapshot normalisation

The optimiser may only receive a prospective sample after an external reader
has supplied four values: reference temperature, outdoor temperature, valve
demand, and boiler availability. Each value carries its source update time; the
bundle also carries its broker receipt time and optional gateway time.

`assess_snapshot` is pure and read-only. It accepts a bundle only when every
value is present, valid, recent against broker receipt, and within the declared
source-time skew. The default limits are fifteen minutes age and two minutes
skew. A future source update is rejected as stale rather than being silently
accepted.

The result is only a normalised `TelemetrySample`. It still requires the
separate ordered-receipt validation and bounded interval construction before
any optimiser training. A parseable 1970 gateway timestamp remains diagnostic
metadata; it cannot establish chronology.

This protects against a common false claim: a dashboard/API snapshot made from
individually plausible entities is not necessarily one coherent physical
observation.
