# Adversarial review: virtual BDR response

## Scope

Add a pure virtual BDR model that aggregates virtual TRV demand into a test-only demand and relay report.

## Failure modes

- Averaging demand could hide a zone that needs heat; unbounded demand could make relay state meaningless.
- The model could be mistaken for a physical BDR91 or boiler-control implementation.
- Input ordering could make reports unstable, or a naive timestamp could create ambiguous state evidence.

## Evidence and tests

The model chooses maximum demand, bounds input demand to zero through one, sorts contributor identifiers, validates threshold and requires a timezone-aware report time. Unit tests cover highest-demand selection, threshold/off behaviour and invalid model inputs.

## Decision

Use a pure in-memory maximum-demand relay model. Expose the decision as test-world state only; leave packet encoding, broker I/O, RF and physical boiler behaviour outside this component.

## Rollback

Revert the model, tests and documentation. No MQTT, RF, Home Assistant or live boiler state is affected.
