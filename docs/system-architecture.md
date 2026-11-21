# System architecture

```text
Home Assistant test integration
        | MQTT command frame (RAMSES/TEST/.../tx)
        v
Virtual RF gateway / test transport
        | structured RAMSES-II frames
        v
Virtual CM67z controllers <-> Virtual TRVs <-> Virtual BDR91
        |
        +-- MQTT receive frame (RAMSES/TEST/.../rx)
```

## Components

| Component | Responsibility |
|---|---|
| Schedule adapter | Supplies a timezone-aware weekly timetable, active setpoint, and next switchpoint. |
| Zone coordinator | Owns schedule, override, target and recovery state for one zone. |
| Virtual TRV | Applies only its bound-zone target, tracks local override/window state, and emits a declared heat-demand response. |
| Predictor | Learns each zone's heating gain and passive loss from bounded observations, then estimates conservative early-start timing. |
| Packet encoder | Produces protocol-valid test frames. |
| Test transport | Publishes/consumes only `RAMSES/TEST/...` MQTT messages. |
| HA adapter descriptor | Pure-Python test-zone names and validated test topics; it imports no Home Assistant runtime. |
| Fixture runner | Replays sanitised traces and checks expected outcomes. |
| Runtime/state store | Learns per-zone coefficients and atomically persists only those coefficients across restart. |

## Boundary

Live RF and `RAMSES/GATEWAY/...` are outside this architecture. The test system must never access them.
