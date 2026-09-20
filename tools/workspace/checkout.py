r"""Whether a component's **checkout** carries work that exists on no ref.

**What it does.** Reads one checkout's working-tree state — an unfinished
merge, rebase, cherry-pick or revert, a conflicted path, a staged or a modified
tracked file, an untracked file git was never told to ignore — and returns one
finding per state, each **named**.

**How you use it.** `uncommitted(directory, run)` returns findings, empty when
the checkout is clean. `run` is a git runner with `tools.workspace.git`'s
signature.

**Depends on.** `git` on `PATH`, through the runner it is handed, and the
standard library.

## ⛔ Why this exists: a pin can only ever record a COMMIT

⚠️ **Measured 2026-09-20 (`W402`, and `TC-06/6` names it from the other side).**
A sibling component's checkout sat in an **abandoned conflicted merge** — a
merge head present, one path left unmerged, a whole task's files staged and
none committed — and `verify` read green throughout. ⭐ It compared that
component's `HEAD` to the pin and said nothing at all about the working tree,
so the component satisfied R18 **while carrying work that exists on no ref**.

⛔ **A pin records a commit, and a commit cannot carry a working tree.** So
*"this component is at the commit recorded"* is only a reproducibility claim
when the checkout holds nothing besides that commit — ⭐ which is a second
question, asked here, rather than an assumption folded silently into the first.

## ⭐ Why each state is named separately, and never folded into one word

⚠️ *"dirty"* is four different repairs. An unfinished merge is finished or
aborted; a conflicted path is resolved; a staged file is committed or reset; an
untracked file is added or ignored. ⛔ **A single word would make the reader go
and look**, which is exactly the step that did not happen in the incident above.

## ⚠️ Untracked-but-not-ignored is dirt; ignored is not — decided here

⭐ **Ignored files are not dirt**: `.scratch/`, `__pycache__/` and the generated
study artifacts are what an ignore file is *for*, and a checkout full of them
is a working checkout, not an unrecorded one. ⛔ **Untracked-but-not-ignored
is** — a new module nobody added is the half of "work on no ref" that carries
the most, and it is invisible to every other reading. ⚠️ So the population is
exactly what `git status` reports by default, and the decision is the ignore
file's, where it already lives.

## ⭐ Why the runner is a parameter and not an import

⛔ `tools.workspace.git` lives in the package's `__init__`, which imports this
module; importing it back would be a cycle. ⭐ Handing the runner in keeps the
dependency one-way — and a test can drive this module with a runner of its own
rather than a real repository, which is how the parse is asserted directly.

## ⚠️ What this reproduces, and what it does not (R7)

⭐ **Paths are repository-relative by construction**: `git status` reports them
relative to the checkout it was run in, so a finding carries `README.md` and
never the directory the component sits in. ⛔ The component's **own name** comes
from the pin file, which `SAFE_NAME` already forbids from holding a path, and
the count of paths is always given so that the cap cannot read as *"that is
all there was"*.
"""

from __future__ import annotations

import subprocess
from collections.abc import Callable
from pathlib import Path

#: A git runner: `tools.workspace.git`'s signature, handed in rather than imported.
Runner = Callable[..., subprocess.CompletedProcess]

#: ⛔ An operation left unfinished, as the marker git itself leaves behind, and the
#: word for it. ⭐ Two rebase forms because git has two — `rebase-merge` is the
#: interactive machinery and `rebase-apply` is `am`'s — and a reader who is told
#: which one it is can reach for the right `--abort` without looking.
OPERATIONS = (
    ("MERGE_HEAD", "a merge is in progress (MERGE_HEAD)"),
    ("CHERRY_PICK_HEAD", "a cherry-pick is in progress (CHERRY_PICK_HEAD)"),
    ("REVERT_HEAD", "a revert is in progress (REVERT_HEAD)"),
    ("rebase-merge", "a rebase is in progress (rebase-merge)"),
    ("rebase-apply", "a rebase is in progress (rebase-apply)"),
)

#: ⛔ How many paths a finding names before it says how many more there are.
#: ⚠️ The count is printed either way, so the cap never reads as the total.
NAMED = 3

#: ⭐ The unmerged status codes `git status --porcelain` writes. Every other code
#: with a `U` in it is unmerged too, which is why `U` is tested for separately.
BOTH_SIDES = ("AA", "DD")


def uncommitted(directory: Path, run: Runner) -> list[str]:
    """Every way this checkout holds work that is on no ref. Empty means clean.

    ⭐ Ordered operation-first: an unfinished merge explains the conflicted
    paths under it, so a reader who acts on the first line does the right thing.
    """
    directory = Path(directory)
    findings = [*_operations(directory, run)]
    conflicted, staged, modified, untracked = _buckets(_status(directory, run))
    for label, paths in (
        ("conflicted and unresolved", conflicted),
        ("staged and not committed", staged),
        ("modified and not staged", modified),
        ("untracked and not ignored", untracked),
    ):
        if paths:
            findings.append(f"{len(paths)} path(s) {label}: {_name(paths)}")
    return findings


def _operations(directory: Path, run: Runner) -> list[str]:
    """Name each unfinished git operation this checkout is sitting in."""
    result = run(directory, "rev-parse", "--absolute-git-dir")
    if result.returncode != 0 or not result.stdout.strip():
        return []
    git_dir = Path(result.stdout.strip())
    return [said for marker, said in OPERATIONS if (git_dir / marker).exists()]


def _status(directory: Path, run: Runner) -> str:
    """Return the porcelain status, or empty when this is not a checkout at all.

    ⚠️ `--untracked-files=normal` is passed rather than inherited: a machine
    that had set `status.showUntrackedFiles` would otherwise silence the half of
    this check that catches a module nobody added.
    """
    result = run(directory, "status", "--porcelain=v1", "-z", "--untracked-files=normal")
    return result.stdout if result.returncode == 0 else ""


def _entries(text: str) -> list[tuple[str, str]]:
    """Parse `--porcelain=v1 -z` into `(code, path)` pairs.

    ⛔ **`-z` because a path may hold anything**, including a newline and a
    quote, and the non-`-z` form escapes those into a shape that would have to
    be un-escaped here. ⚠️ A rename or a copy writes its **source** as a second
    field; that field is the same path under another name, so it is stepped
    over rather than counted twice.
    """
    fields = text.split("\0")
    entries: list[tuple[str, str]] = []
    index = 0
    while index < len(fields):
        field = fields[index]
        index += 1
        if len(field) < 4:
            continue
        code = field[:2]
        entries.append((code, field[3:]))
        if code[:1] in ("R", "C"):
            index += 1
    return entries


def _buckets(text: str) -> tuple[list[str], list[str], list[str], list[str]]:
    """Sort the status into the four repairs. ⚠️ A path may land in two."""
    conflicted: list[str] = []
    staged: list[str] = []
    modified: list[str] = []
    untracked: list[str] = []
    for code, path in _entries(text):
        if code == "??":
            untracked.append(path)
        elif "U" in code or code in BOTH_SIDES:
            conflicted.append(path)
        else:
            if code[0] != " ":
                staged.append(path)
            if code[1] != " ":
                modified.append(path)
    return conflicted, staged, modified, untracked


def _name(paths: list[str]) -> str:
    """Name the first few paths, and say how many were not named."""
    shown = ", ".join(paths[:NAMED])
    rest = len(paths) - NAMED
    return f"{shown}, and {rest} more" if rest > 0 else shown
