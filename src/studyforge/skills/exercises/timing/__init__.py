"""A lint for short absolute waits in a practice's tests.

**What it does.** Reads practice test files and reports every sleep, delay, await or
timeout whose literal duration is below `FLOOR_MS` milliseconds (1000). A concurrency
practice whose pass condition is a sub-second wait passes or fails with the machine's
load, not with the reader's code; a latch or a join with a generous timeout does not.

**How you use it.**

    from studyforge.skills.exercises.timing import FLOOR_MS, scan_text, scan_tree

    scan_text("Thread.sleep(200);", "Race.java")   # [Short(line=1, wait_ms=200, ...)]
    scan_tree(practice_root)                       # every finding under it, in path order

    python3 -m studyforge.skills.exercises.timing PATH...        # warns, exits 0
    python3 -m studyforge.skills.exercises.timing --strict PATH  # exits 1 on a finding

**Depends on.** `re` and `pathlib`; standard library only.

## ⭐ WARNING-ONLY BY DEFAULT

A finding is a prompt to use a latch, not a verdict: nothing in the framework calls this
lint, and the command exits 0 unless `--strict` is given, so no existing course changes.
A line carrying `timing: ok` is skipped, for the rare wait that is not a pass condition.
"""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path

#: A literal wait below this many milliseconds is reported.
FLOOR_MS = 1000

#: The test-file suffixes read, and the ones whose bare numbers are seconds.
SUFFIXES = (".java", ".kt", ".py", ".js", ".mjs", ".ts")
SECONDS_SUFFIXES = (".py",)

#: Millisecond multipliers for `TimeUnit.X` and `ChronoUnit`-style names.
UNITS = {
    "NANOSECONDS": 1e-6,
    "MICROSECONDS": 1e-3,
    "MILLISECONDS": 1,
    "SECONDS": 1000,
    "MINUTES": 60_000,
}

_NUM = r"(\d+(?:\.\d+)?)"
#: `sleep(N)`, `delay(N)`, `withTimeout(N)`, `setTimeout(f, N)`, `Duration.ofMillis(N)`, `timeout=N`.
_BARE = re.compile(
    rf"\b(?:sleep|delay|withTimeout|withTimeoutOrNull|ofMillis|waitFor)\s*\(\s*{_NUM}\b"
    rf"|\bsetTimeout\s*\(.*,\s*{_NUM}\s*\)"
    rf"|\btimeout\s*[=:]\s*{_NUM}\b"
)
#: `await(N, TimeUnit.X)`, `join(N, ...)`, `tryAcquire`, `awaitTermination`, `poll`, `get`.
_UNITED = re.compile(
    rf"\b(?:await|awaitTermination|tryAcquire|poll|offer|get|join)\s*\(\s*{_NUM}\s*,\s*"
    rf"(?:java\.util\.concurrent\.)?TimeUnit\.(\w+)"
)
_KOTLIN_UNIT = re.compile(rf"\b{_NUM}\.(milliseconds|millis|seconds)\b")


@dataclass(frozen=True, slots=True)
class Short:
    """One wait below the floor: the file, the line, and the milliseconds it waits."""

    file: str
    line: int
    wait_ms: float
    text: str


def scan_text(text: str, name: str) -> list[Short]:
    """Return every literal wait below `FLOOR_MS` in `text`, which is the file `name`."""
    seconds = name.endswith(SECONDS_SUFFIXES)
    found: list[Short] = []
    for number, line in enumerate(text.splitlines(), start=1):
        if "timing: ok" in line:
            continue
        waits = []
        for match in _BARE.finditer(line):
            value = float(next(group for group in match.groups() if group))
            is_seconds = seconds and not re.search(r"ofMillis|setTimeout", match.group())
            waits.append(value * (1000 if is_seconds else 1))
        for match in _UNITED.finditer(line):
            waits.append(float(match.group(1)) * UNITS.get(match.group(2), float("inf")))
        for match in _KOTLIN_UNIT.finditer(line):
            waits.append(float(match.group(1)) * (1000 if match.group(2) == "seconds" else 1))
        found += [
            Short(name, number, wait, line.strip()) for wait in waits if 0 < wait < FLOOR_MS
        ]
    return found


def scan_tree(root: Path | str) -> list[Short]:
    """Return every finding under `root` (a file or a folder), in path order."""
    base = Path(root)
    files = [base] if base.is_file() else sorted(p for p in base.rglob("*") if p.is_file())
    found: list[Short] = []
    for path in files:
        if path.suffix in SUFFIXES:
            text = path.read_text(encoding="utf-8", errors="replace")
            found += scan_text(text, path.as_posix())
    return found


def main(argv: list[str] | None = None) -> int:
    """Print each finding; return 1 only under `--strict` with a finding, otherwise 0."""
    parser = argparse.ArgumentParser(prog="python3 -m studyforge.skills.exercises.timing")
    parser.add_argument("paths", nargs="+")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)
    found = [one for path in args.paths for one in scan_tree(path)]
    for one in found:
        print(
            f"warning: {one.file}:{one.line}: waits {one.wait_ms:g} ms (< {FLOOR_MS}); "
            f"use a latch with a generous timeout: {one.text}"
        )
    print(f"{len(found)} short wait(s)")
    return 1 if found and args.strict else 0

