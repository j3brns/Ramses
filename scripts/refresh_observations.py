"""Create a sanitised topology fixture from a ramses_cc packet-cache export.

Use stdin for a direct SSH pipe; raw input is never written to the repository.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


def short_id(device_id: str | None) -> str | None:
    return device_id[-3:] if device_id and ":" in device_id else None


def build_topology(payload: dict[str, Any]) -> dict[str, Any]:
    packets = payload["data"]["client_state"]["packets"].values()
    zones: dict[tuple[str, str], set[str]] = defaultdict(set)
    for packet in packets:
        if packet.get("code") not in {"2309", "3150"}:
            continue
        source = packet.get("src", "")
        destination = packet.get("dst", "")
        zone = packet.get("payload", {}).get("zone_index")
        if not (source.startswith("04:") and destination.startswith("12:") and zone):
            continue
        zones[(short_id(destination), zone)].add(short_id(source))
    return {
        "format": 1,
        "description": "Sanitised zone membership derived from ramses_cc packet cache",
        "zones": [
            {"controller": controller, "zone": zone, "trvs": sorted(trvs)}
            for (controller, zone), trvs in sorted(zones.items())
        ],
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="-", help="packet-cache JSON file, or - for stdin")
    parser.add_argument("--output", default="data/observed/topology.json")
    args = parser.parse_args()
    raw = __import__("sys").stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
    observed = build_topology(json.loads(raw))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(observed, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
