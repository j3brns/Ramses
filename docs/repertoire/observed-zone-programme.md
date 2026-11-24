# Programme values advertised by the CM67Zs

At 23:55 UTC on 24 November 2026, the receiver had heard all four zones
within the previous three minutes.

| Zone | Receipt time UTC | Current | Next | Estimated change UTC on 25 Nov |
|---|---|---:|---:|---|
| Kitchen (487/01) | 23:52:03 | 10°C | Unknown | Unknown |
| EJMB + RDGB (487/02) | 23:52:03 | 12°C | 17°C | 06:56 |
| Lounge (751/01) | 23:54:17 | 12°C | Unknown | Unknown |
| CMQ JGB (751/02) | 23:54:17 | 12°C | 18°C | 06:51 |

The installed RAMSES RF library's `NowNextSetpointPayload` in
`ramses_rf/payloads/hvac.py` decodes seven bytes of `2249` as a zone index,
two signed temperatures in hundredths of a degree Celsius, and an unsigned
countdown in minutes. Add the countdown to broker receipt time to estimate
the next change. The countdown has minute resolution. In both windows zone
01 advertised its current target using `2309`; its next transition is unknown.

Replay raw passive RX envelopes by piping NDJSON to
`py scripts/observed_zone_programme.py --as-of 2026-11-24T23:55:00Z`
with the project source on PYTHONPATH. Each zone includes the time and values
from its last programmer report. After ten minutes the report is marked stale.
An elapsed countdown marks the forecast elapsed until a fresh report arrives.
The ten-minute freshness policy is a display choice. Neither a countdown nor
a repeated transition establishes a weekly schedule.

Each countdown also carries an agreement label. A single advertisement is
`single`. For the same current and next targets, compare the most recent
advertisement received at least a minute earlier within the freshness window.
Agreement within 90 seconds is `corroborated`; a larger movement is `revised`.
The report retains both ETAs. A change of target begins a new comparison.
On 24 November at 22:25:23, 487/02 advertised 767 minutes and moved its ETA
from about 06:56 to 11:12 the next morning. The next two broadcasts put it
back around 06:56. The capture leaves the cause of the isolated shift open.

## Two contrasting observations for valve 040

On 24 November at 22:57:05, programmer 751 advertised 18°C for zone 02,
followed by 12°C in four minutes. It first advertised 12°C at 23:01:29.
Valve 040 last reported 18°C at 22:59:21 and first reported 12°C at
23:03:24, 114.4 seconds after the changed programmer report. This measures
reporting lag; valve actuation time is unknown. Zone 01 stayed at 22°C
on the adjacent announcements. Lounge valve 387 reported 22°C at 23:00:02 and
23:05:27; valve 472's closest reports were 22:22:56 and 23:22:57, also 22°C.

On 23 November all 58 zone 02 programmer announcements reported 12°C with
19.5°C next. Valve 040 first reported 19.5°C at 04:23:12 although the
04:20:42 countdown still had 151 minutes to run. The cause of this earlier
valve change is unknown. Reading valve targets alone would misclassify it
as a normal programmer transition.
