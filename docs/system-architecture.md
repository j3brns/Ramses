# System architecture

## Household context

Home Assistant runs on a Raspberry Pi as the household controller. The mobile
app supplies household access and identity; Alexa and NSPanel are interaction
surfaces. A Sonoff Zigbee radio serves lighting. A remotely mounted Elecram
bridge observes RAMSES traffic for this project.

The heating work is a digital twin: it models each room and the system-level
communication contract above the RAMSES-II data-link layer. The existing
heating estate remains authoritative. Direct TRV or boiler tasking is a future,
evidence-gated decision, not a current architectural capability.

See the editable [logical system diagram](diagrams/logical-ha-system.md). It
shows roles and boundaries only; it deliberately excludes configuration,
addresses, credentials and live-control paths.

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
| Schedule adapter | Maps HA Schedule helper blocks plus `target_temperature` additional data to a timezone-aware weekly timetable. It maps active entity data and `next_event` to the current target/next switchpoint; off periods use an explicit frost/off target. |
| Zone coordinator | Owns schedule, override, target and recovery state for one zone. |
| Virtual TRV | Applies only its bound-zone target, tracks local override/window state, and emits a declared heat-demand response. |
| Virtual BDR | Uses the highest current virtual-TRV demand as an explicit test-only demand value and turns a virtual relay on above a declared threshold. |
| Predictor | Learns each zone's heating gain and passive loss from bounded observations, then estimates conservative early-start timing. |
| Packet encoder | Produces protocol-valid test frames. |
| Test transport | Publishes/consumes only `RAMSES/TEST/...` MQTT messages. |
| HA adapter descriptor | Pure-Python test-zone names, validated test topics, and read-only effective-target/next-change/optimiser/planned-start diagnostics; it imports no Home Assistant runtime. |
| Fixture runner | Replays sanitised traces and checks expected outcomes. |
| Runtime/state store | Learns per-zone coefficients and atomically persists only those coefficients across restart. |

## Boundary

Live RF and `RAMSES/GATEWAY/...` are outside this architecture. The test system must never access them.
