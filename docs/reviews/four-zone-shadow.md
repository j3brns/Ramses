# Adversarial review

## Scope

Four-zone test programming, passive boiler-demand attribution and relay timing.

## Failure modes

Repeated values exaggerate apparent source agreement. Compare sources at
common timestamps and on the day demand changed. Separation of programme
zones and a boiler call is material: a valve reporting demand cannot alone
establish that the receiver acted on it. An absent relay packet can merge
cycles. Expire old state and label incomplete predictions.

## Evidence and tests

The two receiver captures support the eight-valve zone map. The November 24
replay produced five rising-edge predictions using only demand available at
the preceding falling edge. Tests cover stale relay observations and a
thermostat update after a forecast. The four-zone runtime tests cover a
restart during boost, cancellation and cross-zone isolation.

## Decision

Use this model in the shadow observer. Score new forecasts by comparing
processing time to the eventual observed rising edge. The thermostat fit
has little validation near zero demand. The installed synthetic timetables
are examples. Live control authority stays with the installed programmers.

## Rollback

Stop the bounded forecast reader to end the observation. Revert the
test-dashboard Programmer view and its dedicated helpers to withdraw the
interactive experiment. Neither rollback requires RF transmission.
