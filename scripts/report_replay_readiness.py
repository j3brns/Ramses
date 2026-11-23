"""Report observed-scenario replay coverage without treating a baseline as behaviour."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from ramses_twin.replay_readiness import replay_readiness


def _documents(directory: Path) -> tuple[dict[str, dict[str, object]], dict[str, dict[str, object]]]:
    scenarios: dict[str, dict[str, object]] = {}
    manifests: dict[str, dict[str, object]] = {}
    for path in sorted(directory.glob("*.json")):
        document = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(document, dict):
            raise ValueError(f"{path} must contain a JSON object")
        if document.get("kind") == "ordered-rx-scenario":
            name = document.get("name")
            if not isinstance(name, str) or not name:
                raise ValueError(f"{path} scenario needs a name")
            scenarios[name] = document
        elif document.get("kind") == "scenario-qualification":
            name = document.get("scenario")
            if not isinstance(name, str) or not name:
                raise ValueError(f"{path} qualification needs a scenario")
            manifests[name] = document
    return scenarios, manifests


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--scenarios", type=Path, default=Path("data/scenarios"))
    parser.add_argument("--require-ready", action="store_true", help="exit 1 until all required behaviours qualify")
    args = parser.parse_args()

    scenarios, manifests = _documents(args.scenarios)
    report = replay_readiness(scenarios, manifests)
    print(json.dumps(report.as_dict(), indent=2, sort_keys=True))
    if args.require_ready and not report.ready:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
