"""Small dependency-free guard against committing obvious credentials."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path


PATTERNS = (
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"gh[pousr]_[A-Za-z0-9_]{20,}"),
    re.compile(r"github_pat_[A-Za-z0-9_]{20,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)(password|api[_-]?key|access[_-]?token)\s*[:=]\s*[\"'][^\"']{8,}"),
)


def main() -> int:
    files = subprocess.check_output(["git", "ls-files"], text=True).splitlines()
    hits: list[str] = []
    for filename in files:
        path = Path(filename)
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        for line_number, line in enumerate(text.splitlines(), start=1):
            if any(pattern.search(line) for pattern in PATTERNS):
                hits.append(f"{filename}:{line_number}: possible secret")
    if hits:
        print("\n".join(hits))
        return 1
    print("Secret scan passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
