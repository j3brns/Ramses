# Architecture decision records

ADRs preserve consequential decisions that should not be rediscovered from code,
tasks, or conversation. They state the decision and its consequences; detailed
behaviour and evidence belong in the Programmer Contract, test contracts, and
scenario records.

## Current decision summary

The project is proving a Home Assistant-led replacement for the legacy heating
controls while retaining the RAMSES-II TRVs. Development is software-only and
receive-only: the digital twin uses `RAMSES/TEST/...`, live RF is observed but
never transmitted, and a physical cutover needs an explicit later decision.
Zones use a weekly programme plus temporary boost semantics; virtual TRVs and
the virtual BDR use declared, testable models rather than claims about hidden
Honeywell firmware. Observed evidence is sanitised and bounded before it enters
the repository.

## Reading decisions

Read ADRs in number order. An **Accepted** ADR is current unless a later ADR
explicitly supersedes it. An ADR does not authorise a live heating, RF, binding,
gateway, or boiler change.

| ADR | Decision |
| --- | --- |
| [0001](0001-software-only-first.md) | Build the software-only test world first. |
| [0002](0002-observed-data-refresh.md) | Refresh sanitised observed evidence deliberately. |
| [0003](0003-weekly-timer-and-boost.md) | Use weekly timer and temporary-boost semantics. |
| [0004](0004-virtual-trv-response.md) | Use an explicit virtual TRV response model. |
| [0005](0005-replacement-target-and-retained-devices.md) | Replace controls while retaining TRVs and planning cylinder telemetry. |
| [0006](0006-virtual-bdr-response.md) | Model virtual BDR demand as a declared test-world aggregate. |

## Adding or changing an ADR

Create the next zero-padded number when a choice is consequential, difficult to
reverse, or constrains safety, authority, transport, data retention, or cutover.
Use `Context`, `Decision`, `Consequences`, and `Status`. Link deterministic
tests and observed evidence where they constrain the decision. A changed
decision gets a new ADR that names what it supersedes; do not rewrite history.

Before committing, add an adversarial review when the change affects a boundary
or contract, run `scripts/check.ps1`, and wait for CI before calling a shared
release ready.
