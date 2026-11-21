# Change management

## Change classes

| Change | Required evidence |
|---|---|
| Model or encoder behaviour | Unit test and contract test. |
| Observed topology | Sanitised trace/manifest and target-system update. |
| MQTT contract | Contract test and architecture review. |
| Schedule/boost semantics | Scenario fixture and ADR if behaviour changes. |
| Observed live data refresh | Sanitised derived fixture, target-system review, and contract test. |
| RF transmission or binding | New ADR plus explicit approval; out of current scope. |

## Review checklist

1. Is the change software-only and confined to `RAMSES/TEST`?
2. Does it update the relevant contract, target map, or ADR?
3. Does it add/adjust a deterministic test?
4. Does `scripts/check.ps1` pass?
5. Does the secret scan pass?

## Versioning

Use small conventional commits. Tag only reproducible simulator milestones, not exploratory captures.
