# Adversarial review: passive cache refresh

## Scope

Refresh bounded RAMSES observation fixtures from the Home Assistant `ramses_cc` packet cache.

## Failure modes

- The refresh treats an unordered cache as an ordered behavioural trace.
- The committed fixtures contain credentials, Home Assistant configuration, addresses, topics, or an unbounded log.
- Changed setpoints or demands are presented as a new controller rule without an ordered scenario.

## Evidence and tests

The collector read the cache through the documented passive SSH command. `test_evidence.py` passed after the refresh. The extractor replaces bounded fixtures and keeps only the existing protocol fields; it does not publish MQTT or transmit RF.

## Decision

Accept the refreshed topology/state samples as current observation evidence only. They may inform candidate scenarios but do not prove timing, schedule semantics, or physical-control fidelity.

## Rollback

Revert the two refreshed observed fixtures. No Home Assistant, broker, RF, or heating state changes with that revert.
