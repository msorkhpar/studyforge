"""`W366`: the merge gate takes the tests a change can reach, and AUDITS that with a full suite.

**What it does.** Reads from git which paths a branch changed — its merge base against its
tip — and decides the SCOPE of the suite gates: the test files those paths can reach
(`tools/testmap.py`'s import map, plus every test that reads the tree), or the full suite.
It says WHY in every reading, and a targeted scope never prints as a full one. On every
`AUDIT_EVERY`-th merge, and whenever the register asks (`--full`, at a milestone close), the
suite runs FULL and the reading names every failure the selection would have MISSED.

**How you use it.** `tools.mergegate` calls it; nothing else needs to.

    scope = decide(root, branch, requested="M5 closes")
    lines = describe(scope)                 # what was selected, and why
    missed(scope.tests, failed_ids(output)) # the audit: failures outside the selection

**Depends on.** `dataclasses`, `re`, `subprocess` and `pathlib` — the standard library — `git`
on the path, `tools.testmap` and `tools.treereaders`. ⛔ Nothing from `studyforge` or
`tools.quality` (`W310`).

## ⛔ WHAT SELECTS EVERYTHING — the row's clause 2, and why each is on the list

⭐ `SHARED`: the conftests, `pyproject.toml`, `docker/dev/`, `tools/quality/`, `tools/gates.py`,
`tests/fixtures/`, and this selector with its import map — a change to the thing that
decides must be read by the thing it cannot fool. ⭐ So does any path of a KIND the selection
cannot scope (a `Dockerfile`, `workspace.json`, a data file outside a package): unknown is
never read as *reaches nothing* (Ruling 191). ⚠️ What a conftest IMPORTS is deliberately not on
the list: a conftest loads in EVERY run, targeted or full, so a defect it reaches breaks the
targeted run itself and cannot hide outside the selection.

## ⛔ WHAT A PATH SELECTS WHEN IT IS NOT SHARED

- ⭐ **A document** (`docs/`, or any `.md`): the tree readers only — `reads_tree`.
- ⭐ **A Python module**: every test file that imports it, transitively, and the tree readers.
- ⭐ **A non-Python file inside a package directory** under `src/`: whatever that directory's
  modules select, because package data is read through the package.
- ⭐ The tree readers run on EVERY change: a test that walks the tree is reached by any path.
  ⭐ They are taken TEST BY TEST (`file::name`, `tools/treereaders.py`), so a document change
  does not pay for a file's other tests; a file the import map reaches is taken whole.

## ⛔ THE AUDIT, AND WHY IT READS HISTORY WHEN `tools/mergegate.py` MAY NOT

⭐ The cadence is `git rev-list --count --first-parent --merges HEAD`: a COUNTER, never a
judgement of a landed commit, so it is not the report over frozen tips `W302` refused — and
it lives HERE so `mergegate` stays free of every history verb (its mirror asserts that).
⚠️ An audit that finds a failure OUTSIDE the selection is RED by name: that test's dependency
is one the import map cannot see, and the fix is a `reads_tree` mark or an import, never a
wider default.
"""

from __future__ import annotations

import re
import subprocess
from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path

from tools.testmap import TestMap, is_conftest, module_of
from tools.treereaders import WHOLE, TreeReaders

#: ⛔ Clause 2: a change under any of these selects the whole suite.
SHARED = (
    "pyproject.toml",
    "docker/dev/",
    "tools/quality/",
    "tools/gates.py",
    "tools/selection.py",
    "tools/testmap.py",
    "tools/treereaders.py",
    "tests/fixtures/",
)

#: ⭐ Clause 4: every Nth merge to the release branch takes the FULL suite, and audits.
AUDIT_EVERY = 5

#: How many reasons a reading prints before it summarises the rest.
SHOWN = 12

#: A failure line in pytest's short summary: `FAILED <id> - …` or `ERROR <id> - …`. ⚠️ An id
#: may hold spaces inside its parameter brackets, so it runs to the ` - ` or the line's end.
FAILURE = re.compile(r"^(?:FAILED|ERROR) (.+?)(?: - .*)?$")


@dataclass(frozen=True)
class Scope:
    """What the suite gates take, and why. ⛔ `full` and `audit` are never both silent."""

    #: True when the suite runs WHOLE; its argv then carries no path at all.
    full: bool
    #: The selection: the test files a targeted run takes, or the set an audit checks against.
    tests: tuple[str, ...]
    #: How many test files the tree holds, so every reading states the fraction.
    total: int
    #: One line per reason, in the order the paths were read.
    why: tuple[str, ...]
    #: ⭐ Non-empty when the suite is full BECAUSE it is auditing the selection.
    audit: str = ""


def _git(root: Path, *arguments: str) -> tuple[int, str]:
    """Run git in `root` and return its exit code with its stripped stdout."""
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "-C", str(root), *arguments],  # noqa: S607 - git from the path, by design
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return 1, ""
    return result.returncode, result.stdout.strip()


def changed_paths(root: Path, branch: str) -> tuple[str, ...] | None:
    """Return what `branch` changed since its merge base with `HEAD`, or None when unread."""
    code, base = _git(root, "merge-base", "HEAD", branch)
    if code != 0 or not base:
        return None
    code, out = _git(root, "diff", "--name-only", "--no-renames", base, branch)
    return None if code != 0 else tuple(line for line in out.splitlines() if line)


def merge_number(root: Path) -> int | None:
    """Return the number the NEXT merge to `HEAD` will be, counted on its first parents."""
    code, out = _git(root, "rev-list", "--count", "--first-parent", "--merges", "HEAD")
    return int(out) + 1 if code == 0 and out.isdigit() else None


def shared(path: str) -> bool:
    """Report whether `path` is shared machinery, which selects the whole suite."""
    return is_conftest(path) or path.startswith(SHARED)


def document(path: str) -> bool:
    """Report whether `path` is a document: under `docs/`, or Markdown anywhere."""
    return path.startswith("docs/") or path.endswith(".md")


def _package_modules(root: Path, path: str) -> set[str]:
    """The modules of the package directory holding the non-Python `path`, or none."""
    directory = root / path.rpartition("/")[0]
    if not path.startswith("src/") or not (directory / "__init__.py").is_file():
        return set()
    return {module_of(p.relative_to(root).as_posix()) for p in directory.glob("*.py")}


def select(root: Path, changed: Iterable[str], every: TestMap | None = None) -> Scope:
    """Decide the scope `changed` needs on the tree at `root` (the docstring's rules)."""
    graph = TestMap.build(root) if every is None else every
    readers = TreeReaders(root)
    total = len(graph.tests)
    everything = tuple(graph.tests)
    why: list[str] = []
    modules: set[str] = set()
    for path in changed:
        if shared(path):
            return Scope(True, everything, total, (f"{path}: shared machinery",))
        if document(path):
            why.append(f"{path}: a document — the tree readers")
            continue
        found = {module_of(path)} if module_of(path) else _package_modules(root, path)
        if not found:
            reason = f"{path}: a kind the selection cannot scope"
            return Scope(True, everything, total, (reason,))
        modules |= found
        why.append(f"{path}: {'a module' if path.endswith('.py') else 'package data'}")
    reached = graph.dependents(modules)
    trees = readers_of(readers, graph.tests, reached)
    chosen = tuple(sorted(reached | trees))
    if not chosen:
        # ⛔ Ruling 191: an EMPTY selection is never a pass; `pytest` with no path is the full
        #    suite anyway, so this says so rather than letting argv decide it silently.
        return Scope(True, everything, total, ("the selection is empty, so nothing is scoped",))
    why.append(
        f"{len(reached)} importing test file(s); {len(trees)} tree reader(s), by the marker rule"
    )
    return Scope(False, chosen, total, tuple(why))


def readers_of(readers: TreeReaders, tests: Iterable[str], taken: set[str]) -> set[str]:
    """Every tree-reading test as a pytest id — `file::name`, or `file` when all of it reads.

    ⭐ A file the import map already takes WHOLE is not named again test by test.
    """
    found: set[str] = set()
    for test in tests:
        nodes = readers.nodes(test)
        if test in taken or not nodes:
            continue
        found |= {test} if WHOLE in nodes else {f"{test}::{name}" for name in nodes}
    return found


def decide(root: Path, branch: str, requested: str = "", every: int = AUDIT_EVERY) -> Scope:
    """Return the scope for merging `branch` into `root`'s `HEAD`, audit cadence included."""
    changed = changed_paths(root, branch)
    if changed is None:
        return Scope(True, (), 0, ("git could not name what the branch changed",))
    if not changed:
        return Scope(True, (), 0, ("the branch changes no path, so nothing is scoped",))
    scope = select(root, changed)
    if scope.full:
        return scope
    number = merge_number(root)
    if requested:
        audit = f"requested: {requested}"
    elif number is None:
        audit = "git could not count the merges, so the cadence is unread"
    elif number % every == 0:
        audit = f"merge {number} is a multiple of {every}"
    else:
        return scope
    return Scope(True, scope.tests, scope.total, scope.why, audit)


def fraction(scope: Scope) -> str:
    """Say how much of the suite `scope.tests` is: whole files, and tests taken by name."""
    whole = [test for test in scope.tests if "::" not in test]
    named = [test for test in scope.tests if "::" in test]
    files = {test.split("::", 1)[0] for test in named}
    return (
        f"{len(whole)} whole test file(s) and {len(named)} test(s) named from {len(files)} "
        f"other(s), of {scope.total} test file(s)"
    )


def describe(scope: Scope) -> list[str]:
    """Return the lines a reading prints for `scope`: what it took, and why (clause 3)."""
    selected = fraction(scope)
    if scope.audit:
        head = f"scope: FULL, AUDITING the selection ({scope.audit}) — it would take {selected}"
    elif scope.full:
        head = "scope: FULL — every test file"
    else:
        head = f"scope: ⚠️ SELECTED {selected} — this is NOT a full-suite reading"
    shown = [f"  why: {line}" for line in scope.why[:SHOWN]]
    if len(scope.why) > SHOWN:
        shown.append(f"  why: … and {len(scope.why) - SHOWN} more")
    return [head, *shown]


def failed_ids(lines: Iterable[str]) -> tuple[str, ...]:
    """Return every test id pytest's short summary names as FAILED or ERROR."""
    return tuple(match[1] for line in lines if (match := FAILURE.match(line)))


def missed(selection: Iterable[str], failed: Iterable[str]) -> tuple[str, ...]:
    """Return every failure the selection would NOT have run (the audit's RED).

    ⭐ A failure is inside when its file was taken whole, or its top-level test by name.
    """
    chosen = set(selection)

    def inside(test: str) -> bool:
        path, _, rest = test.partition("::")
        top = rest.split("::", 1)[0].split("[", 1)[0]
        return path in chosen or f"{path}::{top}" in chosen

    return tuple(test for test in failed if not inside(test.rstrip()))
