---
scope: docs
load: [repository-contract.md, test-contracts.md, repertoire/index.md]
canonicality:
  behaviour: programmer-contract.md
  architecture: system-architecture.md
  objectives: system-objectives.md
  decisions: adr/
  user_help: user-guide.md
  agent_knowledge: repertoire/
  review_records: reviews/
invariants:
  source: "canonical Markdown > generated dashboard/help rendering"
  provenance: "observed fact != model decision != manual-derived behaviour"
  review: "{scope, failures, evidence, decision, rollback}; conversation/prompt ∉ review"
---

# Documentation scope

- Update the one canonical document that owns the changed claim => references do not drift.
- Link a behavioural rule to a deterministic test and, when a UI exists, a computer-use scenario => documentation remains verifiable.
- Distil manuals in original words with source/page range => public sources inform behaviour without copying them or claiming hidden implementation detail.
- Treat reviews as durable decision records; put generated-asset prompts only with asset provenance => repository history remains useful and private.
