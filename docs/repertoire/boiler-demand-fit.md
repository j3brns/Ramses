# Boiler demand and relay timing, 24 November 2026

Thermostat 226's most recent demand predicted all 238 relay demand replies in the
23 November capture and all 16 in the 24 November capture ending around 22:56 UTC.
On the four later replies with fresh data from all eight valves and both programmers,
the maximum-valve predictor missed by 17 percentage points on average. The mean
valve predictor missed by 55.12 points. Carrying forward the last relay demand missed
by 1.75 points. Each source reading expired after ten minutes.

Score each bounded receiver capture separately with
`py scripts/score_boiler_models.py < capture.ndjson` in a shell supporting
stdin redirection, with the project source on PYTHONPATH.

The relay off-duration estimate in seconds is 601.995 × (1 − demand/100).
The median period estimate uses 140 completed off intervals before 24 November.
On four later intervals the mean absolute error was 0.30 seconds. Predicting
the median training duration gave 167.51 seconds. Input demand permits one
second of recorder lag at the falling edge. This predicts when the relay turns
back on given a falling edge. The physical boiler flame is outside this model.
Run `py scripts/fit_relay_timing.py 2026-11-24T00:00:00+00:00` with grouped
HA recorder history JSON on stdin (relay active and relay demand, state changes).

An exploratory thermostat model fitted to 100 earlier distinct temperature-error
and demand pairs is demand = clamp(39 + 36 × error in °C, 0, 100). Four later
pairs gave 1.23 percentage points mean absolute error. Recorded demand can vary
at the same displayed error. Internal thermostat state, low-demand response and
minimum switching times remain open. Both captures and the later recorder
intervals had already been examined during investigation. A future unseen
episode is needed for prospective validation.
