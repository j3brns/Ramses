# Adversarial review: telemetry snapshot normalisation

## Scope

Add a pure conversion from externally supplied Home Assistant-style readings to
one prospective optimiser sample. It does not query Home Assistant, connect to
MQTT, access the radio, or train a model.

## Failure modes

- Fresh room temperature could be combined with stale weather, valve, or
  boiler values and misrepresented as a physical observation.
- Entity update times could be in the future, missing, naive, or too far apart.
- Python's `bool`/`int` overlap could admit a boolean as a temperature or
  demand.
- Normalisation could be misrepresented as interval construction, calibration,
  or a thermal-fidelity result.

## Evidence and tests

Deterministic tests accept a fresh, tightly aligned four-reading bundle and
reject stale/future, skewed, incomplete, invalid-receipt, and invalid-type
inputs. Existing bounded receipt-order validation remains separate.

## Decision

Use broker receipt as the observation reference. Require source values to be no
older than fifteen minutes and no more than two minutes apart by default.
Return a normalised sample only; it remains subject to the existing ordered
receipt and interval/training contracts. The limits are project-defined
evidence hygiene, not a claim about Home Assistant polling or device cadence.

## Rollback

Revert the snapshot classes, normaliser, tests, repertoire note, contract
clarification, and this review together. No runtime transport or live system
behaviour depends on them.
