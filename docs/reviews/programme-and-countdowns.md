# Adversarial review

## Scope

Passive programme reports, relay countdown decoding, and chronological
comparison of demand and duty-cycle forecasts.

## Failure modes

Repeated packets are correlated. Thermostat gain fitted to future samples
would inflate accuracy. A valve can report a different target before the
programmer changes. A relay timer can be revised mid-cycle.

## Evidence and tests

Compare all demand models on the same timestamp pairs, using prior days for
fitting. Retain the incumbent relay prediction alongside the 600-second
challenger. Cover stale programmer reports and distinct relay timers in
regression tests. Compare zone 02 changes with zone 01 on the same controller.

## Decision

Treat advertised next targets as dated observations. Keep boiler timing
predictions in the passive observer. The early valve transition and minimum
relay pulse each have insufficient evidence for a unique cause.

## Rollback

Revert the offline readers and challenger fields to restore the previous
observer output. These readers have no command transport.
