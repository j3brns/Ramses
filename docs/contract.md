# Test RF transport contract

The test world mirrors the gateway boundary, not the dashboard boundary.

```text
RAMSES/TEST/<gateway-id>/rx  gateway-to-backend frames
RAMSES/TEST/<gateway-id>/tx  backend-to-gateway frames
```

The transport accepts commands only on its own `<gateway-id>/tx` topic and publishes responses only to its own `<gateway-id>/rx` topic. Both directions use `{"msg": "<frame>", "ts": "<ISO-8601-with-timezone>"}` envelopes. It rejects live roots, foreign gateways, RX topics, MQTT wildcard gateway IDs and malformed envelopes at runtime. It has no MQTT-client, in-memory message queue or RF dependency; an adapter may add broker I/O later, but cannot bypass runtime topic validation.

The first climate write seam is deliberately pure: a temporary target changes the virtual controller and returns a matching test `tx` envelope. It does not publish that envelope, call Home Assistant, or expose a permanent override. Expiry returns through the virtual schedule/override contract.

Initial observed frame types:

- `1F09` controller synchronisation
- `2309` zone setpoint
- `3150` TRV heat demand
- `30C9` temperature report
- `1060` battery status
- `3EF0` BDR relay state

The transport contract is deliberately separate from the [Programmer Contract](programmer-contract.md): the latter defines what a user-visible heating programmer must do; this document defines the test MQTT boundary that carries those decisions.
