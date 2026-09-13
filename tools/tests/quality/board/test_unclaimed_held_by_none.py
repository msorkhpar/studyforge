"""Mirror of `tools/quality/board/unclaimed.py` (R12), part two — ⛔ the branches NO checkout holds.

⛔ **Split out of `test_unclaimed.py` by `W251` at the seam the gate line NAMES in its own text**:
⭐ **its population is LIVE CHECKOUTS, and the line below it reads the branches NO worktree holds.**
The live-checkout readings stay there, where `W251`'s detached checkout joins them; this module
reads the other population. ⚠️ The tests MOVED rather than being copied.

## ⛔ The GATE's OTHER HALF — a branch HELD BY NO CHECKOUT, and the CONTROL that goes SILENT

| direction | ⛔ the expectation, written BEFORE the run |
|---|---|
| a branch AHEAD, held by NO worktree, no row | ⭐ **NAMED**, ⛔ **and STILL absent from the
  gate line, whose population is UNCHANGED** |
| ⭐ the CONTROL that must go SILENT | with `Graph.heads` answering the LIVE branches alone —
  the pre-change population, exactly — the line reads `none.` |
| an office or `trial/*` branch in the same state | ⛔ **exempt on BOTH halves** |
| a `fix/W*` branch in the same state | ⛔ **still read** — Ruling 319's refusal, held here too |
| ⚠️ the EXIT CODE | ⛔ **does not move**, and neither does the fold for a branch git DECLINED
  to count: Ruling 216 built that fold over LIVE CHECKOUTS |
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.quality.board.corroborate import CORROBORATED, corroborate
from tools.quality.board.graph import Graph
from tools.workspace import git

from .conftest import RELEASE, commit, unreadable, write_board


def _run(root: Path, release: str = RELEASE) -> tuple[int, str]:
    lines, code = corroborate(root, release)
    return code, "\n".join(lines)


# --------------------------------------------------------------------------
# ⛔ The GATE's OTHER HALF — a branch HELD BY NO CHECKOUT, in both directions
# --------------------------------------------------------------------------

#: ⛔ **The LIVE instance, reproduced as a SHAPE rather than cited:** `docs/NS-07-handoff` at
#: `10a5470` carried a real commit, was named by no row, and the gate printed
#: `dispatched and unnamed: none.` — ⚠️ **because the office that made it used a throwaway
#: worktree and REMOVED it, which is correct hygiene.** ⭐ **Replanted here at `2d2af22`,
#: role `wt/dev2`, environment HOST: `docs/plant-dispatch-population`, `1` ahead, held by no
#: worktree — silent on the pristine instrument, NAMED after the change, `CORROBORATE_EXIT`
#: equal at `1` in both readings.**
#:
#: ⚠️ **The fixture needs no new plant: `feat/live` is already `1` ahead and held by nobody.**
ADRIFT = "feat/live"


def _adrift(printed: str) -> str:
    """The gate's other half, selected on ITS OWN anchor and on no other line's."""
    return next(line for line in printed.split("\n") if "held by no checkout" in line.lower())


def test_planted_an_UNMERGED_branch_HELD_BY_NO_CHECKOUT_is_NAMED_and_the_GATE_is_UNMOVED(
    repository: Path,
) -> None:
    """⛔ DIRECTION 1 — the reading the gate could not take, and the gate did not change.

    ⚠️ **Expected, written before the run:** ⛔ **`feat/live` is ABSENT from
    `dispatched and UNNAMED by any row` — which is UNCHANGED and still correct, its
    population being live checkouts — and PRESENT on the line below it.** ⭐ **Refuted if it
    appears on the gate line: that is the widening this row REFUSED, because a branch
    somebody is sitting on and a branch nobody is sitting on need different actions.**
    """
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    ahead = Graph.read(repository, RELEASE).ahead(ADRIFT)
    assert ahead is not None and ahead > 0, f"⛔ born vacuous: {ADRIFT} is {ahead} ahead"
    _code, printed = _run(repository)
    gate = next(line for line in printed.split("\n") if "dispatched and" in line)
    assert ADRIFT not in gate, f"⛔ the GATE was widened, and that was refused — {gate}"
    assert "population: LIVE CHECKOUTS only" in gate, "⭐ and the gate NAMES its own half"
    adrift = _adrift(printed)
    # ⚠️ CORRECTED AGAINST THE RUN: my expectation said `(1)` and the fixture carries THREE
    # branches that are ahead and held by nobody — `fix/W4` and `fix/Wmoved` share a tip.
    # ⭐ The correction is the reading's, not the instrument's, and it is the widened
    # population doing exactly what it is for.
    assert "named by no row (3): feat/live fix/W4 fix/Wmoved" in adrift, adrift
    assert "NOT folded into the exit code" in adrift, "⛔ the refusal, printed where it acts"


def test_the_CONTROL_with_the_POPULATION_reverted_to_LIVE_CHECKOUTS_the_LINE_GOES_SILENT(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⭐ Ruling 266's form — a control that MUST go silent, or the reading is ASSERTED.

    ⛔ **One tree, one branch, TWO readings, and the ONLY variable is whether the population
    comes from `heads()` or from the checkouts.** ⚠️ **`Graph.heads` is patched to answer
    with the live branches alone, which is the pre-change population expressed exactly** —
    ⭐ **the line then reads `none.` while `feat/live` still exists and is still ahead, so
    the speech above is caused by the widened population and not by the fixture.**
    """
    write_board(repository, "")
    _code, printed = _run(repository)
    assert ADRIFT in _adrift(printed), "⛔ born vacuous: it must speak before it can go silent"
    live = set(Graph.read(repository, RELEASE).checkouts())
    monkeypatch.setattr(Graph, "heads", lambda self: sorted(live))
    _code, reverted = _run(repository)
    silent = _adrift(reverted)
    assert ADRIFT not in silent, f"⛔ the control did not isolate the population — {silent}"
    assert "held by no checkout, named by no row: none." in silent, silent


def test_the_LINE_REPORTS_and_the_EXIT_CODE_DOES_NOT_MOVE_WITH_IT(repository: Path) -> None:
    """⚠️ Explicitly refused: this NOTICE does not carry `corroborate`'s exit code.

    ⛔ **Moving it would change every merge's disclosure in this project, which is a ruling
    and not a detail** — ⭐ **so it is asserted rather than intended: the line NAMES a branch
    and the run still exits `CORROBORATED`.**
    """
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    code, printed = _run(repository)
    assert ADRIFT in _adrift(printed), "⛔ born vacuous: nothing was named, so nothing is proved"
    assert code == CORROBORATED, printed


def test_the_THREE_EXEMPTIONS_TRANSFER_to_the_new_population_and_fix_W_STILL_REACHES_IT(
    repository: Path,
) -> None:
    """⛔ DIRECTION 2 — the same three exemptions, and Ruling 319's refusal held.

    ⚠️ **Expected, written before the run:** an office branch and a `trial/*` branch that are
    AHEAD and held by NO checkout are ABSENT from this line, and a `fix/W*` branch in the
    same state is PRESENT. ⛔ **Ruling 319 refuses the `fix/*` widening because it would
    empty the population the gate exists to read, and that refusal has to hold on BOTH
    halves of the gate or it holds on neither.**
    """
    for branch in ("chore/po-round99", "trial/round99", "fix/W99-adrift", "chore/po-round9-x"):
        assert git(repository, "checkout", "-q", "-b", branch).returncode == 0
        commit(repository, f"{branch.replace('/', '-')}.txt", "a round's record\n")
        assert git(repository, "checkout", "-q", RELEASE).returncode == 0
        ahead = Graph.read(repository, RELEASE).ahead(branch)
        assert ahead is not None and ahead > 0, f"⛔ born vacuous: {branch} is {ahead} ahead"
    write_board(repository, "")
    _code, printed = _run(repository)
    adrift = _adrift(printed)
    assert "fix/W99-adrift" in adrift, f"⛔ Ruling 319's refusal did not hold here — {adrift}"
    assert "chore/po-round9-x" in adrift, f"⛔ `W136`: a topic branch is not exempt — {adrift}"
    assert "chore/po-round99" not in adrift and "trial/round99" not in adrift, adrift


def test_planted_a_branch_git_DECLINED_to_count_that_NO_CHECKOUT_HOLDS_is_PRINTED(
    repository: Path,
) -> None:
    """⛔ `W115`'s coercion, refused in the new population before it can be written.

    ⚠️ **A ref written to a sha no object carries: `rev-parse --verify` answers and
    `rev-list --count` does not** (`conftest.unreadable`). ⭐ **A `n is not None and n > 0`
    filter would drop it in SILENCE, which is the shape `ahead(branch) or 0` had** — so it
    gets its own printed line, ⛔ **and NOT the exit code, whose fold Ruling 216 built over
    LIVE CHECKOUTS.**
    """
    branch = unreadable(repository, "fix/Wnocount")
    write_board(repository, "")
    code, printed = _run(repository)
    declined = next(line for line in printed.split("\n") if "git DECLINED to answer" in line)
    assert f"1 branch(es) NO WORKTREE IS ON: {branch}" in declined, declined
    assert code == CORROBORATED, "⛔ the fold was widened, and that was refused"
