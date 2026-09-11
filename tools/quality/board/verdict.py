"""`W110`: ONE observation row against ONE branch, and ⛔ TERMINALITY decides it first.

**What it does.** Turns a row's `Checkout` cell into a `Claim` — the names git
resolves as branches, the names that resolve as checkouts, and the names that
resolve as neither — and returns a `Verdict` per branch: the answer as a FLAG, with
the sentences that argue it.

**How you use it.** `claim(row, graph, live)` then `verdict(claim, branch, graph,
live)`. ⛔ **Nothing here prints or exits** — `corroborate.py` owns the population,
the exit code and the other two readings, and keeping the decision apart from the
report is what lets the two terminality shapes be printed against each other.

**Depends on.** `board.graph` for every git answer and `board.observation` for the
row. ⛔ **No `subprocess`, no `git` call of its own, no `print`.**

## ⛔ The defect, MEASURED IN BOTH DIRECTIONS WITH ONE VARIABLE CHANGED

⚠️ **Measured by the PO at `1c5e913`:** ⛔ **this verdict was a DISJUNCTION and its
first arm was `if branch in live:`, so `merged()` was never called when any checkout
held the branch.** ⭐ **One worktree planted outside every checkout (Ruling 153) on
`feat/SF-26-goldens` — MERGED at `8d17314`, `0` ahead — moved the reading from
`2 of 2 REFUTED, exit 1` to `1 of 2`, printing
`⭐ CORROBORATED … is 0 commits ahead` for a branch eleven commits spent.**
⚠️ **Restored, and the reading returned to `2 of 2`.**

⛔ **A detached checkout of the same commit did NOT corroborate it**, which narrows
the arm usefully: `checkouts()` is keyed by BRANCH, so the arm was *a worktree with
this branch attached* and not *somebody has these bytes on disk*.

## ⛔ THE REMEDY IS NOT `MERGED ∧ 0-ahead`, and that matters more than the fix

⚠️ **`merged()` is `merge-base --is-ancestor` and a branch cut AT the release tip is
an ancestor of it.** ⛔ **MEASURED at `2d0cfe7` in the `dev2` worktree: that shape is
true of ALL 124 local branches — `release/m0-foundations` itself, the CTO's round
branch, and both developer branches dispatched that hour.** ⚠️ **`git branch
--no-merged` is EMPTY at that ref, which is the same reading from the other side.**
⭐ **A predicate whose first wave refutes the work its author just did is the `W87`
and `board-disagreement` shape for a third and fourth time.**

⭐ **What ships is Ruling 199's shape `C`, and the ruling is POINTED AT rather than
paraphrased** (Ruling 195): ⛔ **`docs/conventions/board.md`, `RULED ROUND 51`
clause (a).** ⚠️ **Shape `B` — a merge subject naming the branch — is PRINTED beside
it and never decides, because the shipped `merge_of()` tested `if branch in subject:`
and `chore/cto-round3` therefore read terminal off `Merge chore/cto-round39:`.**

## ⛔ `PO-40/2` — the CLAIMED checkout is COMPARED now, and a mismatch is a NOTICE

⚠️ **Measured by the PO: a planted checkout named `plant-sf26` corroborated a row
claiming `wt/dev1`, while the row's own claim was printed as `checkouts ['wt/dev1']`
on the line above.** ⛔ **Two strings, parsed, printed, and never compared — so the
false pass did not even require the named worktree to exist.**

⭐ **They are compared now and the result is a NOTICE with BOTH names, never a
refusal** — ⚠️ **office worktrees are legitimately re-pointed between waves, and
`wt/dev1` moved from `feat/SF-26-goldens` to `feat/SF-30-reader-state` inside one
round.** ⛔ **The refutation belongs to TERMINALITY, which is a property of the
branch; the name mismatch is a property of the bookkeeping** (`rows/W110.md`).
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from tools.quality.board.graph import Graph
from tools.quality.board.observation import Observation


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


@dataclass(frozen=True)
class Verdict:
    """One branch's observation — ⛔ the answer as a FLAG, and the sentences beside it.

    ⚠️ **The flag is a FIELD and not a substring of `lines`.** ⭐ The shipped form
    asked `any("REFUTED" in verdict …)` of its own output, which is the same
    substring-for-a-predicate family Ruling 199 retired from `merge_of()`.
    """

    refuted: bool
    lines: tuple[str, ...]


def tokens(cell: str) -> tuple[str, ...]:
    """Return every code-spanned token of a `Checkout` cell, in order, de-duplicated.

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


def designates(name: str, where: str) -> bool:
    """Whether the board's `name` for a checkout designates the checkout at `where`.

    ⛔ **ONE definition, used by the partition AND by `PO-40/2`'s comparison**, and
    that is load-bearing rather than tidy: ⚠️ **this board writes `` `wt/dev1` `` for a
    checkout whose BASENAME is `dev1`**, so a comparison against the basename alone
    would print a mismatch notice on every correctly-written row — ⭐ **which is the
    notice-fires-on-correct-work family the same ruling exists to avoid.**
    """
    return Path(where).name == name or where.endswith(name)


def claim(row: Observation, graph: Graph, live: dict[str, str]) -> Claim:
    """Partition one row's claimed carriers by what git can actually resolve."""
    branches, paths, unresolved = [], [], []
    for name in tokens(row.checkout):
        if graph.exists(name):
            branches.append(name)
        elif any(designates(name, where) for where in live.values()):
            paths.append(name)
        else:
            unresolved.append(name)
    return Claim(row, tuple(branches), tuple(paths), tuple(unresolved))


def verdict(asserted: Claim, branch: str, graph: Graph, live: dict[str, str]) -> Verdict:
    """Judge one branch — ⛔ TERMINALITY FIRST, and it beats every checkout.

    ⭐ **Ruling 199's ORDER, and the order IS the fix** (`docs/conventions/board.md`,
    `RULED ROUND 51` clause (a)): shape `C` is consulted before the live-checkout
    arm, because no checkout can make an absorbed branch in flight again.
    """
    count = graph.ahead(branch)
    absorbed, named = graph.terminal(branch), graph.named(branch)
    lines = [_shapes(branch, absorbed, named)] if absorbed or named else []
    if absorbed:
        where = Path(live[branch]).name if branch in live else ""
        held = f"checked out at {where}" if where else "checked out nowhere"
        return Verdict(
            True,
            (
                *lines,
                f"    ⛔ REFUTED: {branch} is TERMINAL — its tip was ABSORBED by the merge "
                f"{absorbed} on {graph.release}'s first-parent line, and it is {count} ahead "
                f"and {held}. ⚠️ A checkout cannot make an absorbed branch in flight again "
                f"(Ruling 199, `docs/conventions/board.md`), and the arm that said it could "
                f"kept a spent row green for as long as somebody forgot a worktree.",
            ),
        )
    if branch in live:
        return Verdict(False, (*lines, *_held(asserted, branch, live, count)))
    if count:
        return Verdict(
            False,
            (*lines, f"    ⭐ CORROBORATED: {branch} is {count} commits ahead of {graph.release}."),
        )
    return Verdict(
        True,
        (
            *lines,
            f"    ⛔ REFUTED: {branch} is 0 ahead of {graph.release}, no checkout holds it, and "
            f"NO merge commit absorbed its tip (ancestor: {graph.merged(branch)}; message `B`: "
            f"{named or 'none'}). ⚠️ TWO readings reach this line and NEITHER can be separated "
            f"from the other by position, which is why one sentence names both: (a) it was "
            f"merged by a FAST-FORWARD, Ruling 199's NAMED blind spot — 7 genuinely spent "
            f"branches at `2d0cfe7` — and (b) it never carried a commit of its own, which is "
            f"invisible to `--no-merged` BY CONSTRUCTION (Ruling 130). ⛔ Both refute a started "
            f"row, and that is the 350-commit case.",
        ),
    )


def _shapes(branch: str, absorbed: str, named: str) -> str:
    """Print shape `C`, shape `B`, and ⛔ their DISAGREEMENT (Ruling 199)."""
    both = (
        f"    terminality (Ruling 199): graph `C` {absorbed or 'none'}, "
        f"message `B` {named or 'none'}"
    )
    if bool(absorbed) == bool(named):
        return both
    if absorbed:
        return (
            f"{both} — ⚠️ DISAGREE: absorbed by a merge whose subject does not declare "
            f"`Merge {branch}:`. That is `B`'s false-NEGATIVE population (pre-convention "
            f"history, 25 branches at `2d0cfe7`), and `C` is the gate."
        )
    return (
        f"{both} — ⚠️ DISAGREE: a merge subject declares `Merge {branch}:` and the branch's "
        f"TIP is absorbed by no merge. ⭐ Either the tip MOVED past its own merge, or the "
        f"merge was a fast-forward. ⛔ `C` is the gate and this is NOT a refutation."
    )


def _held(asserted: Claim, branch: str, live: dict[str, str], count: int | None) -> tuple[str, ...]:
    """Corroborate from the live checkout, ⛔ with `PO-40/2`'s comparison beside it."""
    path = live[branch]
    where = Path(path).name
    lines = [
        f"    ⭐ CORROBORATED: {branch} is checked out at {where} and is {count} commits ahead."
    ]
    if asserted.checkouts and not any(designates(n, path) for n in asserted.checkouts):
        lines.append(
            f"    ⚠️ NOTICE, not a refusal (`PO-40/2`): the row CLAIMS "
            f"{', '.join(asserted.checkouts)} and the checkout holding {branch} is {where}. "
            f"⭐ Office worktrees are legitimately re-pointed between waves, so both names "
            f"are PRINTED and neither refutes — ⛔ but the two used to be parsed, printed and "
            f"never compared, and a plant under ANY name discharged the row."
        )
    elif not asserted.checkouts:
        lines.append(
            f"    ⚠️ NOTICE, not a refusal (`PO-40/2`): the row names no checkout and the "
            f"live-checkout arm is what answered, from {where}."
        )
    return tuple(lines)
