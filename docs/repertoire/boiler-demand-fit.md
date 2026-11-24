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
episode was subsequently scored using the [shadow observer](relay-shadow-run.md).

On 24 November, thermostat demand was 68% at the 23:06:11.049 UTC relay
falling edge. At 23:06:13.093 the observer logged an expected rising edge at
23:09:23.689. The receiver saw the rising edge at 23:09:23.054, 0.635 seconds
early. This is one prospective relay-state prediction.

## Extended validation, 24 November

Two comparisons distinguish radiator demand from boiler demand. At 22:46:15
Lounge valve 387's latest report was 100% and the boiler relay reported 78%.
At 23:36:02 all eight valves most recently reported zero and the relay reported
61%. All valve reports used here were less than ten minutes old. Eight of
eleven qualifying relay demand replies up to 23:57 had a valve reading above
relay demand. This contradicts a simple maximum-of-all-callers model under
the ten-minute freshness assumption. The samples are asynchronous.

Five previously logged forecasts (23:06–23:46 falling edges, demand
61–68%) averaged 0.713 seconds absolute error. All five switch-ons arrived
early. Recalculating the same widths with exactly 600 seconds reduced the
mean error to 0.007 seconds on broker receipt timestamps. This comparison
was retrospective. The observer now issues both forecasts before the outcome.

At 23:56:06 UTC both models issued a prediction at 65% demand. The
600-second model forecast 23:59:34.121; the incumbent forecast 23:59:34.821.
The received rising edge was 23:59:34.128. Absolute errors were 0.008 and
0.692 seconds respectively. These are differences in broker timestamps.

The relay also reports an actuator countdown to thermostat 226. The installed
RAMSES RF 0.61.4 decoder defines the seven-byte `3EF1` reply as domain,
cycle countdown, actuator countdown, modulation and flags. At 23:46:08.298
the two countdowns were 583 and 217 seconds. The actuator deadline was
23:49:45.298; the relay reported on at 23:49:45.113. Read these timers
with `scripts/read_relay_countdowns.py`. Updated replies can revise a
deadline, especially during continuous demand.

Rolling validation on 22–24 November exposed two limits. On 22 November,
one 96% demand off pulse lasted 60 seconds; the linear duty model expected
24. A 60-second minimum explains that single example. Two on intervals
lasted hours as demand reached 100% during the run. Freezing demand at
the start of those intervals fails. Use `scripts/score_relay_history.py`
to compare models by date and relay state.

On 67 later demand observations, the static temperature-error model averaged
5.71 percentage points absolute error. Carrying forward previous demand
scored 3.60. Starting with previous demand and adjusting for the change in
temperature error scored 3.04. The last model needs a fresh prior demand
measurement. Its gain was fitted separately on earlier days. Run
`py -m scripts.validate_thermostat_forecasts 2026-11-22` with full grouped
HA history on stdin. The previous four-sample static-model result describes
only that narrow window.

For programme timing and valve response, see the
[four-zone advertised programme](observed-zone-programme.md).
