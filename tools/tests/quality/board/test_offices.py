"""Mirror of `tools/quality/board/offices.py` (R12): `W96/5` and `W132/3`, landed by `W125`.

⛔ **The subject is a synthesised repository** (`conftest.py`, Ruling 191(b)). ⭐ **The office
checkouts are deliberately named `po` and `cto`, which are the names the board's prose uses.**
A name copied into code would therefore take them off the line while the block is ABSENT, and
`test_planted_the_block_MISSING_…` would go RED. ⚠️ **A copied name the fixture never uses
survives that test, and the handoff says so.**

| clause | ⛔ the expectation, written before the run |
|---|---|
| the block ABSENT | the line says ABSENT, NOT ANSWERED, and every checkout stays named |
| the block DECLARED | its entries are taken off, printed with a count, and unmatched ones named |
| the names | FOLLOW the block when it changes, so they cannot be code |
| zero | `none.`, never a bare `0` (`W132/3`) |
| the gate | ⛔ NOT narrowed by the declaration, and the exit code does not move |
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.board.corroborate import CORROBORATED, corroborate
from tools.quality.board.offices import ABSENT, DECLARED, OFFICES_OPEN, UNREADABLE, read
from tools.quality.board.register import BOARD
from tools.workspace import git

from .conftest import RELEASE, commit, write_board

HEADER = "| Checkout | Why it is not a row |\n|---|---|\n"


def _block(body: str, header: str = HEADER) -> str:
    return f"\n<!-- offices -->\n{header}{body}<!-- /offices -->\n"


def _board(root: Path, offices: str | None) -> None:
    """An empty, declared observation table, with the offices block appended when given."""
    write_board(root, "")
    if offices is not None:
        with (root / BOARD).open("a", encoding="utf-8") as board:
            board.write(offices)


def _offices(root: Path) -> None:
    """Two `0`-ahead checkouts no row names, laid out as the host lays out `wt/po`."""
    assert git(root, "branch", "fix/Wcto0").returncode == 0
    for name, branch in (("po", "feat/bare"), ("cto", "fix/Wcto0")):
        where = root.parent / "x-wt" / name
        assert git(root, "worktree", "add", "-q", str(where), branch).returncode == 0


def _lines(root: Path) -> tuple[int, str, str]:
    lines, code = corroborate(root, RELEASE)
    blind = next(line for line in lines if "BY CONSTRUCTION" in line)
    office = next(line for line in lines if line.startswith(f"  office checkouts ({OFFICES_OPEN})"))
    return code, blind, office


# --------------------------------------------------------------------------
# The parser
# --------------------------------------------------------------------------


def test_the_declaration_is_ABSENT_when_the_board_declares_no_block() -> None:
    """⛔ No block is not an empty block: nothing was declared, so nothing is answered."""
    assert read("# Board\n\n| Checkout |\n|---|\n| `wt/po` |\n") == read("") != read(_block(""))
    assert read("").state == ABSENT
    assert read(f"prose that mentions {OFFICES_OPEN} inline\n").state == ABSENT


def test_a_DECLARED_block_reads_its_Checkout_spans_in_order_and_once() -> None:
    """⭐ The entries are the code spans of the `Checkout` column, and nothing else."""
    body = "| `wt/po`, `wt/cto` | offices |\n| `wt/po` | again |\n| none | `not/this` |\n"
    declaration = read(_block(body))
    assert declaration.state == DECLARED
    assert declaration.entries == ("wt/po", "wt/cto")


def test_a_block_with_NO_Checkout_column_is_UNREADABLE_and_NOT_empty() -> None:
    """⛔ `W111`'s rule, one block over: a declared block that did not read is not empty."""
    text = "# Board\n" + _block("| `wt/po` | x |\n", header="| Where | Why |\n|---|---|\n")
    declaration = read(text)
    assert declaration.state == UNREADABLE
    assert declaration.line == 3, declaration
    assert read(_block("")).state == DECLARED and read(_block("")).entries == ()


def test_an_UNCLOSED_block_is_still_DECLARED() -> None:
    """⚠️ A missing close marker must not make a declared block vanish."""
    declaration = read(f"{OFFICES_OPEN}\n{HEADER}| `wt/po` | office |\n")
    assert (declaration.state, declaration.entries) == (DECLARED, ("wt/po",))


# --------------------------------------------------------------------------
# The line, over the synthesised repository
# --------------------------------------------------------------------------


def test_planted_the_block_MISSING_says_ABSENT_and_every_checkout_STAYS_NAMED(
    repository: Path,
) -> None:
    """⛔ PLANT 2, and PLANT 4's check: no block, no answer, and no name read from code."""
    _offices(repository)
    _board(repository, None)
    _code, blind, office = _lines(repository)
    assert "named by no row: 3 — cto leak po" in blind, blind
    assert "ABSENT" in office and "NOT ANSWERED" in office, office


def test_a_DECLARED_block_takes_its_offices_off_the_line_and_PRINTS_them(
    repository: Path,
) -> None:
    """⭐ The judgement `W96/5` asked for: the declared offices leave the line and are named."""
    _offices(repository)
    _board(repository, _block("| `wt/po`, `wt/cto`, `wt/gone` | offices |\n"))
    _code, blind, office = _lines(repository)
    assert "named by no row: 1 — leak" in blind, blind
    assert "DECLARED with 3 entries; taken off the line above (2): cto po" in office, office
    assert "matching none of those checkouts: wt/gone" in office, office


def test_the_names_FOLLOW_THE_BLOCK_and_are_never_read_from_code(repository: Path) -> None:
    """⛔ PLANT 4: change the block and the classification must change with it."""
    _offices(repository)
    readings = {}
    for declared in ("wt/cto", "wt/po"):
        _board(repository, _block(f"| `{declared}` | office |\n"))
        readings[declared] = _lines(repository)[1]
    assert "named by no row: 2 — leak po" in readings["wt/cto"], readings
    assert "named by no row: 2 — cto leak" in readings["wt/po"], readings


def test_planted_ZERO_prints_none_and_never_a_bare_0(repository: Path) -> None:
    """⛔ PLANT 3, `W132/3`: at zero the line prints `none.`, like its two neighbours.

    ⭐ **Zero is reached two ways and both are read**: no invisible checkout at all, and every
    invisible checkout declared an office.
    """
    assert git(repository, "worktree", "remove", str(repository.parent / "leak")).returncode == 0
    _board(repository, None)
    empty = _lines(repository)[1]
    _offices(repository)
    _board(repository, _block("| `wt/po`, `wt/cto` | offices |\n"))
    declared = _lines(repository)[1]
    for line in (empty, declared):
        assert line.endswith("named by no row: none."), line
        assert "row: 0" not in line, f"⛔ a bare `0` — {line}"


def test_an_EMPTY_or_UNREADABLE_declaration_takes_NOTHING_off(repository: Path) -> None:
    """⚠️ Neither is a clean answer, and neither narrows the line."""
    _offices(repository)
    _board(repository, _block(""))
    _code, empty_blind, empty = _lines(repository)
    _board(repository, _block("| `wt/po` | x |\n", header="| Where | Why |\n|---|---|\n"))
    _code, unreadable_blind, unreadable = _lines(repository)
    assert "DECLARED and EMPTY" in empty and "not a clean answer" in empty, empty
    assert "UNREADABLE" in unreadable and "NOT ANSWERED" in unreadable, unreadable
    for blind in (empty_blind, unreadable_blind):
        assert "named by no row: 3 — cto leak po" in blind, blind


def test_a_declared_office_carrying_UNMERGED_work_is_STILL_GATED_and_the_exit_is_unmoved(
    repository: Path,
) -> None:
    """⛔ The declaration narrows the invisible line ALONE (Ruling 319's ground)."""
    assert git(repository, "checkout", "-q", "-b", "fix/Woffice").returncode == 0
    commit(repository, "office.txt", "work\n")
    assert git(repository, "checkout", "-q", RELEASE).returncode == 0
    where = repository.parent / "x-wt" / "po"
    assert git(repository, "worktree", "add", "-q", str(where), "fix/Woffice").returncode == 0
    codes = {}
    for name, offices in (("absent", None), ("declared", _block("| `wt/po` | office |\n"))):
        _board(repository, offices)
        lines, codes[name] = corroborate(repository, RELEASE)
        gate = next(line for line in lines if "dispatched and" in line)
        assert "UNNAMED by any row" in gate and "fix/Woffice" in gate, gate
    assert codes == {"absent": CORROBORATED, "declared": CORROBORATED}, codes


def test_the_office_line_carries_NO_other_line_s_anchor(repository: Path) -> None:
    """⚠️ `W170`'s decoy-anchor cost: every reading selects its line by a substring."""
    _offices(repository)
    anchors = (
        "BY CONSTRUCTION",
        "dispatched and",
        "round branches",
        "namespaces exempt from the gate",
        "could not count",
        "held by no checkout",
        "STILL CHECKED OUT",
        "Ruling 265",
    )
    for offices in (None, _block(""), _block("| `wt/po` | office |\n")):
        _board(repository, offices)
        office = _lines(repository)[2]
        assert not [anchor for anchor in anchors if anchor in office], office
