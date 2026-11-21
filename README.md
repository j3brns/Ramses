# Ramses

A software model of the existing CM67z/HR80 heating network, built before any live RF control changes.

![Voxel cutaway heating-programmer ident](assets/ident/explorations/voxel-house-white-v4.png)

## Scope

- Mirror the observed RAMSES-II packet contract over a separate `RAMSES/TEST` MQTT namespace.
- Model two CM67z controllers, their zones, TRVs, schedules and temporary boosts.
- Compare simulated packet sequences against passive captures from the live system.
- Keep the BDR91/thermostat 226 boiler-enable loop independent during the first phase.

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

## User-facing documentation

- [Programmer Contract](docs/programmer-contract.md) — the manual-derived behaviour Home Assistant will implement.
- [Test-system user guide](docs/user-guide.md) — the canonical, versioned guide for the future Ramses Test dashboard.
- [Repertoire](docs/repertoire/index.md) — concise, source-traceable concepts shared by agents, documentation and the eventual Help subview.
- [Skills inventory](docs/skills-inventory.md) — capability contracts required to maintain the project.

## Repository layout

- `docs/` — protocol notes, scenarios and acceptance criteria.
- `fixtures/` — anonymised packet traces used by tests.
- `src/ramses_twin/` — virtual CM67z domain model and MQTT frame adapter.
- `tests/` — deterministic schedule, boost and frame-contract tests.
