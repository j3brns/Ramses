"""Require an adversarial review note beside each reviewable change."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REQUIRED_HEADINGS = ("# Adversarial review", "## Scope", "## Failure modes", "## Evidence and tests", "## Decision", "## Rollback")
REVIEWABLE_PREFIXES = ("src/", "scripts/", "custom_components/", "data/observed/", "data/scenarios/", "target-system/", ".github/")
REVIEWABLE_FILES = {".gitlab-ci.yml", "pyproject.toml"}


def requires_review(paths: list[str]) -> bool:
    return any(path.startswith(REVIEWABLE_PREFIXES) or path in REVIEWABLE_FILES for path in paths)


def review_errors(review_texts: dict[str, str]) -> list[str]:
    if not review_texts:
        return ["reviewable change requires a changed file under docs/reviews/"]
    errors = []
    for path, text in review_texts.items():
        missing = [heading for heading in REQUIRED_HEADINGS if heading not in text]
        if missing:
            errors.append(f"{path}: missing " + ", ".join(missing))
    return errors


def git_lines(arguments: list[str]) -> list[str]:
    return subprocess.check_output(["git", *arguments], text=True).splitlines()


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true", help="validate the index before commit")
    parser.add_argument("--working", action="store_true", help="validate the current working tree")
    args = parser.parse_args()
    if args.staged:
        changed = git_lines(["diff", "--cached", "--name-only"])
    elif args.working:
        changed = git_lines(["diff", "--name-only", "HEAD"]) + git_lines(["ls-files", "--others", "--exclude-standard"])
    else:
        try:
            changed = git_lines(["diff", "--name-only", "HEAD^", "HEAD"])
        except subprocess.CalledProcessError:
            changed = []  # Initial commit: there is no parent revision to review.
    if not requires_review(changed):
        return 0
    review_paths = [path for path in changed if path.startswith("docs/reviews/") and path.endswith(".md")]
    texts: dict[str, str] = {}
    for path in review_paths:
        if args.staged:
            texts[path] = subprocess.check_output(["git", "show", f":{path}"], text=True)
        else:
            texts[path] = Path(path).read_text(encoding="utf-8")
    errors = review_errors(texts)
    if errors:
        print("Adversarial review gate failed:\n- " + "\n- ".join(errors))
        return 1
    print("Adversarial review gate passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
