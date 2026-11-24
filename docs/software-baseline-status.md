# Software baseline status

## Decision

The software-only Ramses Twin baseline is complete. It is ready for bounded
test-world deployment and evidence collection. It is not a Home Assistant
integration release, an MQTT broker service, an RF controller or a heating
cutover.

## What is complete

- Fixed-clock weekly schedule, temporary/permanent override, timed Boost, Eco,
  Away and Day Off models.
- Bounded per-zone thermal learner and conservative optimum-start planner.
- Virtual TRV and BDR response models.
- Runtime restart recovery of learned coefficients and zone-local overrides.
- Runtime validation that executable topics are confined to `RAMSES/TEST/...`.
- Pure-Python Home Assistant schedule/climate descriptors, Test View blueprint
  and generated Help source.
- Passive, bounded observation ingestion, scenario qualification and replay
  tooling.

The local gate currently proves this baseline with the secret scan, 150 unit
tests and 3 test-world integration tests. Run `./scripts/check.ps1` to repeat
the result locally.

## Acceptance still required

The following are external validation gates, not unfinished coding tasks:

1. Deploy an isolated `RAMSES/TEST` Test View and pass UI-01 through UI-08 at
   desktop and mobile widths using the computer-use runbook.
2. Qualify bounded, ordered observations for `schedule-change`,
   `override-expiry` and `restart-reconnect`.
3. Replay those observations against declared packet and timing tolerances.
4. Complete the RF validation ADR before any transmission, binding, live
   gateway change, BDR91 actuation or physical-controller replacement.

## Operating position

The observed heating system remains authoritative. The repository remains
receive-only for live evidence and executable only in its isolated test
transport. A future physical replacement must be a separately approved,
reversible decision under [ADR 0007](adr/0007-rf-validation-gate.md).
