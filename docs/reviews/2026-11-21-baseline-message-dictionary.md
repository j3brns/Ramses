# Adversarial review: baseline message dictionary

## Scope

Document the bounded baseline message-code coverage and cache-topology cross-check.

## Failure modes

- A raw frame code is presented as a decoded protocol meaning without evidence.
- Baseline traffic is treated as proof of a schedule or override transition.
- Invalid 1970 gateway timestamps are used as wall-clock evidence.

## Evidence and tests

`baseline-rx-window.json` contains 111 passive RX envelopes and no `/tx` topic.
The dictionary counts are locked to that fixture by `test_baseline_dictionary.py`.
The cache fixtures provide the limited decoded roles and separately derive zone
membership.

## Decision

Publish code, count, direction and evidence status. Leave unsupported codes as
observed-only and label the topology as a cross-check. Exclude clock, schedule,
override and thermal claims.

## Rollback

Remove the repertoire entry, its test and this review. No live state or captured
fixture changes with that revert.
