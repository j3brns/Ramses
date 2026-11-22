"""Extract one bounded Kitchen transition context from passive RX NDJSON."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from ramses_twin.kitchen_watch import select_kitchen_watch_window


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", default="-", help="raw RX NDJSON file, or - for stdin")
    parser.add_argument("--output", type=Path, required=True, help="replacement candidate scenario path")
    parser.add_argument("--max-events", type=int, default=500)
    parser.add_argument("--before", type=int, default=12)
    parser.add_argument("--after", type=int, default=12)
    args = parser.parse_args()

    source = sys.stdin if args.input == "-" else Path(args.input).open(encoding="utf-8")
    try:
        raw_events = [json.loads(line) for line in source if line.strip()]
    finally:
        if source is not sys.stdin:
            source.close()
    result = select_kitchen_watch_window(
        raw_events,
        max_events=args.max_events,
        before=args.before,
        after=args.after,
    )
    if result is None:
        print(json.dumps({"candidate": None, "output_written": False}))
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(f"{args.output.suffix}.tmp")
    temporary.write_text(json.dumps(result.scenario, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({"candidate": result.transition.as_dict(), "output_written": True}))


if __name__ == "__main__":
    main()
