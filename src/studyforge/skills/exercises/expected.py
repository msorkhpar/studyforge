r"""A project practice's expected-output check: one test that runs the entry point and diffs it.

**What it does.** `check_source(expected, entry, depth=)` writes the text of one pytest module that
runs the project's entry point, reads what it printed, and compares it line by line with the
expected report: every number within the stated tolerances, every other character exactly.
⭐ When they differ, the assertion says which lines differ and why, then shows a unified diff, so
a reader sees what their program printed against what it should have.

**How you use it.**

    text = check_source(Expected("expected/report.txt", abs_tol=0.005), "main.py", depth=1)
    # write it to tests/test_expected_output.py; its one test is CHECK_TEST

**Depends on.** The standard library only. ⛔ **So does the module it writes**: it runs in the
course's runner image, where this framework is not installed, so it imports nothing but the
standard library and names no path outside the workspace.

## ⭐ A NUMBER IS COMPARED AS A NUMBER, AND EVERYTHING ELSE AS TEXT

⚠️ An optimizer's report is the place two correct programs differ in the last digit: a solver's
objective, a sum of floats taken in another order. ⭐ So each line is cut at its numbers
(`NUMBER`), the text between them must match exactly, and each pair of numbers must be within
`abs_tol` or `rel_tol` of each other, as `math.isclose` reads the two. ⛔ Trailing spaces and
trailing blank lines are not compared, because an editor or a `print` adds them invisibly.

## ⛔ THE ENTRY POINT RUNS AS RUN RUNS IT

⭐ With the interpreter the tests run under and from the working directory the tests run from,
which is the directory Run starts the entry point in. ⛔ So a program that finds its data only
from one directory fails this check exactly where it would fail a reader's Run.
"""

from __future__ import annotations

from dataclasses import dataclass

#: The check's file, inside the project's tests folder, and the one test in it.
CHECK_FILE = "test_expected_output.py"
CHECK_TEST = "test_the_report_matches_the_expected_output"

#: What the check's case says to a reader when it fails, unless the manifest words it.
CHECK_SAYS = "the report the entry point prints matches the expected report"

#: How long the entry point may run, in seconds, before the check fails.
TIMEOUT = 120


@dataclass(frozen=True, slots=True)
class Expected:
    """The expected report: its workspace-relative path and the tolerances numbers are read with."""

    output: str
    abs_tol: float = 1e-6
    rel_tol: float = 1e-9


def check_source(expected: Expected, entry: str, *, depth: int) -> str:
    """Return the check module's text, for a test file `depth` folders below the workspace."""
    return _TEMPLATE.format(
        depth=depth,
        entry=repr(entry),
        output=repr(expected.output),
        abs_tol=repr(float(expected.abs_tol)),
        rel_tol=repr(float(expected.rel_tol)),
        timeout=TIMEOUT,
        test=CHECK_TEST,
    )


_TEMPLATE = '''"""The expected-output check, written by studyforge for this project. Read-only.

It runs the project's entry point and compares what it prints with the expected report: every
number within the tolerances below, every other character exactly.
"""

import difflib
import math
import re
import subprocess
import sys
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[{depth}]
ENTRY = {entry}
EXPECTED = {output}
ABS_TOL = {abs_tol}
REL_TOL = {rel_tol}
NUMBER = re.compile(r"[-+]?(?:\\d+\\.?\\d*|\\.\\d+)(?:[eE][-+]?\\d+)?")


def _lines(text):
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return lines


def _why(got, want):
    if NUMBER.split(got) != NUMBER.split(want):
        return "the text differs"
    for mine, theirs in zip(NUMBER.findall(got), NUMBER.findall(want)):
        if not math.isclose(float(mine), float(theirs), rel_tol=REL_TOL, abs_tol=ABS_TOL):
            return f"{{mine}} is not {{theirs}} within abs {{ABS_TOL:g}} or rel {{REL_TOL:g}}"
    return None


def {test}():
    try:
        done = subprocess.run(
            [sys.executable, str(WORKSPACE / ENTRY)],
            capture_output=True, text=True, timeout={timeout}, check=False,
        )
    except subprocess.TimeoutExpired:
        raise AssertionError(f"{{ENTRY}} printed no report within {timeout} seconds") from None
    assert done.returncode == 0, (
        f"{{ENTRY}} exited with {{done.returncode}} instead of printing a report:\\n"
        + done.stderr[-3000:]
    )
    got = _lines(done.stdout)
    want = _lines((WORKSPACE / EXPECTED).read_text(encoding="utf-8"))
    problems = [
        f"line {{number}}: {{why}}"
        for number, (mine, theirs) in enumerate(zip(got, want), start=1)
        if (why := _why(mine, theirs)) is not None
    ]
    if len(got) != len(want):
        problems.append(f"the report has {{len(got)}} lines and the expected one {{len(want)}}")
    diff = difflib.unified_diff(want, got, "expected report", "your report", lineterm="")
    assert not problems, (
        f"{{ENTRY}} printed a report that differs from {{EXPECTED}}:\\n"
        + "\\n".join(problems[:10])
        + "\\n\\n"
        + "\\n".join(diff)
    )
'''
