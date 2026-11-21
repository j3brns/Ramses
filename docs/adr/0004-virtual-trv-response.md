# ADR 0004: Virtual TRV response model

## Status

Accepted.

## Decision

Model a virtual TRV as a bound-zone actuator with a target, local override, sensed temperature, window state, battery flag, and a declared proportional demand response. Keep packet encoding outside this component until the test transport has its own observed-frame contract.

The next accepted setpoint from the bound controller clears a virtual local override. A foreign-zone setpoint does not change it. This is a simulator coordination rule, not a statement about physical TRV firmware.

## Consequences

- The model supports end-to-end test-world state transitions without claiming to reproduce Honeywell's proprietary valve algorithm.
- The proportional band is an explicit simulator parameter, to be calibrated only from recorded scenarios.
- The controller has a deterministic, testable event at which it regains target ownership; physical local-override expiry remains unclaimed until ordered observations establish it.
- A later transport task owns conversion of state reports into RAMSES frames.
