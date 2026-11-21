# ADR 0006: virtual BDR response

## Status

Accepted.

## Decision

Model a virtual BDR as a test-world aggregate of current virtual-TRV demands. The maximum demand becomes the declared aggregate demand. The virtual relay is on when that demand reaches its configured threshold. The report identifies the virtual devices that contributed non-zero demand.

## Consequences

- The boiler-enable boundary is observable in the digital twin without a broker, RF frame, or physical relay action.
- The highest-demand rule and threshold are explicit, deterministic simulator choices.
- The model does not assert BDR91 timing, RF semantics, boiler interlock wiring, physical modulation, or actual boiler behaviour.
- Ordered observations and a separate cutover decision remain necessary before physical authority is considered.
