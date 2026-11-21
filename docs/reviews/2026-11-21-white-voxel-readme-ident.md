# Adversarial review: white voxel README ident

## Scope

Promotion of the white voxel house as the production top-level README ident, using hand-authored `assets/ident/voxel-house-white.svg` and retaining `voxel-house-white-v4.png` as its high-fidelity reference.

## Failure modes

- A detailed house cross-section could be too busy at banner scale or distract from the project summary.
- A voxel visual language could be mistaken for a copied game asset or for a literal Home Assistant UI.
- An off-white or aged background could look muddy against GitHub Markdown and weaken the requested clarity.
- A later edit could lose the prompt, decision, and review context that makes the generated asset repeatable.
- An automatic vector trace could preserve raster artefacts and be less maintainable than the PNG.

## Evidence and tests

The candidate was generated from explicitly original, asset-free constraints and visually reviewed at generated-banner and asset-directory context. The production prompt fixes the background as pure white and calls for bright, high-clarity control, heat, water and time colours. The image is local to the repository and renders directly in the Markdown README. Its causal chain is symbolic only; it does not assert live telemetry, a physical configuration, or control authority.

## Decision

Use `voxel-house-white-v4.png` in the README. Keep the SVG as an editable alternative and retain the preceding v3/dark candidates for provenance and alternatives. Retain `sundial-wireframe.png` for dark dashboard/panel uses. The asset is an explanatory ident, not a product UI.

## Rollback

Restore the README image link to `assets/ident/sundial-wireframe.png`, while retaining the new file, prompt history and review as evidence. No Home Assistant, MQTT, RF or heating state is involved.
