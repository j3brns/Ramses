# Target system

This is the current, evidence-backed map of the live system. It is descriptive only; it must not be used to transmit, bind, or alter the live system.

## Observed controller zones

| Controller | Zone | Intended room label | Bound radiator valves |
|---|---:|---|---|
| `487` | `01` | Kitchen | `027`, `030`, `049` |
| `487` | `02` | EJMB / RDGB | `048`, `389` |
| `751` | `01` | Lounge | `387`, `472` |
| `751` | `02` | CMQ JGB | `040` |

The source of membership is the derived fixture at `data/observed/topology.json`, generated only from passively observed `2309`/`3150` cache records. Raw packet captures and identifiers are deliberately excluded.

## Related devices and limits

- Thermostat `326` and boiler relay `642` are recorded as a separate boiler-demand path; their exact binding is not yet proven by the derived topology fixture.
- The target model is a software-only controller and test MQTT world. Live RF operation remains out of scope pending a separate ADR and explicit approval.
