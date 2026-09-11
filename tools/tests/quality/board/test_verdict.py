"""Mirror of `tools/quality/board/verdict.py` (R12) — ⛔ `W110`, INHABITED IN BOTH DIRECTIONS.

⛔ **The defect this module closes was measured with ONE VARIABLE CHANGED, and the
test reproduces the variable rather than citing the reading:** ⭐ **`fix/Wleak` is
absorbed by a merge AND held by a checkout**, and the shipped verdict returned
`CORROBORATED … is 0 commits ahead` for exactly that shape.
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.board.graph import Graph
from tools.quality.board.observation import read
from tools.quality.board.verdict import claim, tokens, verdict
from tools.tests.quality.board.support import board

from .conftest import RELEASE


def _row(cell: str, state: str = "in flight") -> object:
    """One observation row, parsed from the board shape the PO actually authors."""
    text = board(f"| `W42` | Dev | {cell} | 0 | {state} |\n", delimited=True)
    return read(text).rows[0]


def _judge(repository: Path, cell: str, branch: str) -> tuple[bool, str]:
    graph = Graph.read(repository, RELEASE)
    live = graph.checkouts()
    answer = verdict(claim(_row(cell), graph, live), branch, graph, live)
    return answer.refuted, "\n".join(answer.lines)


# --------------------------------------------------------------------------
# Reading 1 — the defect, PLANTED and inhabited with one variable changed
# --------------------------------------------------------------------------


def test_planted_a_TERMINAL_branch_THAT_IS_CHECKED_OUT_is_REFUTED(repository: Path) -> None:
    """⛔ **`W110` and `PO-40/1`: the live-checkout arm used to discharge this row.**

    ⚠️ **MEASURED by the PO at `1c5e913`, one variable changed:** a worktree planted
    outside every checkout on `feat/SF-26-goldens` — MERGED at `8d17314`, `0` ahead —
    moved the reading from `2 of 2 REFUTED, exit 1` to `1 of 2`, printing
    `⭐ CORROBORATED … is 0 commits ahead` for a spent branch.

    ⭐ **The ORDER is the fix** (Ruling 199, `docs/conventions/board.md`): terminality
    is consulted BEFORE the checkout, because no checkout can make an absorbed branch
    in flight again.
    """
    graph = Graph.read(repository, RELEASE)
    assert "fix/Wleak" in graph.checkouts(), "⛔ born vacuous: the plant must BE checked out"
    refuted, printed = _judge(repository, "`leak`, `fix/Wleak`", "fix/Wleak")
    assert refuted
    assert "REFUTED: fix/Wleak is TERMINAL" in printed
    assert "checked out at leak" in printed, "⭐ the checkout is NAMED and still refuted"
    assert "Ruling 199" in printed


def test_planted_THE_SAME_BRANCH_WITH_THE_WORKTREE_GONE_reads_the_same_way(
    repository: Path,
) -> None:
    """⭐ The other direction of the same variable: retiring the worktree must not MOVE it.

    ⛔ **That is the whole point of the fix.** ⚠️ **Before it, the two readings
    differed — which is how a leaked worktree kept a row green and how retiring it
    turned the row red with nothing else changed.**
    """
    held, held_printed = _judge(repository, "`leak`, `fix/Wleak`", "fix/Wleak")
    assert Graph.read(repository, RELEASE).checkouts().get("fix/Wleak")
    from tools.workspace import git

    assert git(repository, "worktree", "remove", str(repository.parent / "leak")).returncode == 0
    gone, gone_printed = _judge(repository, "`leak`, `fix/Wleak`", "fix/Wleak")
    assert held == gone is True, "⛔ the verdict may not depend on whether a worktree stands"
    assert "checked out at leak" in held_printed
    assert "checked out nowhere" in gone_printed


def test_planted_the_POSITIVE_row_still_CORROBORATES(repository: Path) -> None:
    """⭐ Ruling 191(c): a synthesised control owes its own POSITIVE row.

    ⛔ **Without one, every assertion here is *the instrument said no* and nothing
    shows it can say yes** — ⚠️ and a predicate that refuted everything would have
    passed a test suite that only planted failures.
    """
    refuted, printed = _judge(repository, "`held`, `feat/held`", "feat/held")
    assert refuted is False
    assert "CORROBORATED: feat/held is checked out at held and is 1 commits ahead" in printed


def test_planted_a_branch_AHEAD_with_no_checkout_CORROBORATES(repository: Path) -> None:
    """⭐ The second corroborating arm, untouched by `W110`: commits are their own answer."""
    refuted, printed = _judge(repository, "`feat/live`", "feat/live")
    assert refuted is False
    assert "is 1 commits ahead of" in printed


# --------------------------------------------------------------------------
# Reading 2 — `PO-40/2`: the claimed checkout is COMPARED, and is a NOTICE
# --------------------------------------------------------------------------


def test_planted_a_CLAIMED_CHECKOUT_THAT_DID_NOT_ANSWER_is_a_NOTICE_and_NOT_A_REFUSAL(
    repository: Path,
) -> None:
    """⛔ `PO-40/2`: the claim was parsed, PRINTED, and never compared.

    ⚠️ **MEASURED by the PO: a checkout named `plant-sf26` corroborated a row claiming
    `wt/dev1`** — ⛔ **so the false pass did not even require the named worktree to
    exist.** ⭐ **Both names are printed now and NEITHER refutes**, because office
    worktrees are legitimately re-pointed between waves (`rows/W110.md`).
    """
    refuted, printed = _judge(repository, "`leak`, `feat/held`", "feat/held")
    assert refuted is False, "⛔ a name mismatch is bookkeeping, never a refutation"
    assert "NOTICE, not a refusal (`PO-40/2`)" in printed
    assert "the row CLAIMS leak" in printed
    assert "the checkout holding feat/held is held" in printed


def test_planted_a_row_that_names_a_BRANCH_AND_NO_CHECKOUT_says_which_arm_answered(
    repository: Path,
) -> None:
    """⭐ The quieter half of `PO-40/2`: *nothing was claimed* is also an answer.

    ⚠️ **A name that resolves to NEITHER a branch nor a checkout lands in
    `unresolved`**, so this arm covers the unresolvable claim as well as the empty
    one — ⛔ and both used to be silent.
    """
    refuted, printed = _judge(repository, "`feat/held`", "feat/held")
    assert refuted is False
    assert "the row names no checkout and the" in printed
    assert "from held" in printed
    _refuted, typo = _judge(repository, "`wt/nowhere`, `feat/held`", "feat/held")
    assert "the row names no checkout and the" in typo


def test_planted_the_BOARD_S_OWN_wt_IDIOM_does_NOT_raise_a_mismatch_notice(
    repository: Path,
) -> None:
    """⛔ THE PLANT THAT REFUTED MY FIRST COMPARISON, and it would have fired on the live board.

    ⚠️ **This board writes `` `wt/dev1` `` for a checkout whose DIRECTORY BASENAME is
    `dev1`** — the live tree's worktrees sit at `studyforge-wt/dev1` — ⛔ **so a
    comparison against the basename alone prints `PO-40/2`'s notice on every
    correctly-written row.** ⭐ **`designates` is therefore the SAME resolution the
    partition uses, and this is its negative control.**
    """
    from tools.workspace import git

    nested = repository.parent / "wt"
    assert (
        git(repository, "worktree", "add", "-q", str(nested / "dev9"), "feat/live").returncode == 0
    )
    refuted, printed = _judge(repository, "`wt/dev9`, `feat/live`", "feat/live")
    assert refuted is False
    assert "NOTICE, not a refusal" not in printed, printed


def test_the_claim_PARTITIONS_the_cell_by_OBSERVATION_and_not_by_NAME_SHAPE(
    repository: Path,
) -> None:
    """⛔ A reader cannot tell `wt/dev1` from `feat/SF-15-contents` by shape.

    ⭐ **So the partition is by what git RESOLVES**, and a classifier guessing from a
    prefix would have read a renamed worktree as a missing branch.
    """
    graph = Graph.read(repository, RELEASE)
    live = graph.checkouts()
    asserted = claim(_row("`held`, `feat/held`, `wt/typo`"), graph, live)
    assert asserted.branches == ("feat/held",)
    assert asserted.checkouts == ("held",)
    assert asserted.unresolved == ("wt/typo",)


def test_tokens_reads_the_code_spans_and_not_the_prose() -> None:
    """⭐ The board's own idiom for a carrier is a code span."""
    assert tokens("`wt/dev2`, `fix/W95-shared-origin-fixture`") == (
        "wt/dev2",
        "fix/W95-shared-origin-fixture",
    )
    assert tokens("none") == ()
    assert tokens("`wt/x`, `wt/x`") == ("wt/x",)


# --------------------------------------------------------------------------
# Reading 3 — the shapes are PRINTED, and a DISAGREEMENT says so
# --------------------------------------------------------------------------


def test_shape_B_and_shape_C_are_BOTH_PRINTED_on_every_judged_branch(repository: Path) -> None:
    """⛔ Ruling 199: `B` is printed beside `C` and the disagreements are PRINTED."""
    _refuted, printed = _judge(repository, "`fix/Wmerged`", "fix/Wmerged")
    assert "terminality (Ruling 199): graph `C`" in printed
    assert "message `B`" in printed
    assert "DISAGREE" not in printed, "⭐ these two agree, so nothing is claimed"


def test_a_branch_C_absorbed_and_B_CANNOT_SEE_prints_B_s_FALSE_NEGATIVE(
    repository: Path,
) -> None:
    """⛔ `B`'s false-negative population — 25 branches at `2d0cfe7`, pre-convention history."""
    refuted, printed = _judge(repository, "`fix/Wsilent`", "fix/Wsilent")
    assert refuted
    assert "message `B` none" in printed
    assert "DISAGREE: absorbed by a merge whose subject does not declare" in printed
    assert "`C` is the gate" in printed


def test_a_branch_B_NAMES_and_C_does_not_is_NOT_REFUTED_and_says_so(repository: Path) -> None:
    """⛔ The disagreement that must NOT become a refutation.

    ⚠️ **`chore/cto-round17` is this shape in the real repository and the CTO's record
    attributes it to the PREFIX mechanism** — ⭐ **MEASURED at `2d0cfe7`, it is not: a
    merge subject reading `Merge chore/cto-round17:` exists and the branch's TIP has
    moved since.** ⛔ **So the exact-match fix does NOT empty `B`'s false-positive
    population, and that is precisely why `B` may not be the gate.**
    """
    refuted, printed = _judge(repository, "`fix/Wmoved`", "fix/Wmoved")
    assert refuted is False
    assert "DISAGREE: a merge subject declares `Merge fix/Wmoved:`" in printed
    assert "NOT a refutation" in printed


def test_a_BARE_branch_and_a_FAST_FORWARDED_one_REACH_ONE_ARM_and_it_says_so(
    repository: Path,
) -> None:
    """⛔ THE DEAD ARM `W110` FOUND, and the honest sentence that replaced two.

    ⚠️ **`0` ahead IMPLIES `merge-base --is-ancestor`**, so the shipped `_verdict`'s
    final arm — the one carrying Ruling 130's sentence — was UNREACHABLE, and the old
    test that asserted it passed off `_unnamed`'s line instead. ⭐ **`feat/bare` (no
    commit of its own) and `fix/Wff` (merged by fast-forward) arrive at the SAME arm
    and CANNOT be separated by position**, so one sentence names both readings.
    """
    bare_refuted, bare = _judge(repository, "`feat/bare`", "feat/bare")
    ff_refuted, ff = _judge(repository, "`fix/Wff`", "fix/Wff")
    assert bare_refuted and ff_refuted
    for printed in (bare, ff):
        assert "BY CONSTRUCTION (Ruling 130)" in printed
        assert "merged by a FAST-FORWARD" in printed
        assert "ancestor: True" in printed


def test_the_verdict_carries_its_answer_as_a_FIELD_and_not_as_a_SUBSTRING(
    repository: Path,
) -> None:
    """⛔ The shipped form asked `any("REFUTED" in verdict …)` of its OWN output.

    ⚠️ **That is the same substring-for-a-predicate family Ruling 199 retired from
    `merge_of()`** — ⭐ **so the flag is a field, and a sentence may contain the word
    without being one.**
    """
    graph = Graph.read(repository, RELEASE)
    live = graph.checkouts()
    answer = verdict(claim(_row("`held`, `feat/held`"), graph, live), "feat/held", graph, live)
    assert answer.refuted is False
    assert isinstance(answer.lines, tuple), "⛔ frozen, so a caller cannot append to a verdict"
