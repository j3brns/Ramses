"""Follow the existing bounded RX file and log prospective forecasts and outcomes."""

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import re
import subprocess
from threading import Timer

from predict_relay_edges import forecasts


def follow(host, seconds):
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9._-]*", host) or not 5 <= seconds <= 21600:
        raise ValueError("invalid SSH host or duration")
    remote = "/home/hassio/.config/ramses-temporal-capture/kitchen-rx.ndjson.tmp"
    started = datetime.now(timezone.utc)
    directory = Path(__file__).resolve().parents[1] / "captures"
    directory.mkdir(exist_ok=True)
    output = directory / f"relay-shadow-{started:%Y%m%dT%H%M%S%fZ}.jsonl"
    with output.open("x", encoding="utf-8") as log:
        print(output, flush=True)
        def record(event):
            log.write(json.dumps(dict(event, processed_at=datetime.now(timezone.utc).isoformat())) + "\n")
            log.flush()

        record({"event": "start", "at": started.isoformat(), "max_seconds": seconds})
        command = (f"sh -c 'test -r {remote} || exit 2; timeout {seconds} tail -n +1 -f {remote}; "
                   'code=$?; case "$code" in 124|137|143) exit 124;; *) exit "$code";; esac' + "'")
        with subprocess.Popen(
            ["ssh", "-T", "-o", "BatchMode=yes", "-o", "ConnectTimeout=5", host, command],
            stdout=subprocess.PIPE, text=True, encoding="utf-8",
        ) as reader:
            watchdog = Timer(seconds + 10, reader.kill)
            watchdog.daemon = True
            watchdog.start()
            pending = False
            try:
                for event in forecasts(reader.stdout):
                    at = event.get("at")
                    if at and datetime.fromisoformat(at) < started:
                        continue  # Older records initialise the model.
                    if event["event"] in {"result", "expired", "pending_at_end"} and not pending:
                        continue
                    record(event)
                    pending = event["event"] == "forecast"
                status = reader.wait()
                elapsed = (datetime.now(timezone.utc) - started).total_seconds()
                if status != 0 and not (status in {124, 137, 143} and elapsed >= seconds):
                    raise RuntimeError(f"SSH capture follow exited {status}")
                record({"event": "end"})
            finally:
                watchdog.cancel()
                if reader.poll() is None:
                    reader.kill()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("host")
    parser.add_argument("seconds", type=int)
    args = parser.parse_args()
    follow(args.host, args.seconds)
