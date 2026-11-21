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
| Predictor | Estimates conservative early-start timing from completed heat-up events. |
| Packet encoder | Produces protocol-valid test frames. |
| Test transport | Publishes/consumes only `RAMSES/TEST/...` MQTT messages. |
| Fixture runner | Replays sanitised traces and checks expected outcomes. |

## Boundary

Live RF and `RAMSES/GATEWAY/...` are outside this architecture. The test system must never access them.
