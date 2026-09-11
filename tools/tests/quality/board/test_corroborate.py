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

from .conftest import RELEASE, write_board

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


def test_planted_the_OTHER_direction_work_git_sees_and_the_board_does_not_name(
    repository: Path,
) -> None:
    """⛔ The measured failure was BIDIRECTIONAL — stale rows present, live rows absent."""
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    _code, printed = _run(repository)
    assert "dispatched and UNNAMED by any row: feat/live" not in printed, (
        "feat/live has no checkout, so `worktree list` cannot see it either"
    )
    assert git(repository, "worktree", "add", "-q", str(repository.parent / "two"), "feat/live")
    _code, printed = _run(repository)
    assert "dispatched and UNNAMED by any row: feat/live" in printed


def test_planted_a_spent_trial_branch_is_the_reading_no_board_cell_carries(
    repository: Path,
) -> None:
    """⭐ The standing form, measured by the CTO at `0285a92` and `c3e2919`.

    ⛔ **Such a branch carries nothing unique and is invisible to `--no-merged` by
    construction** — ⚠️ **its only remaining effect is to read as dispatched work
    to a human, which is Ruling 189's subject with no cell to print it in.**
    """
    write_board(repository, "")
    _code, printed = _run(repository)
    assert "spent and deletable (1): trial/spent" in printed
    assert "ancestor of" in printed
    assert "trial/tmp branches still checked out: none." in printed


def test_planted_a_STANDING_trial_worktree_is_PRINTED_and_never_removed(
    repository: Path,
) -> None:
    """⚠️ Ruling 206(ii) named this line's own blind spot, and it routed it to `W110`.

    ⛔ **`name not in live` excluded exactly the shape that keeps a spent row
    green** — a trial worktree still standing — ⭐ **so it is printed separately, as a
    NOTICE**, because reporting a worktree you did not cut is never wrong and removing
    one always is.
    """
    assert (
        git(
            repository, "worktree", "add", "-q", str(repository.parent / "t"), "trial/spent"
        ).returncode
        == 0
    )
    write_board(repository, "")
    _code, printed = _run(repository)
    assert "trial/tmp branches STILL CHECKED OUT (1): trial/spent" in printed
    assert "never remove one you did not cut (Ruling 206(ii))" in printed
    assert "spent trial/tmp branches: none." in printed, "it is no longer *deletable*"


def test_the_blind_spot_is_COUNTED_AND_NAMED_rather_than_judged(repository: Path) -> None:
    """⚠️ *Just dispatched* and *an office checkout* are the same bytes to `git`.

    ⛔ **So a 0-commit checkout is named as UNREADABLE here** rather than reported
    as a defect — ⭐ the board is the only instrument that can tell them apart,
    which is the whole of Ruling 171.
    """
    assert git(repository, "worktree", "add", "-q", str(repository.parent / "office"), "feat/bare")
    write_board(repository, "")
    _code, printed = _run(repository)
    assert "invisible to git BY CONSTRUCTION (Ruling 130), 0 commits ahead" in printed
    assert "office" in printed, "the directory BASENAME, which is what identifies it"


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
    """
    row = "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n"
    readings = {}
    write_board(repository, row)
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
        "declared and read": CORROBORATED,
        "declared and empty": CORROBORATED,
        "no marker at all": NOT_AUTHORITATIVE,
        "declared and unreadable": NOT_AUTHORITATIVE,
    }, codes
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
