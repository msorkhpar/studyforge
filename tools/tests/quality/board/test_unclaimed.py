"""Mirror of `tools/quality/board/unclaimed.py` (R12) — ⛔ the OTHER DIRECTION's six readings.

⛔ **These readings MOVED here from `test_corroborate.py` with the code they measure**, the
way `test_bounds.py`'s moved with `W100`'s split and `test_bijection.py`'s with `W129`'s —
⭐ **and they MOVED rather than being copied: a reading with two homes is the defect this
package's own instrument exists to forbid, one layer up.**

⚠️ **The SUBJECT is a synthesised repository** (`conftest.py`), and that is Ruling 191(b)
rather than convenience: ⛔ **between waves every population this module reads is empty**, so
a control drawn from the live tree is born vacuous exactly when a close run is taken — ⭐ and
`test_host_population.py` forbids a committed assertion taking its population from the host.

## ⛔ `W132` / Ruling 265 — the OFFICE-BRANCH exemption, asserted in BOTH directions

| direction | ⛔ the expectation, written BEFORE the run |
|---|---|
| an office branch AHEAD `> 0` | ⭐ **exempt**, and PRINTED with its count and its reason |
| a `fix/W*` branch at `0` ahead, no row | ⛔ **still NAMED**, on Ruling 130's own line |
| a branch merely CONTAINING `po-round` | ⛔ **NOT exempt** — the prefix is ANCHORED |
| ⚠️ a DETACHED checkout | ⛔ **in NONE of the four lines**, and that hole stays visible |

⚠️ **The office plant is AHEAD and never `0`-ahead, deliberately:** ⛔ **`0`-ahead was
ALREADY exempt under Ruling 130, so a `0`-ahead fixture would measure nothing** — which is
`rows/W132.md`'s own instruction and the whole of what Ruling 265 changes.
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.board.corroborate import corroborate
from tools.quality.board.graph import Graph
from tools.workspace import git

from .conftest import RELEASE, commit, write_board


def _run(root: Path, release: str = RELEASE) -> tuple[int, str]:
    lines, code = corroborate(root, release)
    return code, "\n".join(lines)


# --------------------------------------------------------------------------
# ⛔ The four lines of `unnamed()` — the board's blind side
# --------------------------------------------------------------------------


def test_planted_the_OTHER_direction_work_git_sees_and_the_board_does_not_name(
    repository: Path,
) -> None:
    """⛔ The measured failure was BIDIRECTIONAL — stale rows present, live rows absent."""
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    _code, printed = _run(repository)
    assert "dispatched and UNNAMED by any row: feat/live" not in printed, (
        "feat/live has no checkout, so `worktree list` cannot see it either"
    )
    assert git(repository, "worktree", "add", "-q", str(repository.parent / "two"), "feat/live")
    _code, printed = _run(repository)
    assert "dispatched and UNNAMED by any row: feat/live" in printed


def test_the_blind_spot_is_COUNTED_AND_NAMED_rather_than_judged(repository: Path) -> None:
    """⚠️ *Just dispatched* and *an office checkout* are the same bytes to `git`.

    ⛔ **So a 0-commit checkout is named as UNREADABLE here** rather than reported
    as a defect — ⭐ the board is the only instrument that can tell them apart,
    which is the whole of Ruling 171.
    """
    assert git(repository, "worktree", "add", "-q", str(repository.parent / "office"), "feat/bare")
    write_board(repository, "")
    _code, printed = _run(repository)
    assert "invisible to git BY CONSTRUCTION (Ruling 130), 0 commits ahead" in printed
    assert "office" in printed, "the directory BASENAME, which is what identifies it"


# --------------------------------------------------------------------------
# ⛔ `W132` / Ruling 265 — the OFFICE-BRANCH exemption, in BOTH directions
# --------------------------------------------------------------------------


#: ⛔ An office branch that is AHEAD, which is the case Ruling 130 does NOT exempt and the
#: one `W132` is about. ⭐ `0`-ahead was already exempt, so a `0`-ahead fixture would measure
#: nothing (`rows/W132.md`: *"not a fixture that is 0 ahead"*).
def _office(repository: Path, branch: str, where: str) -> int:
    """Cut `branch`, commit on it, check it out at `where`, and return its ahead count."""
    assert git(repository, "checkout", "-q", "-b", branch).returncode == 0
    commit(repository, f"{branch.replace('/', '-')}.txt", "a round's record\n")
    assert git(repository, "checkout", "-q", RELEASE).returncode == 0
    assert (
        git(repository, "worktree", "add", "-q", str(repository.parent / where), branch).returncode
        == 0
    )
    ahead = Graph.read(repository, RELEASE).ahead(branch)
    assert ahead is not None and ahead > 0, f"⛔ born vacuous: {branch} is {ahead} ahead"
    return ahead


def test_planted_an_OFFICE_branch_that_is_AHEAD_is_EXEMPT_and_the_REASON_is_PRINTED(
    repository: Path,
) -> None:
    """⛔ DIRECTION 1 — Ruling 265, against a branch that is AHEAD rather than empty.

    ⚠️ **Expected, written before the run:** under Ruling 130's `0 ahead` form this
    branch appears on `dispatched and UNNAMED by any row` — ⛔ **the line Ruling 264(c)
    just turned into the project's ONE pre-merge gate** — ⭐ **so a reviewer was taught to
    skim a gate, checking only whether a DEVELOPER name appeared in it.**

    ⭐ **MEASURED in the live tree, both states, by the two offices Ruling 265 cites:**
    `chore/po-round45` exempt at `6c4e3d0` at `0` ahead, and `chore/po-round44` named as
    *dispatched and UNNAMED* at `b5b0577` after it committed — ⚠️ **one branch, two
    readings, the only variable being whether the office had written anything down yet.**

    ⛔ **And the exemption is PRINTED with its reason and its count**, because Ruling
    264(c) made this a gate and a gate that hides a rule is unreadable.
    """
    ahead = _office(repository, "chore/po-round46", "po")
    write_board(repository, "")
    _code, printed = _run(repository)
    dispatched = next(line for line in printed.split("\n") if "dispatched and" in line)
    assert "chore/po-round46" not in dispatched, (
        f"⛔ THE DEFECT: an office branch named on the pre-merge gate — {dispatched}"
    )
    # ⭐ The CONTROL, in the same line: `feat/held` is the fixture's ahead-and-unclaimed
    # DEVELOPER branch and it is still named, so the exemption narrowed the population
    # rather than emptying the gate (Ruling 185, and Ruling 191(c)'s positive row).
    assert "feat/held" in dispatched, dispatched
    exemption = next(line for line in printed.split("\n") if "Ruling 265" in line)
    assert f"chore/po-round46 +{ahead}" in exemption, (
        f"⭐ the count is printed, so nobody can read the exemption as `0 ahead` — {exemption}"
    )
    assert "BRANCH NAMESPACE and not emptiness" in exemption, "⛔ the REASON, not just the name"
    assert "naming its own recorder" in exemption


def test_planted_a_fix_branch_at_ZERO_AHEAD_and_NAMED_BY_NO_ROW_IS_STILL_NAMED(
    repository: Path,
) -> None:
    """⛔ DIRECTION 2 — the widening must not reach a DEVELOPER branch.

    ⭐ **`feat/bare` is the fixture's Ruling 130 row: a branch with no commit, checked
    out, named by no row.** ⚠️ **It stays on the *invisible BY CONSTRUCTION* line with its
    own count and its own name** — ⛔ **because *just dispatched* and *an office checkout*
    are the same bytes to git, and the board is the only instrument that can tell them
    apart, which is the whole of Ruling 171.**
    """
    assert git(repository, "worktree", "add", "-q", str(repository.parent / "dev2"), "feat/bare")
    _office(repository, "chore/cto-round59", "cto")
    write_board(repository, "")
    _code, printed = _run(repository)
    blind = next(line for line in printed.split("\n") if "BY CONSTRUCTION" in line)
    assert "dev2" in blind, f"⛔ a 0-ahead developer checkout is STILL NAMED — {blind}"
    # ⚠️ `leak` is the fixture's other 0-ahead unclaimed checkout (`fix/Wleak`), so the
    # count is TWO — ⭐ printed in full, because a count with no names is Ruling 48's `0`.
    assert "named by no row: 2 — dev2 leak" in blind, blind
    assert "cto" not in blind, "⭐ and the office checkout is NOT counted here twice"


def test_planted_a_branch_that_merely_CONTAINS_po_round_is_NOT_EXEMPT(
    repository: Path,
) -> None:
    """⛔ The plant is adversarial to the PATTERN rather than to the subject (Ruling 140).

    ⚠️ **`fix/W99-po-round-guard` is a DEVELOPER's branch whose name contains
    `po-round`** — ⭐ **and an unanchored pattern would exempt it**, which is exactly the
    defect `graph.py` records one module over: the shipped `merge_of()` tested
    `if branch in subject:` and `chore/cto-round3` therefore read TERMINAL off
    `Merge chore/cto-round39:`'s merge.

    ⛔ **So the prefix is ANCHORED, and this is the reading that says so.**
    """
    ahead = _office(repository, "fix/W99-po-round-guard", "sneaky")
    write_board(repository, "")
    _code, printed = _run(repository)
    dispatched = next(line for line in printed.split("\n") if "dispatched and" in line)
    assert "UNNAMED by any row" in dispatched and "fix/W99-po-round-guard" in dispatched, (
        f"⛔ THE DEFECT an anchored prefix prevents — {dispatched}; it is {ahead} ahead"
    )
    exemption = next(line for line in printed.split("\n") if "Ruling 265" in line)
    assert "fix/W99" not in exemption, f"⭐ and it is not on the exemption line — {exemption}"


def test_the_DETACHED_checkout_is_in_NONE_of_the_FOUR_lines_and_that_hole_STAYS_VISIBLE(
    repository: Path,
) -> None:
    """⛔ `rows/W132.md` clause 3: widening this arm must not make a known hole harder to see.

    ⚠️ **A DETACHED checkout has no `branch refs/heads/…` line in
    `worktree list --porcelain`, so `graph.checkouts()` never sees it and it appears in
    NEITHER arm** (`PO-44/5`). ⭐ **That hole belongs to `W125` with `W96/5` and is NOT
    silently absorbed here.**

    ⛔ **This is a RECORDED NEGATIVE with a named population** (Ruling 191(c)'s form): the
    detached checkout is asserted ABSENT from all four lines, and the office line carries
    its OWN count so that Ruling 265's exemption SHRINKS no other line's number without
    saying where the branches went.
    """
    tip = git(repository, "rev-parse", "HEAD").stdout.strip()
    assert (
        git(
            repository, "worktree", "add", "-q", "--detach", str(repository.parent / "poi"), tip
        ).returncode
        == 0
    )
    assert "poi" not in str(Graph.read(repository, RELEASE).checkouts()), "⛔ born vacuous"
    _office(repository, "chore/po-round46", "po")
    write_board(repository, "")
    _code, printed = _run(repository)
    for label in ("dispatched and", "Ruling 265", "BY CONSTRUCTION", "could not count"):
        line = next(line for line in printed.split("\n") if label in line)
        assert "poi" not in line, f"⛔ the detached checkout must stay in NO arm — {line}"
    assert "Ruling 265" in printed, "⭐ and the office line is there, carrying its own count"


# --------------------------------------------------------------------------
# ⛔ `spent()` — Ruling 206(ii)'s two lines, and neither is ever a removal
# --------------------------------------------------------------------------


def test_planted_a_spent_trial_branch_is_the_reading_no_board_cell_carries(
    repository: Path,
) -> None:
    """⭐ The standing form, measured by the CTO at `0285a92` and `c3e2919`.

    ⛔ **Such a branch carries nothing unique and is invisible to `--no-merged` by
    construction** — ⚠️ **its only remaining effect is to read as dispatched work
    to a human, which is Ruling 189's subject with no cell to print it in.**
    """
    write_board(repository, "")
    _code, printed = _run(repository)
    assert "spent and deletable (1): trial/spent" in printed
    assert "ancestor of" in printed
    assert "trial/tmp branches still checked out: none." in printed


def test_planted_a_STANDING_trial_worktree_is_PRINTED_and_never_removed(
    repository: Path,
) -> None:
    """⚠️ Ruling 206(ii) named this line's own blind spot, and it routed it to `W110`.

    ⛔ **`name not in live` excluded exactly the shape that keeps a spent row
    green** — a trial worktree still standing — ⭐ **so it is printed separately, as a
    NOTICE**, because reporting a worktree you did not cut is never wrong and removing
    one always is.
    """
    assert (
        git(
            repository, "worktree", "add", "-q", str(repository.parent / "t"), "trial/spent"
        ).returncode
        == 0
    )
    write_board(repository, "")
    _code, printed = _run(repository)
    assert "trial/tmp branches STILL CHECKED OUT (1): trial/spent" in printed
    assert "never remove one you did not cut (Ruling 206(ii))" in printed
    assert "spent trial/tmp branches: none." in printed, "it is no longer *deletable*"
