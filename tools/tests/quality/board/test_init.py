"""Mirror of `tools/quality/board/__init__.py` (R12) — ⛔ the SURFACE, and the COMPOSITION.

⛔ **This module's subject is what `__init__.py` still does after `W129`/`W130`/`W132`
discharged the standing SPLIT decision: it reads the board ONCE and composes FOUR ARMS.**
⭐ **It judges nothing itself, so there is nothing here to plant against** — ⚠️ **what is
left to assert is that each arm is WIRED IN, which is a different claim from *the arm
works* and is exactly the claim a split can silently break.**

## ⛔ What is NOT here, and every line of it is a pointer rather than a deletion

| the arm | its readings live in |
|---|---|
| the bijection, the states, the frames | ⭐ **`test_bijection.py`** (`W129`'s split) |
| the three SIZE bounds | `test_bounds.py` (`W100`'s split) |
| the observation table's four rules | `test_contradiction.py` |
| the `## Scheduled` trigger rule | `test_scheduled.py` |
| the notice's population lines | `test_notice.py` |

⚠️ **Each moved WITH its code and none was copied:** ⛔ **a reading with two homes is the
defect this package's own instrument exists to forbid, one layer up.**
"""

from __future__ import annotations

from pathlib import Path

from tests.support import repository_root
from tools.quality.board import (
    BOARD,
    BOARD_NARRATIVE_CEILING,
    BOARD_ROW_CEILING,
    RULE_DETAIL,
    RULE_DISAGREEMENT,
    RULE_DUPLICATE,
    RULE_FRAME,
    RULE_INFLIGHT,
    RULE_NARRATIVE,
    RULE_ORPHAN,
    RULE_SIZE,
    RULE_STATE,
    RULE_TRIGGER,
    RULE_UNOBSERVED,
    RULE_UNREADABLE,
    RULE_WIDTH,
    board_state,
    check_board,
)

#: ⛔ **Every rule code the package declares, BY THE ARM THAT RAISES IT.** ⭐ Written out
#: per arm rather than as one flat set, because the claim asserted below is *`check_board`
#: reaches all four arms* and a flat set cannot say WHICH arm went missing.
ARMS = {
    "bijection": {RULE_DETAIL, RULE_ORPHAN, RULE_DUPLICATE, RULE_STATE, RULE_FRAME},
    "bounds": {RULE_NARRATIVE, RULE_WIDTH, RULE_SIZE},
    "contradiction": {RULE_INFLIGHT, RULE_UNOBSERVED, RULE_DISAGREEMENT, RULE_UNREADABLE},
    "scheduled": {RULE_TRIGGER},
}


# --------------------------------------------------------------------------
# Reading 1 — LIVE
# --------------------------------------------------------------------------


def test_live_board_is_clean() -> None:
    """⭐ The real board in this repository passes every rule of every arm.

    ⛔ **This is the reading that makes every planted one mean something.** A check
    proved only against fixtures is a check whose subject has never been measured —
    the shape `check_pointers` was scoped on, arriving here.
    """
    assert check_board(repository_root()) == []


def test_live_notice_names_every_bound_and_the_population() -> None:
    """⛔ Ruling 128: print the population in full before reducing it to a scalar.

    ⭐ **`W130` added the allowance's THREE TERMS to this line, each with its own
    count**, because a total against one denominator is what hid Ruling 271's slope
    defect for as long as it hid it.
    """
    line = board_state(repository_root())[0]
    assert line.startswith("board: ")
    assert "register rows" in line and "live" in line and "detail files" in line
    assert str(BOARD_NARRATIVE_CEILING) in line
    assert str(BOARD_ROW_CEILING) in line
    for term in ("frame", "register", "observation", "scheduled"):
        assert term in line, f"⛔ `W130`: the allowance's {term} term is not printed"


def test_live_board_has_a_detail_file_for_every_live_row() -> None:
    """⭐ The bijection, stated as a number rather than as an absence.

    ⛔ **`W137`: Ruling 270 RETIRED `live == files`, and this test asserted it for as
    long as the protocol went unused.** ⭐ **The bijection after a close is
    `detail files == live rows + REDIRECT STUBS`** — ⚠️ **and the third term is read
    from the notice's SECOND line, which already prints it, rather than recounted
    here by a second instrument that could disagree with the shipped one.**

    ⛔ **The `+ stubs` term is not a widening, and the reading that shows it is not:
    the notice's stub population is every CLOSED id whose file REDIRECTS.** ⭐ **So a
    closed row whose FULL argument file was left behind by a close still reddens this
    line — it is on disk, it is not a stub, and nothing else counts it.** ⚠️ **The
    complementary direction — a LIVE row whose file is a stub — is `test_register.py`'s
    `test_the_LIVE_tree_reads_ZERO_stubs_and_the_CONTAINS_form_would_read_FIFTY`, and
    neither test alone closes both.**
    """
    counts, closed = board_state(repository_root())[:2]
    live = int(counts.split(" register rows, ")[1].split(" live")[0])
    files = int(counts.split("live, ")[1].split(" detail files")[0])
    stubs = int(closed.split("; of those, ")[1].split(" are REDIRECT STUBS")[0])
    assert files == live + stubs, (
        f"⛔ {files} detail file(s) for {live} live row(s) + {stubs} REDIRECT STUB(s). "
        f"⭐ Ruling 270 allows a CLOSED row's file to stay only as a stub, so the "
        f"surplus is a closed row whose FULL argument was left on disk by a close."
    )


# --------------------------------------------------------------------------
# ⛔ The COMPOSITION — four arms, and the claim a SPLIT can silently break
# --------------------------------------------------------------------------


def test_check_board_REACHES_ALL_FOUR_ARMS(tmp_path: Path) -> None:
    """⛔ One board that breaks a rule in EVERY arm, so a dropped arm cannot hide.

    ⚠️ **This is the assertion the `W129` split needed and `W100`'s did not have:** ⭐ **a
    `findings.extend(...)` line deleted from `check_board` leaves every one of that arm's
    own tests passing, because they call the arm directly.** ⛔ **Only a reading taken
    through `check_board` can see an arm that is no longer composed.**

    ⭐ **The population is the `ARMS` table above, asserted as a SET rather than a
    count**, so a fifth arm joining the package cannot be silently unwired either: this
    test reddens until its codes are in the table and its plant is in this board.
    """
    board = (
        # ⛔ bounds: one table row over `BOARD_ROW_CEILING`.
        "| " + "x" * 700 + " |\n"
        # ⛔ contradiction: a started observation row naming no checkout and 0 ahead.
        "<!-- inflight -->\n"
        "| Row | Owner | Checkout | Commits ahead | State |\n|---|---|---|---|---|\n"
        "| `W2` | Dev | none | 0 | in flight |\n"
        "<!-- /inflight -->\n"
        # ⛔ scheduled: a trigger cell that declares no state.
        "<!-- scheduled -->\n"
        "| Item | Trigger | State |\n|---|---|---|\n"
        "| a thing | when M1 opens | before M1's wave opens |\n"
        "<!-- /scheduled -->\n"
        # ⛔ bijection: a live row with no detail file, and one id twice.
        "<!-- register -->\n| # | Row | Owner | State | Detail |\n|---|---|---|---|---|\n"
        "| W2 | a naming | PO | `todo` | [d](rows/W2.md) |\n"
        "| W2 | again | PO | `todo` | [d](rows/W2.md) |\n"
        "<!-- /register -->\n"
    )
    (tmp_path / "docs" / "tasks").mkdir(parents=True)
    (tmp_path / BOARD).write_text(board, encoding="utf-8")
    raised = {finding.rule for finding in check_board(tmp_path)}
    assert raised, "⛔ born vacuous: the plant raised nothing at all"
    silent = [arm for arm, codes in sorted(ARMS.items()) if not codes & raised]
    assert silent == [], f"⛔ {silent} raised NOTHING — the arm is not composed into check_board"


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE
# --------------------------------------------------------------------------


def test_impossible_no_board_at_all(tmp_path: Path) -> None:
    """⛔ A tree with no board is CLEAN, and the notice says so out loud.

    ⚠️ **The floor runs over arbitrary roots** — a temp tree, a corpus repository —
    ⛔ **so a finding here would be asserting which repository you are in.** ⭐ **This is
    `check_knowledge_index`'s split, reused**: absence is reported through the notice
    channel and presence is enforced by a test that knows the answer should be yes.

    ⚠️ **`0 = 0` is not a pass** (Ruling 48), which is why the notice may not be silent —
    and it is not. ⭐ **The presence half is
    `test_bijection.py::test_this_repository_has_a_board_with_a_DELIMITED_register`.**
    """
    (tmp_path / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
    assert check_board(tmp_path) == []
    assert "board: none" in board_state(tmp_path)[0]
