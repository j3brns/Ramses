# Adversarial review: bounded Kitchen watch window

## Scope

Review the local extractor that chooses a potential Kitchen controller-target
transition from passive, already captured RX NDJSON. It must not perform live
capture, MQTT access, RF transmit, or scenario promotion.

## Failure modes

- A gateway epoch clock could manufacture a timeline. Mitigation: only the
  Mosquitto receipt clock is accepted for target ordering.
- Generic `2309` traffic could be mistaken for Kitchen. Mitigation: selector
  requires source `12:216487`, zone `01`, `I`, and a valid target range.
- A trailing target can lack enough context. Mitigation: no output is written
  until the requested post-transition context is present.
- Repeated runs could grow storage indefinitely. Mitigation: input is capped;
  output is an explicit replacement file; no append behaviour exists.
- A manual target change can resemble a schedule edge. Mitigation: the result
  is named a candidate and policy forbids a schedule claim without external
  corroboration.

## Evidence and tests

The focused tests cover valid receipt-timestamped transitions, ordinary
traffic, incomplete trailing context, bounded input retention, and receipt
time preservation through scenario replay. The repository gate additionally
checks the broader contracts.

## Decision

Accept for passive, local candidate selection only. Do not connect it to a
broker or automate promotion to schedule evidence.

## Rollback

Remove the extractor and its output file. It has no service, credential,
broker, radio, Home Assistant, or live-capture state to unwind.
