"""Render canonical Markdown help into the undeployed Test View blueprint.

The generated content is deliberately stored inside the version-controlled
blueprint so it can be reviewed before a separate Home Assistant deployment.
It has no Home Assistant, MQTT, RF, or filesystem effects beyond replacing the
marked generated region when invoked without ``--check``.
"""

from __future__ import annotations

import argparse
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
GUIDE = ROOT / "docs" / "user-guide.md"
BLUEPRINT = ROOT / "target-system" / "ramses-test-dashboard.yaml"
START = "              <!-- HELP-GENERATED:START -->"
END = "              <!-- HELP-GENERATED:END -->"
INDENT = "              "


def guide_body(source: str) -> str:
    """Return Markdown after optional YAML front matter, with stable links."""
    lines = source.splitlines()
    if lines[:1] == ["---"]:
        try:
            closing = lines.index("---", 1)
        except ValueError as error:
            raise ValueError("user guide front matter is not closed") from error
        lines = lines[closing + 1 :]
    return "\n".join(lines).strip()


def render_region(guide: str) -> str:
    notice = (
        "This is generated test-only help from `docs/user-guide.md`. "
        "It does not control the live heating system."
    )
    content = f"{START}\n{INDENT}{notice}\n\n"
    content += "\n".join(f"{INDENT}{line}" if line else "" for line in guide.splitlines())
    return f"{content}\n{END}"


def replace_region(blueprint: str, replacement: str) -> str:
    try:
        before, tail = blueprint.split(START, 1)
        _, after = tail.split(END, 1)
    except ValueError as error:
        raise ValueError("blueprint must contain exactly one generated Help region") from error
    if START in tail or END in after:
        raise ValueError("blueprint must contain exactly one generated Help region")
    return f"{before}{replacement}{after}"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail when generated help is stale")
    args = parser.parse_args()

    expected = replace_region(BLUEPRINT.read_text(encoding="utf-8"), render_region(guide_body(GUIDE.read_text(encoding="utf-8"))))
    current = BLUEPRINT.read_text(encoding="utf-8")
    if args.check:
        if current != expected:
            print("Ramses Test Help is stale; run python scripts/render_lovelace_help.py")
            return 1
        print("Ramses Test Help is current")
        return 0
    BLUEPRINT.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Rendered {BLUEPRINT.relative_to(ROOT)} from {GUIDE.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
