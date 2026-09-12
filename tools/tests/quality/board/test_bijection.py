"""Mirror of `tools/quality/board/bijection.py` (R12) — the board read AS A REGISTER.

⛔ **These readings MOVED here from `test_init.py` with the code they measure**, the way
`test_bounds.py`'s moved with `W100`'s split — ⭐ **and they MOVED rather than being copied:
a reading with two homes is the defect this package's own instrument exists to forbid, one
layer up.** ⚠️ **`test_init.py` keeps the LIVE readings and the one assertion that the four
arms are WIRED IN**, because *the arm works* and *the arm is composed* are two claims.

⭐ **Ruling 123's three readings, all three here:** ⛔ **LIVE** — the real board and the
real `rows/` pass every rule of this arm; ⛔ **PLANTED** — each rule fires on a tree built
to break exactly it, adversarial to the SEARCH TERM rather than to the subject (Ruling 140);
⛔ **IMPOSSIBLE** — a state the rule cannot reach reports nothing, and the reading DIFFERS
from the pass by naming its own `0` (Ruling 48).

## ⛔ `W129` — Ruling 270's stub, in FOUR DIRECTIONS, because a clause that only
## WIDENS is a clause that cannot fail

⚠️ **Ruling 201 defines a close as DELETING the row's detail file; Rulings 106 and 174
forbid editing a frozen record; and frozen records POINT AT row files.** ⛔ **Those three
are jointly unsatisfiable, and the PO measured it: performing the delete left **3 FROZEN
pointers** unresolved in `BOARD-ARCHIVE.md` — pointers NO OFFICE MAY REPAIR.**

⭐ **The stub is the remedy and the clause is NARROW, so it is planted PER DIRECTION:**

| direction | ⛔ the expectation, written BEFORE the run |
|---|---|
| a stub for a CLOSED row | ⭐ **clean** |
| a FULL argument file left by a close | ⛔ `board-orphan` |
| a stub for an id with NO register row | ⛔ `board-orphan` |
| a stub for a LIVE register row | ⛔ `board-detail` |
| ⚠️ **IMPOSSIBLE** — a stub with its frame phrase gone | ⛔ `board-frame` **and**
  `board-orphan`, which is the PO's own measured fifth state |

⛔ **The fourth direction — a stub whose archive pointer does not RESOLVE — is the POINTER
FLOOR's and is asserted in `tools/tests/test_pointers.py`'s own population**, not here:
this arm never opens the target, and a second resolver would be a second answer.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import repository_root
from tools.quality.board import (
    BOARD,
    REGISTER_CLOSE,
    REGISTER_OPEN,
    ROW_FRAME,
    ROWS,
    RULE_DETAIL,
    RULE_DUPLICATE,
    RULE_FRAME,
    RULE_ORPHAN,
    RULE_STATE,
    STATES,
    board_state,
    check_board,
)
from tools.quality.board.bijection import born_detail
from tools.quality.board.register import cells, is_closed, register, table_lines

#: A minimal register: a header, a separator, one closed row and one live one.
#: ⛔ Written out rather than generated, so a reader can see what the check reads
#: without running it.
HEADER = "<!-- register -->\n| # | Row | Owner | State | Detail |\n|---|---|---|---|---|\n"
FOOTER = "<!-- /register -->\n"

#: ⛔ **`W185`: this fixture's Detail cell CHANGED, and the change is the clause.**
#: ⚠️ **It read `[record](BOARD-ARCHIVE.md#w1)` until this row landed** — the
#: re-pointed form a close used to perform, and the one that grew the board by the
#: row's whole naming every time. ⭐ **A close now LEAVES the cell as it was born, so
#: a fixture still carrying the old form would be ten tests asserting the retired
#: behaviour** — which is what they were, and what `board-detail` caught.
CLOSED = f"| W1 | a naming | PO | ✅ done — `abc1234` | {born_detail('W1')} |\n"

#: ⛔ **The retired form itself, kept as a PLANT and never as a fixture.** ⭐ Naming it
#: once is what stops the next fixture author reaching for it by habit.
RETIRED_DETAIL = "[record](BOARD-ARCHIVE.md#w1-a-naming)"

LIVE = "| W2 | another naming | PO | `todo` | [rows/W2.md](rows/W2.md) |\n"

#: ⭐ Ruling 270's REDIRECT STUB, verbatim in the shape the ruling prescribes: the
#: `# <ID>` frame line, the frame phrase, and ONE pointer at the archive anchor.
#: ⛔ Written out rather than generated, for the same reason `HEADER` is.
STUB = (
    "# {name}\n\n⛔ **This file carries the ARGUMENT for board row `{name}` "
    "and nothing else.**\n⭐ **Its argument has CLOSED and moved to the record.**"
    "\n\n[the argument](../BOARD-ARCHIVE.md#{lower}-a-naming)\n"
)


#: The frame every row file carries, and the fixtures carry it because the live ones
#: do — a fixture that skipped it would test a shape nothing ships.
def _row(name: str) -> str:
    return (
        f"# {name}\n\n⛔ **This file carries the ARGUMENT for board row `{name}` "
        f"and nothing else.**\n⭐ **Its naming, owner and state live once, in the "
        f"register in [`../BOARD.md`](../BOARD.md).**\n\nThe argument.\n"
    )


def _stub(name: str) -> str:
    return STUB.format(name=name, lower=name.lower())


def _tree(tmp_path: Path, board: str, rows: tuple[str, ...] = (), body=_row) -> Path:
    (tmp_path / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / BOARD).write_text(board, encoding="utf-8")
    if rows:
        (tmp_path / ROWS).mkdir(exist_ok=True)
        for name in rows:
            (tmp_path / ROWS / f"{name}.md").write_text(body(name), encoding="utf-8")
    return tmp_path


def _rules(findings: list) -> list[str]:
    return sorted(finding.rule for finding in findings)


# --------------------------------------------------------------------------
# Reading 1 — LIVE
# --------------------------------------------------------------------------


def test_live_every_rule_of_THIS_ARM_is_clean_on_the_real_board() -> None:
    """⭐ The real board and the real `rows/` in this repository pass this arm.

    ⛔ **This is the reading that makes the other two mean something.** A check proved
    only against fixtures is a check whose subject has never been measured.
    """
    mine = {RULE_DETAIL, RULE_ORPHAN, RULE_DUPLICATE, RULE_STATE, RULE_FRAME}
    assert [f for f in check_board(repository_root()) if f.rule in mine] == []


def test_live_no_register_row_on_this_board_is_board_state() -> None:
    """⭐ The LIVE reading. ⛔ `RULE_STATE` was the one code with no test of its path.

    ⚠️ **Ruling 152's reachability held, so this was a test gap, not a missing
    guard.** ⭐ The population is read out beside the verdict (Ruling 48).
    """
    root = repository_root()
    assert [f for f in check_board(root) if f.rule == RULE_STATE] == []
    assert int(board_state(root)[0].split("board: ")[1].split(" register")[0]) > 0


# --------------------------------------------------------------------------
# Reading 2 — PLANTED, one per rule
# --------------------------------------------------------------------------


def test_planted_live_row_with_no_detail_file(tmp_path: Path) -> None:
    root = _tree(tmp_path, HEADER + CLOSED + LIVE + FOOTER)
    assert _rules(check_board(root)) == [RULE_DETAIL]


def test_planted_detail_file_with_no_live_row(tmp_path: Path) -> None:
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER, rows=("W1",))
    findings = check_board(root)
    assert _rules(findings) == [RULE_ORPHAN]
    assert "W1" in findings[0].message


def test_planted_duplicate_id(tmp_path: Path) -> None:
    root = _tree(tmp_path, HEADER + LIVE + LIVE + FOOTER, rows=("W2",))
    findings = check_board(root)
    assert _rules(findings) == [RULE_DUPLICATE]
    assert "ONE row" in findings[0].message


# --------------------------------------------------------------------------
# ⛔ `W129` / Ruling 270 — the STUB, in FOUR directions and one impossible one
# --------------------------------------------------------------------------


def test_planted_a_STUB_for_a_CLOSED_row_is_CLEAN(tmp_path: Path) -> None:
    """⭐ DIRECTION 1, and it is the only direction that the clause WIDENS.

    ⛔ **The expectation, written first: `0` findings.** ⚠️ **Before Ruling 270 this was
    `board-orphan`, which is why three closes stood behind one clause** — `W100`, `W122`
    and `W124` could not reach a CLOSED state at all, so every round ended with a
    register that was true only because it declined to say `done`.
    """
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER, rows=("W1",), body=_stub)
    assert check_board(root) == []


def test_planted_a_FULL_ARGUMENT_FILE_left_behind_by_a_CLOSE_still_FAILS(
    tmp_path: Path,
) -> None:
    """⛔ DIRECTION 2 — the one a `contains` predicate would have lost.

    ⚠️ **MEASURED at `51dee3b`, role `wt/dev1`: of the 83 live row files, 50 carry an
    anchored `BOARD-ARCHIVE.md#` pointer somewhere and 42 END with one** — ⛔ **so a
    predicate asking whether the argument CONTAINS an archive pointer would have read
    FIFTY full argument files on today's board as stubs.** ⭐ **The predicate is *the
    argument IS the pointer*, and this is the plant that says so.**
    """
    full = _row("W1") + "\n[the record](../BOARD-ARCHIVE.md#w1-a-naming)\n"
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER)
    (root / ROWS).mkdir(exist_ok=True)
    (root / ROWS / "W1.md").write_text(full, encoding="utf-8")
    findings = check_board(root)
    assert _rules(findings) == [RULE_ORPHAN]
    assert "REDIRECT STUB" in findings[0].message, "⭐ the message names the remedy"


def test_planted_a_STUB_for_an_id_with_NO_REGISTER_ROW_still_FAILS(tmp_path: Path) -> None:
    """⛔ DIRECTION 3a — *not closed at all* in its first shape: the register lost it.

    ⭐ **The clause is gated on a CLOSED REGISTER ROW and never on the file's shape**,
    so a stub whose id the register does not name at all is still an orphan.
    """
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2", "W7"))
    (root / ROWS / "W7.md").write_text(_stub("W7"), encoding="utf-8")
    assert _rules(check_board(root)) == [RULE_ORPHAN]


def test_planted_a_STUB_for_a_LIVE_register_row_is_board_detail(tmp_path: Path) -> None:
    """⛔ DIRECTION 3b — *not closed at all* in its second shape, and it is `board-detail`.

    ⭐ **No new rule code was needed, and that is the point:** ⚠️ **`board-detail`'s
    shipped message has said since it was written that *"a live row's argument is
    AMENDED, so it may not live in the archive"*** — ⛔ **and a stub is precisely a file
    whose argument has moved to the archive.** ⭐ **So the widening of `board-orphan` is
    paid for by the rule that already meant this.**
    """
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",), body=_stub)
    findings = check_board(root)
    assert _rules(findings) == [RULE_DETAIL]
    assert "REDIRECT STUB" in findings[0].message
    assert "does not say closed" in findings[0].message


def test_impossible_a_STUB_WITH_ITS_FRAME_PHRASE_GONE_is_TWO_findings(tmp_path: Path) -> None:
    """⚠️ The IMPOSSIBLE reading, and it is the PO's own measured fifth state.

    ⛔ **A stub is STILL JUDGED.** ⭐ **The clause being asked for is *a CLOSED row's
    detail file MAY be a stub*, never *a file under `rows/` may be anything*** — ⚠️ **so
    a stub that lost its frame phrase fires `board-frame` AND falls back out of the
    exception into `board-orphan`, which is what keeps the clause narrow.**

    ⛔ **And the reading DIFFERS from the pass**: `test_planted_a_STUB_for_a_CLOSED_row`
    reads `[]` against this one's two codes.
    """
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER, rows=("W1",), body=_stub)
    assert check_board(root) == [], "the control, before the frame phrase is removed"
    broken = _stub("W1").replace(ROW_FRAME, "and so on.")
    assert ROW_FRAME not in broken, "⛔ the plant must actually remove the phrase"
    (root / ROWS / "W1.md").write_text(broken, encoding="utf-8")
    assert _rules(check_board(root)) == [RULE_FRAME, RULE_ORPHAN]


def test_impossible_a_stub_with_NO_ANCHOR_is_not_a_stub(tmp_path: Path) -> None:
    """⛔ The anchor is REQUIRED, and a bare archive link is not a redirect.

    ⚠️ **Ruling 270's own sentence is *"the reader lands on the argument"*** — ⭐ **and a
    bare `BOARD-ARCHIVE.md` lands them at the top of a record hundreds of sections long,
    which is Ruling 244(e)'s whole subject.**
    """
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER, rows=("W1",), body=_stub)
    assert check_board(root) == []
    bare = _stub("W1").replace("../BOARD-ARCHIVE.md#w1-a-naming", "../BOARD-ARCHIVE.md")
    (root / ROWS / "W1.md").write_text(bare, encoding="utf-8")
    assert _rules(check_board(root)) == [RULE_ORPHAN]


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE
# --------------------------------------------------------------------------


def test_a_W_shaped_table_outside_the_markers_is_not_the_register(tmp_path: Path) -> None:
    """⛔ The defect this check found in its own author, kept as a test.

    ⚠️ **An *In flight* table naming four rows was read as four DUPLICATE register
    rows** by the first version, which inferred the register from row shape.
    ⭐ **A board may hold many `W`-shaped tables; one of them says it is the register.**
    """
    elsewhere = "| W2 | in flight | Dev | none | +3 |\n"
    root = _tree(tmp_path, HEADER + LIVE + FOOTER + elsewhere, rows=("W2",))
    assert check_board(root) == []


def test_impossible_board_with_no_register_rows(tmp_path: Path) -> None:
    """⚠️ A board whose register is EMPTY is clean, and the notice says so.

    ⛔ **That is the honest answer and it is why the notice exists.** The rules here
    bound shape, not inhabitation — ⭐ **so the population is printed, and a reader who
    sees `0 register rows` knows the verdict is about nothing.**
    """
    root = _tree(tmp_path, HEADER + FOOTER)
    assert check_board(root) == []
    assert "0 register rows, 0 live" in board_state(root)[0]


@pytest.mark.parametrize("state", ["✅ done — `abc1234`", "done", "DONE at `abc1234`"])
def test_a_closed_row_never_wants_a_FULL_detail_file(tmp_path: Path, state: str) -> None:
    """⭐ The other direction of `board-detail`, and it is the one that regresses.

    ⛔ A rule that only fired on a missing file would let every closed row keep an
    editable argument, which is the state `BOARD-ARCHIVE.md` exists to prevent.

    ⚠️ **Ruling 270 narrowed this and did not retire it:** ⭐ **a closed row may keep a
    STUB and may not keep an ARGUMENT**, which is the third assertion below.
    """
    row = f"| W1 | a naming | PO | {state} | {born_detail('W1')} |\n"
    assert check_board(_tree(tmp_path / "without", HEADER + row + FOOTER)) == []
    with_file = _tree(tmp_path / "with", HEADER + row + FOOTER, rows=("W1",))
    assert _rules(check_board(with_file)) == [RULE_ORPHAN]
    stubbed = _tree(tmp_path / "stub", HEADER + row + FOOTER, rows=("W1",), body=_stub)
    assert check_board(stubbed) == [], "⭐ Ruling 270, and it holds for every closed word"


# --------------------------------------------------------------------------
# ⛔ `W185` — A CLOSE MAY NOT GROW THE BOARD: the assertion arm the clause was owed
#
# ⭐ **The clause is `docs/conventions/board.md`'s and it shipped HALF-ASSERTED.**
# ⚠️ **The *reader lands on the argument* half was already held** — Ruling 270's
# exception above requires a closed row's file to BE an anchored stub, and the
# pointer floor resolves it — ⛔ **but NOTHING read the register CELL, so the next
# close could have re-pointed it at an archive anchor with every gate green.**
#
# ⛔ **THE PLANT IS THE RETIRED FORM ITSELF.** ⭐ Until this arm landed,
# `CLOSED` above CARRIED that form and ten tests passed on it — ⚠️ **which is the
# strongest evidence available that the arm was owed: the fixtures encoded the
# behaviour the clause abolished, and nothing said so.**
# --------------------------------------------------------------------------


def test_planted_a_CLOSED_row_RE_POINTED_at_the_archive_is_board_detail(tmp_path: Path) -> None:
    """⛔ THE DIRECTION THAT HAD NO INSTRUMENT — the close that grows the board.

    ⭐ **This is the edit Ruling 201 used to prescribe**, replayed verbatim: the
    Detail cell of a closed row re-pointed from `rows/<ID>.md` at the archive anchor.
    ⚠️ **An archive anchor is the row's whole NAMING slugified** — ⛔ **`PO-58/10`
    measured four such closes costing 296 bytes against 224 of allowance, and the
    round overran `board-size` by 257 bytes before one word of STATE was written.**

    ⛔ **The row is otherwise PERFECT**: closed, with a Ruling 270 stub on disk that
    the pointer floor would resolve. ⭐ So the one finding is the cell and nothing
    else, which is what makes this a plant of the clause rather than of a broken row.
    """
    row = f"| W1 | a naming | PO | ✅ done — `abc1234` | {RETIRED_DETAIL} |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W1",), body=_stub)
    findings = check_board(root)
    assert _rules(findings) == [RULE_DETAIL]
    assert RETIRED_DETAIL in findings[0].message, "⭐ the message quotes the cell it read"
    assert born_detail("W1") in findings[0].message, "⭐ and the cell it wanted"
    assert "grows the board" in findings[0].message


def test_planted_the_predicate_is_an_EQUALITY_and_not_merely_NO_ARCHIVE(tmp_path: Path) -> None:
    """⛔ THE CONTROL THAT CONSTRAINS THE PREDICATE, and it is the reason for Ruling 186's form.

    ⚠️ **A predicate reading *the cell does not mention `BOARD-ARCHIVE.md`* passes on a
    cell pointing ANYWHERE** — at another row, at a handoff, at nothing. ⛔ **That is
    the direction a bijection check fails toward: silently, on the case that looks
    right.** ⭐ **So the clause is asserted as the EQUALITY it is written as**, and this
    plant carries no archive link at all and must still be refused.
    """
    row = "| W1 | a naming | PO | ✅ done — `abc1234` | [`rows/W9.md`](rows/W9.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W1",), body=_stub)
    findings = check_board(root)
    assert _rules(findings) == [RULE_DETAIL], "⭐ refused, and no archive anchor was involved"
    assert "BOARD-ARCHIVE.md anchor" not in findings[0].message, (
        "⛔ the message may not blame an archive anchor when the cell carries none — "
        "⚠️ a finding that names the wrong cause sends the next reader to the wrong fix"
    )


def test_a_LIVE_row_pointing_at_the_archive_is_NOT_this_finding(tmp_path: Path) -> None:
    """⚠️ THE ARM MAY NOT WIDEN — the clause is gated on a CLOSED row and only a closed one.

    ⛔ **A live row whose Detail cell points at the archive is already `board-detail`'s
    neighbour's business and it is a DIFFERENT defect** — the argument is still being
    amended, so what is wrong is that it lives in the archive at all, not that the cell
    moved. ⭐ **This plant fires the rules that already existed and adds none**, which
    is how a new arm is shown not to have swallowed its neighbours.
    """
    row = f"| W2 | another naming | PO | `todo` | {RETIRED_DETAIL} |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    assert check_board(root) == [], "⭐ the new arm is silent on every LIVE row's cell"


def test_live_every_CLOSED_row_on_the_real_board_carries_the_BORN_cell() -> None:
    """⭐ THE LIVE READING, and it DECLARES ITS OWN DENOMINATOR (Ruling 48).

    ⛔ **A board with no closed rows would satisfy this clause vacuously**, and a
    vacuous pass is the state `0 = 0` exists to make visible — ⚠️ **so the population
    is asserted non-empty in the same breath as the property.** ⭐ Without that, the
    arm would go quietly green on exactly the board it has nothing to say about.
    """
    text = (repository_root() / BOARD).read_text(encoding="utf-8")
    lines = dict(table_lines(text))
    closed = [
        (ids[0], cells(lines[number])[4].strip())
        for number, ids, cell_state in register(text)
        if is_closed(cell_state)
    ]
    assert closed, "⛔ no CLOSED register row on this board, so the clause is untested here"
    moved = [name for name, detail in closed if detail != born_detail(name)]
    assert moved == [], (
        f"⛔ {len(moved)} of {len(closed)} closed rows have a MOVED Detail cell: "
        f"{', '.join(moved)}. A close leaves the cell as it was born."
    )


def test_a_multi_id_row_is_one_row_and_one_file(tmp_path: Path) -> None:
    """⚠️ `W17 + W19` are one commit, ruled, and therefore one row.

    ⛔ **The first id owns the file and the rest ride with it**, so a register that
    carries them as one does not owe two files — and a check that demanded two would
    push the PO into splitting a row the CTO fused.
    """
    row = "| W17 + W19 | a naming | PO | `todo` | [rows/W17.md](rows/W17.md) |\n"
    assert check_board(_tree(tmp_path, HEADER + row + FOOTER, rows=("W17",))) == []


# --------------------------------------------------------------------------
# `board-frame` — the live-tree guarantee Ruling 180 would otherwise have cost
# --------------------------------------------------------------------------


def test_a_row_file_that_lost_its_frame_is_a_finding(tmp_path: Path) -> None:
    """⛔ The one live-tree property left after Ruling 180, and why it is that one.

    ⚠️ **`test_migration.py`'s subject is now the migration's OUTPUT ref**, which is
    right — a migration is a claim about refs — ⛔ **but it means nothing was left
    watching a live row file at all.**

    ⭐ **A frame survives every amendment**, because amending a row means adding to its
    argument and never removing its identity — ⛔ **so this is the one thing that can be
    required of a file the PO is told to edit freely.**
    """
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",))
    assert check_board(root) == []
    (root / ROWS / "W2.md").write_text("a fragment with no frame at all\n", encoding="utf-8")
    assert _rules(check_board(root)) == [RULE_FRAME]


def test_appending_to_a_row_file_is_always_clean(tmp_path: Path) -> None:
    """⭐ The contract's own action — *"editing it is the point"* — stays green.

    ⛔ **This is the assertion `CTO-46/1` was about.** ⚠️ A test that reddened on an
    ordinary amendment would be a gate people edit their way around.
    """
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",))
    path = root / ROWS / "W2.md"
    path.write_text(path.read_text(encoding="utf-8") + "\n⛔ **Re-scoped.**\n", encoding="utf-8")
    assert check_board(root) == []


def test_a_row_file_named_for_a_different_row_is_a_finding(tmp_path: Path) -> None:
    """⚠️ The frame names its own id, so a copied file cannot pass as a new one."""
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",))
    (root / ROWS / "W2.md").write_text(_row("W9"), encoding="utf-8")
    assert _rules(check_board(root)) == [RULE_FRAME]


def test_the_frame_finding_states_what_is_CHECKED_not_what_is_hoped(tmp_path: Path) -> None:
    """⛔ `CTO-47/4`: the predicate is two substrings; the message claimed more.

    ⚠️ **It said the file *"states which row it argues…"*** — ⛔ **which `startswith` and
    `in` cannot read.** ⭐ **The weak predicate is the RIGHT trade for
    amendment-proofness** — ⛔ **a message describing a check nobody wrote sends the next
    reader to debug the wrong claim.**
    """
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",))
    (root / ROWS / "W2.md").write_text("a fragment with no frame at all\n", encoding="utf-8")
    findings = check_board(root)
    assert _rules(findings) == [RULE_FRAME]
    message = findings[0].message
    assert "`# W2`" in message, "the message names the first substring"
    assert repr(ROW_FRAME) in message, "and the second one, verbatim"
    assert "TWO SUBSTRINGS" in message, "and says that is the whole of it"


# --------------------------------------------------------------------------
# ⛔ `CTO-47/5` — `board-state`'s FINDING path, which had no reading at all
# --------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cell",
    [
        "after `W44` is done",
        "DONE-ish — merged `abc1234`",
        "→ folded into `SF-10`",
        "◐ spec text landed; the asserting test is owed",
    ],
)
def test_planted_a_state_cell_that_declares_nothing_is_board_state(
    tmp_path: Path, cell: str
) -> None:
    """⛔ The PLANTED reading, adversarial to the SEARCH TERM (Ruling 140).

    ⚠️ **Each wears the word the first `is_closed` searched for, in a form the clause
    did not picture** — including `W5`'s and `W16`'s real shapes, which declare nothing.
    ⭐ **`DONE-ish` came from the impossible plant.**
    """
    row = f"| W2 | a naming | PO | {cell} | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    findings = check_board(root)
    assert _rules(findings) == [RULE_STATE]
    assert "declares no state" in findings[0].message
    assert "W2" in findings[0].message


def test_the_cell_that_walked_out_of_the_register_is_LIVE_and_owes_a_FILE(
    tmp_path: Path,
) -> None:
    """⛔ The defect's own cell, and the finding the substring test silently lost.

    ⚠️ **`` `todo` — after `W44` is done ``** read as CLOSED: no detail file owed, out
    of the bijection, floor green. ⭐ **It DECLARES `todo`**, so the mention is ambiguous
    and the declaration is not.
    """
    row = "| W2 | a naming | PO | `todo` — after `W44` is done | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER)
    rules = _rules(check_board(root))
    assert RULE_STATE not in rules, "it declares todo; only the mention is loose"
    assert rules == [RULE_DETAIL], "⛔ the finding a substring test lost in silence"


@pytest.mark.parametrize("declared", sorted(STATES))
def test_a_cell_that_DECLARES_a_state_is_never_board_state(tmp_path: Path, declared: str) -> None:
    """⭐ Every word of the closed vocabulary, derived rather than retyped.

    ⛔ **Parametrised over `STATES` itself**, so a word added to the vocabulary joins
    this population without the test being edited and an EMPTY vocabulary skips rather
    than passing (Ruling 48).
    """
    row = f"| W2 | a naming | PO | ⛔ **{declared}** — `abc1234` | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    assert RULE_STATE not in _rules(check_board(root))


def test_impossible_board_state_cannot_fire_on_an_EMPTY_register(tmp_path: Path) -> None:
    """⛔ The IMPOSSIBLE reading, and it DIFFERS from the pass by naming `0`.

    ⭐ A register with no rows has no cell to judge, so silence here is correct —
    ⚠️ **and `0 = 0` is not a pass**, which is why the population is read out of the
    notice in the same assertion.
    """
    root = _tree(tmp_path, HEADER + FOOTER)
    assert [f for f in check_board(root) if f.rule == RULE_STATE] == []
    assert "0 register rows, 0 live" in board_state(root)[0]


def test_this_repository_has_a_board_with_a_DELIMITED_register() -> None:
    """⛔ The enforcement half, and it lives with the arm that reads the delimiter.

    ⭐ `test_init.py`'s `test_impossible_no_board_at_all` says a missing board is not a
    floor failure anywhere; this says it is a build failure HERE.
    """
    assert (repository_root() / BOARD).is_file()
    assert (repository_root() / ROWS).is_dir()
    board = (repository_root() / BOARD).read_text(encoding="utf-8")
    assert REGISTER_OPEN in board and REGISTER_CLOSE in board
