# Ramses experiment rules

## Safety boundary

- This repository models and tests RAMSES-II behaviour only.
- Do not transmit RF, alter gateway transmit settings, bind devices, or change live heating configuration.
- Use only `RAMSES/TEST/...` MQTT topics in simulator code and fixtures.
- Never store credentials, Home Assistant tokens, broker passwords, or Home Assistant configuration in Git. Bounded RAMSES-II packet corpora under `data/observed/` are explicitly allowed.

## Working agreement

- Treat observed packet traces as evidence; record source, time range, and scenario in `data/` metadata.
- Keep the target-system map in `target-system/` current and cite packet evidence for topology changes.
- Add or update an ADR for decisions affecting architecture, controller identity, RF transport, or cutover.
- Add a deterministic test for every schedule, override, encoding, or state-transition change.
- Add a concise adversarial review under `docs/reviews/` for every model, collector, scenario, transport, CI, or deployment change; it must name failure modes, evidence, decision, and rollback.
- Documentation is a release artifact: update the relevant architecture, objective, contract, rule, target-system, or ADR document in the same change.
- Refresh observed data through the collector; raw RAMSES-II packet fixtures may be committed only through its bounded packet-corpus output.
- Keep derived observation data bounded. The collector replaces its fixtures and caps representative samples; do not introduce append-only logs or captures.
- Treat cache snapshots as topology/state evidence only. Any claimed timed behaviour requires a bounded ordered `/rx` scenario under `data/scenarios/` and a replay test.
- Keep the simulator software-only until an explicit, separately approved RF test plan exists.

## Test and commit gates

- Run `scripts/check.ps1` before every commit.
- Unit tests use `pytest`; they must be deterministic and use a fixed clock.
- Contract tests consume sanitised fixtures only and must never access the live MQTT broker.
- Integration tests are opt-in and use `RAMSES/TEST/...` only.
- Keep commits small, imperative, and scoped to one behaviour or decision.
- CI must pass before merging; no RF-capable code is merged without an ADR and explicit approval.
- Install `.githooks` with `scripts/install_hooks.ps1`; do not bypass the adversarial-review hook.
- Use `scripts/tk.ps1`: claim one ready task before editing, respect dependencies, and log evidence before closing it. `tk` coordinates local agents; Git documents remain the release authority.
