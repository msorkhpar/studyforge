"""`W176` — every count `corroborate` prints NAMES ITS UNIT (Ruling 224), asserted both ways (R12).

⛔ **The contract is `docs/tasks/rows/W176.md`'s four clauses.** ⭐ **One In-flight cell may
name several ids (Rulings 218 and 274)**, so a row count and an id count are different numbers
on exactly the boards that bundle, and the SAME number on every board that does not:

| the board | ⛔ the expectation, written BEFORE the run |
|---|---|
| the refuted reading `CTO-71/11` quoted, `NS-04 NS-06` bundled | `3 rows across 4 ids`, exit `1` |
| one id per cell, both vocabularies | `2 rows across 2 ids`, exit `1` — ⭐ the arm a rename fails |
| a bundled cell git cannot count | `1 rows across 2 ids` on its OWN line, exit `2` |

⚠️ **The coordinator's merge guard parses these lines from outside the repository**, so the
line prefixes and the `: ` then backticked-ids shape are PINNED here, not only the counts.
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.quality.board.corroborate import NOT_AUTHORITATIVE, REFUTED, corroborate
from tools.workspace import git

from .conftest import RELEASE, unreadable, write_board

#: ⛔ The reading `CTO-71/11` took at a release tip: three rows, one of them naming TWO ids.
BUNDLED = (
    "| `NS-04` `NS-06` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n"
    "| `NS-05` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n"
    "| `W167` | Dev | `wt/x`, `fix/Wsilent` | 0 | in flight |\n"
)

#: ⭐ One id per cell, and one of EACH vocabulary, so a counter reading only `W` ids differs.
SINGLE = (
    "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n"
    "| `NS-04` | Dev | `wt/x`, `fix/Wsilent` | 0 | in flight |\n"
)

#: ⛔ The coordinator's three anchors, verbatim, and the carrier line `W153` owns.
GUARDED = (
    r"^  ⛔ rows REFUTED by git",
    r"^  (⛔ )?dispatched and",
    r"^  (⛔ )?(unmerged branches held|UNMERGED and HELD)",
    r"^  ⭐ carriers DECLARED",
)


def _run(root: Path, rows: str) -> tuple[int, list[str]]:
    write_board(root, rows)
    lines, code = corroborate(root, RELEASE)
    return code, lines


def _line(lines: list[str], prefix: str) -> str:
    found = [line for line in lines if line.startswith(prefix)]
    assert len(found) == 1, (prefix, lines)
    return found[0]


def test_a_BUNDLED_cell_prints_TWO_numbers_that_DIFFER_and_says_which_is_which(
    repository: Path,
) -> None:
    """⛔ Clause 1 and clause 3's first arm: `3` rows and `4` ids, both NAMED, exit unmoved."""
    code, lines = _run(repository, BUNDLED)
    assert code == REFUTED, "⛔ clause 4: the labels move and the exit code does not"
    refuted = _line(lines, "  ⛔ rows REFUTED by git")
    assert (
        refuted == "  ⛔ rows REFUTED by git (3 rows across 4 ids): `NS-04` `NS-06` `NS-05` `W167`"
    )
    tail = refuted.split(": ", 1)[1]
    assert len(tail.split()) == 4, "⭐ the ids a reader counts are the ids the line names"
    assert "corroborate: 3 of 3 rows REFUTED by git, 0 rows NOT ANSWERABLE" in lines[-1]


def test_ONE_ID_per_cell_prints_the_SAME_number_under_BOTH_units(repository: Path) -> None:
    """⭐ Clause 3's second arm — the one that stops the fix being read as a rename."""
    code, lines = _run(repository, SINGLE)
    assert code == REFUTED
    refuted = _line(lines, "  ⛔ rows REFUTED by git")
    assert refuted == "  ⛔ rows REFUTED by git (2 rows across 2 ids): `W42` `NS-04`"


def test_a_BUNDLED_cell_git_CANNOT_COUNT_names_both_units_on_its_OWN_line(
    repository: Path,
) -> None:
    """⛔ Clause 2: the twin fold line and the summary's second count, and exit `2` survives."""
    branch = unreadable(repository, "fix/W4")
    code, lines = _run(
        repository, f"| `W42` + `W43` | Dev | `wt/x`, `{branch}` | 0 | in flight |\n"
    )
    assert code == NOT_AUTHORITATIVE
    assert _line(lines, "  ⛔ rows NOT ANSWERABLE").startswith(
        "  ⛔ rows NOT ANSWERABLE (1 rows across 2 ids): `W42` + `W43` — "
    )
    assert "0 of 1 rows REFUTED by git, 1 rows NOT ANSWERABLE" in "\n".join(lines)


def test_the_HEADER_counts_are_ROWS_and_say_so_over_a_bundled_cell(repository: Path) -> None:
    """⛔ Clause 2's sweep: over ONE row naming TWO `W` ids, every header count reads `1`.

    ⭐ **If any of them were an id count it would read `2` here**, so the unit each line
    names is the unit the count is in — rows, and started rows where the population is
    narrowed to them.
    """
    code, lines = _run(
        repository, "| `W42` + `W43` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n"
    )
    assert code == REFUTED
    assert lines[0].startswith("corroborate: release release/m0-foundations, 1 observation rows, ")
    reading = lines[1]
    for count in (
        ": 1 rows, ",
        " 1 rows naming a `W` row id, ",
        " 1 rows declaring a started state, ",
        " 0 rows declaring NO state this vocabulary carries ",
        " started rows with a checkout, ",
        " started rows ahead; ",
    ):
        assert count in reading, (count, reading)
    assert "1 of 1 rows REFUTED by git" in lines[-1]
    assert "(1 rows across 2 ids)" in _line(lines, "  ⛔ rows REFUTED by git")


def test_the_GUARDED_PREFIXES_and_the_ID_SHAPE_are_byte_stable(repository: Path) -> None:
    """⛔ The coordinator's merge guard reads these lines: a prefix change is irreversible mid-wave.

    ⭐ **One reading inhabits all four**: the fixture's `held` and `leak` checkouts are named by
    no row, `feat/live` is unmerged and held by nothing, and it declares an OPEN row (`W153`).
    """
    assert git(repository, "config", "branch.feat/live.description", "W901").returncode == 0
    register = "| W901 | a dispatched row | Dev | `todo` | [rows/W901.md](rows/W901.md) |\n"
    write_board(repository, BUNDLED, register=register)
    lines, code = corroborate(repository, RELEASE)
    assert code == REFUTED
    for anchor in GUARDED:
        assert any(re.match(anchor, line) for line in lines), (anchor, lines)
    tail = _line(lines, "  ⛔ rows REFUTED by git").split(": ", 1)[1]
    assert re.fullmatch(r"`[^`]+`( `[^`]+`)*", tail), tail
    assert re.findall(r"`([^`]+)`", tail) == ["NS-04", "NS-06", "NS-05", "W167"]
