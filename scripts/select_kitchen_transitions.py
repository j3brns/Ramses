"""Print candidate Kitchen controller-target transitions from one scenario."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ramses_twin.kitchen import kitchen_setpoint_transitions


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("scenario", type=Path)
    args = parser.parse_args()
    scenario = json.loads(args.scenario.read_text(encoding="utf-8"))
    candidates = [candidate.as_dict() for candidate in kitchen_setpoint_transitions(scenario)]
    print(json.dumps({"candidates": candidates}, indent=2))


if __name__ == "__main__":
    main()
