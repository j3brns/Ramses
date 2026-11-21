---
type: observed-message-dictionary
source: data/scenarios/baseline-rx-window.json
capture: passive-rx
status: bounded-observation
time_status: gateway-clock-invalid
---

# Baseline RX observations

This is a compact dictionary of the 111 receive-only messages in the bounded
baseline window. It is evidence, not a protocol specification or a model of
controller behaviour.

The sequence order is retained. The gateway packet timestamps are in 1970, so
they must not be used for wall-clock timing, schedule transitions, retries, or
optimiser training. The capture receipt time belongs at the collector boundary.

## Observed codes

| Code | Messages | Observed role | Evidence status |
| --- | ---: | --- | --- |
| `0008` | 23 | relay/demand exchange | decoded in cache samples; baseline shows `I`, `RQ`, and `RP` traffic |
| `000A` | 2 | controller-originated status | observed only |
| `1060` | 24 | TRV battery/status exchange | decoded in cache samples |
| `1F09` | 4 | controller synchronisation | decoded in cache samples |
| `1F41` | 1 | request from an external device | observed only |
| `2249` | 2 | controller-originated status | observed only |
| `2309` | 13 | zone setpoint | decoded in cache samples |
| `2349` | 1 | request from an external device | observed only |
| `30C9` | 21 | temperature | decoded in cache samples |
| `3150` | 11 | TRV heat demand / zone membership context | decoded in cache samples |
| `31DA` | 1 | device-originated status | observed only |
| `3B00` | 3 | controller-originated status | observed only |
| `3EF0` | 1 | relay modulation | decoded in cache samples |
| `3EF1` | 4 | request/reply exchange | observed only |

“Observed only” means the repository has no claim yet about semantics beyond
the frame code, direction and participating devices.

## Topology cross-check

The baseline contains `2309` and `3150` traffic involving the two known
controllers, `487` and `751`, and their observed valves. It is consistent with
the separately refreshed cache topology:

| Controller | Zone | TRVs |
| --- | --- | --- |
| `487` | `01` | `027`, `030`, `049` |
| `487` | `02` | `048`, `389` |
| `751` | `01` | `387`, `472` |
| `751` | `02` | `040` |

This is a cross-check, not a new binding claim. A cache identifies membership;
an ordered scenario is needed before asserting a timed controller transition.

## Use now

Use this fixture to test frame acceptance, code coverage and sequence handling.
Do not use it to calibrate thermal behaviour, prove a schedule change, infer an
override expiry, or estimate clock accuracy.
