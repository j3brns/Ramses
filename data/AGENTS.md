---
scope: data
load: [../docs/ingest-contract.md, ../docs/scenario-recording.md, ../docs/test-contracts.md]
invariants:
  ingest: "passive RX only; TX = forbidden"
  retention: "bounded + sanitised; replace fixture, never append log"
  time: "snapshot != chronology; timed claim => ordered scenario + replay"
---

# Evidence scope

- Refresh fixtures only through the collector => source schema and sanitisation remain reproducible.
- Store topology/state snapshots separately from ordered scenarios => the model cannot claim timing that the evidence lacks.
- Do not commit credentials, HA configuration, addresses or unbounded captures => project data remains shareable and reviewable.
