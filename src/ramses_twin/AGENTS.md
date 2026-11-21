---
scope: src/ramses_twin
load: [../../docs/system-architecture.md, ../../docs/contract.md, ../../docs/test-contracts.md]
invariants:
  side_effects: "domain/model code has no broker, RF, Home Assistant or filesystem side effect unless its narrow adapter contract says otherwise"
  transport: "TX/RX boundary => RAMSES/TEST only; topic validation occurs before model dispatch"
  time: "behavioural time => explicit timezone-aware clock; tests => fixed clock"
  state: "persist only declared bounded state; runtime history != log archive"
---

# Model-code scope

- Prefer small deterministic Python primitives and dependency injection => model tests remain broker-free and replayable.
- Add/adjust the matching test with every behaviour/state/encoding/transport change => the Programmer Contract stays executable.
- Do not infer live protocol behaviour from a snapshot => use ordered scenario/replay evidence or label the rule as a model decision.
- When a change expands authority, persistence or a transport boundary: route to the root switchboard's governance sources before editing.
