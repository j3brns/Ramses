# Observe the next boiler relay cycle

Run `scripts/start_relay_shadow.ps1 -SshHost ha -DurationSeconds 3600` from
PowerShell. The foreground observer reads the active capture's
`kitchen-rx.ndjson.tmp` via SSH and exits after the requested interval
(5 seconds to 6 hours). The capture must already be running. Old rows
initialise the predictor's state. The observer writes subsequent derived
events to the named, Git-ignored `captures/relay-shadow-*.jsonl` it prints.
Each run creates a separate file. The source capture's own expiry or byte
limit may end new observations before the observer exits.

For each forecast, `at` is the broker receipt time of the falling edge,
`expected_on` is the predicted rising edge, and `processed_at` is the PC
time when the forecast was written. Pair it with the next `result`. Count it
as prospective only if the forecast's `processed_at` is **earlier than the
result's `at`**, with the PC and HA clocks synchronised. Recorder or SSH
buffering can delay processing; order within the output alone is insufficient.
`error_seconds` is observed minus predicted. Report pending, expired and
unscored cycles separately. Five seconds is sufficient to check connectivity;
a full off/on cycle is needed for a scored forecast.
