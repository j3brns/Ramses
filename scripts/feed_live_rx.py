"""Normalise a local MQTT subscriber stream into bounded, passive RX NDJSON.

The feeder opens no broker connection. A locally authenticated subscriber may
pipe JSON lines into stdin; this program accepts only gateway RX envelopes and
writes a bounded replacement stream to stdout or an explicit local file.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from ramses_twin.evidence import normalise_rx_event


def feed(stream: TextIO, topic_root: str, max_events: int) -> tuple[list[dict[str, str]], int]:
    """Validate ordered passive RX events and retain at most ``max_events``."""
    if max_events < 1:
        raise ValueError("max-events must be positive")
    retained: list[dict[str, str]] = []
    discarded = 0
    for line_number, line in enumerate(stream, start=1):
        if not line.strip():
            continue
        try:
            event = normalise_rx_event(json.loads(line), topic_root)
        except (json.JSONDecodeError, ValueError) as error:
            raise ValueError(f"line {line_number}: {error}") from error
        if len(retained) < max_events:
            retained.append(event)
        else:
            discarded += 1
    return retained, discarded


def write_ndjson(events: list[dict[str, str]], output: TextIO) -> None:
    for event in events:
        output.write(json.dumps(event, separators=(",", ":")) + "\n")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="NDJSON file, or - for stdin")
    parser.add_argument("--output", default="-", help="NDJSON file to replace, or - for stdout")
    parser.add_argument("--max-events", type=int, default=500)
    parser.add_argument("--topic-root", default="RAMSES/GATEWAY")
    args = parser.parse_args()

    source = sys.stdin if args.input == "-" else Path(args.input).open(encoding="utf-8")
    try:
        events, discarded = feed(source, args.topic_root, args.max_events)
    except ValueError as error:
        raise SystemExit(str(error)) from error
    finally:
        if source is not sys.stdin:
            source.close()

    if args.output == "-":
        write_ndjson(events, sys.stdout)
    else:
        target = Path(args.output)
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary = target.with_suffix(f"{target.suffix}.tmp")
        with temporary.open("w", encoding="utf-8", newline="\n") as output:
            write_ndjson(events, output)
        temporary.replace(target)
    print(f"retained={len(events)} discarded={discarded}", file=sys.stderr)


if __name__ == "__main__":
    main()
