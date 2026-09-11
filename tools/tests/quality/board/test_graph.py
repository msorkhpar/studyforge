"""Mirror of `tools/quality/board/graph.py` (R12) — Ruling 199's THREE candidate shapes.

⛔ **All three are computed here and compared, because the decision rests on their
DISAGREEMENT and a test of the winner alone would assert nothing about why it won.**
⭐ **Shape `A` — `MERGED ∧ 0-ahead` — is the remedy first routed for `W110`, and the
reading that refutes it is reproduced rather than cited.**
"""

from __future__ import annotations

from pathlib import Path

from tests.support import repository_root
from tools.quality.board.graph import MERGE_IDIOM, Graph
from tools.workspace import git

from .conftest import RELEASE, commit

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


def _shape_a(graph: Graph, branch: str) -> bool:
    """Shape `A`, spelled out so the test does not depend on it living in the source."""
    return graph.merged(branch) and graph.ahead(branch) == 0


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
# Reading 2 — LIVE, so the shapes are exercised against real history
# --------------------------------------------------------------------------


def test_live_the_release_branch_and_every_LIVE_CHECKOUT_read_NON_TERMINAL() -> None:
    """⛔ The reading that would have made `W110` fire on its own author.

    ⭐ **MEASURED at `2d0cfe7`: shape `A` is true of ALL 124 local branches** — ⚠️ so a
    predicate built on it would have refuted the release branch, the CTO's round
    branch and both developer branches dispatched that hour. ⛔ **`C` must read `0`
    for every branch a checkout currently holds with no merge of its own.**
    """
    graph = Graph.read(repository_root(), RELEASE)
    if not graph.exists(RELEASE):
        return
    for branch in graph.checkouts():
        if graph.ahead(branch):
            continue
        assert graph.terminal(branch) == "", f"⛔ {branch} is held by a live checkout"
    assert graph.absorbed, "⛔ born vacuous: this repository has first-parent merges"


def test_live_shape_B_and_shape_C_DISAGREE_and_the_disagreement_is_READABLE() -> None:
    """⚠️ Ruling 199 measured `27` disagreements over `120` branches and ruled them PRINTED.

    ⭐ **This asserts the disagreement population is INHABITED rather than pinning its
    size** — ⛔ **a number here would be a measurement in a test, stale the next time
    anything merges** (Ruling 181's family, one layer down).
    """
    graph = Graph.read(repository_root(), RELEASE)
    if not graph.exists(RELEASE):
        return
    heads = graph.heads()
    disagree = [b for b in heads if bool(graph.terminal(b)) != bool(graph.named(b))]
    assert disagree, "⛔ born vacuous: the two shapes are expected to disagree on real history"
    assert len(disagree) < len(heads), "⭐ and they agree on most of it"


def test_live_no_reading_from_the_graph_prints_an_absolute_path(repository: Path) -> None:
    """⛔ R7: `git worktree list` answers in absolute paths and a path carries a home."""
    del repository
    graph = Graph.read(repository_root(), RELEASE)
    for ref, subject in graph.subjects:
        assert "/home/" not in subject and "/Users/" not in subject, ref


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
