"""`W119`'s SWEEP: no test in this package's WORKING TREE takes its POPULATION from the HOST.

⛔ **RULING 259 — *working tree*, not *committed*, and the one word is the whole point.**
⚠️ **This guard reads the files beside it with `path.read_text()`, which is the WORKING
TREE.** ⭐ **That is the RIGHT span and it is stated rather than left to be inferred: a
guard reading the INDEX would pass the very file its author is about to commit** — ⛔ **it
would be green on the edit that introduces the defect and red only afterwards, which is a
tripwire that fires after the trespass.** ⚠️ **The retired first line said *committed*, and
a reader who believed it would have looked for a `git show` that is not here.**

⛔ **This module mirrors no source module, and `test_migration.py` is the precedent** — its
subject is not a module but a PROPERTY OF THE PACKAGE, which is why it has a file of its
own rather than a section of `test_graph.py`.

⚠️ **One instance is a bug and the POPULATION is the finding** (Ruling 126, Ruling 128).
⭐ **MEASURED over the whole tree at `f71c566` before this was written, with the command in
`W119`'s handoff: exactly THREE committed lines handed the live repository root to a reader
of branches or worktrees, and all three were in `test_graph.py`** — ⛔ **the module Ruling
225 was minted against.** ⚠️ **The two other live-root git readings in the tree are
`ls-files` — `tests/test_knowledge_index.py` and `tests/gate_coverage/test_coverage.py` —
and they are NAMED and excluded: their subject is the INDEX, which is the commit.**

⛔ **So this is the enforcement arm, and it is narrow on purpose**: it governs the package
the row repaired, where the defect lived and where a regression would land.
"""

from __future__ import annotations

import ast
from pathlib import Path

#: ⛔ **The calls that ask GIT a question.** ⚠️ **Resolving the live repository root is
#: NOT the defect and must not be flagged: SEVEN modules in this package resolve it to
#: read the tracked board, which is the COMMIT.** ⭐ **Ruling 225's subject is handing
#: that root to one of THESE, because what they answer is branches, worktrees and
#: history — ⛔ the purest untracked state there is** (Ruling 80).
#:
#: ⚠️ **Matched on the dotted spelling or its last segment**, so `Graph.read`,
#: `git(...)`, `subprocess.run(...)` and `corroborate(...)` are all reached and
#: `path.read_text(...)` is not.
#:
#: ⛔ **RULING 257 — THIS IS A SUPERSET MATCHER, AND THE GUARD IS SAFE ONLY BY ITS REACH.**
#: ⚠️ **`run` and `git` are matched on the LAST SEGMENT, so they reach every callable in
#: the tree spelled that way — git-shaped or not.** ⭐ **Over this package that over-reach
#: is FREE: the only `run(...)` and `git(...)` calls here ARE git, so a superset of the
#: true population is the true population.** ⛔ **So the reach is declared HERE, where the
#: population is declared, rather than being a property somebody re-derives:**
#:
#: ⛔ **WIDENING THE GLOB IN
#: `test_no_module_in_this_package_takes_its_POPULATION_from_the_HOST` — the `*.py` that
#: bounds this guard to ONE package — REQUIRES NARROWING `GIT_READERS` FIRST.** ⚠️ **A
#: wider population brings in modules that spell an ordinary helper `run` or `git`, and
#: the matcher cannot tell those from `tools.workspace.git`: the guard would redden a
#: correct commit, which is Ruling 179's cost and the failure this module's own
#: `_hands_the_live_root_to_git` docstring records being caught by running it.**
GIT_READERS = ("Graph.read", "corroborate", "git", "run", "check_output")

#: ⛔ **The ONE module in this package licensed to hand the live root to git, and the
#: licence is Ruling 182 rather than convenience.** ⭐ **`test_migration.py`'s subject is
#: a PAIR OF REFS**: it fetches both sides with `git show <ref>:<path>`, its own guard
#: asserts that no reader of its opens a file under the working tree, and an unreachable
#: ref makes it SKIP rather than pass. ⚠️ **So its verdict cannot depend on a worktree or
#: a branch position, which is the property Ruling 225 is about.**
#:
#: ⛔ **Ruling 185's form: the POPULATION is narrowed and the exclusion is NAMED; the
#: predicate is never widened.** ⭐ **And it doubles as this guard's POSITIVE row
#: (Ruling 191(c)): the reading is `1` against a declared `1`, never `0` against `0`.**
LIVE_ROOT_READERS = ("test_migration.py",)


def _dotted(node: ast.expr) -> str:
    """`Graph.read` for an attribute chain, `git` for a bare name, `""` for anything else."""
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        return f"{_dotted(node.value)}.{node.attr}"
    return ""


def _names_the_live_root(trees: tuple[ast.expr, ...], bound: set[str]) -> bool:
    """Whether any of `trees` is `repository_root()` itself or a name bound to it."""
    for tree in trees:
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and _dotted(node.func).endswith("repository_root"):
                return True
            if isinstance(node, ast.Name) and node.id in bound:
                return True
    return False


def _hands_the_live_root_to_git(source: str) -> list[str]:
    """Every git reading in `source` whose root is the LIVE repository (Ruling 225).

    ⭐ **`ast`, not a grep, and the reason is measured rather than aesthetic:** ⚠️ **my
    first predicate asked whether a module IMPORTED `repository_root` and it read SEVEN
    modules in this package as offenders** — every one correct, because they resolve the
    root to read the tracked board. ⛔ **The fires-on-correct-work class, caught by
    running the instrument** (Ruling 179, and this package's own `PO-40/2` precedent).

    ⭐ **It follows ONE binding**, because the shape people actually write is
    `root = repository_root()` and then `cwd=root` — which is how `test_migration.py`
    reads its refs, and a predicate that only saw the inline spelling would have scored
    the licensed module clean and had no positive row at all.

    ⚠️ **What it does NOT cover, DECLARED rather than implied** (Ruling 220): a root
    rebound through a second name, a dynamic import, a reader not in `GIT_READERS`, and
    ⛔ **RULING 258's MISSING SHAPE — a live root obtained WITHOUT CALLING
    `repository_root()` at all**: `Path(__file__).parents[N]`, `os.getcwd()`,
    `Path.cwd()`, or a root handed in by a fixture.

    ⛔ **That fourth gap is the one that was missing from this list, and a declared-gaps
    list is read as EXHAUSTIVE — so an incomplete one is worse than none** (Ruling 258,
    and Ruling 276 measured the same defect in `board.md`'s rule table). ⚠️ **It is also
    the gap that is SILENT in the same way as the other three: `_names_the_live_root`
    looks for the CALL or a name bound to it, so a root spelled any other way reads as an
    ordinary argument and the module scores clean.**

    ⭐ **Nothing in this package does any of the FOUR**, and that is a measurement rather
    than a hope: ⛔ **a guard claiming to cover them would be claiming a reach it has not
    got, which is Ruling 225's own shape.**
    """
    tree = ast.parse(source)
    bound = {
        target.id
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        for target in node.targets
        if isinstance(target, ast.Name)
        and isinstance(node.value, ast.Call)
        and _dotted(node.value.func).split(".")[-1] == "repository_root"
    }
    found = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        spelling = _dotted(node.func)
        if spelling not in GIT_READERS and spelling.split(".")[-1] not in GIT_READERS:
            continue
        arguments = (*node.args, *(keyword.value for keyword in node.keywords))
        if _names_the_live_root(arguments, bound):
            found.append(f"{spelling} at line {node.lineno}")
    return found


def test_no_module_in_this_package_takes_its_POPULATION_from_the_HOST() -> None:
    """⛔ `W119`'s second half: the class is CLOSED over this package, not just the bug.

    ⚠️ **One instance is a bug and the population is the finding** (Ruling 126,
    Ruling 128). ⭐ **MEASURED over the whole tree before this was written: exactly THREE
    committed lines handed the live repository root to a reader of branches or
    worktrees, and all three were in this module.** ⛔ **The two other live-root git
    readings in the tree — `tests/test_knowledge_index.py`'s and
    `tests/gate_coverage/test_coverage.py`'s `ls-files` — are NAMED and excluded: their
    subject is the INDEX, which is the commit, not the host's housekeeping.**

    ⭐ **This is the enforcement arm, and it is narrow on purpose**: it governs the
    package `W119` repaired, where the defect lived and where a regression would land.
    """
    package = Path(__file__).parent
    modules = sorted(path.name for path in package.glob("*.py"))
    assert len(modules) >= 10, f"born vacuous: the package has {len(modules)} modules"
    reading = {
        name: found
        for name in modules
        if (found := _hands_the_live_root_to_git((package / name).read_text(encoding="utf-8")))
    }
    assert sorted(reading) == sorted(LIVE_ROOT_READERS), (
        f"⛔ {reading} hands the LIVE repository root to git. A committed assertion may "
        f"not take its POPULATION from the host (Ruling 225): a branch position is "
        f"untracked state (Ruling 80), and a test whose subject leaks out of the "
        f"repository reddens a correct commit on any machine whose worktree set differs. "
        f"⭐ Build the shape in `conftest.py` and assert it there, or read a NAMED REF the "
        f"way {LIVE_ROOT_READERS[0]} does."
    )


def test_the_SWEEP_guard_is_PLANTED_in_both_directions_and_the_two_readings_DIFFER() -> None:
    """⛔ Ruling 123: the guard above is validated by PLANTING, not only by running.

    ⭐ **Four readings.** The PLANT is the retired line itself, in both the spellings
    this package has carried — ⛔ **inline, and through one binding** — and the
    IMPOSSIBLE readings are the two shapes that must stay silent: ⚠️ **a module that
    resolves the live root and hands it to NOTHING git-shaped, and this module's own
    prose mention of the retired call.**
    """
    mine = Path(__file__).read_text(encoding="utf-8")
    assert "Graph.read(repository_root()" in mine, "⛔ the impossible reading needs its mention"
    assert _hands_the_live_root_to_git(mine) == [], "⭐ a MENTION in prose is not a reading"
    inline = "from tests.support import repository_root\nGraph.read(repository_root(), R)\n"
    bound = "root = repository_root()\nrun(['git', 'show'], cwd=root)\n"
    silent = "root = repository_root()\n(root / 'docs' / 'tasks' / 'BOARD.md').read_text()\n"
    assert _hands_the_live_root_to_git(inline) == ["Graph.read at line 2"]
    assert _hands_the_live_root_to_git(bound) == ["run at line 2"]
    assert _hands_the_live_root_to_git(silent) == [], "⛔ resolving the root is NOT the defect"
    assert _hands_the_live_root_to_git(inline) != _hands_the_live_root_to_git(silent)
