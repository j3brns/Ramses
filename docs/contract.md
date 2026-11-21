# Test RF contract

The test world mirrors the gateway boundary, not the dashboard boundary.

```text
RAMSES/TEST/<gateway-id>/rx  gateway-to-backend frames
RAMSES/TEST/<gateway-id>/tx  backend-to-gateway frames
```

Initial observed frame types:

- `1F09` controller synchronisation
- `2309` zone setpoint
- `3150` TRV heat demand
- `30C9` temperature report
- `1060` battery status
- `3EF0` BDR relay state
