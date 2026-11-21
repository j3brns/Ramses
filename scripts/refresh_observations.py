"""Create sanitised observed fixtures from a ramses_cc packet-cache export.

Use stdin for a direct SSH pipe; raw input is never written to the repository.
"""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from typing import Any


OBSERVED_CODES = {"1F09", "2309", "3150", "30C9", "1060", "3EF0"}
PAYLOAD_FIELDS = {
    "1F09": ("remaining_seconds", "seqx_num", "zone_index"),
    "2309": ("setpoint", "seqx_num", "zone_index"),
    "3150": ("heat_demand", "zone_index"),
    "30C9": ("temperature", "seqx_num", "zone_index"),
    "1060": ("battery_level", "battery_low", "zone_index"),
    "3EF0": ("modulation_level",),
}


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


def build_samples(payload: dict[str, Any]) -> dict[str, Any]:
    """Return sorted, sanitised protocol samples from a cache snapshot."""
    packets = payload["data"]["client_state"]["packets"].values()
    samples: list[dict[str, Any]] = []
    for packet in packets:
        code = packet.get("code")
        if code not in OBSERVED_CODES:
            continue
        packet_payload = packet.get("payload", {})
        values = {
            field: packet_payload[field]
            for field in PAYLOAD_FIELDS[code]
            if field in packet_payload
        }
        sample = {"code": code, "source": short_id(packet.get("src")), "values": values}
        destination = short_id(packet.get("dst"))
        if destination:
            sample["destination"] = destination
        samples.append(sample)
    samples.sort(key=lambda item: (item["code"], item["source"] or "", item.get("destination", ""), str(item["values"])))
    return {
        "format": 1,
        "description": "Sanitised RAMSES-II examples derived from ramses_cc packet cache",
        "snapshot": True,
        "samples": samples,
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", default="-", help="packet-cache JSON file, or - for stdin")
    parser.add_argument("--output", default="data/observed/topology.json")
    parser.add_argument("--samples-output", default="data/observed/samples.json")
    args = parser.parse_args()
    raw = __import__("sys").stdin.read() if args.input == "-" else Path(args.input).read_text(encoding="utf-8")
    payload = json.loads(raw)
    observed = build_topology(payload)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(observed, indent=2) + "\n", encoding="utf-8")
    samples_output = Path(args.samples_output)
    samples_output.parent.mkdir(parents=True, exist_ok=True)
    samples_output.write_text(json.dumps(build_samples(payload), indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
