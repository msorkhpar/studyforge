"""`board_state`'s readings — the NOTICE half of `tools/quality/board/` (R12).

⛔ **A second test module for one source module, and the reason is measured.**
⚠️ **`test_init.py` reached 607 lines against a 600 ceiling while Ruling 186(b)'s
two clauses were being added**, and the package's own `__init__.py` stood at 388
of 400 — ⛔ **`W67`'s zero-headroom shape arriving in the module written to stop
the board growing unnoticed.** ⭐ **The seam is the one the handoff had already
named: `check_board` and `board_state` depend on nothing of each other's.**
⚠️ `test_migration.py` is the precedent for a subject-named module in this test
package; `check_mirrors` requires a mirror to EXIST and does not forbid a second.

## ⛔ Both readings here forbid nothing, which is what they are for

⭐ **Rulings 183 and 186 are NOTICES.** ⛔ **So no test here asserts a pass
condition, and none asserts a CARDINALITY**: `rows/` bytes under a total is a
bound, but `50 live rows` is a cardinality and the contract's own prescribed
actions — minting, closing, re-scoping — change it. ⚠️ **Every live expectation
below is DERIVED from the tree on the same run** (Ruling 180's question arriving
in a notice), and the populations are asserted inhabited first (Ruling 48).
"""

from __future__ import annotations

from pathlib import Path

from tests.support import repository_root
from tools.quality.board import (
    BOARD,
    ROWS,
    RULE_UNOBSERVED,
    board_state,
    check_board,
)
from tools.quality.board.register import (
    duplicates_a_state,
    namings,
    repeats_its_naming,
    row_order,
)
from tools.tests.quality.board.test_bijection import CLOSED, FOOTER, HEADER, LIVE, _tree

# --------------------------------------------------------------------------
# ⛔ Ruling 183 — `rows/` is printed with its BYTES, and the three readings
# --------------------------------------------------------------------------


def test_live_notice_names_the_row_files_BYTES_and_not_only_their_count() -> None:
    """⭐ The LIVE reading, against a DERIVED sum rather than a typed number.

    ⛔ **Ruling 181**: the expectation is re-derived from the directory every run.
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

    ⚠️ **Measured by the CTO, pinned: `rows/` inflated 112×, to 3.2 MB, and the
    `board:` line came back BYTE-IDENTICAL with the floor clean.** ⭐ **The plant
    is adversarial to the SEARCH TERM** (Ruling 140) — it printed a COUNT — ⛔ **and
    it stays a NOTICE: the same edit leaves `check_board` clean.**
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

    ⭐ `0 files holding 0 bytes` is honest for a register with no arguments beside
    it — ⚠️ **a reader who sees it knows the figure is about nothing** (Ruling 48).
    """
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER)
    assert f"0 detail files in {ROWS}/ holding 0 bytes" in board_state(root)[0]
    assert check_board(root) == []
    assert not (root / ROWS).exists(), "and the directory is genuinely absent, not empty"


# --------------------------------------------------------------------------
# ⛔ Ruling 186(b) — the second notice line, and its two closed predicates
# --------------------------------------------------------------------------

#: The notice's second line, which is where both clauses are reported.
ROW_LINE = f"row arguments in {ROWS}/ (Ruling 186, no bound): "


def _rows_line(root: Path) -> str:
    return next(line for line in board_state(root) if line.startswith(ROW_LINE))


def test_live_row_line_names_exactly_what_the_two_PREDICATES_name() -> None:
    """⭐ The LIVE reading, DERIVED — and deliberately not a count.

    ⛔ **No cardinality is asserted.** ⚠️ **`50 live rows` is a cardinality and the
    contract's own prescribed actions change it** — minting, closing and
    re-scoping — ⭐ **so what is asserted is the WIRING**: that the line reports
    the same sets the predicates do, each row against its OWN naming cell.
    """
    root = repository_root()
    named = namings((root / BOARD).read_text(encoding="utf-8"))
    files = sorted((root / ROWS).glob("*.md"))
    assert files and named, "Ruling 48: neither side of the comparison may be empty"
    bodies = {path.stem: path.read_text(encoding="utf-8") for path in files}
    line = _rows_line(root)
    for what, holds in (
        ("repeat their own naming", lambda n, b: repeats_its_naming(b, named.get(n, ""))),
        ("duplicate a state", lambda n, b: duplicates_a_state(b)),
    ):
        found = sorted((n for n, b in bodies.items() if holds(n, b)), key=row_order)
        expected = f"{len(found)} {what}" + (f" — {' '.join(found)}" if found else "")
        assert expected in line, (what, line)


def test_planted_an_argument_that_merely_REPEATS_the_naming_is_named(tmp_path: Path) -> None:
    """⛔ PLANTED, clause 1 — and the plant is a real live shape.

    ⚠️ **Files on the tree carry exactly this: their whole argument is a
    normalised copy of the naming** — ⛔ **the one thing the frame sentence inside
    them forbids.** ⭐ **`board-frame` passes it and must**, which is why this is
    the notice's business and not the rule's.
    """
    naming = "a naming worth one sentence"
    row = f"| W2 | {naming} | PO | `todo` | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    path = root / ROWS / "W2.md"
    head = path.read_text(encoding="utf-8").rsplit("\n\n", 1)[0]
    path.write_text(f"{head}\n\n⛔ **{naming.upper()}.**\n", encoding="utf-8")
    assert "1 repeat their own naming — W2" in _rows_line(root)
    assert check_board(root) == [], "⛔ a NOTICE. A gate here is the one Ruling 180 removed."


def test_planted_an_argument_that_OPENS_WITH_A_STATE_is_named(tmp_path: Path) -> None:
    """⛔ PLANTED, clause 2 — and this plant is the only thing that proves it can fire.

    ⚠️ **The live population is `0` once the two rows that carried it close**, and
    ⛔ **a clause-2 pass with no planted hit is VACUOUS, not green** (Ruling 48,
    Ruling 186(b)(ii)). ⭐ The planted text is the opening idiom of `W14`'s record
    in `BOARD-ARCHIVE.md`, verbatim in shape from `798956c`.
    """
    row = "| W2 | a naming | PO | `in flight` | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    path = root / ROWS / "W2.md"
    head = path.read_text(encoding="utf-8").rsplit("\n\n", 1)[0]
    path.write_text(
        f"{head}\n\n⏳ **in flight** — ⛔ **TWO missing fixtures, and they are one task**\n",
        encoding="utf-8",
    )
    line = _rows_line(root)
    assert "1 duplicate a state — W2" in line
    assert "0 repeat their own naming" in line, "the two clauses are independent"
    # ⛔ **REPAIRED AT THE ONE READER, and `W96` says so** (Ruling 190(b)). ⚠️ This
    # line read `check_board(root) == []`, and it went red for being WRONG rather
    # than for `W96` being wrong: ⭐ **the fixture's register cell declares
    # `in flight` and the fixture board carries no observation table**, which is
    # exactly `board-unobserved`'s subject — an asserted state with no observer.
    # ⛔ The clause this test exists for is untouched: Ruling 186(b) is a NOTICE,
    # and the rule below is a different rule of a different ruling.
    assert [f.rule for f in check_board(root)] == [RULE_UNOBSERVED], (
        "⛔ Ruling 186(b) is still a NOTICE; this finding is Ruling 189(b)'s, on the "
        "fixture's own `in flight` register cell"
    )


def test_planted_an_argument_that_EXTENDS_the_naming_is_NOT_named(tmp_path: Path) -> None:
    """⛔ The control, and without it the notice flags correct work.

    ⭐ **Restating the row and then arguing it is what the file is for.** ⚠️ **A
    prefix test reports 17 more files on the live tree**, and a notice people
    learn to scroll past is worse than none.
    """
    naming = "a naming worth one sentence"
    row = f"| W2 | {naming} | PO | `todo` | [d](rows/W2.md) |\n"
    root = _tree(tmp_path, HEADER + row + FOOTER, rows=("W2",))
    path = root / ROWS / "W2.md"
    head = path.read_text(encoding="utf-8").rsplit("\n\n", 1)[0]
    path.write_text(f"{head}\n\n{naming} — and the reason it matters.\n", encoding="utf-8")
    assert "0 repeat their own naming" in _rows_line(root)


def test_impossible_a_board_with_no_row_files_names_NEITHER(tmp_path: Path) -> None:
    """⛔ The IMPOSSIBLE reading, and it DIFFERS from the pass by naming `0` twice.

    ⚠️ **A register with no arguments beside it can satisfy neither clause** —
    ⭐ **and the line says `0` out loud rather than falling silent**, which is
    Ruling 48's whole complaint about an absent denominator.
    """
    root = _tree(tmp_path, HEADER + CLOSED + FOOTER)
    line = _rows_line(root)
    assert "0 repeat their own naming; 0 duplicate a state." in line
    assert f"0 detail files in {ROWS}/ holding 0 bytes" in board_state(root)[0]
