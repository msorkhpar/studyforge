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
branch; the name mismatch is a property of the bookkeeping** (`W110`'s record in
`BOARD-ARCHIVE.md`).

## ⛔ `W115` — Ruling 216: the answer is THREE-VALUED, because a FAILED READING IS NOT A VERDICT

⚠️ **MEASURED by the CTO at `b5b3982` and RE-MEASURED by me at `6c4e3d0`, in the
pinned container, with a planted branch git genuinely cannot count:** ⛔ **`Graph.ahead()`
returns `None` when git could not answer, `if count:` is FALSEY, and the two arms below
it then printed a number git never produced:**

```text
no checkout holds the branch  ->  "is 0 ahead of release/…"     ⛔ a FALSE REFUTATION
a checkout does hold it       ->  "is None commits ahead."      ⛔ and refuted=False, exit 0
```

⭐ **The fix is NOT a fourth arm: it is that `None` is checked FIRST and never reaches a
sentence.** ⛔ **`_held()` now takes `count: int`, so the second site is closed by making
`None` UNREACHABLE there rather than by handling it** — ⚠️ **a handled `None` is a site
that can be reintroduced, and an unreachable one is not.**

⚠️ **And the unanswerable arm does NOT print shape `C`.** ⛔ **`terminal()` reads `tip()`,
which returns `""` on failure, so `graph `C` none` in that arm would be a second reading
git never gave** — ⭐ **it is reported as UNREAD, with shape `B` printed beside it because
the merge log needs no tip to answer.**

## ⛔ `PO-42/7` — the CLAIMED COUNT is COMPARED now, and a disagreement is a NOTICE

⭐ **MEASURED by the PO twice, forty minutes apart, in one round, with no plant:** two
cells reading `2` and `2` were `3` and `5` by the second reading, ⛔ **and `corroborate`
printed `⭐ CORROBORATED … is 3 commits ahead` beside a cell claiming `2` and compared
neither.** ⚠️ **So the instrument corroborated the ROW and never the CELL.**

⛔ **The remedy is a printed comparison and NOT a refutation, and the reason is
measured rather than stylistic:** ⭐ **a commits-ahead cell is a reading of a MOVING
TIP, and the release ref does not move when a developer commits — so the cell was true
when written and false an hour later with nothing on the board changed.** ⚠️ **A stale
NUMBER is not a stale ROW, and refuting on one would fire on every wave where somebody
committed after the board was written, which is every wave** (`rows/W115.md`).
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path

from tools.quality.board.graph import Graph
from tools.quality.board.observation import Observation


class Answer(StrEnum):
    """⛔ Ruling 216's THREE answers, in the ruling's own words and as a CLOSED set.

    ⚠️ **`corroborate` had three PROCESS codes and a row verdict had two**, so *git
    could not answer about this branch* folded onto `REFUTED` — ⛔ **a FALSE
    REFUTATION, which is the failure mode Ruling 199 refused in a predicate.**
    ⭐ **An enum rather than a `bool` pair: a caller cannot spell a fourth answer,
    and `any(answer.refuted …)` cannot silently swallow the third.**
    """

    CORROBORATED = "corroborated"
    REFUTED = "refuted"
    #: ⛔ Neither *the board is right* nor *the board is wrong*: git did not answer.
    NOT_ANSWERABLE = "not answerable"


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
    """One branch's observation — ⛔ the answer as a FIELD, and the sentences beside it.

    ⚠️ **The answer is a FIELD and not a substring of `lines`.** ⭐ The shipped form
    asked `any("REFUTED" in verdict …)` of its own output, which is the same
    substring-for-a-predicate family Ruling 199 retired from `merge_of()`.

    ⛔ **`W115`: the field was a `bool` and is now `Answer`** — ⚠️ **two values cannot
    carry three answers, and the shipped `bool` sent *git could not answer* to whichever
    of the two it happened to fall through to** (Ruling 216).
    """

    answer: Answer
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

    ⛔ **`W115` puts ONE arm ahead of even that one: did git answer at all.** ⚠️ **Every
    arm below embeds `count` in its own sentence, so a `None` reaching any of them prints
    a number git never gave** (Ruling 216).
    """
    count = graph.ahead(branch)
    if count is None:
        return Verdict(Answer.NOT_ANSWERABLE, _unanswerable(branch, graph, live))
    absorbed, named = graph.terminal(branch), graph.named(branch)
    lines = [_shapes(branch, absorbed, named)] if absorbed or named else []
    cell = _cell(asserted, branch, count, graph)
    if absorbed:
        where = Path(live[branch]).name if branch in live else ""
        held = f"checked out at {where}" if where else "checked out nowhere"
        return Verdict(
            Answer.REFUTED,
            (
                *lines,
                f"    ⛔ REFUTED: {branch} is TERMINAL — its tip was ABSORBED by the merge "
                f"{absorbed} on {graph.release}'s first-parent line, and it is {count} ahead "
                f"and {held}. ⚠️ A checkout cannot make an absorbed branch in flight again "
                f"(Ruling 199, `docs/conventions/board.md`), and the arm that said it could "
                f"kept a spent row green for as long as somebody forgot a worktree.",
                *cell,
            ),
        )
    if branch in live:
        return Verdict(Answer.CORROBORATED, (*lines, *_held(asserted, branch, live, count), *cell))
    if count:
        return Verdict(
            Answer.CORROBORATED,
            (
                *lines,
                f"    ⭐ CORROBORATED: {branch} is {count} commits ahead of {graph.release}.",
                *cell,
            ),
        )
    return Verdict(
        Answer.REFUTED,
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
            *cell,
        ),
    )


def _unanswerable(branch: str, graph: Graph, live: dict[str, str]) -> tuple[str, ...]:
    """⛔ Ruling 216's THIRD answer: git did not answer, so this row has NO verdict.

    ⚠️ **Shape `C` is NOT printed here and that is deliberate:** `terminal()` reads
    `tip()`, which returns `""` when git could not resolve the tip — ⛔ **so
    `graph `C` none` would be a second reading git never gave, in the arm whose whole
    subject is a reading git never gave.** ⭐ **Shape `B` IS printed: the merge log
    answers without the tip.**

    ⛔ **This sentence deliberately quotes NEITHER of the two strings the defect
    produced** (`is 0 ahead`, `is None commits ahead`) ⚠️ **and neither of the two
    verdict words.** ⭐ **Their absence from the output is what the gate asserts, and a
    sentence that mentioned them would make that assertion unwritable** — the history
    lives in this module's docstring, which no instrument reads as a reading.
    """
    where = Path(live[branch]).name if branch in live else ""
    held = f"checked out at {where}" if where else "checked out nowhere"
    return (
        f"    ⛔ NOT ANSWERABLE: git could not count {graph.release}..{branch}, so this row "
        f"has NO commits-ahead reading and NO terminality reading — the name resolves as a "
        f"branch, its tip reads {graph.tip(branch) or 'NOTHING'}, and it is {held}. "
        f"⚠️ Shape `C` is UNREAD rather than `none` (it needs the tip); shape `B` needs only "
        f"the merge log and says {graph.named(branch) or 'none'}. ⛔ This is Ruling 216's third "
        f"answer: one of them makes the RUN exit NOT AUTHORITATIVE — never the PASS code and "
        f"never the refutation code — because *git could not answer about this branch* is "
        f"neither *the board is right* nor *the board is wrong* (`rows/W115.md`).",
    )


def _cell(asserted: Claim, branch: str, count: int, graph: Graph) -> tuple[str, ...]:
    """`PO-42/7`: the row's CLAIMED count against git's — ⛔ a NOTICE, never a refutation.

    ⚠️ **The two were parsed, printed on adjacent lines, and compared to nothing.**
    ⛔ **A row naming several branches is PRINTED and not compared**: one cell cannot be
    a claim about N branches, and a comparison that invented one would fire on correct
    work, which is Ruling 179's cost.
    """
    claimed = asserted.row.commits
    if len(asserted.branches) != 1:
        return (
            f"    commits ahead: the row claims {claimed} over {len(asserted.branches)} branches, "
            f"so ONE cell is not a claim about {branch}'s {count} — PRINTED, not compared.",
        )
    if claimed is None:
        return (
            f"    commits ahead: the row DECLARES none and git reads {count} — ⚠️ a cell reading "
            f"`—` declares no ahead observation and is not a claim of `0` (Ruling 130), so there "
            f"is nothing to compare.",
        )
    if claimed == count:
        return (f"    commits ahead: the row claims {claimed}, git reads {count} — AGREE.",)
    if (tip := asserted.row.declared_tip) is not None:
        return _as_of(claimed, count, branch, tip, graph)
    return (
        f"    ⚠️ NOTICE, not a refusal (`PO-42/7`): the row claims {claimed} commits ahead and "
        f"git reads {count} for {branch}. ⭐ A commits-ahead cell is a reading of a MOVING TIP "
        f"and {graph.release} does not move when a developer commits — MEASURED twice forty "
        f"minutes apart in one round, two cells still reading 2 and 2 were 3 and 5. ⛔ So a "
        f"stale NUMBER is not a stale ROW: refuting on it would fire on every wave where "
        f"somebody committed after the board was written, which is every wave (Ruling 179). "
        f"⚠️ The two used to be printed side by side and compared to nothing.",
    )


def _as_of(claimed: int, count: int, branch: str, tip: str, graph: Graph) -> tuple[str, ...]:
    """`PO-50/12`: resolve the tip the SAME cell declares — ⛔ still a NOTICE, never a verdict.

    ⚠️ **MEASURED at `504bb47`, three takes of one pair of cells in one round: 3 of 3
    were TRUE AT THEIR OWN DECLARED REF and the notice printed a disagreement for each
    the moment the branch moved** — ⛔ **so it could not say whether the office
    MISCOUNTED (a register defect) or the branch MOVED (Rulings 97 and 246 obeyed).**
    ⭐ **`PO-42/7` is UNTOUCHED: the notice SAYS more, the verdict ANSWERS the same.**
    ⛔ **An unresolvable tip is Ruling 216's THIRD ANSWER, not a fourth arm** —
    `ahead()` is `None` when git declines, and such a cell reaches NEITHER case.
    """
    if (at_tip := graph.ahead(tip)) is None:
        return (
            f"    ⚠️ UNREAD as-of (Ruling 216's third answer): the row claims {claimed} @ {tip}, "
            f"git reads {count} for {branch}, and git could not count {graph.release}..{tip} — "
            f"⛔ NEITHER dated NOR disagreeing, and a FAILED READING is not a verdict.",
        )
    if at_tip == claimed:
        return (
            f"    ⭐ DATED, not wrong (`PO-50/12`): the row claims {claimed} @ {tip}, git reads "
            f"{count} for {branch} TODAY, and {graph.release}..{tip} is {at_tip} — TRUE AT ITS "
            f"OWN DECLARED REF, and the branch moved past it. ⚠️ The word is DATED, never "
            f"`stale`, `refuted` or `wrong` (Ruling 97, Ruling 310(b), `CTO-62/2`).",
        )
    return (
        f"    ⚠️ NOTICE, not a refusal (`PO-42/7`): the row claims {claimed} @ {tip}, git reads "
        f"{count} for {branch}, and {graph.release}..{tip} is {at_tip} — ⛔ WRONG AT ITS OWN "
        f"DECLARED REF, so the branch moving does not account for it. ⭐ That is case (a) — the "
        f"office MISCOUNTED — which a bare count could not tell from case (b) (`PO-50/12`).",
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


def _held(asserted: Claim, branch: str, live: dict[str, str], count: int) -> tuple[str, ...]:
    """Corroborate from the live checkout, ⛔ with `PO-40/2`'s comparison beside it.

    ⛔ **`count` is `int` and NOT `int | None`** (`W115`, Ruling 216): this function
    printed *"is None commits ahead"* and returned the row CORROBORATED, exit `0`, which
    is a FAILED reading reaching the PASS code. ⭐ **`verdict()` refuses a `None` before
    this arm, so the site is closed by UNREACHABILITY rather than by a handler** — ⚠️ a
    handled `None` is a site somebody can reintroduce.
    """
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
