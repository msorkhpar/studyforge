"""The command line of the personal-data gate: `python -m studyforge.archive.scrub check PATH...`.

Reads each file (a directory is walked, `.git` skipped, binary files skipped), prints
`path:line: <shape>` for every finding and never the matched text, and exits 1 when
there is any finding, 0 when there is none, 2 on a usage error. A course's checker
calls this, or `studyforge.archive.scrub.findings`, so there is one pattern set.
"""

from __future__ import annotations

import sys
from collections.abc import Iterator, Sequence
from pathlib import Path

from studyforge.archive.scrub import findings

SKIPPED_DIRECTORIES = frozenset({".git"})


def _files(path: Path) -> Iterator[Path]:
    if path.is_file():
        yield path
        return
    for one in sorted(path.rglob("*")):
        if one.is_file() and not SKIPPED_DIRECTORIES.intersection(one.relative_to(path).parts):
            yield one


def check(paths: Sequence[Path]) -> list[tuple[str, str]]:
    """Every `(path:line, shape)` finding in the files under `paths`."""
    found: list[tuple[str, str]] = []
    for path in paths:
        for one in _files(Path(path)):
            try:
                text = one.read_text(encoding="utf-8")
            except (UnicodeDecodeError, OSError):
                continue
            found.extend(findings(text, str(one)))
    return found


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) < 2 or args[0] != "check":
        print("usage: python -m studyforge.archive.scrub check PATH...", file=sys.stderr)
        return 2
    missing = [one for one in args[1:] if not Path(one).exists()]
    if missing:
        print(f"no such path: {missing[0]}", file=sys.stderr)
        return 2
    found = check([Path(one) for one in args[1:]])
    for where, name in found:
        print(f"{where}: {name}")
    return 1 if found else 0
