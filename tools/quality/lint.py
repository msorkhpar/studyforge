"""Ruling 78's lint notice: what the linter said, or that nobody was there to ask.

**What it does.** Reports the repository's **lint state** as a line the floor
prints and never counts — the linter's version and verdict where one is
installed, and, where none is, the fact that no lint signal exists in this run
at all. ⛔ It is a NOTICE, never a check: it cannot fail a build, and the exit
code of `python3 -m tools.quality` is identical with it and without it.

**How you use it.** `lint_notice(root)` is registered in `tools.quality.NOTICES`
and prints above `quality floor:`. Nothing else calls it.

**Depends on.** `json`, `re`, `shutil` and `subprocess` — the standard library,
and ⛔ **never ruff**. Absence is detected with `shutil.which`; a tool that is
not there is never imported, never required, and never installed on anybody's
behalf.

## ⛔ Why a notice and not a check (Rulings 77 and 78)

⚠️ **The defect this closes is silence, not the split.** `quality floor: clean`
means *the standard-library floor passed*. It has never meant *lint-clean*, and
until this module nothing in that output said so — so three agents in one wave
read a green floor as a lint verdict, and one of them shipped four `D401`
errors under it.

⛔ **Ruling 77 forbids the obvious fix.** `check_style` may not shell out to
ruff, because that would make the floor's **exit code** depend on whether
somebody ran `pip install` — and *"a check that can be skipped is a check that
will be"* (`style.py`'s own contract). The floor stays standard-library-only.

⭐ **The trick that makes both hold at once: a notice reporting a tool's absence
does not depend on that tool.** Nothing here is required for the floor to reach
a verdict, so nothing here can weaken one. ⭐ The shape the ruling names is an
absence notice that says *"this is not a failure"* in the same breath as it
names what is missing, and exits 0.

⚠️ **Enforcement stays in `tests/test_repository.py`**, which fails the build
where ruff exists. ⭐ **This notice supplies visibility of absence; that test
supplies enforcement of presence.** Neither closes the hole alone, and the
measurement that proves it is the CTO's `SF-12` sweep: a mutant that passes all
2923 tests and is killed only by `ruff F401`, by a gate that was skipping.

## ⛔ Absence has to be as loud as a finding, without being one

⚠️ A notice that said nothing when the tool was missing would reproduce exactly
the defect Ruling 78 exists to close — the reader would still have `quality
floor: clean` and no way to know that half the instrument was switched off. So
the absent line is the **longest** of the three: it names both commands that
did not run, the two gates that skipped, the install, and the image.

## ⚠️ What is deliberately never printed

⛔ **No path ruff reports.** `--output-format=json` carries an **absolute**
`filename` for every finding, which on a contributor's machine contains their
home directory (R7). Counts and rule codes are printed; filenames are counted
and dropped. The same reasoning drops stderr on the unrunnable path — an exit
code cannot leak a path and a diagnostic can.

⛔ **`--no-cache` on both invocations.** A notice that made the floor write
`.ruff_cache/` into the tree it is reporting on would be changing its subject
to describe it.
"""

from __future__ import annotations

import json
import re
import shutil
import subprocess
from pathlib import Path

#: The linter this reports on. ⚠️ Named once: `pyproject.toml`'s `lint` extra,
#: `docker/dev/requirements.txt` and `tests/test_repository.py` all mean this
#: tool, and a second spelling here would let them drift apart silently.
TOOL = "ruff"

#: What is run, and what a reader is told was run. ⛔ The displayed form must
#: stay the command a contributor can paste; the argument list carries the
#: machine-readable and cache-suppressing flags that would only be noise in a
#: report.
CHECK_ARGS = ("check", "--no-cache", "--output-format=json", ".")
CHECK_SHOWN = "ruff check ."
FORMAT_ARGS = ("format", "--no-cache", "--check", ".")
FORMAT_SHOWN = "ruff format --check ."

#: Where a reader goes to obtain the missing signal, in both forms. ⛔ The image
#: is named second and is the one that reproduces: R15's pinned environment is
#: what makes a lint result attributable to a version.
INSTALL = "pip install -e '.[lint]'"
IMAGE = "docker/dev/check"

#: The module that *enforces* what this only reports (Ruling 78). Named in the
#: absent line because the two gates there are what skipped.
GATES = "tests/test_repository.py"

#: Seconds before an invocation is abandoned. ⚠️ A notice may never hang the
#: floor: the floor's job is to reach a verdict, and this cannot be allowed to
#: stop it reaching one.
TIMEOUT = 120

#: How many distinct rule codes a dirty line names before it stops listing.
#: ⚠️ The codes are the useful half — `F401` and `D401` are what tell a reader
#: which class of defect is loose — but a wall of forty is not a notice.
MAX_CODES = 6

_WOULD_REFORMAT = re.compile(r"(\d+) files? would be reformatted")
_ALREADY_FORMATTED = re.compile(r"(\d+) files? already formatted")


class _Unrunnable(Exception):
    """The tool is on the path and could not be made to answer.

    ⛔ Carries a reason that is safe to print: an exit code, a timeout or a
    class of failure — ⚠️ **never** a captured stream, which can contain an
    absolute path (R7).
    """


def _which(name: str) -> str | None:
    """Return the absolute path to `name`, or None when it is not installed.

    ⛔ Wrapped rather than called inline so a test can make the tool absent on
    a machine where it is installed, and present on one where it is not. Both
    directions are needed: absence is the state this module exists for, and it
    is the state a container can never reproduce.
    """
    return shutil.which(name)


def _run(executable: str, args: tuple[str, ...], root: Path) -> subprocess.CompletedProcess[str]:
    """Run `executable` with `args` in `root`, or raise `_Unrunnable`."""
    try:
        return subprocess.run(
            [executable, *args],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=TIMEOUT,
            check=False,
        )
    except subprocess.TimeoutExpired as expired:
        raise _Unrunnable(f"it did not finish within {TIMEOUT}s") from expired
    except OSError as error:
        raise _Unrunnable(f"the process could not be started ({type(error).__name__})") from error


def _version(executable: str) -> str:
    """Return the linter's own version string, or a stated inability to read one.

    ⭐ Ruling 79 asks a review to state the version that produced its lint
    line, so the notice a review copies from has to carry it.
    """
    try:
        result = _run(executable, ("--version",), Path("."))
    except _Unrunnable:
        return "of unknown version"
    words = result.stdout.split()
    return words[-1] if result.returncode == 0 and words else "of unknown version"


def _check_state(executable: str, root: Path) -> tuple[int, int, list[str]]:
    """Return `(findings, files, codes)` from a lint run over `root`.

    ⛔ Filenames are counted and discarded, never returned: ruff reports them
    absolutely, and an absolute path in a build log carries the user's home
    directory (R7).
    """
    result = _run(executable, CHECK_ARGS, root)
    if result.returncode not in (0, 1):
        raise _Unrunnable(f"it exited {result.returncode}")
    try:
        reported = json.loads(result.stdout or "[]")
    except json.JSONDecodeError as error:
        raise _Unrunnable("its report could not be parsed") from error

    files = {entry.get("filename") for entry in reported}
    codes = sorted({str(entry.get("code") or entry.get("name") or "?") for entry in reported})
    return len(reported), len(files), codes


def _format_state(executable: str, root: Path) -> tuple[int, int]:
    """Return `(would_reformat, already_formatted)` from a format check over `root`.

    ⚠️ Read from the summary line rather than by counting the per-file diffs:
    the diff rendering is presentation and has changed between versions, while
    the summary is the sentence the tool writes for a human to read.
    """
    result = _run(executable, FORMAT_ARGS, root)
    if result.returncode not in (0, 1):
        raise _Unrunnable(f"its formatter exited {result.returncode}")
    return _count(_WOULD_REFORMAT, result.stdout), _count(_ALREADY_FORMATTED, result.stdout)


def _count(pattern: re.Pattern[str], text: str) -> int:
    """Return the number `pattern` reports in `text`, or 0 when it says nothing."""
    match = pattern.search(text)
    return int(match.group(1)) if match else 0


def _absent() -> str:
    """Build the line for a run with no linter — the reason this module exists."""
    return (
        f"lint: {TOOL} is NOT installed, so this run carries no lint signal at all. "
        f"`{CHECK_SHOWN}` and `{FORMAT_SHOWN}` did not run, and the two gates in "
        f"{GATES} skipped rather than passed. `quality floor: clean` reports the "
        f"standard-library floor and has never meant lint-clean (Ruling 78). Get the "
        f"signal with `{INSTALL}`, or run the pinned environment: `{IMAGE}`. This is "
        f"not a failure — Ruling 77 keeps the floor standard-library-only, so absence "
        f"is reported here and never punished."
    )


def _unrunnable(version: str, reason: str) -> str:
    """Build the fourth state's line: installed, and it would not answer."""
    return (
        f"lint: {TOOL} {version} is installed and could not be run — {reason}. This run "
        f"carries no lint signal; run `{CHECK_SHOWN}` and `{FORMAT_SHOWN}` yourself to "
        f"see why, or use `{IMAGE}`. This is not a failure."
    )


def _check_phrase(findings: int, files: int, codes: list[str]) -> str:
    """Build the lint half of a present line, clean or dirty."""
    if findings == 0:
        return f"`{CHECK_SHOWN}` clean"
    listed = ", ".join(codes[:MAX_CODES])
    if len(codes) > MAX_CODES:
        listed += f", and {len(codes) - MAX_CODES} more"
    return f"`{CHECK_SHOWN}` {findings} finding(s) in {files} file(s) ({listed})"


def _format_phrase(would: int, already: int) -> str:
    """Build the format half of a present line, clean or dirty."""
    if would == 0:
        return f"`{FORMAT_SHOWN}` clean ({already} file(s) already formatted)"
    return f"`{FORMAT_SHOWN}` {would} file(s) would be reformatted"


def _present(version: str, check: tuple[int, int, list[str]], fmt: tuple[int, int]) -> str:
    """Build the line for a run that actually has a lint verdict to report."""
    head = f"lint: {TOOL} {version} — {_check_phrase(*check)}; {_format_phrase(*fmt)}."
    if check[0] == 0 and fmt[0] == 0:
        return f"{head} This run carries a real lint signal."
    return (
        f"{head} Not a floor failure and not a floor pass: enforcement is in {GATES}, "
        f"which fails the build on these wherever {TOOL} is installed (Ruling 78)."
    )


def lint_notice(root: Path) -> list[str]:
    """Report the lint state at `root` as one line that is never a finding.

    ⛔ Returns a line in every state, including the state where there is
    nothing to report, because *"nothing was printed"* and *"there was nothing
    to say"* are indistinguishable to a reader — which is the whole of the
    defect Ruling 78 closes.
    """
    executable = _which(TOOL)
    if executable is None:
        return [_absent()]
    version = _version(executable)
    try:
        return [_present(version, _check_state(executable, root), _format_state(executable, root))]
    except _Unrunnable as reason:
        return [_unrunnable(version, str(reason))]
