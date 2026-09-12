"""Mirror of `tools/quality/board/cell.py` (R12) — ⛔ `PO-42/7`, `PO-50/12`, and `W40`'s SEAM.

⭐ **`W40` split `verdict.py` at `400/400` — zero headroom against R11 — and this
module is the test half of that split, cut at the same seam** (R12: a package's tests
are split the way the package is). ⛔ **The seam is asserted here IN BOTH DIRECTIONS
rather than only described in a docstring:** the `Answer` is invariant under every
commits-ahead cell this module can produce a notice for, and the notice is NOT — so
the invariance is not passing because the notice is silent.
"""

from __future__ import annotations

import ast
from pathlib import Path

from tools.quality.board import cell as cell_module
from tools.quality.board import verdict as verdict_module
from tools.quality.board.graph import Graph
from tools.quality.board.observation import read
from tools.quality.board.verdict import Answer, claim, verdict
from tools.tests.quality.board.support import board

from .conftest import MISSING_OBJECT, RELEASE, commit


def _reading(repository: Path, cell: str, branch: str = "feat/live") -> tuple[Answer, str]:
    """Judge one row whose commits-ahead cell is `cell`, and return what it PRINTED."""
    graph = Graph.read(repository, RELEASE)
    live = graph.checkouts()
    text = board(f"| `W46` | Dev | `{branch}` | {cell} | in flight |\n", delimited=True)
    answer = verdict(claim(read(text).rows[0], graph, live), branch, graph, live)
    return answer.answer, "\n".join(answer.lines)


def _moved_past(repository: Path, branch: str) -> str:
    """⭐ PLANT `PO-50/12`'s own shape: take the tip a cell would DECLARE, then MOVE the branch.

    ⛔ **This is the case the shipped notice could not tell from a miscount** — the
    cell is written at a tip and the developer commits after the register round closed,
    which is every wave.
    """
    from tools.workspace import git

    assert git(repository, "checkout", "-q", branch).returncode == 0
    tip = git(repository, "rev-parse", "--short", "HEAD").stdout.strip()
    commit(repository, f"after-{branch.replace('/', '-')}.txt", "moved\n")
    assert git(repository, "checkout", "-q", RELEASE).returncode == 0
    assert tip, "⛔ born vacuous: the declared tip must be a ref git actually gave"
    return tip


# --------------------------------------------------------------------------
# Reading 5 — `PO-42/7`: the CLAIMED count is compared, and it is a NOTICE
# --------------------------------------------------------------------------


def test_a_row_whose_CLAIMED_count_DISAGREES_with_git_gets_a_NOTICE_and_NOT_a_refutation(
    repository: Path,
) -> None:
    """⛔ **`PO-42/7`: the two were parsed, printed side by side, and compared to nothing.**

    ⚠️ **MEASURED by the PO twice, forty minutes apart, with no plant: two cells reading
    `2` and `2` were `3` and `5`, and the run exited `0`.** ⭐ **The remedy is a printed
    comparison and NOT a refutation — a commits-ahead cell reads a MOVING TIP, so
    refuting on a stale number would fire on every wave where somebody committed after
    the board was written** (Ruling 179, `rows/W115.md`).
    """
    graph = Graph.read(repository, RELEASE)
    assert graph.ahead("feat/live") == 1, "⛔ born vacuous: git's own count is the control"
    agree, agreed = _reading(repository, "0")
    assert agree is Answer.CORROBORATED, "⛔ the cell reads 0 and git reads 1 — still not refuted"
    assert "NOTICE, not a refusal (`PO-42/7`)" in agreed
    assert "claims 0 commits ahead and git reads 1" in agreed

    stale, printed = _reading(repository, "9")
    assert stale is Answer.CORROBORATED, "⛔ a stale NUMBER is not a stale ROW"
    assert "NOTICE, not a refusal (`PO-42/7`)" in printed
    assert "claims 9 commits ahead and git reads 1" in printed


def test_a_row_whose_CLAIMED_count_AGREES_with_git_says_so_rather_than_staying_silent(
    repository: Path,
) -> None:
    """⭐ Ruling 128: the comparison is PRINTED on the agreeing case too.

    ⛔ **A comparison visible only when it fails is one nobody can tell from a comparison
    that was never made** — which is precisely the defect `PO-42/7` reports.
    """
    _, printed = _reading(repository, "1")
    assert "commits ahead: the row claims 1, git reads 1 — AGREE." in printed


# --------------------------------------------------------------------------
# Reading 6 — `PO-50/12`: the cell's OWN declared tip, resolved
# --------------------------------------------------------------------------


def test_planted_a_cell_TRUE_AT_ITS_OWN_DECLARED_TIP_reads_DATED_and_a_FALSE_one_does_NOT(
    repository: Path,
) -> None:
    """⛔ **`PO-50/12`, BOTH DIRECTIONS with ONE VARIABLE CHANGED: the claimed number.**

    ⚠️ **MEASURED by the PO at `504bb47`, three takes of one pair of cells: 3 of 3 were
    TRUE AT THEIR OWN DECLARED REF and the notice printed a disagreement for every one
    of them.** ⭐ **Same tip, same branch, same git — only the cell's number differs, so
    the DATED arm cannot be passing because the tip resolves.**

    ⚠️ **Expected, written before the run:** the plant leaves `feat/live` `2` ahead and
    its declared tip `1` ahead, so `1 @ <tip>` is DATED and `5 @ <tip>` is WRONG AT ITS
    OWN DECLARED REF — ⛔ and neither may move the ANSWER, which is `PO-42/7`.
    """
    tip = _moved_past(repository, "feat/live")
    graph = Graph.read(repository, RELEASE)
    assert graph.ahead("feat/live") == 2, "⛔ born vacuous: the branch must have MOVED"
    assert graph.ahead(tip) == 1, "⛔ born vacuous: the declared tip must still COUNT"

    dated_answer, dated = _reading(repository, f"1 @ `{tip}`")
    assert dated_answer is Answer.CORROBORATED, "⛔ `PO-42/7` is untouched: a NOTICE, not a verdict"
    assert "DATED, not wrong (`PO-50/12`)" in dated
    assert f"{RELEASE}..{tip} is 1" in dated
    assert "NOTICE, not a refusal" not in dated, "⛔ case (b) is NOT a disagreement"

    wrong_answer, wrong = _reading(repository, f"5 @ `{tip}`")
    assert wrong_answer is Answer.CORROBORATED, "⛔ a WRONG cell is still not a refutation"
    assert "NOTICE, not a refusal (`PO-42/7`)" in wrong
    assert "WRONG AT ITS OWN DECLARED REF" in wrong
    assert "DATED" not in wrong, "⛔ THE NEGATIVE ARM: a miscount must not read as dated"
    assert "case (a)" in wrong, "⭐ and it NAMES which of the two cases it is"


def test_planted_an_UNRESOLVABLE_declared_tip_is_NEITHER_of_the_two_cases(
    repository: Path,
) -> None:
    """⛔ **Ruling 216's THIRD ANSWER, and clause 2 asks for exactly this discipline.**

    ⚠️ **Expected, written before the run:** `MISSING_OBJECT` is a well-formed sha no
    object carries, so `ahead()` DECLINES — ⭐ **a GENUINE failure and never a stubbed
    `None`** — and the line says neither `DATED` nor a disagreement.
    """
    graph = Graph.read(repository, RELEASE)
    assert graph.ahead(MISSING_OBJECT) is None, "⛔ born vacuous: git must GENUINELY decline"
    assert graph.ahead("feat/live") == 1, "⛔ born vacuous: the BRANCH is still countable"
    answer, printed = _reading(repository, f"7 @ `{MISSING_OBJECT}`")
    assert answer is Answer.CORROBORATED, "⛔ a failed AS-OF is not a failed row reading"
    assert "UNREAD as-of (Ruling 216's third answer)" in printed
    assert "DATED" not in printed and "NOTICE, not a refusal" not in printed


def test_a_cell_declaring_NO_TIP_keeps_EXACTLY_the_notice_it_had(repository: Path) -> None:
    """⛔ **Clause 3: the pre-Ruling-246 cell is UNCHANGED, and that is asserted here.**

    ⭐ **A remedy that turned a missing tip into a finding would fire on correct
    historical work** (Ruling 179, Ruling 185(a)) — ⚠️ so the older form must reach the
    SAME sentence it reached before this row, and neither new word may appear.
    """
    answer, printed = _reading(repository, "9")
    assert answer is Answer.CORROBORATED
    assert "claims 9 commits ahead and git reads 1" in printed
    assert "DATED" not in printed and "UNREAD as-of" not in printed


def test_a_cell_that_AGREES_never_resolves_its_tip_because_there_is_nothing_to_explain(
    repository: Path,
) -> None:
    """⭐ The as-of arm is reached only where the numbers DISAGREE — Ruling 179 again.

    ⛔ **An agreeing cell carrying a tip must print the AGREE line it always printed**,
    or the notice grows a sentence on every correct row in the table.
    """
    graph = Graph.read(repository, RELEASE)
    tip = graph.tip("feat/live")[:7]
    answer, printed = _reading(repository, f"1 @ `{tip}`")
    assert answer is Answer.CORROBORATED
    assert "commits ahead: the row claims 1, git reads 1 — AGREE." in printed
    assert "DATED" not in printed


# --------------------------------------------------------------------------
# Reading 7 — `W40`: the SEAM, inhabited in BOTH directions
# --------------------------------------------------------------------------


def test_the_CELL_moves_the_NOTICE_and_never_the_ANSWER(repository: Path) -> None:
    """⛔ **The seam, stated as a property of the output and not of the file layout.**

    ⭐ **`verdict.py` ANSWERS and `cell.py` SAYS.** ⚠️ **Expected, written before the
    run:** with one branch and one git fixed, six different commits-ahead cells reach
    six DIFFERENT notices and ONE answer. ⛔ **Both halves are asserted — an invariant
    answer alone would also pass if `compared()` printed nothing at all**, which is
    exactly the `PO-42/7` shape (a comparison nobody can tell from no comparison).
    """
    graph = Graph.read(repository, RELEASE)
    assert graph.ahead("feat/live") == 1, "⛔ born vacuous: the branch must be countable"
    tip = graph.tip("feat/live")[:7]
    cells = ["0", "1", "9", "—", f"5 @ `{tip}`", f"7 @ `{MISSING_OBJECT}`"]

    taken = [_reading(repository, one) for one in cells]
    assert {answer for answer, _ in taken} == {Answer.CORROBORATED}, [a for a, _ in taken]
    notices = [printed.rsplit("\n", 1)[-1] for _, printed in taken]
    assert len(set(notices)) == len(cells), "⛔ THE NEGATIVE ARM: the notice must MOVE too"


def test_the_cell_module_IMPORTS_NO_NAME_FROM_THE_VERDICT_AND_THE_VERDICT_IMPORTS_IT() -> None:
    """⛔ **The seam's ACYCLICITY, read off the shipped source rather than assumed.**

    ⭐ **A module that could decide a row from here would need `Answer`, and importing
    it is a cycle** — so *no import of `board.verdict` in `board.cell`* is the machine-
    checkable form of *this half never decides*. ⚠️ **The control is the other half:
    `board.verdict` MUST import `board.cell`**, or this assertion would pass over two
    modules that simply do not know each other.
    """

    def imported(module: object) -> set[str]:
        source = Path(str(module.__file__)).read_text(encoding="utf-8")
        found: set[str] = set()
        for node in ast.walk(ast.parse(source)):
            if isinstance(node, ast.ImportFrom) and node.module:
                found.add(node.module)
            elif isinstance(node, ast.Import):
                found.update(alias.name for alias in node.names)
        return found

    assert "tools.quality.board.verdict" not in imported(cell_module), "⛔ the seam is a CYCLE"
    assert "tools.quality.board.cell" in imported(verdict_module), "⛔ born vacuous: no seam here"
