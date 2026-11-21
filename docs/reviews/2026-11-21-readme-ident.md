# Adversarial review: README ident

## Scope

The generated Ramses README banner and its prompt/version history.

## Failure modes

- An overly literal recreation of an identifiable wireframe arcade game's screen or brand.
- An attractive image that fails to communicate time, scheduling or heating at README scale.
- A generated asset with no prompt, rationale or usable path for later iteration.
- Treating a raster image as editable vector source.

## Evidence and tests

Three prompt revisions are retained with the selection rationale in `assets/ident/prompt.md`. Computer-use preview in File Explorer verified the first two versions at banner scale. V2 was selected because its sun path, sundial and schedule tick ring remained legible; V3's clearer shadow was not sufficient to offset its weaker schedule cue.

## Decision

Use the original, vector-like raster V2 as the README asset. Retain source prompts and candidates. Describe the visual influence at a high level only; do not claim affiliation with, or reproduce, another game's protected elements.

## Rollback

Remove the README image link and `assets/ident/`; no executable, Home Assistant or heating-system behaviour depends on this asset.
