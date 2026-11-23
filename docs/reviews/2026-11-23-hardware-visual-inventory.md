# Adversarial review: hardware visual inventory

## Scope

Review the new source-linked inventory and original logical transition diagram.

## Failure modes

- A third-party supplier or manufacturer image is copied into Git without a
  recorded reuse right.
- A product-family image is presented as proof of the installed model.
- A legacy-to-target arrow is understood as a live wiring or control path.
- Uncertain `DHW500`, Sonoff, Raspberry Pi, or valve variants become asserted
  facts.

## Evidence and tests

The inventory links external product or archival references rather than
embedding their images. The project already documents the Elecram live-boundary
rules in `hardware-foundation.md`; the Mermaid source is an original logical
diagram and contains no configuration, credential, topic, or wiring detail.

## Decision

Keep exact-model uncertainty explicit. Use only source links until the relevant
installed label is verified. Mark all future-control arrows as evidence-gated.

## Rollback

Revert this inventory, its index link, and this review together. It changes no
Home Assistant, MQTT, radio, hardware, or repository asset state outside these
documents.
