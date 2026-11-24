# Four-zone membership from received valve reports

All eight valves repeatedly reported the expected programmer and zone in both
captures. Room names come from the household map. Programmer and zone values
below come from the RF reports and agree with the [saved topology](../../data/observed/topology.json).

| Programme | Programmer | Zone | Valve | 23 Nov setpoint / demand reports | 24 Nov setpoint / demand reports |
|---|---|---|---|---:|---:|
| Kitchen | 487 | 01 | 027 | 87 / 88 | 17 / 17 |
| Kitchen | 487 | 01 | 030 | 76 / 75 | 14 / 15 |
| Kitchen | 487 | 01 | 049 | 79 / 81 | 14 / 18 |
| EJMB + RDGB | 487 | 02 | 389 (EJMB) | 85 / 87 | 17 / 16 |
| EJMB + RDGB | 487 | 02 | 048 (RDGB) | 76 / 77 | 16 / 14 |
| Lounge | 751 | 01 | 472 | 4 / 13 | 1 / 2 |
| Lounge | 751 | 01 | 387 | 86 / 77 | 19 / 15 |
| CMQ JGB | 751 | 02 | 040 | 85 / 86 | 17 / 19 |

Use subscriber receipt time in UTC. The first window covers 23 Nov 2026
00:26:44–04:42:29 (5,592 envelopes). The second covers 24 Nov 22:05:08
through 22:54:59 (947 envelopes). For each passive gateway RX frame with an
`04:` source, a `12:` peer address and code `2309` or `3150`, group by full
valve address, full programmer address and the first payload byte. Display
the last three address digits. Counts include repeated reports. No qualifying
frame in either window placed any valve in another group.

This establishes the grouping for the digital twin. Physical room labels still
depend on the household map. The two captures contain routine reports; accepting
a command from a replacement programmer and calling the boiler are separate
behaviours requiring their own evidence.
