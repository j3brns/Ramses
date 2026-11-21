# Ramses

A software model of the existing CM67z/HR80 heating network, built before any live RF control changes.

## Scope

- Mirror the observed RAMSES-II packet contract over a separate `RAMSES/TEST` MQTT namespace.
- Model two CM67z controllers, their zones, TRVs, schedules and temporary boosts.
- Compare simulated packet sequences against passive captures from the live system.
- Keep the BDR91/thermostat 326 boiler-enable loop independent during the first phase.

## Current topology

```text
Controller 487
  Zone 1: Kitchen      -> 027, 030, 049
  Zone 2: EJMB + RDGB  -> 389, 048

Controller 751
  Zone 1: Lounge       -> 472, 387
  Zone 2: CMQ JGB      -> 040

Boiler enable: BDR91 642
```

## Safety boundary

The simulator uses test MQTT topics only. It does not transmit RF.

## Repository layout

- `docs/` — protocol notes, scenarios and acceptance criteria.
- `fixtures/` — anonymised packet traces used by tests.
- `src/ramses_twin/` — virtual CM67z domain model and MQTT frame adapter.
- `tests/` — deterministic schedule, boost and frame-contract tests.
