"""Mirror of `tools/quality/board/inflight.py` (R12): the generator, and Ruling 191 both ways.

⛔ **The subject is a synthesised repository** (`conftest.py`, Ruling 191(b)).

| clause | ⛔ the expectation, written before the run |
|---|---|
| generated halves | the checkout half and `n @ tip` from git; the rest verbatim |
| a wrong correspondence | ⛔ still REFUTED after generation (PLANT 1) |
| the refuting population | ⭐ verdicts EQUAL before and after, INHABITED (Ruling 48) |
| ⚠️ the survivor | a row claiming ANOTHER row's live branch is CORROBORATED in both states |
| the control that must fail | generating the branch half too makes an absorbed row CORROBORATE |
| a generated cell later | DATED, not wrong, once the branch moves: not vacuous over time |
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.quality.board import inflight
from tools.quality.board.contradiction import observation_findings
from tools.quality.board.corroborate import (
    CORROBORATED,
    NOT_AUTHORITATIVE,
    REFUTED,
    corroborate,
)
from tools.quality.board.graph import Graph
from tools.quality.board.inflight import GENERATED, generate, main
from tools.quality.board.observation import INFLIGHT_CLOSE, INFLIGHT_OPEN
from tools.quality.board.register import BOARD
from tools.quality.board.verdict import Claim

from .conftest import RELEASE, commit, unreadable, write_board

RENAMED = "| Row | Owner | Where | Commits on it | Phase |"


def _paste(root: Path) -> list[str]:
    """Generate, and paste the printed block over the board's, as the register would."""
    lines, code = generate(root, RELEASE)
    assert code == GENERATED, lines
    block = lines[lines.index(INFLIGHT_OPEN) : lines.index(INFLIGHT_CLOSE) + 1]
    text = (root / BOARD).read_text(encoding="utf-8")
    start, end = text.index(INFLIGHT_OPEN), text.index(INFLIGHT_CLOSE) + len(INFLIGHT_CLOSE)
    (root / BOARD).write_text(text[:start] + "\n".join(block) + text[end:], encoding="utf-8")
    return lines


def _tip(root: Path, branch: str) -> str:
    return Graph.read(root, RELEASE).tip(branch)[:7]


def test_planted_a_HELD_branch_gets_its_checkout_and_count_from_git_and_the_rest_is_VERBATIM(
    repository: Path,
) -> None:
    """⭐ The shape: two cells from git, and the assertion untouched."""
    write_board(repository, "| `W42` | Dev | `wt/wrong`, `feat/held` | 9 | in flight |\n")
    lines = _paste(repository)
    expected = f"| `W42` | Dev | `feat/held` @ `wt/held` | 1 @ `{_tip(repository, 'feat/held')}` |"
    assert f"{expected} in flight |" in lines, lines
    assert "  rows left verbatim: none." in lines, lines


def test_planted_a_WRONG_correspondence_is_STILL_REFUTED_after_generation(
    repository: Path,
) -> None:
    """⛔ PLANT 1: the row claims an ABSORBED branch, and generation cannot make it right."""
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 3 | in flight |\n")
    _printed, before = corroborate(repository, RELEASE)
    lines = _paste(repository)
    assert any("`fix/Wmerged` @ none | 0 @" in line for line in lines), lines
    printed, after = corroborate(repository, RELEASE)
    assert before == after == REFUTED, printed
    assert any("REFUTED: fix/Wmerged is TERMINAL" in line for line in printed), printed


#: ⭐ Four populations, and the verdict each must reach in BOTH states. ⚠️ `W43` claims `W42`'s
#: live branch: git cannot say which row a branch is for, so it CORROBORATES — the SURVIVOR.
POPULATIONS = {
    "an absorbed branch": ("| `W42` | Dev | `wt/x`, `fix/Wmerged` | 1 | in flight |\n", REFUTED),
    "a branch git lacks": ("| `W42` | Dev | `wt/x`, `fix/Wtypo` | 1 | in flight |\n", REFUTED),
    "its own live branch": (
        "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n",
        CORROBORATED,
    ),
    "ANOTHER row's live branch (survivor)": (
        "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n"
        "| `W43` | Dev | `wt/y`, `feat/held` | 5 | in flight |\n",
        CORROBORATED,
    ),
}


def _verdicts(repository: Path) -> dict[str, tuple[int, int]]:
    readings = {}
    for name, (rows, _expected) in POPULATIONS.items():
        write_board(repository, rows)
        before = corroborate(repository, RELEASE)[1]
        _paste(repository)
        readings[name] = (before, corroborate(repository, RELEASE)[1])
    return readings


def test_the_REFUTING_population_is_UNCHANGED_by_generation_BOTH_WAYS(repository: Path) -> None:
    """⛔ Ruling 191: a remedy that empties the population it was judged by was not judged.

    ⭐ **Ruling 48: the two derived collections are asserted INHABITED in the same test**, so
    `{} == {}` cannot pass it: both verdicts occur, over four populations.
    """
    readings = _verdicts(repository)
    assert readings == {name: (code, code) for name, (_rows, code) in POPULATIONS.items()}
    assert {after for _before, after in readings.values()} == {REFUTED, CORROBORATED}, readings
    assert len(readings) == 4, readings


def test_the_CONTROL_generating_the_BRANCH_half_too_empties_the_refuting_population(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ Ruling 266's form: the refused shape, MEASURED rather than argued.

    ⚠️ **With the branch half taken from git — here, the live branch — an absorbed row
    CORROBORATES after generation.** ⭐ **So the equality above is caused by keeping the
    branch asserted, and not by a fixture that cannot refute.**
    """
    write_board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 1 | in flight |\n")
    assert corroborate(repository, RELEASE)[1] == REFUTED
    monkeypatch.setattr(
        inflight, "claim", lambda row, graph, live: Claim(row, ("feat/held",), (), ())
    )
    _paste(repository)
    assert corroborate(repository, RELEASE)[1] == CORROBORATED, "⛔ the control did not bite"


def test_a_generated_cell_READS_DATED_once_the_branch_moves(repository: Path) -> None:
    """⭐ The cell comparison agrees by construction at generation, and is not vacuous after it."""
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 7 | in flight |\n")
    _paste(repository)
    printed, _code = corroborate(repository, RELEASE)
    assert any("the row claims 1, git reads 1 — AGREE" in line for line in printed), printed
    commit(repository.parent / "held", "moved.txt")
    printed, code = corroborate(repository, RELEASE)
    assert code == CORROBORATED
    assert any("DATED, not wrong" in line for line in printed), printed


def test_a_row_naming_NO_branch_is_left_VERBATIM_and_the_floor_still_reads_it(
    repository: Path,
) -> None:
    """⭐ Ruling 189(b) survives: its founding bytes are exactly the rows the generator leaves."""
    rows = "| `W27` | Dev | none | 0 | in flight |\n"
    write_board(repository, rows)
    before = (repository / BOARD).read_text(encoding="utf-8")
    lines = _paste(repository)
    after = (repository / BOARD).read_text(encoding="utf-8")
    assert rows.strip() in lines and after == before, lines
    assert any("left verbatim: `W27` names 0 branch(es)" in line for line in lines), lines
    findings = observation_findings(after)
    assert findings and [f.rule for f in findings] == [f.rule for f in observation_findings(before)]


def test_planted_a_branch_git_CANNOT_COUNT_is_NOT_generated_and_exits_2(
    repository: Path,
) -> None:
    """⛔ Ruling 216: a generated table missing a count is not a generated table."""
    branch = unreadable(repository, "fix/W4")
    row = f"| `W42` | Dev | `wt/x`, `{branch}` | 0 | in flight |"
    write_board(repository, row + "\n")
    lines, code = generate(repository, RELEASE)
    assert code == NOT_AUTHORITATIVE
    assert row in lines, "⭐ copied verbatim"
    assert any("NOT GENERATED: git could not count" in line for line in lines), lines


def test_impossible_no_board_no_release_or_an_unread_table_generates_NOTHING(
    repository: Path, tmp_path: Path
) -> None:
    """⛔ With no readable assertion there is nothing to generate FROM, and that is exit `2`."""
    row = "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n"
    codes = [generate(tmp_path / "nowhere", RELEASE)[1]]
    write_board(repository, row)
    codes.append(generate(repository, "release/no-such-branch-60713")[1])
    write_board(repository, row, delimited=False)
    codes.append(generate(repository, RELEASE)[1])
    write_board(repository, row)
    text = (repository / BOARD).read_text(encoding="utf-8")
    (repository / BOARD).write_text(
        text.replace("| Row | Owner | Checkout | Commits ahead | State |", RENAMED),
        encoding="utf-8",
    )
    lines, code = generate(repository, RELEASE)
    codes.append(code)
    assert codes == [NOT_AUTHORITATIVE] * 4, codes
    assert INFLIGHT_OPEN not in lines, lines


def test_the_command_line_prints_the_block_and_no_absolute_path(
    repository: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """⭐ The entry point, and ⛔ R7: `worktree list` answers in absolute paths."""
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    assert main(["--root", str(repository), "--release", RELEASE]) == GENERATED
    printed = capsys.readouterr().out
    assert INFLIGHT_OPEN in printed and "`feat/held` @ `wt/held`" in printed, printed
    assert str(repository.parent) not in printed
