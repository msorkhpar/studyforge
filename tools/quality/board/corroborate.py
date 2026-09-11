"""Ruling 189(c) and (d): the corroborating reading, which is `git` and is NOT the floor.

**What it does.** Takes every row the board asserts is started and corroborates it
against git in **two printed steps** — row → branch, which is an ASSERTION, and
branch → merge, which is an OBSERVATION — then names the rows git refutes, the
checkouts the board does not name, and the `trial/*` and `tmp-*` branches that
now carry nothing.

**How you use it.** `python3 -m tools.quality.board.corroborate` from any
checkout of this repository, at a wave's close. ⛔ **Exit `0` corroborated, `1`
refuted, and `2` NOT AUTHORITATIVE** — Ruling 53's fourth state, because *"git
could not answer"* and *"nothing is wrong"* must never arrive as the same answer.

**Depends on.** `board.observation` for the population, `tools.workspace.git` for
the one definition of *run one git command*, and `argparse`. ⛔ **Nothing in
`tools.quality.CHECKS` imports this**, and that is the design answer below.

## ⛔ May the floor shell out? NO — and the reason is measured, not stylistic

⚠️ **`rows/W96.md` owed this answer before it owed code.** ⭐ **The answer is that
Ruling 189(b)'s reading belongs on the floor and 189(c)'s cannot:**

- ⛔ **Ruling 80 — a floor check's verdict may not depend on untracked state.**
  ⭐ A branch position is the purest untracked state there is: the same tree reads
  green in the main checkout and red in a worktree that has not fetched.
- ⛔ **R10 — byte-for-byte reproducible.** ⚠️ `git worktree list` answers
  differently on every machine, and the floor runs over **arbitrary roots** — a
  temp tree, a corpus repository — where there is no release branch at all.
- ⛔ **Ruling 191 — and this is the decisive one.** A check that shelled into git
  and found nothing would return **the PASS reading from an empty population**,
  which is the failure Ruling 191 exists to forbid. ⭐ **Here that is impossible
  by construction: an unanswerable run exits `2`.**

⭐ **And the separation is also `W100`'s.** ⛔ **`W100` is a PURE TREE property and
may not inherit a git dependency to get built** (`board.md`, ruled round 49) — so
the predicate and its corroboration are two modules, and the half `W100` needs is
the half with no `subprocess` in it.

## ⛔ Ruling 189(d) — the ref comes from the BRANCH, never from the ROW

⚠️ **Measured, and it is why this is two steps rather than one:** a branch carries
N rows and a merge message names one thing, **itself**. ⛔ **`--grep '<row id>'`
over merge messages is a LOWER BOUND and reads `0` for every row that shared a
branch** — all three of `W85`, `W86` and `W87` returned nothing, and `W86` is
named in no commit message on its own branch at all.

⛔ **So existence is checked as its OWN command** — `git rev-parse --verify`,
never behind a pipeline — ⚠️ **because `$?` after a pipeline is the pipeline's
last command and `rev-parse` echoes an unknown name back at you as if it were an
answer.** ⭐ **And `--ancestry-path | tail -1` is RECORDED AS WRONG and is not
reused: it returned a different branch's merge, and the error was caught only
because both forms were run.**
"""

from __future__ import annotations

import argparse
import sys
from dataclasses import dataclass
from pathlib import Path

from tools.quality.board.observation import (
    Observation,
    asserted,
    observation_reading,
    observations,
)
from tools.quality.board.register import BOARD
from tools.workspace import git

#: The branch every *commits ahead* cell on this board counts against. ⭐ A
#: default rather than a constant: `--release` overrides it, because a milestone
#: branch is a fact about this month and not about the instrument.
RELEASE = "release/m0-foundations"

#: ⛔ Branch namespaces whose members are DELETED once they are ancestors of the
#: release branch. ⚠️ **The standing form, measured by the CTO at `0285a92` and
#: `c3e2919`:** such a branch carries nothing unique, is invisible to
#: `--no-merged` by construction, and its only remaining effect is ⭐ **to read as
#: dispatched work to a human — which is Ruling 189's subject with no board cell
#: to print it in.** ⛔ **So this instrument is where it gets printed.**
SPENT = ("trial/", "tmp-")

CORROBORATED = 0
REFUTED = 1
#: ⛔ **Ruling 53's fourth state, as a number** — not *"the board is right"* and
#: not *"the board is wrong"*: this run could not tell. ⚠️ A check that cannot be
#: authoritative where it is running says so and refuses.
NOT_AUTHORITATIVE = 2


@dataclass(frozen=True)
class Claim:
    """One row's ASSERTION about its carrier, split by what git could observe.

    ⛔ **`branches`, `checkouts` and `unresolved` partition the cell's tokens by
    OBSERVATION rather than by naming convention** — ⚠️ a reader cannot tell
    `wt/dev1` from `feat/SF-15-contents` by shape, and a classifier that guessed
    from the prefix would have read a renamed worktree as a missing branch.
    """

    row: Observation
    branches: tuple[str, ...]
    checkouts: tuple[str, ...]
    unresolved: tuple[str, ...]


def tokens(cell: str) -> tuple[str, ...]:
    """Every code-spanned token of a `Checkout` cell, in order, de-duplicated.

    ⛔ The code span is the board's own idiom for a carrier — `` `wt/dev1`,
    `feat/SF-15-contents` `` — and reading the spans rather than the words is what
    keeps the surrounding prose out of the population.
    """
    found: list[str] = []
    for piece in cell.split("`")[1::2]:
        name = piece.strip().strip(",")
        if name and name not in found:
            found.append(name)
    return tuple(found)


def branch_exists(root: Path, name: str) -> bool:
    """Whether `refs/heads/<name>` resolves. ⛔ Its OWN command, never a pipeline."""
    return git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{name}").returncode == 0


def checkouts(root: Path) -> dict[str, str]:
    """`{branch: checkout path}` for every live checkout, the MAIN one included.

    ⚠️ A detached checkout has no branch line and is not in this map; it is
    reported as a checkout nothing names rather than dropped, because *"nobody is
    on that branch"* and *"that checkout has no branch"* are different answers.
    """
    result = git(root, "worktree", "list", "--porcelain")
    found: dict[str, str] = {}
    where = ""
    for line in result.stdout.split("\n"):
        if line.startswith("worktree "):
            where = line[len("worktree ") :].strip()
        elif line.startswith("branch refs/heads/"):
            found[line[len("branch refs/heads/") :].strip()] = where
    return found


def ahead(root: Path, branch: str, release: str) -> int | None:
    """Return the commits on `branch` and not on `release`, or `None` if git cannot say."""
    result = git(root, "rev-list", "--count", f"{release}..{branch}")
    return int(result.stdout.strip()) if result.returncode == 0 else None


def merged(root: Path, branch: str, release: str) -> bool:
    """Whether `branch` is an ancestor of `release`. ⚠️ Equal counts, as git says."""
    return git(root, "merge-base", "--is-ancestor", branch, release).returncode == 0


def merge_of(root: Path, branch: str, release: str) -> str:
    """Ruling 189(d) step two: the merge ref derived from the BRANCH.

    ⛔ **The branch, never the row**, and the match is on the merge subject's own
    `Merge <branch>:` idiom. ⚠️ **A row id is a LOWER BOUND here** — three rows
    that shared one branch are named in no merge message at all — ⭐ so this reads
    the thing a merge message is guaranteed to carry: itself.
    """
    result = git(root, "log", "--merges", "--first-parent", "--format=%h %s", release)
    for line in result.stdout.split("\n"):
        ref, _, subject = line.partition(" ")
        if branch in subject:
            return ref
    return ""


def _claim(root: Path, row: Observation) -> Claim:
    live = checkouts(root)
    branches, paths, unresolved = [], [], []
    for name in tokens(row.checkout):
        if branch_exists(root, name):
            branches.append(name)
        elif any(Path(where).name == name or where.endswith(name) for where in live.values()):
            paths.append(name)
        else:
            unresolved.append(name)
    return Claim(row, tuple(branches), tuple(paths), tuple(unresolved))


def corroborate(root: Path, release: str = RELEASE) -> tuple[list[str], int]:
    """Every asserted row against git, as printed steps and one exit code.

    ⛔ **The population is printed in full before any verdict** (Ruling 128), and
    ⚠️ **an EMPTY population is not a pass**: between waves the observation table
    is empty and `--no-merged` is empty with it, which is exactly when a close run
    is taken. ⭐ **So the size is printed and the verdict says which case it was.**
    """
    board = root / BOARD
    if not board.is_file():
        return [f"corroborate: no {BOARD} in this checkout — nothing to corroborate."], (
            NOT_AUTHORITATIVE
        )
    if git(root, "rev-parse", "--verify", "--quiet", f"refs/heads/{release}").returncode != 0:
        return [
            f"corroborate: NOT AUTHORITATIVE — no branch {release!r} in this checkout, so "
            f"every *commits ahead* cell on this board counts against nothing. ⛔ This is "
            f"exit {NOT_AUTHORITATIVE} and not a pass (Ruling 191)."
        ], NOT_AUTHORITATIVE

    text = board.read_text(encoding="utf-8")
    rows = observations(text)
    live = checkouts(root)
    lines = [
        f"corroborate: release {release}, {len(rows)} observation rows, "
        f"{len(live)} checkouts on a branch, {len(asserted(text))} started register cells.",
        observation_reading(text),
    ]
    refuted = 0
    for row in rows:
        claim = _claim(root, row)
        lines.append(
            f"  row -> branch (ASSERTION, Ruling 189(c)): {row.subject} claims "
            f"{', '.join(tokens(row.checkout)) or 'nothing'} — branches "
            f"{list(claim.branches)}, checkouts {list(claim.checkouts)}, "
            f"unresolved {list(claim.unresolved)}"
        )
        if not row.started:
            lines.append("    not a started state; no carrier is owed.")
            continue
        verdicts = [_verdict(root, claim, branch, release, live) for branch in claim.branches]
        if not claim.branches:
            verdicts = [
                "    ⛔ REFUTED: the row names no branch this checkout has. An assertion owes "
                "its own observation (Ruling 189(c))."
            ]
        lines.extend(verdicts)
        if any("REFUTED" in verdict for verdict in verdicts):
            refuted += 1
    lines.extend(_unnamed(rows, live, root, release))
    lines.extend(_spent(root, release, live))
    lines.append(
        f"corroborate: {refuted} of {len(rows)} rows REFUTED by git."
        if rows
        else "corroborate: ⚠️ the observation table is EMPTY — nothing was read, which is not "
        "the same answer as nothing being in flight (Ruling 191(a))."
    )
    return lines, REFUTED if refuted else CORROBORATED


def _verdict(root: Path, claim: Claim, branch: str, release: str, live: dict[str, str]) -> str:
    """One branch's observation, with the merge ref derived from the branch."""
    count = ahead(root, branch, release)
    if branch in live:
        return (
            f"    ⭐ CORROBORATED: {branch} is checked out at {Path(live[branch]).name} "
            f"and is {count} commits ahead."
        )
    if count:
        return f"    ⭐ CORROBORATED: {branch} is {count} commits ahead of {release}."
    if merged(root, branch, release):
        where = merge_of(root, branch, release) or "(no merge message names the branch)"
        return (
            f"    ⛔ REFUTED: {branch} is MERGED at {where}, is 0 ahead, and no checkout holds "
            f"it. ⚠️ Every git instrument reads correctly here — that is the 350-commit case."
        )
    return (
        f"    ⛔ REFUTED: {branch} exists, is 0 ahead of {release}, and no checkout holds it. "
        f"⚠️ A branch with no commit is invisible to `--no-merged` BY CONSTRUCTION (Ruling 130)."
    )


def _unnamed(rows: list[Observation], live: dict[str, str], root: Path, release: str) -> list[str]:
    """Report the other direction: work git can see that the board does not name.

    ⛔ **The measured failure was BIDIRECTIONAL** — stale rows present and live
    rows absent, in the same table — ⚠️ **and a check that only read the rows the
    board printed would have passed the half where the board printed nothing.**

    ⛔ **And the BLIND SPOT is printed rather than implied.** ⚠️ **A checkout with
    no commit is invisible to every git instrument BY CONSTRUCTION** (Ruling 130,
    and Ruling 171's founding case): *just dispatched* and *office checkout* are
    the same bytes to `git`. ⭐ **So those are COUNTED AND NAMED as unreadable
    here, never silently dropped and never judged** — the board is the only
    instrument that can tell them apart, which is the whole of Ruling 171.

    ⛔ **Directory BASENAMES, never the path** (R7): `git worktree list` answers
    in absolute paths, and an absolute path carries the user's home directory.
    """
    claimed = {name for row in rows for name in tokens(row.checkout)}
    counts = {branch: ahead(root, branch, release) or 0 for branch in live if branch != release}
    missing = sorted(b for b, n in counts.items() if n > 0 and b not in claimed)
    blind = sorted(Path(live[b]).name for b, n in counts.items() if n == 0 and b not in claimed)
    lines = (
        [f"  ⛔ dispatched and UNNAMED by any row: {' '.join(missing)}"]
        if missing
        else ["  dispatched and unnamed: none."]
    )
    lines.append(
        f"  invisible to git BY CONSTRUCTION (Ruling 130), 0 commits ahead and named by no "
        f"row: {len(blind)}" + (f" — {' '.join(blind)}" if blind else "")
    )
    return lines


def _spent(root: Path, release: str, live: dict[str, str]) -> list[str]:
    """`trial/*` and `tmp-*` branches that are now ancestors of the release branch."""
    result = git(root, "for-each-ref", "--format=%(refname:short)", "refs/heads")
    spent = sorted(
        name
        for name in result.stdout.split()
        if name.startswith(SPENT) and name not in live and merged(root, name, release)
    )
    if not spent:
        return ["  spent trial/tmp branches: none."]
    return [
        f"  ⚠️ spent and deletable ({len(spent)}): {' '.join(spent)} — each is an ancestor of "
        f"{release}, checked out nowhere, and reads as dispatched work to a human."
    ]


def main(argv: list[str] | None = None) -> int:
    """Print every step and return the exit code. ⛔ Three answers, never two."""
    parser = argparse.ArgumentParser(description="Corroborate the board's asserted states.")
    parser.add_argument("--root", default=".", help="the checkout to read")
    parser.add_argument("--release", default=RELEASE, help="the branch cells count against")
    arguments = parser.parse_args(argv)
    lines, code = corroborate(Path(arguments.root), arguments.release)
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":  # pragma: no cover - the CLI's one line
    sys.exit(main())
