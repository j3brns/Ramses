# Adversarial review: baseline RX window

## Scope

Add one bounded, passive receive-only RAMSES gateway scenario captured through a Mosquitto subscriber.

## Failure modes

- A transmit or retained message is mistaken for observed radio evidence.
- The bounded baseline is misrepresented as a scheduled-change or override scenario.
- Gateway timestamps with an invalid clock are treated as reliable wall-clock timing.

## Evidence and tests

The subscriber connected and received a `RAMSES/GATEWAY/18:016440/rx` event after CONNACK and SUBACK. The capture used `-R`, a five-minute timeout and a 500-event cap; it retained 111 RX envelopes and discarded none. `test_live_rx_feeder.py` and `test_evidence.py` passed. The scenario contains receive topics only.

## Decision

Accept the ordered baseline as traffic and ordering evidence only. Its packet timestamp values are in 1970, so it cannot establish real elapsed time, schedule timing, or optimiser training data. Required named schedule, override and restart scenarios remain open.

## Rollback

Remove `data/scenarios/baseline-rx-window.json` and this review. No live broker, RF, Home Assistant or heating state is changed.
