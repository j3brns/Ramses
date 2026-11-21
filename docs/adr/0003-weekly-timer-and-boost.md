# ADR 0003: Weekly timer and boost semantics

## Status

Accepted.

## Decision

Model each zone clock as a repeating, timezone-aware weekly timetable of local switch points. A temporary boost ends exactly at the next timetable switch point and returns to the target selected by that switch.

## Consequences

- The initial model represents documented CM67z/Evohome-style behaviour without claiming to reproduce the original programmer's hidden implementation.
- Actual programme entries remain unknown until recorded or entered into the test world.
- DST edge cases require dedicated scenario evidence before a live-control milestone.
