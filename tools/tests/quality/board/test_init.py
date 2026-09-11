"""Mirror of `tools/quality/board.py` (R12), and the instrument's three readings.

⛔ **Ruling 122: a clause naming an instrument is not final until its author has
RUN it, in BOTH directions, and recorded both readings.** ⭐ **Ruling 123 names
the three: LIVE, PLANTED and IMPOSSIBLE**, and all three are here as tests
rather than as a paragraph in a handoff, because a reading recorded in prose is
one nobody can re-take.

| Reading | What it asserts | Where |
|---|---|---|
| **live** | the real `BOARD.md` here is clean under all five rules |
  `test_live_board_is_clean` |
| **planted** | each rule fires on a board built to break exactly it | the five `test_planted_*` |
| **impossible** | a state the rule cannot reach reports nothing, and
  absence is not a pass | `test_impossible_*` |

## ⚠️ The plant is adversarial to the SEARCH TERM, not to the subject (Ruling 140)

⛔ **A narrative governor's evasion is not more prose; it is prose written as a
table**, so that a byte count scoped to non-table lines reads it as rows.
⭐ **`test_planted_narrative_disguised_as_a_table` is that exact move**, and it
is the reading that decides whether the pair of bounds has a gap.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import repository_root
from tools.quality.board import (
    BOARD,
    BOARD_FRAME,
    BOARD_NARRATIVE_CEILING,
    BOARD_PER_ROW,
    BOARD_ROW_CEILING,
    REGISTER_CLOSE,
    REGISTER_OPEN,
    ROW_FRAME,
    ROWS,
    RULE_DETAIL,
    RULE_DUPLICATE,
    RULE_FRAME,
    RULE_NARRATIVE,
    RULE_ORPHAN,
    RULE_SIZE,
    RULE_STATE,
    RULE_WIDTH,
    STATES,
    board_state,
    check_board,
)
from tools.quality.board.register import namings, repeats_its_naming

#: A minimal register: a header, a separator, one closed row and one live one.
#: ⛔ Written out rather than generated, so a reader can see what the check
#: reads without running it.
HEADER = "<!-- register -->\n| # | Row | Owner | State | Detail |\n|---|---|---|---|---|\n"
FOOTER = "<!-- /register -->\n"
CLOSED = "| W1 | a naming | PO | ✅ done — `abc1234` | [record](BOARD-ARCHIVE.md#w1) |\n"
LIVE = "| W2 | another naming | PO | `todo` | [rows/W2.md](rows/W2.md) |\n"


#: The frame every row file carries, and the fixtures carry it because the
#: live ones do — a fixture that skipped it would test a shape nothing ships.
def _row(name: str) -> str:
    return (
        f"# {name}\n\n⛔ **This file carries the ARGUMENT for board row `{name}` "
        f"and nothing else.**\n⭐ **Its naming, owner and state live once, in the "
        f"register in [`../BOARD.md`](../BOARD.md).**\n\nThe argument.\n"
    )


def _tree(tmp_path: Path, board: str, rows: tuple[str, ...] = ()) -> Path:
    (tmp_path / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
    (tmp_path / BOARD).write_text(board, encoding="utf-8")
    if rows:
        (tmp_path / ROWS).mkdir()
        for name in rows:
            (tmp_path / ROWS / f"{name}.md").write_text(_row(name), encoding="utf-8")
    return tmp_path


def _rules(findings: list) -> list[str]:
    return sorted(finding.rule for finding in findings)


# --------------------------------------------------------------------------
# Reading 1 — LIVE
# --------------------------------------------------------------------------


def test_live_board_is_clean() -> None:
    """⭐ The real board in this repository passes every rule.

    ⛔ **This is the reading that makes the other two mean something.** A check
    proved only against fixtures is a check whose subject has never been
    measured — the shape `check_pointers` was scoped on, arriving here.
    """
    assert check_board(repository_root()) == []


def test_live_notice_names_both_ceilings_and_the_population() -> None:
    """⛔ Ruling 128: print the population in full before reducing it to a scalar."""
    line = board_state(repository_root())[0]
    assert line.startswith("board: ")
    assert "register rows" in line and "live" in line and "detail files" in line
    assert str(BOARD_NARRATIVE_CEILING) in line
    assert str(BOARD_ROW_CEILING) in line


def test_live_board_has_a_detail_file_for_every_live_row() -> None:
    """⭐ The bijection, stated as a number rather than as an absence."""
    line = board_state(repository_root())[0]
    live = int(line.split(" register rows, ")[1].split(" live")[0])
    files = int(line.split("live, ")[1].split(" detail files")[0])
    assert live == files


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


def test_planted_narrative(tmp_path: Path) -> None:
    prose = "x" * (BOARD_NARRATIVE_CEILING + 1) + "\n"
    root = _tree(tmp_path, prose + HEADER + CLOSED + FOOTER)
    assert _rules(check_board(root)) == [RULE_NARRATIVE]


def test_planted_narrative_disguised_as_a_table(tmp_path: Path) -> None:
    """⛔ Ruling 140 — the plant is adversarial to the SEARCH TERM.

    ⚠️ A round's narrative written as `| … |` lines contributes **zero** to the
    narrative count. ⭐ **`board-row-width` is what closes that gap**, and this
    is the reading that proves the two bounds have none between them.
    """
    fat = "| " + "x" * (BOARD_ROW_CEILING + 1) + " |\n"
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER + fat)
    rules = _rules(check_board(root))
    assert RULE_NARRATIVE not in rules, "the narrative bound is blind to this, by construction"
    assert rules == [RULE_WIDTH]


def test_planted_narrative_as_MANY_SHORT_table_rows(tmp_path: Path) -> None:
    """⛔ The plant that GOT THROUGH, and the reason `board-size` exists.

    ⚠️ **Run against the first two bounds before this module shipped: 320 lines
    of round 33's narrative, one line per table row, moved the narrative
    reading by ZERO and tripped the width rule ONCE.** ⭐ Neither bound sees
    text that is short per line and enormous in total.

    ⛔ **`board-size` does, because the evasion raises the numerator and leaves
    the denominator alone.**
    """
    prose = "".join(f"| a line of a round's reasoning, number {n} |\n" for n in range(400))
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER + prose)
    rules = _rules(check_board(root))
    assert RULE_NARRATIVE not in rules
    assert RULE_WIDTH not in rules
    assert rules == [RULE_SIZE]


def test_more_rows_can_never_trip_the_size_bound(tmp_path: Path) -> None:
    """⭐ Ruling 149's failure mode, asserted absent rather than argued absent.

    ⛔ **The line-count governor it retired *"alarmed seven times while the
    property improved seven times"*.** ⚠️ **A ratio cannot do that only if a row
    raises the allowance by MORE than a row costs** — so that is what is
    measured here, at a row width well over this board's live mean of 170 B.
    """
    row = "| W{n} | " + "n" * (BOARD_PER_ROW - 60) + " | PO | `todo` | [d](rows/W{n}.md) |\n"
    many = "".join(row.format(n=100 + i) for i in range(400))
    root = _tree(tmp_path, HEADER + many + FOOTER, rows=tuple(f"W{100 + i}" for i in range(400)))
    assert RULE_SIZE not in _rules(check_board(root))


def test_the_size_bound_allows_the_frame_and_says_so(tmp_path: Path) -> None:
    """⚠️ A board with NO rows still gets `BOARD_FRAME`, and nothing more."""
    root = _tree(tmp_path, HEADER + FOOTER + "x" * (BOARD_FRAME + 1))
    assert _rules(check_board(root)) == [RULE_NARRATIVE, RULE_SIZE]


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE
# --------------------------------------------------------------------------


def test_impossible_no_board_at_all(tmp_path: Path) -> None:
    """⛔ A tree with no board is CLEAN, and the notice says so out loud.

    ⚠️ **The floor runs over arbitrary roots** — a temp tree, a corpus
    repository — ⛔ **so a finding here would be asserting which repository you
    are in.** ⭐ **This is `check_knowledge_index`'s split, reused**: absence is
    reported through the notice channel and presence is enforced by a test that
    knows the answer should be yes.

    ⚠️ **`0 = 0` is not a pass** (Ruling 48), which is why the notice may not be
    silent — and it is not.
    """
    (tmp_path / "docs" / "tasks").mkdir(parents=True, exist_ok=True)
    assert check_board(tmp_path) == []
    assert "board: none" in board_state(tmp_path)[0]


def test_this_repository_has_a_board() -> None:
    """⛔ The enforcement half, and it lives here because only here is it true.

    ⭐ `test_impossible_no_board_at_all` says a missing board is not a floor
    failure anywhere; this says it is a build failure HERE.
    """
    assert (repository_root() / BOARD).is_file()
    assert (repository_root() / ROWS).is_dir()
    board = (repository_root() / BOARD).read_text(encoding="utf-8")
    assert REGISTER_OPEN in board and REGISTER_CLOSE in board


def test_a_W_shaped_table_outside_the_markers_is_not_the_register(tmp_path: Path) -> None:
    """⛔ The defect this check found in its own author, kept as a test.

    ⚠️ **An *In flight* table naming four rows was read as four DUPLICATE
    register rows** by the first version, which inferred the register from
    row shape. ⭐ **A board may hold many `W`-shaped tables; one of them
    says it is the register.**
    """
    elsewhere = "| W2 | in flight | Dev | none | +3 |\n"
    root = _tree(tmp_path, HEADER + LIVE + FOOTER + elsewhere, rows=("W2",))
    assert check_board(root) == []


def test_impossible_board_with_no_register_rows(tmp_path: Path) -> None:
    """⚠️ A board whose register is EMPTY is clean, and the notice says so.

    ⛔ **That is the honest answer and it is why the notice exists.** The rules
    here bound shape, not inhabitation — ⭐ **so the population is printed, and
    a reader who sees `0 register rows` knows the verdict is about nothing.**
    """
    root = _tree(tmp_path, HEADER + FOOTER)
    assert check_board(root) == []
    assert "0 register rows, 0 live" in board_state(root)[0]


@pytest.mark.parametrize("state", ["✅ done — `abc1234`", "done", "DONE at `abc1234`"])
def test_a_closed_row_never_wants_a_detail_file(tmp_path: Path, state: str) -> None:
    """⭐ The other direction of `board-detail`, and it is the one that regresses.

    ⛔ A rule that only fired on a missing file would let every closed row keep
    an editable argument, which is the state `BOARD-ARCHIVE.md` exists to
    prevent.
    """
    row = f"| W1 | a naming | PO | {state} | [record](BOARD-ARCHIVE.md#w1) |\n"
    assert check_board(_tree(tmp_path / "without", HEADER + row + FOOTER)) == []
    with_file = _tree(tmp_path / "with", HEADER + row + FOOTER, rows=("W1",))
    assert _rules(check_board(with_file)) == [RULE_ORPHAN]


def test_a_multi_id_row_is_one_row_and_one_file(tmp_path: Path) -> None:
    """⚠️ `W17 + W19` are one commit, ruled, and therefore one row.

    ⛔ **The first id owns the file and the rest ride with it**, so a register
    that carries them as one does not owe two files — and a check that demanded
    two would push the PO into splitting a row the CTO fused.
    """
    row = "| W17 + W19 | a naming | PO | `todo` | [rows/W17.md](rows/W17.md) |\n"
    assert check_board(_tree(tmp_path, HEADER + row + FOOTER, rows=("W17",))) == []


# --------------------------------------------------------------------------
# `board-frame` — the live-tree guarantee Ruling 180 would otherwise have cost
# --------------------------------------------------------------------------


def test_a_row_file_that_lost_its_frame_is_a_finding(tmp_path: Path) -> None:
    """⛔ The one live-tree property left after Ruling 180, and why it is that one.

    ⚠️ **`test_migration.py`'s subject is now the migration's OUTPUT ref**, which
    is right — a migration is a claim about refs — ⛔ **but it means nothing was
    left watching a live row file at all.**

    ⭐ **A frame survives every amendment**, because amending a row means adding
    to its argument and never removing its identity — ⛔ **so this is the one
    thing that can be required of a file the PO is told to edit freely.**
    """
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",))
    assert check_board(root) == []
    (root / ROWS / "W2.md").write_text("a fragment with no frame at all\n", encoding="utf-8")
    assert _rules(check_board(root)) == [RULE_FRAME]


def test_appending_to_a_row_file_is_always_clean(tmp_path: Path) -> None:
    """⭐ The contract's own action — *"editing it is the point"* — stays green.

    ⛔ **This is the assertion `CTO-46/1` was about.** ⚠️ A test that reddened on
    an ordinary amendment would be a gate people edit their way around, and
    *"a checker people rename fields around is a checker on its way to being
    switched off"* is this branch's own sentence.
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


# --------------------------------------------------------------------------
# ⛔ Ruling 183 — `rows/` is printed with its BYTES, and the three readings
# --------------------------------------------------------------------------


def test_live_notice_names_the_row_files_BYTES_and_not_only_their_count() -> None:
    """⭐ The LIVE reading, against a DERIVED sum rather than a typed number.

    ⛔ **Ruling 181: a number typed beside the thing it measures goes stale in
    the copy nobody re-measures**, so the expectation is re-derived from the
    directory on every run and the notice is what carries the figure.
    """
    root = repository_root()
    files = sorted((root / ROWS).glob("*.md"))
    # ⛔ Ruling 48: an empty rows/ would satisfy every byte assertion below.
    assert files, f"{ROWS}/ holds no row files, so this reading is vacuous"
    total = sum(path.stat().st_size for path in files)
    assert total > 0
    assert f"{len(files)} detail files in {ROWS}/ holding {total} bytes" in board_state(root)[0]


def test_planted_relocation_into_rows_MOVES_the_notice(tmp_path: Path) -> None:
    """⛔ `ARCH/14`'s `R2`, which is the reading that decided Ruling 183.

    ⚠️ **Measured by the CTO at round 47, pinned: `rows/` inflated from 28,787
    bytes to 3,231,307 — 112× — and the `board:` line came back BYTE-IDENTICAL
    with the floor clean.** ⭐ **The plant is adversarial to the SEARCH TERM**
    (Ruling 140): the line printed the COUNT, and relocating a board's
    reasoning into the files it already has does not change the count.

    ⛔ **And it stays a NOTICE**: the same edit must leave `check_board` clean,
    because appending to a live row's argument is the contract's own prescribed
    action and a bound there would forbid what the file exists for.
    """
    root = _tree(tmp_path, HEADER + LIVE + FOOTER, rows=("W2",))
    before = board_state(root)[0]
    path = root / ROWS / "W2.md"
    path.write_text(path.read_text(encoding="utf-8") + "x" * 100_000, encoding="utf-8")
    after = board_state(root)[0]
    assert "1 detail files" in before and "1 detail files" in after, "the count cannot see it"
    assert before != after, "Ruling 183: accretion must move a number somebody reads every run"
    assert check_board(root) == [], "a notice forbids nothing, and this edit is legal"


def test_impossible_a_board_with_no_rows_directory_reads_zero_bytes(tmp_path: Path) -> None:
    """⛔ The IMPOSSIBLE reading, and it DIFFERS from the pass rather than echoing it.

    ⭐ `0 files holding 0 bytes` is the honest answer for a tree that has a
    register and no arguments beside it — ⚠️ **and a reader who sees it knows the
    figure above is about nothing** (Ruling 48).
    """
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER)
    assert f"0 detail files in {ROWS}/ holding 0 bytes" in board_state(root)[0]
    assert check_board(root) == []
    assert not (root / ROWS).exists(), "and the directory is genuinely absent, not empty"


# --------------------------------------------------------------------------
# ⛔ `CTO-47/4` — the `board-frame` message describes the PREDICATE
# --------------------------------------------------------------------------


def test_the_frame_finding_states_what_is_CHECKED_not_what_is_hoped(tmp_path: Path) -> None:
    """⛔ `CTO-47/4`: the predicate is two substrings; the message claimed more.

    ⚠️ **It said the file *"states which row it argues and that the naming, owner
    and state are the board's"*** — ⛔ **which `body.startswith` and `in` cannot
    read.** ⭐ **A weak predicate is the RIGHT trade for amendment-proofness**
    (`R3`, round 47: a row file rewritten as `# W10` plus *"I ate the sandwich
    and nothing else."* passes, by design) — ⛔ **but a message that describes a
    check nobody wrote sends the next reader to debug the wrong claim.**
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


def test_live_no_register_row_on_this_board_is_board_state() -> None:
    """⭐ The LIVE reading. ⛔ `RULE_STATE` was the one code with no test of its path.

    ⚠️ **Ruling 152's reachability held — `check_board` does emit all eight — so
    this was a test gap and not a missing guard.** ⭐ The population is printed
    beside the verdict, because `0 register rows` would satisfy this vacuously.
    """
    root = repository_root()
    assert [f for f in check_board(root) if f.rule == RULE_STATE] == []
    assert int(board_state(root)[0].split("board: ")[1].split(" register")[0]) > 0


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

    ⚠️ **Each plant wears the word the first `is_closed` searched for, in a form
    the clause did not picture**: `done` arriving after the mention of another
    row, `done` not ending on a word boundary, and the two shapes that were
    really on the board — `W5`'s and `W16`'s — which declare nothing at all.
    ⭐ **`DONE-ish` came from the impossible plant rather than from argument.**
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

    ⚠️ **`` `todo` — after `W44` is done ``** read as CLOSED when `is_closed` was
    a substring test: it owed no detail file, left the bijection, and the floor
    printed `quality floor: clean` with no finding at all. ⭐ **It DECLARES
    `todo`, so it is not `board-state`** — the mention is ambiguous and the
    declaration is not, which is the whole of the closed-set remedy.
    """
    row = "| W2 | a naming | PO | `todo` — after `W44` is done | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER)
    rules = _rules(check_board(root))
    assert RULE_STATE not in rules, "it declares todo; only the mention is loose"
    assert rules == [RULE_DETAIL], "⛔ the finding a substring test lost in silence"


@pytest.mark.parametrize("declared", sorted(STATES))
def test_a_cell_that_DECLARES_a_state_is_never_board_state(tmp_path: Path, declared: str) -> None:
    """⭐ Every word of the closed vocabulary, derived rather than retyped.

    ⛔ **Parametrised over `STATES` itself**, so a word added to the vocabulary
    joins this population without the test being edited and an EMPTY vocabulary
    skips rather than passing (Ruling 48).
    """
    row = f"| W2 | a naming | PO | ⛔ **{declared}** — `abc1234` | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    assert RULE_STATE not in _rules(check_board(root))


def test_impossible_board_state_cannot_fire_on_an_EMPTY_register(tmp_path: Path) -> None:
    """⛔ The IMPOSSIBLE reading, and it DIFFERS from the pass by naming `0`.

    ⭐ A register with no rows has no cell to judge, so silence here is correct —
    ⚠️ **and `0 = 0` is not a pass**, which is why the population is read out of
    the notice in the same assertion.
    """
    root = _tree(tmp_path, HEADER + FOOTER)
    assert [f for f in check_board(root) if f.rule == RULE_STATE] == []
    assert "0 register rows, 0 live" in board_state(root)[0]


# --------------------------------------------------------------------------
# ⛔ Ruling 186 — the notice names the files whose ARGUMENT IS THEIR NAMING
# --------------------------------------------------------------------------


def test_live_notice_names_exactly_the_files_whose_argument_IS_their_naming() -> None:
    """⭐ The LIVE reading, derived from the tree rather than typed.

    ⛔ **No count is asserted**, and that is deliberate: the PO fixing those
    files is the outcome this notice exists to cause, and an assertion on the
    number would redden on the remedy. ⭐ **What is asserted is the WIRING** —
    that the notice reports the same set the predicate does, against each row's
    OWN naming cell rather than against some other row's.
    """
    root = repository_root()
    text = (root / BOARD).read_text(encoding="utf-8")
    named = namings(text)
    files = sorted((root / ROWS).glob("*.md"))
    assert files and named, "Ruling 48: neither side of the comparison may be empty"
    expected = sorted(
        (
            path.stem
            for path in files
            if repeats_its_naming(path.read_text(encoding="utf-8"), named.get(path.stem, ""))
        ),
        key=lambda name: (len(name), name),
    )
    line = board_state(root)[0]
    if expected:
        assert f"{len(expected)} arguing only their own naming — {' '.join(expected)}" in line
    else:
        assert "none arguing only their own naming" in line


def test_planted_an_argument_that_merely_REPEATS_the_naming_is_named(tmp_path: Path) -> None:
    """⛔ The PLANTED reading, and the plant is a real live shape.

    ⚠️ **Seven files on the tree at `798956c` carry exactly this** — their whole
    argument is a normalised copy of the naming — ⛔ **and it is the one thing
    the frame sentence inside them forbids:** *"not here, and not in two
    places."* ⭐ **`board-frame` passes it, and must**, which is why this is the
    notice's business and not the rule's.
    """
    naming = "a naming worth one sentence"
    row = f"| W2 | {naming} | PO | `todo` | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    path = root / ROWS / "W2.md"
    head = path.read_text(encoding="utf-8").rsplit("\n\n", 1)[0]
    path.write_text(f"{head}\n\n⛔ **{naming.upper()}.**\n", encoding="utf-8")
    assert "1 arguing only their own naming — W2 (Ruling 186)" in board_state(root)[0]
    assert check_board(root) == [], "⛔ a NOTICE. A gate here is the one Ruling 180 removed."


def test_planted_an_argument_that_EXTENDS_the_naming_is_NOT_named(tmp_path: Path) -> None:
    """⛔ The control, and without it the notice flags correct work.

    ⭐ **An argument that restates the row and then argues it is what the file is
    for.** ⚠️ **A prefix test reports 17 more files on the live tree**, and a
    notice people learn to scroll past is worse than none.
    """
    naming = "a naming worth one sentence"
    row = f"| W2 | {naming} | PO | `todo` | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    path = root / ROWS / "W2.md"
    head = path.read_text(encoding="utf-8").rsplit("\n\n", 1)[0]
    path.write_text(f"{head}\n\n{naming} — and the reason it matters.\n", encoding="utf-8")
    assert "none arguing only their own naming" in board_state(root)[0]


def test_impossible_a_board_with_no_row_files_names_NONE(tmp_path: Path) -> None:
    """⛔ The IMPOSSIBLE reading, and it DIFFERS from the pass rather than echoing it.

    ⚠️ **A register with no arguments beside it cannot have one that repeats its
    naming** — ⭐ **and the notice says `none` out loud rather than falling
    silent**, which is Ruling 48's whole complaint about `0`.
    """
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER)
    line = board_state(root)[0]
    assert "none arguing only their own naming (Ruling 186)" in line
    assert f"0 detail files in {ROWS}/ holding 0 bytes" in line
