"""`W161` — the In-flight table's SUBJECT VOCABULARY, asserted in BOTH directions (R12).

⛔ **The contract is `docs/conventions/board.md`'s subject vocabulary; the code is
`tools/quality/board/bijection.py`.** ⭐ **Every direction is planted:**

| the tree | ⛔ the expectation, written BEFORE the run |
|---|---|
| a `W` subject, In-flight table or register, with no row file | `board-detail` |
| an EPIC-TASK subject with no row file | ⭐ **clean** — the arm a careless repair deletes |
| a row file for an epic task | `board-orphan`, and the message names the epic |
| a non-`W` subject handed to the parser | ⭐ **read**, never refused (`NS-01/2`) |
| the notice | names `W` ids ONLY, the epic tasks outside, and the residue |
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import repository_root
from tools.quality.board import RULE_DETAIL, RULE_ORPHAN, board_state, check_board
from tools.quality.board.bijection import EPIC_TASK, subjects
from tools.quality.board.observation import read
from tools.tests.quality.board.test_bijection import CLOSED, FOOTER, HEADER, _tree

#: ⛔ The observation table, delimited, with ROWS spliced in. Written out so the reader
#: sees what the arm reads.
TABLE = (
    "<!-- inflight -->\n| Row | Owner | Checkout | Commits ahead | State |\n"
    "|---|---|---|---|---|\n{rows}<!-- /inflight -->\n"
)


def _line(subject: str) -> str:
    return f"| {subject} | Dev | `feat/x` @ `wt/dev1` | 0 @ `abc1234` | in-progress |\n"


#: ⭐ Every non-`W` subject form the board has AUTHORED, measured over every version of
#: `BOARD.md` at `a2ae2c4` — including the lettered and the two-task forms.
EPIC_SUBJECTS = ("`NS-03`", "`SF-19b`", "`NS-04` `NS-06`")


def _board(*subjects_: str) -> str:
    return TABLE.format(rows="".join(_line(s) for s in subjects_)) + HEADER + CLOSED + FOOTER


def _bijection_line(root: Path) -> str:
    return next(line for line in board_state(root) if line.startswith("bijection ("))


# --------------------------------------------------------------------------
# Clause 3 — BOTH directions
# --------------------------------------------------------------------------


def test_planted_an_IN_FLIGHT_W_subject_with_no_row_file_is_board_detail(tmp_path: Path) -> None:
    """⛔ Re-measured at `a2ae2c4`: this tree read CLEAN — no register row, no file."""
    text = _board("`W9`")
    found = [f for f in check_board(_tree(tmp_path, text)) if f.rule == RULE_DETAIL]
    assert [(f.line, f.rule) for f in found] == [(4, RULE_DETAIL)], found
    assert "W9" in found[0].message and "EPIC" in found[0].message


def test_planted_the_SAME_W_subject_WITH_its_row_file_is_clean(tmp_path: Path) -> None:
    root = _tree(tmp_path, _board("`W9`"), rows=("W9",))
    assert [f for f in check_board(root) if f.rule == RULE_DETAIL] == []


@pytest.mark.parametrize("subject", EPIC_SUBJECTS)
def test_an_EPIC_TASK_subject_with_no_row_file_PASSES(tmp_path: Path, subject: str) -> None:
    """⭐ The arm a careless repair deletes: an epic task's argument is its EPIC."""
    root = _tree(tmp_path, _board(subject))
    assert [f for f in check_board(root) if f.rule in {RULE_DETAIL, RULE_ORPHAN}] == []


def test_planted_a_row_file_FOR_an_epic_task_is_an_orphan_naming_the_epic(tmp_path: Path) -> None:
    """⛔ MUST-NOT: an observation row never OWES a `rows/` file — one is a second home."""
    root = _tree(tmp_path, _board("`NS-03`"), rows=("NS-03",))
    (orphan,) = [f for f in check_board(root) if f.rule == RULE_ORPHAN]
    assert "NS-03" in orphan.message and "EPIC TASK" in orphan.message


def test_a_W_row_file_orphan_does_NOT_claim_to_be_an_epic_task(tmp_path: Path) -> None:
    (orphan,) = [
        f for f in check_board(_tree(tmp_path, _board(), rows=("W7",))) if f.rule == RULE_ORPHAN
    ]
    assert "EPIC TASK" not in orphan.message


# --------------------------------------------------------------------------
# The parser is NOT narrowed
# --------------------------------------------------------------------------


def test_the_parser_READS_every_subject_W_epic_and_neither() -> None:
    """⛔ Refusing a non-`W` subject would re-open `NS-01/2` as a build failure."""
    text = _board("`W9`", *EPIC_SUBJECTS, "`INT-09/5`")
    assert [row.subject.strip("` ") for row in read(text).rows] == [
        "W9",
        "NS-03",
        "SF-19b",
        "NS-04` `NS-06",
        "INT-09/5",
    ]
    vocabulary = subjects(text)
    assert [i for _n, i in vocabulary.w_rows] == ["W9"]
    assert vocabulary.epic_tasks == ("NS-03", "SF-19b", "NS-04", "NS-06")
    assert vocabulary.unclassified == ("`INT-09/5`",)


@pytest.mark.parametrize("token", ["W12", "INT-09/5", "NS-03x1", "ns-03", "X-1-2"])
def test_a_token_that_is_not_an_epic_task_is_not_read_as_one(token: str) -> None:
    assert EPIC_TASK.search(f"`{token}`") is None


# --------------------------------------------------------------------------
# Clause 2 — the arm says which population it was over
# --------------------------------------------------------------------------


def test_the_notice_names_the_W_ONLY_population_and_what_it_left_out(tmp_path: Path) -> None:
    root = _tree(tmp_path, _board("`W9`", "`NS-03`", "`INT-09/5`"), rows=("W9",))
    line = _bijection_line(root)
    assert "over `W` ids ONLY: 1 register ids and 1 observation `W` ids against 1 files" in line
    assert "OUTSIDE it by rule, argued in its EPIC" in line and ": NS-03;" in line
    assert "read and not judged: `INT-09/5`." in line


def test_impossible_an_EMPTY_table_prints_none_rather_than_nothing(tmp_path: Path) -> None:
    line = _bijection_line(_tree(tmp_path, _board()))
    assert "0 observation `W` ids" in line and line.count(": none") == 2


def test_live_the_real_notice_names_the_bijection_population() -> None:
    assert "over `W` ids ONLY" in _bijection_line(repository_root())


# --------------------------------------------------------------------------
# Clause 1 — the vocabulary is DECLARED where the structural contract lives
# --------------------------------------------------------------------------


def test_live_board_md_declares_the_vocabulary_with_the_epic_as_home() -> None:
    text = (repository_root() / "docs/conventions/board.md").read_text(encoding="utf-8")
    heading = "### ⛔ `W161` — the In-flight table's SUBJECT VOCABULARY"
    assert heading in text
    section = text.split(heading, 1)[1].split("\n### ", 1)[0]
    assert "`rows/<ID>.md`" in section and "its EPIC" in section and "never refused" in section
