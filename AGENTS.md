---
schema: ramses-agent-switchboard/v1
purpose: Route agent work to canonical evidence; do not duplicate those sources here.
authority_order:
  - user instruction
  - safety boundary
  - canonical contract or ADR
  - tests and observed evidence
  - task queue
precedence: "ADR > contract > repertoire > generated UI; tests/evidence constrain implementation; task queue tracks work"
load:
  route:
    behaviour: [docs/programmer-contract.md, docs/repertoire/programmer-behaviour.md, docs/test-contracts.md]
    model: [docs/system-architecture.md, docs/test-contracts.md, docs/task-breakdown.md]
    mqtt: [docs/contract.md, docs/hardware-foundation.md, docs/test-contracts.md]
    evidence: [docs/ingest-contract.md, docs/scenario-recording.md, target-system/, data/observed/]
    ui: [docs/user-guide.md, docs/repertoire/lovelace-help-and-ui-assurance.md, docs/skills-inventory.md]
    governance: [docs/task-coordination.md, docs/repository-contract.md, docs/change-management.md, docs/reviews/]
    capability: [docs/skills-inventory.md, docs/repertoire/skills-and-capabilities.md]
match:
  "schedule|override|optimiser|setpoint": behaviour
  "model|thermal|TRV|BDR": model
  "frame|topic|MQTT|gateway": mqtt
  "capture|packet|topology|replay": evidence
  "Lovelace|dashboard|Help|UX": ui
  "scope|authority|RF|binding|cutover|ADR": governance
  "task|agent|parallel|commit|CI": governance
invariants:
  executable_isolation: "model/test TX ∩ LIVE = ∅; use RAMSES/TEST only"
  observed_evidence: "live RX may be passive + bounded + sanitised; live TX = forbidden"
  authority: "test evidence != live authority"
  temporal_claim: "snapshot != chronology; timed claim => ordered RX + replay"
  data: "bounded + sanitised; Git != log archive; secrets ∉ Git"
  docs: "canonical Markdown > generated UI"
  reviews: "{scope, failures, evidence, decision, rollback}; prompts/dialogue ∉ review"
  parallelism: "write ownership exclusive; read-only review shared; one integrator"
---

# Agent switchboard

## Preflight

1. Match the task to `match`; load only its `load.route` sources.
2. Claim a ready `tk` task before writing. Partition overlapping files before delegating.
3. If scope, authority, behaviour or evidence conflicts: stop, cite the collision, and seek a decision/ADR. Do not guess.

## Hard boundary

- Executable model/test traffic: `RAMSES/TEST/...` only. Observed live `/rx`: passive, bounded and sanitised only => a defect cannot address live equipment while evidence can describe it.
- RF TX, binding, live gateway/config/boiler changes and credentials are forbidden => development stays reversible and shareable.
- Cache = topology/state; ordered `/rx` + replay = time/behaviour => claims stay evidence-calibrated.

## Delivery protocol

- Independent leaves => delegate by default; write leaves => exclusive ownership; final contract/test/review/merge => one integrator.
- Behaviour/state/encoding/transport => deterministic fixed-clock tests. Test-world integration => required by `check.ps1`. Broker/live integration => explicit approval only.
- Material boundary/data/scenario/transport/CI/deployment or contract/safety-doc change => adversarial review.
- Before commit: `scripts/check.ps1` + diff/status. Shared release: local gate + independent review; CI passes before status = ready.

## Compression rules

- This file routes; canonical documents define. Add a route, not duplicate prose.
- Rules encode `action => protected_property`; preserve that relation when editing.
- Use notation for sets, precedence and exclusivity where it reduces tokens without obscuring meaning.
