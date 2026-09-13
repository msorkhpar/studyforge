"""Mirror of `tools/quality/board/unclaimed.py` (R12) — ⛔ the OTHER DIRECTION's seven readings.

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
| a branch CONTAINING or PREFIXED by a round spelling | ⛔ **NOT exempt** — the WHOLE name |
| ⚠️ a DETACHED checkout | ⛔ **in NONE of the five lines**, and that hole stays visible |

⚠️ **The office plant is AHEAD and never `0`-ahead, deliberately:** ⛔ **`0`-ahead was
ALREADY exempt under Ruling 130, so a `0`-ahead fixture would measure nothing** — which is
`rows/W132.md`'s own instruction and the whole of what Ruling 265 changes.

## ⛔ `W170` / Ruling 265's OWN ground — the `SPENT`-NAMESPACE exemption, in BOTH directions

| direction | ⛔ the expectation, written BEFORE the run |
|---|---|
| a `trial/*` branch AHEAD and CHECKED OUT | ⭐ **NOT on the GATE line**, ON the exemption
  line with its count and reason, and ⛔ **STILL on `STILL CHECKED OUT`** |
| a `fix/W*` branch AHEAD and named by no row | ⛔ **STILL GATED** — ⚠️ Ruling 319 refuses
  exactly the `fix/*` widening, which would empty the population the gate exists to read |
| ⭐ the CONTROL that must FAIL (Ruling 266) | with `SPENT` reverted to `()`, the gate names
  the trial branch AGAIN — ⛔ **so the exclusion is MEASURED and not asserted** |
| ⚠️ the EXIT CODE | ⛔ **does not move**: this line REPORTS, and Ruling 264(c)'s gate is
  read by a REVIEWER — a fold that carried it would refute every wave under review |

## ⛔ The GATE's OTHER HALF — a branch HELD BY NO CHECKOUT, and the CONTROL that goes SILENT

| direction | ⛔ the expectation, written BEFORE the run |
|---|---|
| a branch AHEAD, held by NO worktree, no row | ⭐ **NAMED**, ⛔ **and STILL absent from the
  gate line, whose population is UNCHANGED** |
| ⭐ the CONTROL that must go SILENT | with `Graph.heads` answering the LIVE branches alone —
  the pre-change population, exactly — the line reads `none.` |
| an office or `trial/*` branch in the same state | ⛔ **exempt on BOTH halves** |
| a `fix/W*` branch in the same state | ⛔ **still read** — Ruling 319's refusal, held here too |
| ⚠️ the EXIT CODE | ⛔ **does not move**, and neither does the fold for a branch git DECLINED
  to count: Ruling 216 built that fold over LIVE CHECKOUTS |

⚠️ **The trial plant is AHEAD and CHECKED OUT, deliberately, and the fixture's own
`trial/spent` is neither:** ⛔ **a `0`-ahead trial branch was NEVER in the gate's
population**, so it would measure nothing here — the same reasoning `rows/W132.md` applied
to `0`-ahead office branches, one namespace over.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tools.quality.board import unclaimed
from tools.quality.board.corroborate import CORROBORATED, corroborate
from tools.quality.board.graph import Graph
from tools.workspace import git

from .conftest import RELEASE, commit, unreadable, write_board


def _run(root: Path, release: str = RELEASE) -> tuple[int, str]:
    lines, code = corroborate(root, release)
    return code, "\n".join(lines)


# --------------------------------------------------------------------------
# ⛔ The five lines of `unnamed()` — the board's blind side
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


#: ⛔ A branch that is AHEAD and CHECKED OUT, which is the case Ruling 130 does NOT exempt
#: and the one `W132` is about. ⭐ `0`-ahead was already exempt, so a `0`-ahead fixture would
#: measure nothing (`rows/W132.md`: *"not a fixture that is 0 ahead"*).
#:
#: ⚠️ **`W170` reuses it VERBATIM and varies ONLY the branch NAME** — ⭐ **which is the row's
#: whole argument made executable: the exemption is decidable from the NAMESPACE, so one
#: plant shape measures the office, the `SPENT` and the `fix/W*` directions alike.** ⛔ **It
#: was called `_office` until `W170`; the name was a lie the moment a second namespace used
#: it, and a helper named after one of its callers is how a shared fixture stops being read.**
def _plant(repository: Path, branch: str, where: str) -> int:
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
    ahead = _plant(repository, "chore/po-round46", "po")
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
    exemption = next(line for line in printed.split("\n") if "round branches" in line)
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
    _plant(repository, "chore/cto-round59", "cto")
    write_board(repository, "")
    _code, printed = _run(repository)
    blind = next(line for line in printed.split("\n") if "BY CONSTRUCTION" in line)
    assert "dev2" in blind, f"⛔ a 0-ahead developer checkout is STILL NAMED — {blind}"
    # ⚠️ `leak` is the fixture's other 0-ahead unclaimed checkout (`fix/Wleak`), so the
    # count is TWO — ⭐ printed in full, because a count with no names is Ruling 48's `0`.
    assert "named by no row: 2 — dev2 leak" in blind, blind
    assert "cto" not in blind, "⭐ and the office checkout is NOT counted here twice"


@pytest.mark.parametrize("branch", ["fix/W99-po-round-guard", "chore/cto-round34-rubric"])
def test_planted_a_branch_that_merely_CONTAINS_po_round_is_NOT_EXEMPT(
    repository: Path, branch: str
) -> None:
    """⛔ The plant is adversarial to the PATTERN rather than to the subject (Ruling 140).

    ⚠️ **`fix/W99-po-round-guard` is a DEVELOPER's branch whose name contains
    `po-round`** — ⭐ **and an unanchored pattern would exempt it**, which is exactly the
    defect `graph.py` records one module over: the shipped `merge_of()` tested
    `if branch in subject:` and `chore/cto-round3` therefore read TERMINAL off
    `Merge chore/cto-round39:`'s merge.

    ⛔ **`W136`: and a PREFIX exempts `chore/cto-round34-rubric`, a TOPIC branch
    `rows/W136.md` measured inside it — so the match is the WHOLE name.**
    """
    ahead = _plant(repository, branch, "sneaky")
    write_board(repository, "")
    _code, printed = _run(repository)
    dispatched = next(line for line in printed.split("\n") if "dispatched and" in line)
    assert "UNNAMED by any row" in dispatched and branch in dispatched, (
        f"⛔ THE DEFECT an anchored prefix prevents — {dispatched}; it is {ahead} ahead"
    )
    exemption = next(line for line in printed.split("\n") if "round branches" in line)
    assert branch not in exemption, f"⭐ and it is not on the exemption line — {exemption}"


#: ⛔ `W136`: the ROW's own measured names, both directions. The False column is the plant
#: target: a restored prefix, `\d`, a class or an office widened turns one True.
WHOLE_NAME = {
    "chore/po-round73": True,
    "chore/cto-round9": True,
    "chore/cto-round17-close": False,
    "chore/cto-round49-annotation": False,
    "chore/po-board-round3": False,
    "chore/po-int-round2": False,
    "chore/po-round": False,
    "chore/po-round7a": False,
    "chore/po-round\u0667": False,
    "chore/po-round73\n": False,
    "fix/W99-po-round-guard": False,
}


@pytest.mark.parametrize(("branch", "exempt"), sorted(WHOLE_NAME.items()))
def test_the_OFFICE_exemption_is_the_WHOLE_NAME_and_never_a_prefix(
    branch: str, exempt: bool
) -> None:
    """⛔ `W136`: exempt iff the whole name is `chore/<office>-round<n>` (`delivery-flow.md`)."""
    assert unclaimed.office(branch) is exempt, f"{branch!r} must read exempt={exempt}"


def test_the_DETACHED_checkout_is_in_NONE_of_the_FIVE_lines_and_that_hole_STAYS_VISIBLE(
    repository: Path,
) -> None:
    """⛔ `rows/W132.md` clause 3: widening this arm must not make a known hole harder to see.

    ⚠️ **A DETACHED checkout has no `branch refs/heads/…` line in
    `worktree list --porcelain`, so `graph.checkouts()` never sees it and it appears in
    NEITHER arm** (`PO-44/5`). ⭐ **That hole belongs to `W125` with `W96/5` and is NOT
    silently absorbed here.**

    ⛔ **This is a RECORDED NEGATIVE with a named population** (Ruling 191(c)'s form): the
    detached checkout is asserted ABSENT from all five lines, and each exemption line
    carries its OWN count so that neither Ruling 265's nor `W170`'s exemption SHRINKS
    another line's number without saying where the branches went.

    ⚠️ **`W170` added the FIFTH line, so this negative was WIDENED to cover it** — ⛔ **a
    recorded negative that still names four lines after a fifth ships is a negative whose
    population quietly stopped matching the instrument's.**
    """
    tip = git(repository, "rev-parse", "HEAD").stdout.strip()
    assert (
        git(
            repository, "worktree", "add", "-q", "--detach", str(repository.parent / "poi"), tip
        ).returncode
        == 0
    )
    assert "poi" not in str(Graph.read(repository, RELEASE).checkouts()), "⛔ born vacuous"
    _plant(repository, "chore/po-round46", "po")
    write_board(repository, "")
    _code, printed = _run(repository)
    for label in (
        "dispatched and",
        "round branches",
        "namespaces exempt from the gate",
        "BY CONSTRUCTION",
        "could not count",
    ):
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


# --------------------------------------------------------------------------
# ⛔ `W170` — the `SPENT`-NAMESPACE exemption, in BOTH directions and with a CONTROL
# --------------------------------------------------------------------------

#: ⛔ The branch name is the one the LIVE witness carried, so the fixture reproduces the
#: SHAPE rather than citing it. ⚠️ The reading it reproduces, role `wt/po`, ref `7455f10`,
#: environment HOST: `dispatched and UNNAMED by any row: trial/cto-round68-wave7`, with the
#: SAME branch on `trial/tmp branches STILL CHECKED OUT (1)` two lines below it.
WITNESS = "trial/cto-round68-wave7"


def test_planted_a_TRIAL_branch_AHEAD_is_EXEMPT_from_the_GATE_and_is_STILL_REPORTED(
    repository: Path,
) -> None:
    """⛔ DIRECTION 1 — a live `trial/*` branch does NOT reach Ruling 264(c)'s ONE gate.

    ⚠️ **Expected, written before the run:** the same branch is named TWICE by one
    instrument, on two lines whose populations are supposed to be disjoint — ⛔ **once on
    the GATE, where it is a FALSE POSITIVE, and once on the line whose whole job is to
    report it, where it is CORRECT.**

    ⭐ **Ruling 265's ground transfers WHOLE:** a `trial/*` branch is a REVIEWER'S TRIAL
    MERGE — never dispatched, never taken by a row — ⛔ **so no register row will EVER name
    one, which is the exact sentence Ruling 265 gave for the office namespace.**

    ⚠️ **And it fires precisely when a review is in progress, which is the only moment the
    gate is read** — ⛔ **a gate that cries wolf during every review is one an office learns
    to read past** (Ruling 179's cost, arriving at the gate rather than at a notice).
    """
    ahead = _plant(repository, WITNESS, "trial-wt")
    write_board(repository, "")
    _code, printed = _run(repository)
    dispatched = next(line for line in printed.split("\n") if "dispatched and" in line)
    assert WITNESS not in dispatched, (
        f"⛔ THE DEFECT: a reviewer's trial branch named on the pre-merge gate — {dispatched}"
    )
    # ⭐ The CONTROL, in the SAME line: `feat/held` is the fixture's ahead-and-unclaimed
    # DEVELOPER branch and it is still named, so the exemption NARROWED the population
    # rather than emptying the gate (Ruling 185(b), and Ruling 191(c)'s positive row).
    assert "feat/held" in dispatched, dispatched
    exemption = next(
        line for line in printed.split("\n") if "namespaces EXEMPT from the GATE" in line
    )
    assert f"{WITNESS} +{ahead}" in exemption, (
        f"⭐ the count is printed, so nobody can read the exemption as `0 ahead` — {exemption}"
    )
    assert "never dispatched, never taken by a row" in exemption, "⛔ the REASON, not the name"
    # ⛔ SETTLING CONDITION 2: removing it from the GATE must not remove it from the
    # INSTRUMENT (Ruling 206(ii): reporting a worktree you did not cut is never wrong).
    #
    # ⚠️ **And EXACTLY ONE line carries the anchor.** ⛔ **The first draft of the exemption
    # line quoted this one's anchor verbatim in its own prose, and this very selector then
    # chose the WRONG line** — ⭐ **so the DECOY is now a reading of its own, because a
    # human grepping the instrument's output pays the same cost the test just paid.**
    carriers = [line for line in printed.split("\n") if "STILL CHECKED OUT" in line]
    assert len(carriers) == 1, f"⛔ a DECOY ANCHOR in the instrument's own output — {carriers}"
    assert f"STILL CHECKED OUT (1): {WITNESS}" in carriers[0], carriers[0]


def test_planted_a_fix_W_branch_AHEAD_and_NAMED_BY_NO_ROW_STILL_REACHES_THE_GATE(
    repository: Path,
) -> None:
    """⛔ DIRECTION 2 — the narrowing must not reach the population the gate EXISTS to read.

    ⚠️ **Ruling 319 refuses this widening BY NAME:** *extending Ruling 265's namespace
    exemption to `fix/*` exempts the whole population the gate exists to read.* ⭐ **So the
    `fix/W*` direction is a RECORDED POSITIVE here, taken in the same reading as the trial
    branch's exemption** — ⛔ **one run, both directions, so neither can be true of a tree
    the other was not measured on.**
    """
    ahead = _plant(repository, "fix/W170-not-exempt", "d3")
    _plant(repository, WITNESS, "trial-wt")
    write_board(repository, "")
    _code, printed = _run(repository)
    dispatched = next(line for line in printed.split("\n") if "dispatched and" in line)
    assert "UNNAMED by any row" in dispatched and "fix/W170-not-exempt" in dispatched, (
        f"⛔ THE DEFECT the narrowing must NOT cause — {dispatched}; it is {ahead} ahead"
    )
    assert WITNESS not in dispatched, f"⭐ and the trial branch is still exempt — {dispatched}"
    exemption = next(
        line for line in printed.split("\n") if "namespaces EXEMPT from the GATE" in line
    )
    assert "fix/W170" not in exemption, f"⭐ and it is not on the exemption line — {exemption}"


def test_the_CONTROL_with_the_SPENT_EXEMPTION_REVERTED_the_GATE_NAMES_IT_AGAIN(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⭐ Ruling 266's form — a control that MUST FAIL, or the exclusion is ASSERTED.

    ⛔ **One tree, one plant, TWO readings, and the ONLY variable is `SPENT`.** ⚠️ **With
    the tuple reverted to `()` the gate names the trial branch again** — ⭐ **so the green
    reading above is caused by this exemption and not by the fixture failing to plant.**

    ⚠️ **The reverted reading ALSO empties `STILL CHECKED OUT`, and that is the coupling
    stated rather than hidden:** ⛔ **both arms read the same tuple, which is exactly why
    the gate could be narrowed without the branch going unreported.**
    """
    _plant(repository, WITNESS, "trial-wt")
    write_board(repository, "")
    _code, printed = _run(repository)
    assert WITNESS not in next(line for line in printed.split("\n") if "dispatched and" in line)
    monkeypatch.setattr(unclaimed, "SPENT", ())
    _reverted_code, reverted = _run(repository)
    dispatched = next(line for line in reverted.split("\n") if "dispatched and" in line)
    assert WITNESS in dispatched, (
        f"⛔ BORN VACUOUS: the gate does not name it even with the exemption reverted "
        f"— {dispatched}"
    )
    assert "trial/tmp branches still checked out: none." in reverted, (
        "⭐ and the reverted tuple empties the REPORTING arm too — the coupling, measured"
    )


def test_the_GATE_line_REPORTS_and_the_EXIT_CODE_DOES_NOT_MOVE_WITH_IT(
    repository: Path,
) -> None:
    """⚠️ Ruling 264(c)'s gate is read by a REVIEWER; `corroborate`'s exit does not carry it.

    ⛔ **This is the claim the row told me to CHECK rather than inherit** — ⭐ **and it is
    checked in both states of the only variable: one tree, a positive row, with and without
    a trial worktree standing.** ⚠️ **It matters in both directions: if the exit HAD moved,
    the defect would have been a false REFUTATION rather than a false positive on a line,
    and the remedy would have had to reach the fold.**
    """
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    before, before_printed = _run(repository)
    assert before == CORROBORATED, before_printed
    _plant(repository, WITNESS, "trial-wt")
    after, after_printed = _run(repository)
    assert after == before == CORROBORATED, after_printed
    assert f"STILL CHECKED OUT (1): {WITNESS}" in after_printed, (
        "⛔ born vacuous: the trial worktree must actually be standing for this to measure"
    )


# --------------------------------------------------------------------------
# ⛔ The GATE's OTHER HALF — a branch HELD BY NO CHECKOUT, in both directions
# --------------------------------------------------------------------------

#: ⛔ **The LIVE instance, reproduced as a SHAPE rather than cited:** `docs/NS-07-handoff` at
#: `10a5470` carried a real commit, was named by no row, and the gate printed
#: `dispatched and unnamed: none.` — ⚠️ **because the office that made it used a throwaway
#: worktree and REMOVED it, which is correct hygiene.** ⭐ **Replanted here at `2d2af22`,
#: role `wt/dev2`, environment HOST: `docs/plant-dispatch-population`, `1` ahead, held by no
#: worktree — silent on the pristine instrument, NAMED after the change, `CORROBORATE_EXIT`
#: equal at `1` in both readings.**
#:
#: ⚠️ **The fixture needs no new plant: `feat/live` is already `1` ahead and held by nobody.**
ADRIFT = "feat/live"


def _adrift(printed: str) -> str:
    """The gate's other half, selected on ITS OWN anchor and on no other line's."""
    return next(line for line in printed.split("\n") if "held by no checkout" in line.lower())


def test_planted_an_UNMERGED_branch_HELD_BY_NO_CHECKOUT_is_NAMED_and_the_GATE_is_UNMOVED(
    repository: Path,
) -> None:
    """⛔ DIRECTION 1 — the reading the gate could not take, and the gate did not change.

    ⚠️ **Expected, written before the run:** ⛔ **`feat/live` is ABSENT from
    `dispatched and UNNAMED by any row` — which is UNCHANGED and still correct, its
    population being live checkouts — and PRESENT on the line below it.** ⭐ **Refuted if it
    appears on the gate line: that is the widening this row REFUSED, because a branch
    somebody is sitting on and a branch nobody is sitting on need different actions.**
    """
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    ahead = Graph.read(repository, RELEASE).ahead(ADRIFT)
    assert ahead is not None and ahead > 0, f"⛔ born vacuous: {ADRIFT} is {ahead} ahead"
    _code, printed = _run(repository)
    gate = next(line for line in printed.split("\n") if "dispatched and" in line)
    assert ADRIFT not in gate, f"⛔ the GATE was widened, and that was refused — {gate}"
    assert "population: LIVE CHECKOUTS only" in gate, "⭐ and the gate NAMES its own half"
    adrift = _adrift(printed)
    # ⚠️ CORRECTED AGAINST THE RUN: my expectation said `(1)` and the fixture carries THREE
    # branches that are ahead and held by nobody — `fix/W4` and `fix/Wmoved` share a tip.
    # ⭐ The correction is the reading's, not the instrument's, and it is the widened
    # population doing exactly what it is for.
    assert "named by no row (3): feat/live fix/W4 fix/Wmoved" in adrift, adrift
    assert "NOT folded into the exit code" in adrift, "⛔ the refusal, printed where it acts"


def test_the_CONTROL_with_the_POPULATION_reverted_to_LIVE_CHECKOUTS_the_LINE_GOES_SILENT(
    repository: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """⭐ Ruling 266's form — a control that MUST go silent, or the reading is ASSERTED.

    ⛔ **One tree, one branch, TWO readings, and the ONLY variable is whether the population
    comes from `heads()` or from the checkouts.** ⚠️ **`Graph.heads` is patched to answer
    with the live branches alone, which is the pre-change population expressed exactly** —
    ⭐ **the line then reads `none.` while `feat/live` still exists and is still ahead, so
    the speech above is caused by the widened population and not by the fixture.**
    """
    write_board(repository, "")
    _code, printed = _run(repository)
    assert ADRIFT in _adrift(printed), "⛔ born vacuous: it must speak before it can go silent"
    live = set(Graph.read(repository, RELEASE).checkouts())
    monkeypatch.setattr(Graph, "heads", lambda self: sorted(live))
    _code, reverted = _run(repository)
    silent = _adrift(reverted)
    assert ADRIFT not in silent, f"⛔ the control did not isolate the population — {silent}"
    assert "held by no checkout, named by no row: none." in silent, silent


def test_the_LINE_REPORTS_and_the_EXIT_CODE_DOES_NOT_MOVE_WITH_IT(repository: Path) -> None:
    """⚠️ Explicitly refused: this NOTICE does not carry `corroborate`'s exit code.

    ⛔ **Moving it would change every merge's disclosure in this project, which is a ruling
    and not a detail** — ⭐ **so it is asserted rather than intended: the line NAMES a branch
    and the run still exits `CORROBORATED`.**
    """
    write_board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    code, printed = _run(repository)
    assert ADRIFT in _adrift(printed), "⛔ born vacuous: nothing was named, so nothing is proved"
    assert code == CORROBORATED, printed


def test_the_THREE_EXEMPTIONS_TRANSFER_to_the_new_population_and_fix_W_STILL_REACHES_IT(
    repository: Path,
) -> None:
    """⛔ DIRECTION 2 — the same three exemptions, and Ruling 319's refusal held.

    ⚠️ **Expected, written before the run:** an office branch and a `trial/*` branch that are
    AHEAD and held by NO checkout are ABSENT from this line, and a `fix/W*` branch in the
    same state is PRESENT. ⛔ **Ruling 319 refuses the `fix/*` widening because it would
    empty the population the gate exists to read, and that refusal has to hold on BOTH
    halves of the gate or it holds on neither.**
    """
    for branch in ("chore/po-round99", "trial/round99", "fix/W99-adrift", "chore/po-round9-x"):
        assert git(repository, "checkout", "-q", "-b", branch).returncode == 0
        commit(repository, f"{branch.replace('/', '-')}.txt", "a round's record\n")
        assert git(repository, "checkout", "-q", RELEASE).returncode == 0
        ahead = Graph.read(repository, RELEASE).ahead(branch)
        assert ahead is not None and ahead > 0, f"⛔ born vacuous: {branch} is {ahead} ahead"
    write_board(repository, "")
    _code, printed = _run(repository)
    adrift = _adrift(printed)
    assert "fix/W99-adrift" in adrift, f"⛔ Ruling 319's refusal did not hold here — {adrift}"
    assert "chore/po-round9-x" in adrift, f"⛔ `W136`: a topic branch is not exempt — {adrift}"
    assert "chore/po-round99" not in adrift and "trial/round99" not in adrift, adrift


def test_planted_a_branch_git_DECLINED_to_count_that_NO_CHECKOUT_HOLDS_is_PRINTED(
    repository: Path,
) -> None:
    """⛔ `W115`'s coercion, refused in the new population before it can be written.

    ⚠️ **A ref written to a sha no object carries: `rev-parse --verify` answers and
    `rev-list --count` does not** (`conftest.unreadable`). ⭐ **A `n is not None and n > 0`
    filter would drop it in SILENCE, which is the shape `ahead(branch) or 0` had** — so it
    gets its own printed line, ⛔ **and NOT the exit code, whose fold Ruling 216 built over
    LIVE CHECKOUTS.**
    """
    branch = unreadable(repository, "fix/Wnocount")
    write_board(repository, "")
    code, printed = _run(repository)
    declined = next(line for line in printed.split("\n") if "git DECLINED to answer" in line)
    assert f"1 branch(es) NO WORKTREE IS ON: {branch}" in declined, declined
    assert code == CORROBORATED, "⛔ the fold was widened, and that was refused"
