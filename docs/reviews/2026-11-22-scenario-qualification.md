# Adversarial review: scenario qualification contract

## Scope

Review a pure local validator and manifest that distinguish baseline RX,
candidate observations, and qualified named behaviour evidence.

## Failure modes

- A candidate can resemble a scheduled change. Mitigation: candidates retain a
  hypothesis only; their public behaviour field is always empty.
- A manifest can falsely declare healthy time. Mitigation: health is recomputed
  from the supplied ordered scenario and must match the manifest.
- Valid packet syntax can still lack causal proof. Mitigation: qualification
  requires independent corroboration and a named replay test.
- Gateway epoch time can appear ordered. Mitigation: only current,
  timezone-aware, strictly increasing broker receipt times qualify.
- A generic manifest could endorse a different scenario. Mitigation: the
  manifest scenario name must exactly match the replayed scenario.

## Evidence and tests

Tests prove baseline and candidate states cannot expose qualified behaviour,
qualification needs healthy chronology plus corroboration and replay test, and
scenario-name or receipt-health mismatches are rejected.

## Decision

Accept as the sole qualification seam for future named schedule, override, and
restart evidence. Existing baseline data remains baseline; no live capture is
changed or promoted.

## Rollback

Remove the module and manifests. No service, MQTT client, radio action, Home
Assistant configuration, or live data is created.
