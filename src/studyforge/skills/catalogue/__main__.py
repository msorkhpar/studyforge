"""`python3 -m studyforge.skills.catalogue` prints the catalogue, then the line a log records."""

from __future__ import annotations

import sys

from studyforge.skills.catalogue import read_line, text


def main(argv: list[str]) -> int:
    """Print the catalogue and the read line; `--line` prints only the line."""
    if argv not in ([], ["--line"]):
        print("usage: python3 -m studyforge.skills.catalogue [--line]", file=sys.stderr)
        return 2
    if not argv:
        sys.stdout.write(text())
        print()
        print("Record this line in .studyforge/findings.md, under its title:")
    print(read_line())
    return 0


if __name__ == "__main__":  # pragma: no cover - exercised as a subprocess
    sys.exit(main(sys.argv[1:]))
