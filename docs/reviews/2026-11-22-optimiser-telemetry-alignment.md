# Adversarial review: optimiser telemetry alignment

## Scope

Add a pure, bounded validator for prospective thermal observations. It accepts
receipt-timestamped reference temperature, outdoor temperature, valve demand,
boiler availability, and diagnostic gateway time. It does not collect data,
connect to a broker, interact with Home Assistant or radio, or train a model.

## Failure modes

- Missing, implausible, or out-of-range fields could enter a thermal interval.
- Gateway time near the 1970 epoch could be mistaken for real chronology.
- Duplicate or non-increasing broker receipt times could form a false interval.
- An unbounded batch could turn an evidence check into retained history.
- Candidate validation could be misrepresented as calibration or physical fidelity.

## Evidence and tests

Deterministic tests cover epoch labelling, complete candidate selection,
incomplete/out-of-range rejection, missing and non-increasing receipt times,
and the fixed batch limit. The optimiser contract retains the independent
requirement for three clean heat and three clean loss observations before it
may plan an early start.

## Decision

Accept broker receipt time as the sole chronology basis. Keep a parseable
gateway epoch timestamp as diagnostic metadata, labelled `gateway-epoch-invalid`.
Expose only aligned candidates; interval construction, thermal training, and
any fidelity claim remain outside this validator.

## Rollback

Revert the telemetry module, its tests, the optimiser-contract clarification,
and this review together. Existing thermal-model tests and runtime behaviour do
not call the validator.
