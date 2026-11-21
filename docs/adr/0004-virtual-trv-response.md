# ADR 0004: Virtual TRV response model

## Status

Accepted.

## Decision

Model a virtual TRV as a bound-zone actuator with a target, local override, sensed temperature, window state, battery flag, and a declared proportional demand response. Keep packet encoding outside this component until the test transport has its own observed-frame contract.

## Consequences

- The model supports end-to-end test-world state transitions without claiming to reproduce Honeywell's proprietary valve algorithm.
- The proportional band is an explicit simulator parameter, to be calibrated only from recorded scenarios.
- A later transport task owns conversion of state reports into RAMSES frames.
