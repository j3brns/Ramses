"""Select one short Kitchen candidate from a bounded passive RX time window."""

from __future__ import annotations

import argparse
import json
from datetime import timedelta
from pathlib import Path

from ramses_twin.temporal_capture import select_temporal_kitchen_window


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--duration-seconds", type=int, default=21600)
    parser.add_argument("--max-events", type=int, default=10000)
    parser.add_argument("--max-bytes", type=int, default=2_097_152)
    parser.add_argument("--before", type=int, default=12)
    parser.add_argument("--after", type=int, default=12)
    args = parser.parse_args()

    size = args.input.stat().st_size
    if size > args.max_bytes:
        raise SystemExit(f"input exceeds byte cap: {size} > {args.max_bytes}")
    raw_events = [json.loads(line) for line in args.input.read_text(encoding="utf-8").splitlines() if line.strip()]
    result = select_temporal_kitchen_window(
        raw_events,
        duration=timedelta(seconds=args.duration_seconds),
        max_events=args.max_events,
        before=args.before,
        after=args.after,
    )
    if result.scenario is None:
        print(json.dumps({"candidate": None, "observed": result.observed, "discarded": result.discarded, "stop_reason": result.stop_reason}))
        return
    args.output.parent.mkdir(parents=True, exist_ok=True)
    temporary = args.output.with_suffix(f"{args.output.suffix}.tmp")
    temporary.write_text(json.dumps(result.scenario, indent=2) + "\n", encoding="utf-8")
    temporary.replace(args.output)
    print(json.dumps({"candidate": result.transition.as_dict(), "observed": result.observed, "discarded": result.discarded, "stop_reason": result.stop_reason, "output_written": True}))


if __name__ == "__main__":
    main()
