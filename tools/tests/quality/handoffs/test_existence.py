"""Mirror of `tools/quality/handoffs/existence.py` (R12).

⛔ **Every condition is asserted in BOTH directions**, because the defect this
arm repairs is a check that could not fire: `check_handoffs` iterates
`rglob("*.md")`, so *the handoff is missing* was unreachable by construction and
a branch shipping none read `FLOOR_EXIT=0`. ⭐ **A test that only proves the new
arm is quiet would reproduce that defect exactly**, so every quiet case here has
a loud twin one cell apart.

⚠️ **The register fixtures are the smallest thing the real parser accepts** —
the delimiters, a header, and one row — so a negative is the positive with one
cell changed rather than a different board that happens to pass.
"""

from __future__ import annotations

import pytest

from tests.support import repository_root
from tools.quality import CHECKS, NOTICES
from tools.quality.board.register import BOARD, REGISTER_CLOSE, REGISTER_OPEN
from tools.quality.handoffs.existence import (
    HANDOFF_OWED_FROM,
    OFFICE_OWNERS,
    RULE_MISSING,
    check_handoff_existence,
    closed_rows,
    declared_task_ids,
    existence_lines,
    handoff_existence,
    owing,
)
from tools.tests.quality.handoffs.support import GOOD, write

ABOVE = f"W{HANDOFF_OWED_FROM + 1}"
AT_THE_BOUND = f"W{HANDOFF_OWED_FROM}"
WORKING_OWNER = "Developer 2"

#: The line the first register row lands on in `board()` below: a title, a
#: blank, the opening delimiter, the header and its separator come first.
FIRST_ROW = 6


def row(identifier, owner=WORKING_OWNER, state="✅ done — `abc1234`"):
    """One register row, in the register's own five-column shape."""
    return f"| {identifier} | a naming | {owner} | {state} | [record](BOARD-ARCHIVE.md#x) |"


def board(tmp_path, *rows, delimited=True):
    """Write a minimal board carrying `rows` inside the register's delimiters."""
    body = ["| # | Row | Owner | State | Detail |", "|---|---|---|---|---|", *rows]
    lines = ["# board", "", *([REGISTER_OPEN, *body, REGISTER_CLOSE] if delimited else body)]
    path = tmp_path / BOARD
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def handoff(tmp_path, *identifiers):
    """A minimally-inhabited task handoff declaring `identifiers`."""
    named = ", ".join(identifiers)
    text = GOOD.replace("# W99 — handoff", f"# {' + '.join(identifiers)} — handoff").replace(
        "**Kind:** task handoff — W99", f"**Kind:** task handoff — {named}"
    )
    return write(tmp_path, f"{identifiers[0]}.md", text)


def rules(tmp_path):
    """The rule names the arm reports for a temporary tree, sorted."""
    return sorted(finding.rule for finding in check_handoff_existence(tmp_path))


# --- the load-bearing pair: it fires, and it does not fire ------------------


def test_a_closed_row_above_the_bound_with_no_handoff_is_a_finding(tmp_path):
    board(tmp_path, row(ABOVE))
    assert rules(tmp_path) == [RULE_MISSING]


def test_and_the_same_row_with_its_handoff_is_clean(tmp_path):
    # ⭐ One cell apart from the test above: the board is identical and the
    # handoff exists, so a `[]` here cannot be a check that never ran.
    board(tmp_path, row(ABOVE))
    handoff(tmp_path, ABOVE)
    assert rules(tmp_path) == []


def test_the_finding_is_raised_against_the_board_on_the_rows_own_line(tmp_path):
    # ⛔ Against `BOARD.md` and not against a path that does not exist: the
    # remedy is to land the handoff or to stop declaring the row closed.
    board(tmp_path, row(ABOVE))
    finding = check_handoff_existence(tmp_path)[0]
    assert finding.path == BOARD
    assert finding.line == FIRST_ROW
    assert ABOVE in finding.message


# --- narrowing one: the pinned legacy bound ---------------------------------


def test_a_closed_row_at_the_bound_owes_nothing(tmp_path):
    board(tmp_path, row(AT_THE_BOUND))
    assert rules(tmp_path) == []


def test_and_the_very_next_row_owes(tmp_path):
    # ⚠️ The bound is inclusive and the pair above and here is what says so.
    board(tmp_path, row(ABOVE))
    assert rules(tmp_path) == [RULE_MISSING]


# --- narrowing two: the owner vocabulary ------------------------------------


@pytest.mark.parametrize("owner", sorted(OFFICE_OWNERS))
def test_a_closed_row_owned_by_a_supervising_office_owes_nothing(tmp_path, owner):
    # ⭐ An office round records in the archive as a `ruling record`, which is a
    # kind this directory already knows — it owes no TASK handoff.
    board(tmp_path, row(ABOVE, owner=owner))
    assert rules(tmp_path) == []


def test_an_owner_nobody_has_enumerated_OWES(tmp_path):
    # ⛔ The direction is chosen: this arm exists because a check could not
    # fire, so an unrecognised owner does not escape by being unrecognised.
    board(tmp_path, row(ABOVE, owner="Office Of Novelty"))
    assert rules(tmp_path) == [RULE_MISSING]


# --- the state cell ---------------------------------------------------------


@pytest.mark.parametrize("state", ["`todo`", "⏳ **in flight** — wave 9", "routed — folded"])
def test_a_row_the_register_does_not_declare_closed_owes_nothing(tmp_path, state):
    board(tmp_path, row(ABOVE, state=state))
    assert rules(tmp_path) == []


def test_and_the_same_row_declared_closed_owes(tmp_path):
    board(tmp_path, row(ABOVE, state="✅ done — `abc1234`"))
    assert rules(tmp_path) == [RULE_MISSING]


# --- the register's boundary ------------------------------------------------


def test_a_row_outside_the_delimiters_is_not_a_register_row(tmp_path):
    # ⚠️ An *In flight* table naming four rows was once read as four register
    # rows. The delimiters are the boundary, here as in `register.py`.
    board(tmp_path, row(ABOVE), delimited=False)
    assert rules(tmp_path) == []


def test_a_tree_with_no_board_at_all_is_not_a_finding(tmp_path):
    assert rules(tmp_path) == []
    assert "no docs/tasks/BOARD.md" in existence_lines(tmp_path, set())[0]


# --- two ids in one cell ----------------------------------------------------


def test_a_cell_naming_two_closed_rows_owes_two_handoffs(tmp_path):
    second = f"W{HANDOFF_OWED_FROM + 2}"
    board(tmp_path, row(f"{ABOVE} + {second}"))
    assert rules(tmp_path) == [RULE_MISSING, RULE_MISSING]


def test_and_one_handoff_declaring_both_satisfies_both(tmp_path):
    second = f"W{HANDOFF_OWED_FROM + 2}"
    board(tmp_path, row(f"{ABOVE} + {second}"))
    handoff(tmp_path, ABOVE, second)
    assert rules(tmp_path) == []


# --- the declaration, never the filename ------------------------------------


def test_the_id_is_read_from_the_declaration_and_not_from_the_filename(tmp_path):
    # ⛔ A document named for one row that declares another satisfies the row
    # it DECLARES. Both directions in one tree.
    other = f"W{HANDOFF_OWED_FROM + 2}"
    board(tmp_path, row(ABOVE), row(other))
    write(
        tmp_path,
        f"{ABOVE}.md",
        GOOD.replace("# W99 — handoff", f"# {other} — handoff").replace(
            "**Kind:** task handoff — W99", f"**Kind:** task handoff — {other}"
        ),
    )
    assert declared_task_ids(tmp_path) == {other}
    assert [finding.line for finding in check_handoff_existence(tmp_path)] == [FIRST_ROW]


@pytest.mark.parametrize("kind", ["ruling record", "session log", "survey", "index"])
def test_a_document_of_another_kind_declares_no_task_id(tmp_path, kind):
    # ⚠️ Only `task handoff` populates the satisfied set; a `ruling record`
    # naming a row in its prose does not discharge that row's obligation.
    write(tmp_path, "other.md", f"# other\n\n**Kind:** {kind} — {ABOVE}\n\nbody.\n")
    assert declared_task_ids(tmp_path) == set()


# --- the notice, and Ruling 191's empty denominator -------------------------


def test_the_notice_says_an_empty_denominator_is_not_a_clean_bill(tmp_path):
    board(tmp_path, row(AT_THE_BOUND))
    line = existence_lines(tmp_path, set())[0]
    assert "0 of 0" in line
    assert "EMPTY" in line
    assert "0 = 0" in line


def test_and_says_nothing_of_the_sort_when_the_population_is_inhabited(tmp_path):
    board(tmp_path, row(ABOVE))
    line = existence_lines(tmp_path, set())[0]
    assert "1 of 1" in line
    assert "EMPTY" not in line


def test_the_notice_prints_the_legacy_population_it_is_not_chasing(tmp_path):
    # ⭐ Ruling 193: the corpus is never chased — and a corpus nobody prints is
    # a corpus nobody re-measures.
    board(tmp_path, row(AT_THE_BOUND), row(ABOVE))
    handoff(tmp_path, ABOVE)
    line = existence_lines(tmp_path, declared_task_ids(tmp_path))[0]
    assert f"NOT chased (Rulings 106, 193): 1 — {AT_THE_BOUND}." in line


def test_the_notice_never_raises_a_finding_of_its_own(tmp_path):
    board(tmp_path, row(ABOVE))
    assert all(isinstance(line, str) for line in handoff_existence(tmp_path))


# --- the readers, asserted directly -----------------------------------------


def test_closed_rows_returns_the_line_the_id_and_the_owner(tmp_path):
    path = board(tmp_path, row(ABOVE), row(AT_THE_BOUND, state="`todo`"))
    assert closed_rows(path.read_text(encoding="utf-8")) == [(FIRST_ROW, ABOVE, WORKING_OWNER)]


def test_owing_applies_both_narrowings_and_neither_alone(tmp_path):
    rows = [
        (1, ABOVE, WORKING_OWNER),
        (2, ABOVE, sorted(OFFICE_OWNERS)[0]),
        (3, AT_THE_BOUND, WORKING_OWNER),
    ]
    assert owing(rows) == [(1, ABOVE, WORKING_OWNER)]


# --- the shipped tree -------------------------------------------------------


def test_this_repository_passes_the_arm():
    findings = check_handoff_existence(repository_root())
    assert findings == [], "\n".join(str(finding) for finding in findings)


def test_the_pin_is_EXACTLY_the_highest_row_it_excuses(tmp_path):
    """⛔ `HANDOFF_OWED_FROM` is a PIN, not a knob.

    ⭐ Derived from the live tree rather than typed: the bound must be exactly
    the highest closed non-office row that lacks a handoff. ⚠️ **Its limit,
    stated rather than left to be found:** an exact-fit raise still passes, so
    this catches a pin raised PAST a defect and not one raised ONTO it — that
    one is caught by the diff, which is why the pin carries its sentence.
    """
    root = repository_root()
    declared = declared_task_ids(root)
    text = (root / BOARD).read_text(encoding="utf-8")
    lacking = [
        int(identifier[1:])
        for _line, identifier, owner in closed_rows(text)
        if identifier not in declared and owner not in OFFICE_OWNERS
    ]
    assert max(lacking) == HANDOFF_OWED_FROM


def test_the_arm_is_registered_in_the_floor():
    # ⚠️ A check nobody registered is a check that cannot fail, which is the
    # class of defect this whole module exists to close.
    assert check_handoff_existence in CHECKS
    assert handoff_existence in NOTICES
