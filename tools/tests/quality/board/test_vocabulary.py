"""`W161` — the In-flight table's SUBJECT VOCABULARY, asserted in BOTH directions (R12).

⛔ **The contract is `docs/conventions/board.md`'s subject vocabulary; the code is
`tools/quality/board/vocabulary.py`, judged in `bijection.py`.** ⭐ **Every direction is planted:**

| the tree | ⛔ the expectation, written BEFORE the run |
|---|---|
| a `W` subject, In-flight table or register, with no row file | `board-detail` |
| an EPIC-TASK subject with no row file | ⭐ **clean** — the arm a careless repair deletes |
| a row file for an epic task | `board-orphan`, and the message names the epic |
| a non-`W` subject handed to the parser | ⭐ **read**, never refused (`NS-01/2`) |
| the notice | names `W` ids ONLY, the epic tasks outside, and the residue |
| `W262`: an epic task no `docs/tasks/E*.md` defines | `board-detail`, naming its prefix's epics |
| `W262`: a non-epic subject, or a frozen record's table | ⭐ **never** that finding |
"""

from __future__ import annotations

import re
from pathlib import Path

import pytest

from tests.support import repository_root
from tools.quality.board import RULE_DETAIL, RULE_ORPHAN, board_state, check_board
from tools.quality.board.observation import read
from tools.quality.board.vocabulary import EPIC_TASK, epic_definitions, subjects
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


#: ⭐ `W262`: the epics that DEFINE `EPIC_SUBJECTS`, each task a `### <ID> —` heading.
DEFINING = {"E13-narration.md": ("NS-03", "NS-04", "NS-06"), "E05-serving.md": ("SF-19b",)}


def _epics(root: Path, epics: dict[str, tuple[str, ...]] = DEFINING) -> Path:
    for name, tasks in epics.items():
        body = "".join(f"### {task} — a task\n\nits argument\n\n" for task in tasks)
        (root / "docs" / "tasks" / name).write_text(f"# {name}\n\n{body}", encoding="utf-8")
    return root


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
    root = _epics(_tree(tmp_path, _board(subject)))
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
    # ⛔ `W279`: both halves, defined AND argued in the epic, and `W262`'s check pointed at.
    epic_row = next(line for line in section.splitlines() if "**EPIC TASK**" in line)
    assert "DEFINES it and argues it there" in epic_row
    assert "`board-detail`" in epic_row and "(../../tools/quality/board/vocabulary.py)" in epic_row


# --------------------------------------------------------------------------
# `W161/5` — the split out of `bijection.py` was a PURE MOVE (`W262`)
# --------------------------------------------------------------------------


#: The modules the brief names as depending on `bijection`, and the package surface.
IMPORTERS = ("observation", "notice", "bounds", "register", "unclaimed", "__init__")


@pytest.mark.parametrize("name", ["EPIC_TASK", "EPIC_HOME", "subjects"])
def test_every_moved_name_still_resolves_from_bijection_as_the_SAME_object(name: str) -> None:
    import tools.quality.board.bijection as bijection
    import tools.quality.board.vocabulary as vocabulary

    assert getattr(bijection, name) is getattr(vocabulary, name)


@pytest.mark.parametrize("module", IMPORTERS)
def test_every_named_importer_still_imports(module: str) -> None:
    import importlib

    name = "tools.quality.board" + ("" if module == "__init__" else f".{module}")
    assert importlib.import_module(name).__name__ == name


# --------------------------------------------------------------------------
# `W262` — an epic task its epic does not DEFINE is named, in BOTH directions
# --------------------------------------------------------------------------


def _details(root: Path) -> list:
    return [f for f in check_board(root) if f.rule == RULE_DETAIL]


def test_planted_an_EPIC_TASK_no_epic_defines_is_board_detail_naming_its_epic(
    tmp_path: Path,
) -> None:
    (found,) = _details(_epics(_tree(tmp_path, _board("`NS-99`"))))
    assert found.line == 4
    assert "NS-99" in found.message and "no docs/tasks/E*.md defines it" in found.message
    assert "prefix `NS-` points at docs/tasks/E13-narration.md." in found.message


def test_planted_a_PREFIX_no_epic_carries_points_at_NO_epic(tmp_path: Path) -> None:
    (found,) = _details(_epics(_tree(tmp_path, _board("`ZZ-01`"))))
    assert "points at NO epic: none defines a `ZZ-` task" in found.message


def test_the_SAME_subject_once_its_epic_DEFINES_it_is_clean(tmp_path: Path) -> None:
    root = _epics(_tree(tmp_path, _board("`NS-99`")), {"E13-narration.md": ("NS-03", "NS-99")})
    assert _details(root) == []


@pytest.mark.parametrize(
    ("subject", "epic"), [("`SF-19b`", "### SF-19 — a task\n"), ("`NS-99`", "NS-99 in prose\n")]
)
def test_a_LETTER_or_a_PROSE_MENTION_defines_nothing(
    tmp_path: Path, subject: str, epic: str
) -> None:
    root = _tree(tmp_path, _board(subject))
    (root / "docs" / "tasks" / "E13-narration.md").write_text(f"# E13\n\n{epic}", encoding="utf-8")
    assert len(_details(root)) == 1


def test_control_a_subject_that_is_NOT_an_epic_task_is_never_this_finding(tmp_path: Path) -> None:
    """⛔ No epic in this tree: the lookup answers nothing, and still nothing fires."""
    root = _tree(tmp_path, _board("`W9`", "`INT-09/5`", "a prose subject"), rows=("W9",))
    assert epic_definitions(root) == {}
    assert _details(root) == []


def test_control_an_ARCHIVED_or_FROZEN_table_naming_undefined_epic_tasks_is_never_read(
    tmp_path: Path,
) -> None:
    """⛔ Ruling 106: a frozen record keeps its In-flight table as written, and is not judged."""
    root = _epics(_tree(tmp_path, _board("`NS-03`")))
    frozen = _board("`NS-99`", "`QQ-01`")
    (root / "docs" / "tasks" / "BOARD-ARCHIVE.md").write_text(frozen, encoding="utf-8")
    (root / "docs" / "tasks" / "handoffs").mkdir()
    (root / "docs" / "tasks" / "handoffs" / "W0.md").write_text(frozen, encoding="utf-8")
    assert _details(root) == []


def test_the_notice_prints_the_EPIC_LOOKUP_population(tmp_path: Path) -> None:
    line = _bijection_line(_epics(_tree(tmp_path, _board("`NS-03`", "`NS-99`"))))
    assert "Epic lookup (`W262`): 4 task(s) defined in 2 docs/tasks/E*.md; " in line
    assert "1 In-flight epic task(s) no epic defines: NS-99." in line


def test_live_the_epic_lookup_is_INHABITED_by_this_repositorys_epics() -> None:
    definitions = epic_definitions(repository_root())
    assert definitions, "no epic in this repository defines a task: the lookup read nothing"
    assert all(re.fullmatch(r"docs/tasks/E[^/]*\.md", epic) for epic in definitions.values())
