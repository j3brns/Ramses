# Adversarial review: runtime recovery frames

## Scope

Add a pure, deterministic recovery seam that recomputes the current frame for
every configured virtual zone. It does not persist controller state, connect to
MQTT, publish a message, or interact with Home Assistant or RF.

## Failure modes

- Recovery waits for the next schedule edge. Mitigation: it evaluates every
  controller at the supplied recovery time immediately.
- A temporary override is silently lost or kept after expiry. Mitigation:
  recovery uses the existing controller target calculation, including its
  expiry rule.
- Unordered controller registration makes assertions or publication order
  unstable. Mitigation: zone IDs are sorted before frames are returned.
- A naive clock makes a weekly schedule ambiguous. Mitigation: recovery rejects
  a time without timezone information.
- Returning frames is mistaken for live resynchronisation. Mitigation: the
  runtime has no transport dependency; an isolated, later test-only adapter
  would decide whether to publish them.

## Evidence and tests

Fixed-clock tests cover an active override, its expiry back to the scheduled
target, stable order, and rejection of a naive recovery time.

## Decision

Use `TwinRuntime.recovery_frames` as the in-process test seam for startup and
reconnect behaviour. Durable reconstruction of schedule and override state is
explicitly outside this seam and remains an adapter responsibility.

## Rollback

Revert the runtime method, its tests, contract note, and this review together.
No persisted controller state, MQTT publication, Home Assistant data, RF
traffic, or heating equipment state is changed.
