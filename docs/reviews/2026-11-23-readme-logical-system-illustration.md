---
scope: readme-logical-system-illustration
date: 2026-11-23
status: accepted
---

# README logical-system illustration review

## Scope

Add an original raster overview to the README and retain its prompt/provenance.

## Failure modes considered

- A polished diagram could look like a live dashboard or claim completed control
  transfer.
- It could reproduce a supplier product image or include inaccurate labels.
- The image could displace the editable architecture source.

## Evidence

- The generated image was visually reviewed for a pure-white background,
  component separation and an explicit gate before the boiler.
- The README identifies it as original explanatory artwork and links the
  editable Mermaid source.

## Decision

Use the PNG for README legibility. Retain the Mermaid diagram as the editable,
canonical logical architecture and keep the generation prompt next to the PNG.

## Rollback

Remove the README At a glance section and `assets/architecture/`. No system,
radio, broker or Home Assistant state is affected.
