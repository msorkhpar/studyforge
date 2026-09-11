"""Mirror of `tools/quality/board/corroborate.py` (R12) — the COMMAND and its THREE exit codes.

⛔ **The per-branch verdict is `test_verdict.py`'s and the git readings are
`test_graph.py`'s.** ⭐ **This module asserts what the command PRINTS, which row
count it reduces to, and — `W111` — **which of the three exit codes it returns for
which of the four populations it can meet.**

⛔ **The subject is a SYNTHESISED repository** (`conftest.py`), and that is Ruling
191(b) rather than convenience: ⚠️ **between waves every population this module reads
is empty**, so a control drawn from the live tree is born vacuous exactly when a
close run is taken.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.quality.board.corroborate import (
    CORROBORATED,
    NOT_AUTHORITATIVE,
    REFUTED,
    corroborate,
    main,
)
from tools.quality.board.graph import Graph
from tools.quality.board.register import BOARD
from tools.workspace import git

from .conftest import RELEASE, unreadable, write_board

#: ⛔ A header that declares NONE of the three roles — the CTO's round-50 plant.
RENAMED = "| Row | Owner | Where | Commits on it | Phase |\n|---|---|---|---|---|\n"


def _run(root: Path, release: str = RELEASE) -> tuple[int, str]:
    lines, code = corroborate(root, release)
    return code, "\n".join(lines)


# --------------------------------------------------------------------------
# Reading 1 — PLANTED, over the synthesised population
# --------------------------------------------------------------------------


def test_planted_a_TERMINAL_branch_is_REFUTED_and_the_two_steps_are_PRINTED(
    repository: Path,
) -> None:
    """⛔ Ruling 189(d): the ref is derived from the BRANCH, in two printed steps.

    ⚠️ **The first step is an ASSERTION** — the row claims a branch — ⭐ **and it
    owes clause (c)'s observation before the second step means anything.**
    """
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n")
    code, printed = _run(repository)
    assert code == REFUTED
    assert "row -> branch (ASSERTION, Ruling 189(c))" in printed
    assert "REFUTED: fix/Wmerged is TERMINAL" in printed
    assert Graph.read(repository, RELEASE).terminal("fix/Wmerged") in printed
    assert "1 of 1 rows REFUTED" in printed


def test_planted_A_LEAKED_WORKTREE_NO_LONGER_KEEPS_A_SPENT_ROW_GREEN(repository: Path) -> None:
    """⛔ **`W110`, AT THE COMMAND LEVEL AND WITH ONE VARIABLE CHANGED.**

    ⚠️ **MEASURED by the coordinator at the then-tip: with two developer worktrees
    standing, `corroborate` read `0 of 2 rows REFUTED, exit 0` and both rows
    `CORROBORATED` — although both branches were already merged and `0` ahead.**
    ⭐ **Retiring exactly those two worktrees, nothing else changed, read `2 of 2
    REFUTED, exit 1`.** ⛔ **The two readings must now be EQUAL.**
    """
    row = "| `W42` | Dev | `leak`, `fix/Wleak` | 0 | in flight |\n"
    write_board(repository, row)
    standing, standing_printed = _run(repository)
    assert git(repository, "worktree", "remove", str(repository.parent / "leak")).returncode == 0
    retired, retired_printed = _run(repository)
    assert standing == retired == REFUTED, (standing_printed, retired_printed)
    assert "1 of 1 rows REFUTED" in standing_printed and "1 of 1 rows REFUTED" in retired_printed


def test_planted_a_row_that_names_NOTHING_git_has_is_REFUTED_by_clause_c(
    repository: Path,
) -> None:
    """⛔ A misspelled branch and an unmerged branch both return empty from a grep.

    ⭐ **So existence is checked as its OWN command**, and a row whose claim
    resolves to nothing is refuted on the assertion rather than passed over.
    """
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wtypo` | **+3** | in flight |\n")
    code, printed = _run(repository)
    assert code == REFUTED
    assert "unresolved ['wt/x', 'fix/Wtypo']" in printed, "⛔ BOTH tokens, in order"
    assert "names no branch this checkout has" in printed


def test_planted_a_HELD_checkout_is_CORROBORATED_and_is_the_positive_row(
    repository: Path,
) -> None:
    """⭐ Ruling 191(c): a synthesised control owes its own POSITIVE row.

    ⛔ **Without one, every assertion below is *"the instrument said no"* and
    nothing shows it can say yes.**
    """
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    code, printed = _run(repository)
    assert code == CORROBORATED, printed
    assert "CORROBORATED: feat/held is checked out at held" in printed
    assert "0 of 1 rows REFUTED" in printed


def test_planted_a_row_declaring_NO_STARTED_STATE_owes_no_carrier(repository: Path) -> None:
    """⭐ `todo`, `done`, `accepted`, `routed` and `blocked` owe nothing, and it is printed."""
    write_board(repository, "| `W42` | Dev | none | 0 | `todo` — next wave |\n")
    code, printed = _run(repository)
    assert code == CORROBORATED
    assert "not a started state; no carrier is owed." in printed


def test_no_reading_prints_an_absolute_path(repository: Path) -> None:
    """⛔ R7: `git worktree list` answers in absolute paths and an absolute path is personal data.

    ⭐ Asserted against the fixture's own root, so the test needs no home
    directory of its own to compare against.
    """
    assert git(repository, "worktree", "add", "-q", str(repository.parent / "held2"), "trial/spent")
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    lines, _code = corroborate(repository, RELEASE)
    for line in lines:
        assert str(repository) not in line
        assert str(repository.parent) not in line


def test_the_row_id_grep_is_a_LOWER_BOUND_and_the_branch_derivation_is_not(
    repository: Path,
) -> None:
    """⛔ Measured: `--grep '<row id>'` reads `0` for every row that shared a branch.

    ⚠️ **All three of `W85`, `W86` and `W87` returned nothing**, and `W86` is named
    in no commit message on its own branch at all. ⭐ **This fixture reproduces the
    shape rather than citing it**: one branch, one merge message, and a row id the
    message never mentions.
    """
    by_row = git(repository, "log", "--merges", "--first-parent", "--grep=W42", RELEASE)
    assert by_row.stdout.strip() == "", "⛔ the lower bound, reading 0 on a real close"
    graph = Graph.read(repository, RELEASE)
    assert graph.terminal("fix/Wmerged"), "⭐ the branch derivation finds it"


# --------------------------------------------------------------------------
# Reading 2 — `W111`: FOUR populations, and the EXIT CODE tells them apart
# --------------------------------------------------------------------------


def test_planted_an_UNREADABLE_DECLARED_TABLE_IS_EXIT_2_AND_NOT_A_PASS(
    repository: Path,
) -> None:
    """⛔ **`PO-40/4`, and it is the sharp half of `W111`.**

    ⚠️ **MEASURED by the PO at `1c5e913`: this command printed Ruling 191(a)'s own
    sentence — *nothing was read, which is not the same answer as nothing being in
    flight* — and returned `0`, THE PASS CODE**, from
    `return lines, REFUTED if refuted else CORROBORATED` with `rows == []`.
    ⛔ **A wave-close gate reading the exit code was green over exactly the board
    `W111` exists to refuse.**
    """
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n")
    (repository / BOARD).write_text(
        (repository / BOARD)
        .read_text(encoding="utf-8")
        .replace("| Row | Owner | Checkout | Commits ahead | State |", RENAMED.split("\n")[0]),
        encoding="utf-8",
    )
    code, printed = _run(repository)
    assert code == NOT_AUTHORITATIVE
    assert code not in (CORROBORATED, REFUTED), "⛔ it must DIFFER from both verdicts"
    assert "NOT AUTHORITATIVE — the board DECLARES an observation table at line" in printed
    assert "used to return the PASS code for it" in printed


def test_planted_a_board_with_NO_MARKER_is_exit_2_and_names_the_RAMP(repository: Path) -> None:
    """⛔ `W111`: the header branch survives, and a board that NEEDS it is not authoritative.

    ⭐ **The markers are this board's contract since the PO's round-40 edit**
    (`board.md`, ruled round 50), ⚠️ **so their absence is this instrument failing to
    read THIS board rather than a board with nothing to say** — and that is exit `2`,
    not exit `0`.
    """
    write_board(
        repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n", delimited=False
    )
    code, printed = _run(repository)
    assert code == NOT_AUTHORITATIVE
    assert "Ruling 196(b) header RAMP" in printed
    assert "read 1 rows" in printed, "⭐ what it DID read is printed, never hidden"


def test_planted_a_DECLARED_and_READABLE_EMPTY_table_is_a_REAL_ANSWER_and_exit_0(
    repository: Path,
) -> None:
    """⭐ The case that must stay a PASS, or `W111` fires on every correct wave close.

    ⛔ **MEASURED distinction: the author DECLARED a block, DECLARED its columns, and
    put no row in it.** ⚠️ **That is *nothing is in flight*, which the old instrument
    could not tell from *I read nothing* — and telling them apart is the whole of the
    delimiter's value.**
    """
    write_board(repository, "")
    code, printed = _run(repository)
    assert code == CORROBORATED
    assert "DECLARED, READ, and carries no row" in printed
    assert "0 observation rows" in printed
    assert "NOT AUTHORITATIVE" not in printed


def test_the_FOUR_populations_return_THREE_DISTINCT_codes_and_FOUR_distinct_sentences(
    repository: Path,
) -> None:
    """⛔ Ruling 196(a)'s pass condition: a claimed code owes its INHABITATION.

    ⭐ **All four populations are run in one test so the readings are compared rather
    than asserted one at a time** — ⚠️ which is what caught the two that used to share
    exit `0`.

    ## ⛔ `W115/1` — THIS NAME OVER-CLAIMED, AND `W132` MADE IT TRUE BY MOVING THE POPULATION

    ⚠️ **The `codes` dict asserted below used to read
    `{CORROBORATED, CORROBORATED, NOT_AUTHORITATIVE, NOT_AUTHORITATIVE}`** — ⛔ **FOUR
    populations, FOUR sentences and TWO distinct codes, under a name claiming THREE.**
    ⭐ **The GATE was always sound: `REFUTED` is inhabited in four sibling tests and
    three-way distinctness is asserted separately. Only the NAME over-claimed, which is
    Ruling 208's class in a test name for the first time.**

    ⛔ **THE NAME IS NOT RENAMED, and the ground is `W74/2`: a name two FROZEN records
    quote is not renamed.** ⭐ **RECEIVED from the CTO's round-59 record §4b, MEASURED by
    them at `b33e01a` — `handoffs/W111.md:134` and
    `handoffs/CTO-2026-09-10-round52.md:731` both already carried this name on the day
    `rows/W115.md` claimed it was cited by none, so the claim was false at the INSTANT it
    was written rather than stale.** ⛔ **`W74/2` is the FIFTH unreversed refusal in its
    family, so the rule binds and the remedy is the other one.**

    ⭐ **So the DECLARED AND READ population is now a row git REFUTES, and the four
    populations really do return three distinct codes.** ⚠️ **Nothing is lost: the
    CORROBORATED-with-rows reading is
    `test_planted_a_HELD_checkout_is_CORROBORATED_and_is_the_positive_row`'s, by name.**
    """
    # ⛔ `fix/Wmerged` is TERMINAL in the fixture — absorbed by a `--no-ff` merge and
    # checked out nowhere — so this population is REFUTED rather than CORROBORATED.
    refuted = "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 1 | in flight |\n"
    row = "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n"
    readings = {}
    write_board(repository, refuted)
    readings["declared and read"] = _run(repository)
    write_board(repository, "")
    readings["declared and empty"] = _run(repository)
    write_board(repository, row, delimited=False)
    readings["no marker at all"] = _run(repository)
    write_board(repository, row)
    (repository / BOARD).write_text(
        (repository / BOARD)
        .read_text(encoding="utf-8")
        .replace("| Row | Owner | Checkout | Commits ahead | State |", RENAMED.split("\n")[0]),
        encoding="utf-8",
    )
    readings["declared and unreadable"] = _run(repository)
    codes = {name: code for name, (code, _printed) in readings.items()}
    assert codes == {
        "declared and read": REFUTED,
        "declared and empty": CORROBORATED,
        "no marker at all": NOT_AUTHORITATIVE,
        "declared and unreadable": NOT_AUTHORITATIVE,
    }, codes
    # ⛔ `W115/1`, discharged as a `W132` clause: the NAME says THREE and the reading is
    # now THREE. ⭐ Asserted as a count of DISTINCT codes, derived rather than retyped, so
    # the name cannot drift from the population again.
    assert len(set(codes.values())) == 3, codes
    assert len(codes) == 4, codes
    lasts = {name: printed.split("\n")[-1] for name, (_code, printed) in readings.items()}
    assert len(set(lasts.values())) == 4, lasts


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE, and it must DIFFER: exit 2, not exit 0
# --------------------------------------------------------------------------


def test_impossible_a_release_branch_that_cannot_exist_is_NOT_AUTHORITATIVE(
    repository: Path,
) -> None:
    """⛔ Ruling 53's fourth state, and Ruling 191's reason for needing it.

    ⚠️ **A check that shelled into git and found nothing would return the PASS
    reading from an empty population.** ⭐ **Here it exits `2`**, which is neither
    *the board is right* nor *the board is wrong*.
    """
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n")
    lines, code = corroborate(repository, "release/no-such-branch-60713")
    assert code == NOT_AUTHORITATIVE
    assert code not in (CORROBORATED, REFUTED), "⛔ it must DIFFER from both verdicts"
    assert "NOT AUTHORITATIVE" in lines[0] and "not a pass" in lines[0]


def test_impossible_a_checkout_with_no_board_is_NOT_AUTHORITATIVE(tmp_path: Path) -> None:
    """⚠️ A tree that is not this repository has nothing to corroborate, and says so."""
    lines, code = corroborate(tmp_path, RELEASE)
    assert code == NOT_AUTHORITATIVE
    assert "nothing to corroborate" in lines[0]


def test_the_command_line_returns_the_code_and_prints_every_step(
    repository: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """⭐ The entry point a wave's close runs, asserted rather than assumed."""
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n")
    code = main(["--root", str(repository), "--release", RELEASE])
    printed = capsys.readouterr().out
    assert code == REFUTED
    assert "row -> branch (ASSERTION, Ruling 189(c))" in printed
    assert "observations (" in printed, "the population comes before the verdict (Ruling 128)"


# --------------------------------------------------------------------------
# Reading 4 — `W115` / Ruling 216: the FOLD, and the third state survives it
# --------------------------------------------------------------------------


def test_LIVE_a_fixture_with_no_plant_reaches_only_EXIT_0_AND_1(repository: Path) -> None:
    """⛔ **The CONTROL, and `W115`'s own row demands it**: this must not become a rule
    that every unreadable thing exits `2`.

    ⭐ **Expected, written before the run:** over the unplanted fixture a corroborating
    row reads `0`, a terminal row reads `1`, and ⛔ **`NOT AUTHORITATIVE` appears in
    NEITHER** — ⚠️ **a third state that fired here would fire on every wave the PO closed
    correctly, which is Ruling 179's cost** (`board.md`, ruled round 50).
    """
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    good, good_printed = _run(repository)
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n")
    spent, spent_printed = _run(repository)
    assert (good, spent) == (CORROBORATED, REFUTED), (good, spent)
    assert "NOT AUTHORITATIVE" not in good_printed and "NOT AUTHORITATIVE" not in spent_printed
    assert "live checkouts git could not count: none." in good_printed
    assert "0 NOT ANSWERABLE and 0 live checkout(s) git could not count" in good_printed


def test_planted_a_ROW_whose_branch_GIT_CANNOT_COUNT_exits_2_AND_NOT_1(
    repository: Path,
) -> None:
    """⛔ **`W115`, site 1, AT THE EXIT CODE — the FALSE REFUTATION Ruling 216 names.**

    ⚠️ **Expected, written before the run:** the shipped fold had two row values, so *git
    could not answer about this branch* landed on `REFUTED` and the run exited `1` while
    printing *is 0 ahead* — ⛔ **a refutation of a row nothing was observed about, from a
    number git never gave.** ⭐ **It is exit `2` now, and the sentence names the defect.**
    """
    branch = unreadable(repository, "fix/W4")
    assert Graph.read(repository, RELEASE).ahead(branch) is None, "⛔ born vacuous"
    write_board(repository, f"| `W42` | Dev | `wt/x`, `{branch}` | 0 | in flight |\n")
    code, printed = _run(repository)
    assert code == NOT_AUTHORITATIVE
    assert code not in (CORROBORATED, REFUTED), "⛔ it must DIFFER from BOTH verdicts"
    assert "NOT ANSWERABLE: git could not count" in printed
    assert "0 of 1 rows REFUTED by git, 1 NOT ANSWERABLE" in printed
    # ⚠️ `is 0 ahead`, not `0 ahead`: the observation READING legitimately prints
    # `3 with a checkout, 0 ahead` about the board's own cells, and that is a real count.
    assert "is 0 ahead" not in printed, "⛔ THE DEFECT: a count git never gave"
    assert "is None commits ahead" not in printed, "⛔ nor the other site's spelling of it"


def test_planted_a_LIVE_CHECKOUT_git_cannot_count_is_NOT_filed_under_BY_CONSTRUCTION(
    repository: Path,
) -> None:
    """⛔ **`W115`, site 3 — and site 2's exit code in the same plant.**

    ⚠️ **Expected, written before the run:** `_unnamed()` coerced `ahead(branch) or 0`, so
    a FAILED reading was filed under *invisible to git BY CONSTRUCTION (Ruling 130), 0
    commits ahead* — ⛔ **the one line whose whole job is to say *this is unreadable*, and
    the one place a reviewer has already agreed to ignore a `0`.** ⭐ **Ruling 130's
    exemption is EARNED by a checkout with no commit; git declining to answer is not that.**

    ⭐ **`feat/held` is the plant because it is the fixture's one branch that is both
    CHECKED OUT and AHEAD** — ⚠️ so the reading moves from *a real count* to *no count*
    with one variable changed, and the board does not name it.
    """
    branch = unreadable(repository, "feat/held")
    graph = Graph.read(repository, RELEASE)
    assert graph.checkouts().get(branch), "⛔ born vacuous: the plant must BE checked out"
    assert graph.ahead(branch) is None, "⛔ born vacuous: git must GENUINELY decline"
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n")
    code, printed = _run(repository)
    assert code == NOT_AUTHORITATIVE, "⛔ site 2 and site 3 both used to reach 0 or 1"
    assert "git COULD NOT COUNT *commits ahead* for 1 live checkout(s): held" in printed
    exemption = next(line for line in printed.split("\n") if "BY CONSTRUCTION" in line)
    assert "held" not in exemption, (
        f"⛔ THE DEFECT: the failed reading used to be COUNTED on this line — {exemption}"
    )
    assert "named by no row: 1 — leak" in exemption, exemption
    assert "1 live checkout(s) git could not count" in printed


def test_the_THREE_ROW_ANSWERS_and_the_THREE_PROCESS_CODES_are_COMPARED_in_one_reading(
    repository: Path,
) -> None:
    """⛔ Ruling 216: the exit code is a FOLD of the row answers, and the fold PRESERVES the third.

    ⭐ **All three populations in ONE test so the codes are compared rather than asserted
    one at a time** — ⚠️ which is the form that caught the two that used to share exit `0`
    (`W111`), applied to the two that used to share exit `1`.
    """
    readings = {}
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    readings["answerable and corroborated"] = _run(repository)
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n")
    readings["answerable and refuted"] = _run(repository)
    branch = unreadable(repository, "fix/W4")
    write_board(repository, f"| `W42` | Dev | `wt/x`, `{branch}` | 0 | in flight |\n")
    readings["git could not answer"] = _run(repository)
    codes = {name: code for name, (code, _printed) in readings.items()}
    assert codes == {
        "answerable and corroborated": CORROBORATED,
        "answerable and refuted": REFUTED,
        "git could not answer": NOT_AUTHORITATIVE,
    }, codes
    assert len(set(codes.values())) == 3, "⛔ THREE answers, and the fold keeps them apart"
    lasts = {name: printed.split("\n")[-1] for name, (_code, printed) in readings.items()}
    assert len(set(lasts.values())) == 3, lasts


def test_a_row_REFUTED_and_a_row_UNANSWERABLE_in_ONE_BOARD_exits_2_and_not_1(
    repository: Path,
) -> None:
    """⛔ **The precedence, asserted rather than assumed:** `NOT ANSWERABLE` DOMINATES.

    ⚠️ **A run that folded the unanswerable row onto the refuted one would report `2 of 2
    REFUTED, exit 1`** — ⭐ **and a wave close reading that exit would conclude the board
    was measured and wrong, when one of its two rows was never measured at all.**
    """
    branch = unreadable(repository, "fix/W4")
    write_board(
        repository,
        f"| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n"
        f"| `W43` | Dev | `wt/x`, `{branch}` | 0 | in flight |\n",
    )
    code, printed = _run(repository)
    assert code == NOT_AUTHORITATIVE
    assert "1 of 2 rows REFUTED by git, 1 NOT ANSWERABLE" in printed
    assert "REFUTED: fix/Wmerged is TERMINAL" in printed, "⭐ the refutation is still PRINTED"

# --------------------------------------------------------------------------
# ⛔ `PO-46/14` — the TWO ROW VERDICTS the exit code folds are NAMED, even when EMPTY
# --------------------------------------------------------------------------


def test_planted_the_REFUTED_ROWS_are_NAMED_and_the_other_fold_prints_its_EMPTY_form(
    repository: Path,
) -> None:
    """⛔ `PO-46/14`: a round-45 brief demanded an output line that DID NOT EXIST.

    ⚠️ **MEASURED at `51dee3b`, role `wt/dev1`: `grep -rn "REFUTED ROWS" tools/ src/ tests/`
    is ABSENT (exit 1) while the string is quoted in `docs/tasks/BOARD-ARCHIVE.md` and
    `docs/tasks/handoffs/PO-2026-09-11-round45.md`.** ⛔ **A fabricated REQUIREMENT induced a
    fabricated MEASUREMENT, and a CTO review reproduced every figure around the line without
    catching the line itself** — Ruling 264(a)'s own subject.

    ⭐ **BOTH fold lines are asserted in ONE reading**, so the inhabited form and the empty
    form are compared rather than asserted one at a time: ⛔ **`fix/Wmerged` is TERMINAL in
    the fixture, so this row is REFUTED and NO row is unanswerable.**
    """
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 1 | in flight |\n")
    code, printed = _run(repository)
    assert code == REFUTED
    assert "  ⛔ rows REFUTED by git (1): `W42`" in printed, printed
    assert "  rows git could not answer about: none." in printed, (
        "⛔ the OTHER fold population owes its empty form in the same reading"
    )
    # ⭐ The subject is printed as the BOARD WROTE it, backticks included, because a reader
    # greps the board for what this line says.
    assert "`W42`" in printed and "rows REFUTED by git (1): W42" not in printed


def test_planted_NO_REFUTED_ROW_still_prints_the_LINE_which_is_the_whole_of_the_clause(
    repository: Path,
) -> None:
    """⭐ THE DIRECTION THE CLAUSE IS ABOUT: the empty case PRINTS A LINE AT ALL.

    ⛔ **Before this, a run with nothing refuted said nothing about refuted rows except a
    `0` inside the closing summary** — ⚠️ **while FIVE branch-side populations each named
    theirs and said `none.` when empty.** ⭐ **`feat/held` is the fixture's ahead-and-held
    branch, so this row CORROBORATES and both fold lines are empty.**
    """
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    code, printed = _run(repository)
    assert code == CORROBORATED
    assert "  rows refuted by git: none." in printed, printed
    assert "  rows git could not answer about: none." in printed, printed


def test_planted_an_UNANSWERABLE_ROW_is_NAMED_on_its_OWN_line_and_NOT_on_the_refuted_one(
    repository: Path,
) -> None:
    """⛔ Ruling 216's third answer gets a POPULATION and not only a counter.

    ⚠️ **Fixing the refuted half alone would have shipped the identical asymmetry one
    population over**, which is Ruling 258's shape: a list read as exhaustive that is not.
    ⭐ **`NOT_ANSWERABLE` DOMINATES, so this row is on its own line and the refuted line
    reads `none.` — which is the pair that proves the two lines are not one line twice.**
    """
    branch = unreadable(repository, "fix/W4")
    assert Graph.read(repository, RELEASE).ahead(branch) is None, "⛔ born vacuous"
    write_board(repository, f"| `W42` | Dev | `wt/x`, `{branch}` | 0 | in flight |\n")
    code, printed = _run(repository)
    assert code == NOT_AUTHORITATIVE
    assert "  ⛔ rows NOT ANSWERABLE (1): `W42`" in printed, printed
    assert "  rows refuted by git: none." in printed, (
        "⛔ a row git could not read is NOT a refuted row — that fold is `W115`'s whole subject"
    )


def test_impossible_neither_FOLD_LINE_appears_for_a_population_that_does_not_EXIST(
    repository: Path,
) -> None:
    """⛔ The IMPOSSIBLE reading, and it DIFFERS from the empty-form pass.

    ⭐ **A DECLARED, READ, EMPTY `<!-- inflight -->` block keeps its ONE sentence and gains
    no second one:** ⚠️ **two lines saying `none.` about a population that has no members to
    have is the `0 = 0` the whole idiom exists to refuse** (Ruling 48). ⛔ **And a table that
    did NOT READ refuses before the loop runs, so it cannot reach either line either.**
    """
    write_board(repository, "")
    code, printed = _run(repository)
    assert code == CORROBORATED
    assert "refuted by git" not in printed, printed
    assert "could not answer about" not in printed, printed
    assert "DECLARED, READ, and carries no row" in printed, "⭐ the ONE sentence it does keep"
    row = "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n"
    write_board(repository, row, delimited=False)
    ramp_code, ramp_printed = _run(repository)
    assert ramp_code == NOT_AUTHORITATIVE
    assert "refuted by git" not in ramp_printed, "⛔ a refusal returns before the fold"
