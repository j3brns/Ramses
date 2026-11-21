# Contributing

## Development loops

### Local loop

Run `scripts/check.ps1`. It compiles the package and runs the deterministic unit/contract suite.

### Observed-data refresh

The local agent, not cloud CI, refreshes the derived fixture from the private Home Assistant host:

```powershell
ssh ha "sudo -n cat /homeassistant/.storage/ramses_cc" |
  py scripts/refresh_observations.py --input -
```

Review `data/observed/topology.json` and `target-system/README.md`, then run the local loop. The collector writes only sanitised controller/zone/last-three-digit valve membership; it never stores the raw cache.

### GitLab loop

GitHub Actions repeats the same checks in a clean Python environment. `.gitlab-ci.yml` provides the equivalent pipeline if the repository is mirrored to GitLab. Neither connects to MQTT, Home Assistant, or RF hardware.

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
- When observed data changes, commit its sanitised fixture, target-system assessment, contract result, and related documentation together.
- Record architectural decisions in `docs/adr/` before implementation when they affect identities, transport, scheduling, or cutover.
