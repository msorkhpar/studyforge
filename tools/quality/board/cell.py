"""`W40`: what the ROW's commits-ahead CELL claims, compared and ⛔ NEVER decisive.

**What it does.** Takes one row's `Commits ahead` cell and git's own count for the
branch, and returns the sentences that report the comparison — including the cell's
own declared tip resolved, where it declares one. ⛔ **Every line it returns is a
NOTICE. Nothing here returns, constructs or names an `Answer`, and by construction it
cannot move one.**

**How you use it.** `compared(row, branches, branch, count, graph)` returns the lines
`verdict.verdict()` appends after its own. ⛔ **Nothing here prints or exits**, and
nothing here reads the checkout cell — that partition is `verdict.claim()`'s.

**Depends on.** `board.graph` for `ahead()` and the release name, and
`board.observation` for the row. ⛔ **Not on `board.verdict`, and the absence is the
seam rather than an accident** — the import would be a cycle, and the cycle is what a
module that decided anything here would need.

## ⛔ THE SEAM `W40` CUT, NAMED BEFORE CUTTING

⭐ **`verdict.py` ANSWERS; this module SAYS.** ⛔ **The split is between *what git
observes of the BRANCH*, which decides — terminality, the count, the live checkout —
and *what the ROW claims about it*, which is printed and never decides.** ⚠️ **The two
were one file at `400/400` against R11's 400-line ceiling: zero headroom, so the next
line added anywhere in it was a build failure, and the standing SPLIT condition on
that module (`docs/tasks/BOARD.md`, *Standing decisions*) could not be discharged by
any row that touched it first.**

⭐ **The seam is checkable and `tools/tests/quality/board/test_cell.py` checks it in
both directions:** the type this module returns is `tuple[str, ...]` and never a
`Verdict`, and the answers `verdict()` reaches are the same answers with these lines
removed. ⛔ **A future notice that refused a row from here would have to import the
enum to say so, which is the cycle above.**

## ⛔ `PO-42/7` — the CLAIMED COUNT is COMPARED, and a disagreement is a NOTICE

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

## ⛔ `PO-50/12` — the cell's OWN declared tip, resolved

⚠️ **MEASURED at `504bb47`, three takes of one pair of cells in one round: 3 of 3 were
TRUE AT THEIR OWN DECLARED REF and the notice printed a disagreement for each the
moment the branch moved** — ⛔ **so it could not say whether the office MISCOUNTED (a
register defect) or the branch MOVED (Rulings 97 and 246 obeyed).**
"""

from __future__ import annotations

from tools.quality.board.graph import Graph
from tools.quality.board.observation import Observation


def compared(
    row: Observation, branches: int, branch: str, count: int, graph: Graph
) -> tuple[str, ...]:
    """`PO-42/7`: the row's CLAIMED count against git's — ⛔ a NOTICE, never a refutation.

    ⚠️ **The two were parsed, printed on adjacent lines, and compared to nothing.**
    ⛔ **A row naming several branches is PRINTED and not compared**: one cell cannot be
    a claim about N branches, and a comparison that invented one would fire on correct
    work, which is Ruling 179's cost.

    ⚠️ **`branches` is the COUNT of branches the row's checkout cell resolved to, not
    the branches themselves.** ⛔ Passed as an `int` rather than as the `Claim` it comes
    from, because importing `Claim` here is the cycle the seam exists to refuse — and
    the only thing this comparison ever asked of that object was *how many*.
    """
    claimed = row.commits
    if branches != 1:
        return (
            f"    commits ahead: the row claims {claimed} over {branches} branches, "
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
    if (tip := row.declared_tip) is not None:
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
