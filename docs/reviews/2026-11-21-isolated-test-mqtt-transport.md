# Adversarial review: isolated test MQTT transport

## Scope

Add a broker-neutral transport that consumes structured commands only from its own `RAMSES/TEST/<gateway-id>/tx` topic and produces structured responses only on its matching `rx` topic.

## Failure modes

- A caller can pass a live, foreign-gateway, RX, malformed, or slash-injected topic.
- An adapter gains a path to a real broker or RF transport through this module.
- A handler can redirect a response to a live topic, return an invalid frame, or cause unbounded message retention.
- Tests validate a prefix convention but not exact per-gateway topic ownership.

## Evidence and tests

The transport has no broker dependency, socket API or message queue. It validates the gateway ID, requires the `RAMSES/TEST/` root, requires its exact TX topic, creates its own matching RX topic, validates timezone-bearing ISO timestamps and validates every handler response. Unit tests cover accepted test flow, live-topic rejection, foreign-gateway rejection, RX-topic rejection, malformed envelope rejection, unsafe gateway-ID rejection and invalid handler responses.

## Decision

Keep the transport in-process and callback-driven. A later adapter may connect broker I/O only outside this module. The transport remains the runtime boundary that rejects every non-test or foreign topic before model code runs.

## Rollback

Revert the transport module, tests and contract amendment. No broker, RF, Home Assistant or live-heating state is affected.
