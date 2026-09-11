"""Mirror of `tools/quality/board/graph.py` (R12) — Ruling 199's THREE candidate shapes.

⛔ **All three are computed here and compared, because the decision rests on their
DISAGREEMENT and a test of the winner alone would assert nothing about why it won.**
⭐ **Shape `A` — `MERGED ∧ 0-ahead` — is the remedy first routed for `W110`, and the
reading that refutes it is reproduced rather than cited.**

## ⛔ `W119` — EVERY POPULATION HERE IS THE FIXTURE'S, AND NONE IS THE HOST'S (Ruling 225)

⚠️ **Three readings in this module used to take their population from the machine the
suite happened to be running on** — `Graph.read(repository_root(), RELEASE)`, then
`checkouts()`, `heads()` and the release branch's own merge subjects. ⛔ **The first of
them asserted a property that is FALSE: it dropped every branch with unmerged work and
then asserted the survivors — the MERGED ones — are not terminal.**

⭐ **MEASURED three times before this module was rewritten, and the third reading is
the one that settles the shape:** twice by the coordinator immediately after a wave
merged (`1 failed, 4910 passed`, then `1 failed, 4929 passed`, both cured by retiring
the worktrees that held the just-merged branches), and ⛔ **once by the CTO with
NOTHING MERGED AT ALL** — one worktree opened on a branch absorbed many rounds earlier
took a clean repository from `1 passed` to `1 FAILED`, and removing it restored green.
⚠️ **So it is not a window between a merge and the housekeeping. It is unconditional,
and it would redden a correct commit on any machine whose worktree set differs from
this one's.**

⭐ **What replaced it is a PREDICATE and not an exemption list** (Ruling 225 is explicit
that a taker who only adds an exemption ships the same defect with a list attached):
⛔ **a branch carrying UNMERGED WORK must not read TERMINAL**, asserted over the
constructed repository `conftest.py` builds, where the population is a fixture and the
predicate is exercised in BOTH directions. ⚠️ **And the retired reading is KEPT, spelled
out beside it, because the fix is *the predicate was wrong* and a reader who cannot see
the old one cannot see why.**
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.board.graph import MERGE_IDIOM, Graph
from tools.workspace import git

from .conftest import AUTHOR, RELEASE, commit

#: ⭐ Every branch the fixture cuts, with the shape each exists to inhabit. ⛔ The
#: POPULATION IS PRINTED as the test's own assertion, never implied by spot checks.
#:
#: `(branch, A: merged ∧ 0-ahead, B: a merge subject names it, C: its tip was absorbed)`
SHAPES = (
    ("fix/Wmerged", True, True, True),
    ("fix/Wsilent", True, False, True),
    ("fix/Wff", True, False, False),
    ("fix/Wmoved", False, True, False),
    ("fix/W4", False, False, False),
    ("fix/Wleak", True, True, True),
    ("feat/held", False, False, False),
    ("feat/live", False, False, False),
    ("feat/bare", True, False, False),
    ("trial/spent", True, False, False),
)


#: ⛔ **A tip no object in the fixture has**, used as the IMPOSSIBLE reading's sha.
#: ⚠️ **It is not asserted to be impossible — it is PROVED to be**, with
#: `git cat-file -e` against the fixture, because a token's impossibility is a
#: property of the population and not of how unlikely the author felt it was.
IMPOSSIBLE_TIP = "b9f3c1" + "0" * 34

#: ⛔ A home-shaped path, ASSEMBLED AT RUN TIME. ⚠️ **Written as one literal it would be
#: a finding against this very file** — `tools.quality.personal_data`'s `home path` shape
#: matches `/home/` followed by an account segment — ⭐ **and the placeholder form
#: `/home/<name>` cannot match the assertion under test, because `<` is outside that
#: shape's character class.** ⚠️ **Same device `shapes.py`'s own comments use, for the
#: same reason**, and the account segment is an obvious placeholder (R7).
PLANTED_HOME = "/home/" + "anaccount/studyforge"


def _shape_a(graph: Graph, branch: str) -> bool:
    """Shape `A`, spelled out so the test does not depend on it living in the source."""
    return graph.merged(branch) and graph.ahead(branch) == 0


def _unmerged_work_reading_terminal(
    graph: Graph, branches: tuple[str, ...]
) -> tuple[list[str], list[str]]:
    """⭐ `W119`'s FIXED predicate: **unmerged work must never read TERMINAL**.

    ⛔ **Returns `(branches that refute it, branches git could not answer about)`** —
    ⚠️ **two lists and not one number, because `ahead()` returns `None` for *git could
    not say* and folding that into `0` is exactly the coercion `W115` exists to close.**
    ⭐ **The retired reading below does fold it, and is left folding it.**

    ⛔ **Spelled out HERE rather than in `graph.py`**, the way `_shape_a` spells out the
    refuted remedy: the source ships the READINGS and this module ships the PROPERTY
    asserted over them (Ruling 225 puts the assertion over the constructed repository).
    """
    refuting, unanswerable = [], []
    for branch in sorted(branches):
        ahead = graph.ahead(branch)
        if ahead is None:
            unanswerable.append(branch)
        elif ahead > 0 and graph.terminal(branch):
            refuting.append(branch)
    return refuting, unanswerable


def _a_live_checkout_holding_a_terminal_branch(graph: Graph) -> list[str]:
    """⛔ The RETIRED predicate — `W110`'s shipped reading, kept INHABITED (Ruling 225).

    ⚠️ **Its population is `checkouts()`, which is THE HOST'S worktree set**, and
    `if graph.ahead(branch): continue` drops every branch with unmerged work — ⛔ **so
    the survivors are the MERGED ones, and asserting those are not terminal asserts a
    contradiction.** ⭐ **A live checkout holding a terminal branch is the ORDINARY
    STATE of every worktree from the moment its branch merges until somebody retires
    it.**

    ⚠️ **`if graph.ahead(branch):` also reads `None` as `0`**, and that is preserved
    rather than corrected: ⛔ **correcting a retired reading hides what it did.**
    """
    found = []
    for branch in sorted(graph.checkouts()):
        if graph.ahead(branch):
            continue
        if graph.terminal(branch):
            found.append(branch)
    return found


# --------------------------------------------------------------------------
# Reading 1 — PLANTED: the whole population, printed before any verdict
# --------------------------------------------------------------------------


def test_planted_all_three_shapes_over_the_WHOLE_population(repository: Path) -> None:
    """⛔ Ruling 128: the population is printed in full before anything is reduced.

    ⭐ **Every row of `SHAPES` is asserted at once and the measured triple is the
    failure message**, so a disagreement names the branch rather than the assertion.
    """
    graph = Graph.read(repository, RELEASE)
    measured = {
        branch: (_shape_a(graph, branch), bool(graph.named(branch)), bool(graph.terminal(branch)))
        for branch, *_ in SHAPES
    }
    expected = {branch: (a, b, c) for branch, a, b, c in SHAPES}
    assert measured == expected, measured


def test_planted_shape_A_REFUTES_WORK_THAT_IS_CORRECT_and_that_is_why_it_is_dead(
    repository: Path,
) -> None:
    """⛔ The remedy first routed for `W110`, inhabited rather than argued about.

    ⚠️ **`merged()` is `merge-base --is-ancestor`, and a branch cut AT the release tip
    IS an ancestor of the tip** — ⛔ **so `A` is true of a branch dispatched five
    minutes ago, of the release branch ITSELF, and of every office branch standing at
    the tip.** ⭐ **MEASURED in the live repository too, at whatever ref it is on:
    `git branch --no-merged` is empty there, which is the same reading inverted.**
    """
    graph = Graph.read(repository, RELEASE)
    assert git(repository, "branch", "-q", "trial/just-cut", RELEASE).returncode == 0
    assert _shape_a(graph, "trial/just-cut"), "⛔ A fires on a branch cut this second"
    assert _shape_a(graph, RELEASE), "⛔ A fires on the RELEASE BRANCH ITSELF"
    assert not graph.terminal("trial/just-cut"), "⭐ C does not"
    assert not graph.terminal(RELEASE), "⭐ C does not"


def test_planted_shape_B_is_a_PREFIX_test_until_the_match_is_EXACT(repository: Path) -> None:
    """⛔ `Merge chore/cto-round39:` made `chore/cto-round3` read terminal. MEASURED.

    ⭐ **The fixture reproduces the mechanism rather than citing it**: `fix/W40` is
    merged with the verdict idiom and `fix/W4` is not merged at all.
    """
    graph = Graph.read(repository, RELEASE)
    subjects = [subject for _ref, subject in graph.subjects]
    assert any(subject.startswith(MERGE_IDIOM.format(branch="fix/W40")) for subject in subjects)
    assert any("fix/W4" in subject for subject in subjects), "⛔ the SUBSTRING would match"
    assert graph.named("fix/W4") == "", "⭐ the EXACT prefix does not"
    assert graph.named("fix/W40") != ""


def test_planted_C_carries_its_OWN_merge_ref_and_never_borrows_B_s(repository: Path) -> None:
    """⭐ `C`'s answer is a map from absorbed tip to merge ref, so it needs no message.

    ⛔ **That is what lets `fix/Wsilent` be REFUTED with a named ref** — the branch
    `B` cannot see at all.
    """
    graph = Graph.read(repository, RELEASE)
    absorbed = graph.terminal("fix/Wsilent")
    assert absorbed and graph.named("fix/Wsilent") == ""
    assert git(repository, "rev-parse", "--verify", f"{absorbed}^2").returncode == 0, (
        "⛔ the ref C named is a MERGE: it has a second parent"
    )
    assert graph.terminal("fix/Wmerged") == graph.named("fix/Wmerged"), "⭐ both shapes agree here"


def test_planted_a_TIP_THAT_MOVED_PAST_ITS_OWN_MERGE_is_NOT_terminal(repository: Path) -> None:
    """⭐ `chore/cto-round17`'s real shape, and it is NOT the prefix defect.

    ⚠️ **MEASURED at `2d0cfe7`: `chore/cto-round17` has a merge subject reading
    `Merge chore/cto-round17:` at first-parent merge 129, so its `B=1 C=0` is NOT a
    prefix artefact** — ⛔ **its TIP has moved since.** ⭐ **The work continued, and `C`
    reading non-terminal is `C` being RIGHT.**
    """
    graph = Graph.read(repository, RELEASE)
    assert graph.named("fix/Wmoved") != ""
    assert graph.terminal("fix/Wmoved") == ""
    assert graph.ahead("fix/Wmoved") == 1


def test_planted_the_FAST_FORWARD_blind_spot_is_REAL_and_FAILS_SAFE(repository: Path) -> None:
    """⚠️ Ruling 199 named this rather than hiding it, and `7` real branches inhabit it.

    ⛔ **A fast-forwarded merge leaves no merge commit, so a genuinely spent branch
    reads non-terminal.** ⭐ **The failure mode is a MISSED REFUTATION, never an
    invented one** — which is the whole reason `C` ships and `A` does not.
    """
    graph = Graph.read(repository, RELEASE)
    assert graph.merged("fix/Wff") and graph.ahead("fix/Wff") == 0
    assert graph.terminal("fix/Wff") == "", "⛔ no merge commit exists to absorb its tip"
    assert graph.named("fix/Wff") == "", "⛔ and no merge subject either"


def test_the_absorbed_map_agrees_with_the_ruling_s_OWN_per_merge_form(repository: Path) -> None:
    """⛔ `board.md`'s fenced command runs `rev-list --parents -n1` ONCE PER MERGE.

    ⭐ **This module's one `log` is asserted EQUAL to it rather than assumed
    equivalent** — ⚠️ **the same comparison was run over the live repository's 177
    absorbed tips at `2d0cfe7` and the two sets were byte-identical.**
    """
    graph = Graph.read(repository, RELEASE)
    per_merge: set[str] = set()
    for merge in git(
        repository, "log", "--merges", "--first-parent", "--format=%H", RELEASE
    ).stdout.split():
        parents = git(repository, "rev-list", "--parents", "-n1", merge).stdout.split()
        per_merge.update(parents[2:])
    assert set(graph.absorbed) == per_merge
    assert per_merge, "⛔ born vacuous: the fixture must carry at least one --no-ff merge"


def test_checkouts_maps_a_branch_to_its_checkout_and_skips_a_detached_one(
    repository: Path,
) -> None:
    """⚠️ *Nobody is on that branch* and *that checkout has no branch* are different answers."""
    graph = Graph.read(repository, RELEASE)
    live = graph.checkouts()
    assert live[RELEASE].endswith("repo")
    assert "feat/held" in live and "fix/Wleak" in live
    assert (
        git(
            repository, "worktree", "add", "-q", "--detach", str(repository.parent / "loose")
        ).returncode
        == 0
    )
    assert sorted(graph.checkouts()) == sorted(live), "a detached checkout has no branch row"


def test_existence_is_its_OWN_command_and_a_sha_is_not_a_branch(repository: Path) -> None:
    """⛔ `$?` after a pipeline is the pipeline's last command, and `rev-parse` echoes.

    ⚠️ **An unknown name comes back looking like an answer**, so this asks
    `refs/heads/<name>` and reads the EXIT CODE — ⭐ and a full sha, which resolves
    as a commit, is correctly NOT a branch.
    """
    graph = Graph.read(repository, RELEASE)
    head = git(repository, "rev-parse", "HEAD").stdout.strip()
    assert graph.exists(RELEASE)
    assert not graph.exists(head)
    assert not graph.exists("fix/Wtypo")
    assert graph.tip(RELEASE) == head
    assert graph.tip("fix/Wtypo") == ""


def test_heads_is_the_whole_local_population_and_ahead_counts_one_direction(
    repository: Path,
) -> None:
    """⭐ Ruling 197(a): a count is one HALF of a position, and this half is named."""
    graph = Graph.read(repository, RELEASE)
    heads = set(graph.heads())
    assert {branch for branch, *_ in SHAPES} | {RELEASE} <= heads
    assert graph.ahead("feat/live") == 1
    assert graph.ahead(RELEASE) == 0
    assert graph.ahead("fix/Wtypo") is None, "⛔ *git cannot say* is not `0`"


# --------------------------------------------------------------------------
# Reading 2 — ⛔ `W119`: the property the HOST reading got WRONG, over the FIXTURE
# --------------------------------------------------------------------------


def test_the_RETIRED_predicate_FIRES_on_the_ORDINARY_POST_MERGE_STATE_and_the_FIXED_one_does_NOT(
    repository: Path,
) -> None:
    """⛔ Ruling 225, both predicates, ONE run, ONE fixture, population printed FIRST.

    ⭐ **`fix/Wleak` IS the ordinary post-merge state** — its tip is absorbed by a merge
    AND a worktree still holds it — ⚠️ **and `conftest.py` has built it since `W110`, so
    the counter-example to the shipped property was already in the fixture and nothing
    was ever asserted over it.** ⛔ **The retired reading refutes it; the fixed one does
    not, and that single disagreement is the whole of this row.**

    ⭐ **The guard is asserted INHABITED on both sides** (Ruling 48, Ruling 124): a
    fixture where nothing carried unmerged work would satisfy the fixed predicate
    vacuously, and `4 + 6 = 10` is the whole of `SHAPES` accounted for.
    """
    graph = Graph.read(repository, RELEASE)
    population = tuple(branch for branch, *_ in SHAPES)
    ahead = {branch: graph.ahead(branch) for branch in population}
    terminal = {branch: bool(graph.terminal(branch)) for branch in population}
    unmerged = sorted(b for b, count in ahead.items() if count)
    spent = sorted(b for b, count in ahead.items() if count == 0)
    assert sorted(graph.checkouts()) == sorted([RELEASE, "feat/held", "fix/Wleak"]), (
        f"the fixture's checkouts moved: {sorted(graph.checkouts())}"
    )
    assert unmerged == ["feat/held", "feat/live", "fix/W4", "fix/Wmoved"], (ahead, terminal)
    assert len(unmerged) == 4 and len(spent) == 6 and len(population) == 10, (unmerged, spent)

    retired = _a_live_checkout_holding_a_terminal_branch(graph)
    assert retired == ["fix/Wleak"], (
        f"⛔ the RETIRED predicate must refute the ordinary post-merge state, and that is "
        f"why it is retired: {retired}"
    )
    assert _unmerged_work_reading_terminal(graph, population) == ([], []), (
        f"⭐ the FIXED predicate holds over the WHOLE fixture, `fix/Wleak` included: "
        f"{ahead}, {terminal}"
    )


def test_planted_the_FIXED_predicate_CAN_FIRE_and_an_IMPOSSIBLE_TIP_leaves_it_SILENT(
    repository: Path,
) -> None:
    """⛔ Ruling 123: the predicate is PLANTED, and the plant is adversarial to the SHA.

    ⭐ **The plant is `feat/held`'s REAL tip mapped to a REAL merge ref from this
    fixture's own history** — ⚠️ **nothing but the sha itself distinguishes it from a
    true terminal reading**, so no shape check could reject it and only the comparison
    can. ⛔ **The IMPOSSIBLE reading is a tip NO OBJECT HAS, and it is PROVED impossible
    against the fixture rather than asserted to be.**
    """
    graph = Graph.read(repository, RELEASE)
    held, merge = graph.tip("feat/held"), graph.terminal("fix/Wmerged")
    assert held and merge, "born vacuous: the plant needs a real tip and a real merge ref"
    probe = git(repository, "cat-file", "-e", f"{IMPOSSIBLE_TIP}^{{commit}}")
    assert probe.returncode != 0, (
        "⛔ the IMPOSSIBLE tip must be no object in this fixture, and that is MEASURED"
    )

    planted = Graph(repository, RELEASE, {**graph.absorbed, held: merge}, graph.subjects)
    impossible = Graph(
        repository, RELEASE, {**graph.absorbed, IMPOSSIBLE_TIP: merge}, graph.subjects
    )
    fired = _unmerged_work_reading_terminal(planted, ("feat/held", "feat/live"))
    silent = _unmerged_work_reading_terminal(impossible, ("feat/held", "feat/live"))
    assert fired == (["feat/held"], []), f"⛔ the predicate must be able to return NO: {fired}"
    assert silent == ([], []), silent
    assert fired != silent, "⛔ the impossible reading must DIFFER from the plant"


def test_the_FIXED_predicate_REPORTS_git_could_not_say_rather_than_folding_it_into_zero(
    repository: Path,
) -> None:
    """⭐ The third answer, and `W115`'s coercion is what it refuses to repeat.

    ⛔ **`ahead()` returns `None` when git cannot answer, and `None` is not `0`**: a
    branch nothing resolves must arrive as *unanswerable* and never as *satisfies the
    property*. ⚠️ **The retired predicate folds it** — `if graph.ahead(branch):` — ⭐ and
    this asserts the replacement does not.
    """
    graph = Graph.read(repository, RELEASE)
    assert graph.ahead("fix/Wtypo") is None, "⛔ *git cannot say* is the premise here"
    assert _unmerged_work_reading_terminal(graph, ("fix/Wtypo", "feat/held")) == (
        [],
        ["fix/Wtypo"],
    )


def test_planted_shape_B_and_shape_C_DISAGREE_and_the_disagreement_is_READABLE(
    repository: Path,
) -> None:
    """⚠️ Ruling 199 measured the disagreement on real history and ruled it PRINTED.

    ⛔ **The population is the FIXTURE's, not the host's** (Ruling 225): the live reading
    this replaces asserted that `heads()` — every branch on the machine — carried at
    least one disagreement, which is a property of somebody's housekeeping. ⭐ **Here the
    two disagreeing shapes are BUILT: `fix/Wsilent` is absorbed and named by nothing,
    `fix/Wmoved` is named and its tip has moved past its own merge** — and the
    disagreement is NAMED rather than counted.
    """
    graph = Graph.read(repository, RELEASE)
    population = tuple(branch for branch, *_ in SHAPES)
    disagree = sorted(b for b in population if bool(graph.terminal(b)) != bool(graph.named(b)))
    assert disagree == ["fix/Wmoved", "fix/Wsilent"], disagree
    assert len(disagree) < len(population), "⭐ and the two shapes agree on the rest"


def test_planted_no_reading_from_the_graph_PRINTS_A_HOME_PATH_and_a_planted_one_IS_CAUGHT(
    repository: Path,
) -> None:
    """⛔ R7, asserted over a population this module BUILDS and can therefore poison.

    ⚠️ **The reading this replaces swept the host's release branch**, which is a sweep of
    whatever history that machine had — ⛔ **and it could not be exercised in the failing
    direction at all, because making it fail means writing a home path into a real merge
    message.** ⭐ **Over the fixture both directions run: the clean history reads `0`, and
    one planted merge subject is caught and NAMED.**
    """
    graph = Graph.read(repository, RELEASE)
    assert graph.subjects, "⛔ born vacuous: the fixture carries --no-ff merges"
    assert [ref for ref, subject in graph.subjects if PLANTED_HOME in subject] == []

    assert git(repository, "checkout", "-q", "-b", "fix/Wr7").returncode == 0
    commit(repository, "r7.txt")
    assert git(repository, "checkout", "-q", RELEASE).returncode == 0
    subject = f"Merge fix/Wr7: a subject carrying {PLANTED_HOME} (CTO: APPROVE)"
    merged = git(repository, *AUTHOR, "merge", "--no-ff", "-q", "fix/Wr7", "-m", subject)
    assert merged.returncode == 0, merged.stderr

    planted = Graph.read(repository, RELEASE)
    caught = [ref for ref, text in planted.subjects if "/home/" in text or "/Users/" in text]
    assert caught == [planted.named("fix/Wr7")], caught
    assert len(planted.subjects) == len(graph.subjects) + 1


def test_a_commit_moves_the_tip_and_therefore_moves_TERMINALITY(repository: Path) -> None:
    """⭐ Terminality is a property of the TIP, asserted by moving one.

    ⛔ **`fix/Wmerged` is terminal; one commit on it and it is not** — which is the
    behaviour that stops this predicate from refuting a branch somebody reopened.
    """
    graph = Graph.read(repository, RELEASE)
    assert graph.terminal("fix/Wmerged")
    assert git(repository, "checkout", "-q", "fix/Wmerged").returncode == 0
    commit(repository, "reopened.txt")
    assert git(repository, "checkout", "-q", RELEASE).returncode == 0
    assert Graph.read(repository, RELEASE).terminal("fix/Wmerged") == ""
