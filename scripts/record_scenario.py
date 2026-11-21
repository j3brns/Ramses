"""Write a bounded, ordered RAMSES gateway-RX scenario from NDJSON stdin.

Input is one JSON object per line, either the gateway envelope plus ``topic``
or ``{"topic": ..., "payload": {"msg": ..., "ts": ...}}``. The script is
transport-neutral: a local MQTT client may feed it, but it opens no network
connection itself.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ramses_twin.evidence import normalise_rx_event, scenario_document


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("name", help="lower-case scenario name, for example kitchen-schedule-change")
    parser.add_argument("--output", help="defaults to data/scenarios/<name>.json")
    parser.add_argument("--max-events", type=int, default=500)
    parser.add_argument("--topic-root", default="RAMSES/GATEWAY")
    args = parser.parse_args()
    events = []
    discarded = 0
    for line_number, line in enumerate(sys.stdin, start=1):
        if not line.strip():
            continue
        try:
            event = normalise_rx_event(json.loads(line), args.topic_root)
        except (json.JSONDecodeError, ValueError) as error:
            raise SystemExit(f"line {line_number}: {error}") from error
        if len(events) < args.max_events:
            events.append(event)
        else:
            discarded += 1
    document = scenario_document(args.name, events, args.max_events)
    document["retention"]["discarded"] = discarded
    output = Path(args.output or f"data/scenarios/{args.name}.json")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
