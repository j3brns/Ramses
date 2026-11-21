# Adversarial review: Programmer Contract fidelity map

## Scope

Refresh the manual-derived Programmer Contract with an explicit source/status
map and a verification map for each control capability.

## Failure modes

- A manual reference is treated as evidence of hidden RF or CM67z behaviour.
- A proposed HA rule appears to be an available dashboard control.
- An unimplemented Quick Action or permanent override gains implied authority.
- A rendered Help panel drifts from the canonical contract.

## Evidence and tests

The ATC928G3000 User Guide `32303496-001 C`, pp. 2 and 4-16, supports the
user-visible capability inventory. `tests/test_programmer_contract.py` verifies
that the Markdown retains its source/status and verification structure. Existing
timer, schedule-adapter and test-climate tests are linked only as evidence for
their implemented slices.

## Decision

Use the manual as a behavioural reference, and label the project state of every
capability. Keep HA precedence, restart handling, optimiser calibration and RF
behaviour outside the manual-derived claim until each has its own evidence.

## Rollback

Revert this map and its documentation test. No Home Assistant, MQTT, RF, or
heating state is changed.
