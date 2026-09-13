"""Mirror of `tools/quality/board/dispatch.py` (R12) — ⛔ `W153`'s four clauses, each planted.

⚠️ **The subject is `conftest.py`'s synthesised repository** (Ruling 191(b)): between register
rounds the live population is exactly the one this row is about, so it cannot be the control.

| clause | the reading | ⛔ expected, written BEFORE the run |
|---|---|---|
| 3, one way | no register round, a carrier declared | ⭐ off the gate, NAMED on its own line |
| 3, other way | the same run | ⛔ `feat/held`, undeclared, STILL gated |
| mechanism 2 | a declared carrier at `0` ahead | ⭐ off Ruling 130's line; `leak` stays |
| 1, narrowing | naming no open register row | ⛔ REFUSED, reason printed, still gated |
| 2, MUST NOT | a register round, the table names it | ⭐ every other line and the exit unchanged |
| 4, `W125` | the generator and the row verdicts | ⛔ identical with declarations planted |

⭐ **Each declaration is written from INSIDE the carrier's worktree and read from the main
checkout**, so every test also measures *shared by every worktree* and *readable at dispatch*.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.quality.board import dispatch
from tools.quality.board.corroborate import corroborate
from tools.quality.board.inflight import generate
from tools.workspace import git

from .conftest import RELEASE, commit, write_board

#: ⛔ One OPEN row, one CLOSED row and a second open one, in the register's own five columns.
REGISTER = (
    "| W901 | a dispatched row | Dev | `todo` | [rows/W901.md](rows/W901.md) |\n"
    "| W902 | a closed row | Dev | ✅ done — `abc1234` | [rows/W902.md](rows/W902.md) |\n"
    "| W903 | another dispatched row | Dev | `todo` | [rows/W903.md](rows/W903.md) |\n"
)

ACCEPTED = "  ⭐ carriers DECLARED by their own branch description, named by no row"
NONE_ACCEPTED = "  carrier declarations (git config branch.<branch>.description), named by no row"
REFUSED = "  ⛔ carrier declarations REFUSED"
#: ⭐ The OPENINGS of the two lines `W153` adds, and nothing looser: `no carrier is owed` is a
#: row-verdict line that a bare `carrier` substring would silently drop from a comparison.
OPENINGS = (ACCEPTED, NONE_ACCEPTED, REFUSED, "  carrier declarations refused: none.")


def _run(root: Path) -> tuple[int, list[str]]:
    lines, code = corroborate(root, RELEASE)
    return code, lines


def _line(lines: list[str], label: str) -> str:
    return next(line for line in lines if label in line)


def _opening(lines: list[str], opening: str) -> str:
    return next(line for line in lines if line.startswith(opening))


def _carrier(repository: Path, branch: str, where: str, ahead: bool = True) -> Path:
    """Cut `branch`, commit on it unless `ahead` is False, and check it out at `where`."""
    assert git(repository, "branch", branch, RELEASE).returncode == 0
    path = repository.parent / where
    assert git(repository, "worktree", "add", "-q", str(path), branch).returncode == 0
    if ahead:
        commit(path, f"{where}.txt", "a carrier's first commit\n")
    return path


def _declare(where: Path, branch: str, value: str) -> None:
    assert git(where, "config", f"branch.{branch}.description", value).returncode == 0


def test_planted_a_NO_REGISTER_wave_a_DECLARED_carrier_leaves_the_gate_and_feat_held_STAYS(
    repository: Path,
) -> None:
    """⛔ Clause 3, BOTH directions, over one board: no In flight row, one open register row."""
    where = _carrier(repository, "fix/W901-carrier", "dev1")
    write_board(repository, "", REGISTER)
    before_code, before = _run(repository)
    gate = _line(before, "dispatched and")
    assert "fix/W901-carrier" in gate, f"⛔ born vacuous: the defect is not reproduced — {gate}"
    assert _opening(before, NONE_ACCEPTED), "⭐ and the empty form is printed before any plant"

    _declare(where, "fix/W901-carrier", "W901")
    code, after = _run(repository)
    gate = _line(after, "dispatched and")
    assert "fix/W901-carrier" not in gate, f"⛔ THE DEFECT: a declared carrier is gated — {gate}"
    assert "feat/held" in gate, f"⛔ a genuinely unclaimed branch must STILL be named — {gate}"
    assert _opening(after, ACCEPTED).startswith(f"{ACCEPTED} (1): fix/W901-carrier=W901 — ")
    assert code == before_code, "⛔ the exit code does not move"

    # ⭐ The gate's other half: the same carrier, its worktree removed, is not held-by-none work.
    assert git(repository, "worktree", "remove", str(where)).returncode == 0
    _code, removed = _run(repository)
    adrift = _line(removed, "HELD BY NO CHECKOUT")
    assert "fix/W901-carrier" not in adrift, adrift
    assert "feat/live" in adrift, "⛔ and the undeclared branch held by no checkout stays"


def test_planted_a_DECLARED_carrier_at_ZERO_AHEAD_leaves_BY_CONSTRUCTION_and_leak_STAYS(
    repository: Path,
) -> None:
    """⛔ The row's SECOND mechanism: every dispatch begins at `0` ahead (PO round 52)."""
    where = _carrier(repository, "fix/W901-carrier", "dev1", ahead=False)
    write_board(repository, "", REGISTER)
    _code, before = _run(repository)
    assert "dev1" in _line(before, "BY CONSTRUCTION"), "⛔ born vacuous: PO round 52's reading"

    _declare(where, "fix/W901-carrier", "W901")
    _code, after = _run(repository)
    blind = _line(after, "BY CONSTRUCTION")
    assert "dev1" not in blind, f"⛔ a declared carrier filed as invisible — {blind}"
    assert "leak" in blind, f"⛔ the undeclared 0-ahead checkout is STILL named — {blind}"


@pytest.mark.parametrize(
    ("value", "reason"),
    [
        ("W999", "W999 has no register row"),
        ("W902", "W902 is closed in the register"),
        ("a carrier", "names no W row id"),
        ("W901 + W999", "W999 has no register row"),
    ],
)
def test_planted_a_declaration_naming_no_OPEN_register_row_is_REFUSED_and_STILL_GATED(
    repository: Path, value: str, reason: str
) -> None:
    """⛔ Ruling 185(b): the declaration NARROWS the gate only where the register vouches."""
    where = _carrier(repository, "fix/W9-refused", "dev2")
    write_board(repository, "", REGISTER)
    _declare(where, "fix/W9-refused", value)
    _code, lines = _run(repository)
    assert "fix/W9-refused" in _line(lines, "dispatched and"), "⛔ a refused carrier left the gate"
    assert f"{REFUSED} (1): fix/W9-refused ({reason})" in _opening(lines, REFUSED)
    assert _opening(lines, NONE_ACCEPTED), "⛔ and nothing was accepted"


def test_a_REGISTER_wave_the_ROW_answers_and_every_other_line_and_the_exit_are_UNCHANGED(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ Clause 2 and the MUST NOT: where the table speaks, the description is never read."""
    rows = "| `W901` | Dev | `held`, `feat/held` | 1 | in flight |\n"
    write_board(repository, rows, REGISTER)
    other = _carrier(repository, "fix/W901-stale", "stale")
    # ⚠️ One declaration the row SUPERSEDES, and one on another branch naming the table's id.
    _declare(repository.parent / "held", "feat/held", "W902")
    _declare(other, "fix/W901-stale", "W901")
    code, lines = _run(repository)
    monkeypatch.setattr(dispatch, "read", lambda _root: dispatch.Reading())
    bare_code, bare = _run(repository)

    def rest(printed: list[str]) -> list[str]:
        return [line for line in printed if not line.startswith(OPENINGS)]

    assert len(rest(lines)) == len(lines) - 2, "⛔ exactly the two `W153` lines are set aside"
    assert rest(lines) == rest(bare), "⛔ a declaration changed a line the register answers"
    assert code == bare_code
    assert "— 1 more on branches a row already claims" in _opening(lines, NONE_ACCEPTED)
    refused = _opening(lines, REFUSED)
    assert "fix/W901-stale (the In flight table carries W901 on feat/held)" in refused
    assert "fix/W901-stale" in _line(lines, "dispatched and"), "⛔ the stale copy stays gated"


def test_W125_the_GENERATOR_and_the_ROW_VERDICTS_never_read_a_declaration(
    repository: Path,
) -> None:
    """⛔ Clause 4: a declaration feeding an asserted half would assert git against itself."""
    rows = "| `W901` | Dev | `held`, `feat/held` | 1 | in flight |\n"
    write_board(repository, rows, REGISTER)
    generated = generate(repository, RELEASE)
    code, lines = _run(repository)
    _declare(repository.parent / "held", "feat/held", "W903")
    _declare(_carrier(repository, "fix/W903-carrier", "dev3"), "fix/W903-carrier", "W903")
    assert generate(repository, RELEASE) == generated

    def verdicts(printed: list[str]) -> list[str]:
        openings = ("  row ->", "    ", "  ⛔ rows", "  rows")
        return [line for line in printed if line.startswith(openings)]

    after_code, after = _run(repository)
    assert verdicts(lines), "⛔ born vacuous: there must be a row verdict to compare"
    assert verdicts(after) == verdicts(lines) and after_code == code
    assert _opening(after, ACCEPTED).startswith(f"{ACCEPTED} (1): fix/W903-carrier=W903")


def test_read_parses_git_s_own_form_and_a_FAILED_read_takes_NOTHING_off(
    repository: Path, tmp_path: Path
) -> None:
    """⭐ Dots in a name, a second line, deletion with the branch, and git declining."""
    assert dispatch.read(repository) == dispatch.Reading(), "⛔ git's exit 1 is *none*"
    where = _carrier(repository, "fix/W1.2-dots", "dots", ahead=False)
    _declare(where, "fix/W1.2-dots", "W901\nsecond line")
    assert dispatch.read(repository).descriptions == {"fix/W1.2-dots": "W901\nsecond line"}
    assert git(repository, "worktree", "remove", str(where)).returncode == 0
    assert git(repository, "branch", "-D", "fix/W1.2-dots").returncode == 0
    assert dispatch.read(repository) == dispatch.Reading(), "⭐ it dies with its branch"

    failed = dispatch.read(tmp_path / "no-such-directory")
    assert failed.failed, "⛔ a git that could not run must not read as *none*"
    assert str(tmp_path) not in failed.failed, "⛔ R7: git's error text carries the path"
    carriers, printed = dispatch.judge(failed, ["feat/held"], (), "")
    assert carriers == frozenset() and "NOT READ" in printed[0]


def test_planted_a_description_in_the_GLOBAL_config_declares_NOTHING(
    repository: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⛔ `--local`: a user's own config is not this repository's dispatch, and it is personal."""
    planted = tmp_path / "global.gitconfig"
    planted.write_text('[branch "feat/held"]\n\tdescription = W901\n', encoding="utf-8")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(planted))
    seen = git(repository, "config", "--global", "--get", "branch.feat/held.description")
    assert seen.stdout.strip() == "W901", "⛔ born vacuous: git must read the planted global file"
    assert dispatch.read(repository) == dispatch.Reading()
