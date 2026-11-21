# Contributing

## Development loops

### Local loop

Run `scripts/check.ps1`. It compiles the package and runs the deterministic unit/contract suite.

### GitLab loop

`.gitlab-ci.yml` repeats the same checks in a clean Python environment. GitLab is the merge gate; it does not connect to MQTT, Home Assistant, or RF hardware.

## Test layers

| Layer | Purpose | Allowed dependencies |
|---|---|---|
| Unit | Zone scheduling, boosts, encoders, optimiser maths | Standard library only |
| Contract | MQTT envelopes and sanitised RAMSES frame fixtures | Repository fixtures only |
| Integration | Virtual gateway and HA test namespace | `RAMSES/TEST/...` only |
| RF | Physical transmission | Separate ADR and explicit approval |

## Commit policy

- Keep one behavioural change per commit.
- Include the test or fixture proving the change.
- Do not commit secrets, production traces, or generated captures.
- Record architectural decisions in `docs/adr/` before implementation when they affect identities, transport, scheduling, or cutover.
