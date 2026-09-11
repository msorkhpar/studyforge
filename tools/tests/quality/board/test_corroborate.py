"""Mirror of `tools/quality/board/corroborate.py` (R12) — Ruling 189(c) and (d).

⛔ **The subject is a SYNTHESISED repository, and that is Ruling 191(b) rather
than convenience.** ⚠️ **Between waves every population this module reads is
empty** — the observation table is replaced at a close, `--no-merged` is empty,
and a just-dispatched checkout carries no commit — ⭐ **so a control drawn from
the live tree is born vacuous exactly when a close run is taken.** ⛔ **The
synthesised repository carries its own POSITIVE row** (a corroborated branch, a
held checkout) so that the refutations are read against something that passes.

⭐ **The identity the fixture commits with is a PLACEHOLDER** (R7): a real name or
address in a test is personal data in a file, and a commit does not need one to
be a commit.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import git as git_binary
from tools.quality.board.corroborate import (
    CORROBORATED,
    NOT_AUTHORITATIVE,
    REFUTED,
    branch_exists,
    checkouts,
    corroborate,
    main,
    merge_of,
    tokens,
)
from tools.quality.board.register import BOARD
from tools.workspace import git

RELEASE = "release/m0-foundations"

#: ⛔ A placeholder identity, never the user's (R7). ⭐ `Example` and `.invalid`
#: are the reserved forms, so a reader cannot mistake either for a real address.
AUTHOR = ("-c", "user.name=Example Author", "-c", "user.email=author@example.invalid")

HEADER = "| Row | Owner | Checkout | Commits ahead | State |\n|---|---|---|---|---|\n"


def _commit(root: Path, name: str, body: str) -> None:
    (root / name).write_text(body, encoding="utf-8")
    assert git(root, "add", name).returncode == 0
    assert git(root, *AUTHOR, "commit", "-q", "-m", f"add {name}").returncode == 0


def _board(root: Path, rows: str, register: str = "") -> None:
    (root / BOARD).parent.mkdir(parents=True, exist_ok=True)
    (root / BOARD).write_text(
        "# Board\n\n## In flight\n\n"
        + HEADER
        + rows
        + "\n<!-- register -->\n| # | Row | Owner | State | Detail |\n|---|---|---|---|---|\n"
        + register
        + "<!-- /register -->\n",
        encoding="utf-8",
    )


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    """A repository with one of every carrier this instrument has to tell apart.

    ⛔ **Five branches and one linked checkout**, because the readings differ:
    `fix/Wmerged` is merged with a verdict-shaped message, `feat/live` is ahead
    and nobody's, `feat/held` is ahead AND checked out, `trial/spent` is an
    ancestor with no checkout, and `feat/bare` exists at the release tip.
    """
    assert git_binary()
    root = tmp_path / "repo"
    root.mkdir()
    assert git(root, "init", "-q", "-b", RELEASE).returncode == 0
    _commit(root, "first.txt", "one\n")

    assert git(root, "checkout", "-q", "-b", "fix/Wmerged").returncode == 0
    _commit(root, "merged.txt", "two\n")
    assert git(root, "checkout", "-q", RELEASE).returncode == 0
    # ⛔ The verdict convention's own shape: `Merge <branch>: <line> (CTO: …)`.
    assert (
        git(
            root,
            *AUTHOR,
            "merge",
            "--no-ff",
            "-q",
            "fix/Wmerged",
            "-m",
            "Merge fix/Wmerged: the naming of one row (CTO: APPROVE)",
        ).returncode
        == 0
    )

    for branch, name in (("feat/live", "live.txt"), ("feat/held", "held.txt")):
        assert git(root, "checkout", "-q", "-b", branch).returncode == 0
        _commit(root, name, "ahead\n")
        assert git(root, "checkout", "-q", RELEASE).returncode == 0

    assert git(root, "branch", "trial/spent").returncode == 0
    assert git(root, "branch", "feat/bare").returncode == 0
    assert git(root, "worktree", "add", "-q", str(tmp_path / "held"), "feat/held").returncode == 0
    return root


# --------------------------------------------------------------------------
# Reading 1 — PLANTED, over the synthesised population
# --------------------------------------------------------------------------


def test_planted_a_merged_branch_with_no_checkout_is_REFUTED_and_names_its_merge(
    repository: Path,
) -> None:
    """⛔ Ruling 189(d): the ref is derived from the BRANCH, in two printed steps.

    ⚠️ **The first step is an ASSERTION** — the row claims a branch — ⭐ **and it
    owes clause (c)'s observation before the second step means anything.**
    """
    _board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n")
    lines, code = corroborate(repository, RELEASE)
    printed = "\n".join(lines)
    assert code == REFUTED
    assert "row -> branch (ASSERTION, Ruling 189(c))" in printed
    assert "REFUTED: fix/Wmerged is MERGED at" in printed
    assert merge_of(repository, "fix/Wmerged", RELEASE) in printed
    assert "1 of 1 rows REFUTED" in printed


def test_planted_a_row_that_names_NOTHING_git_has_is_REFUTED_by_clause_c(
    repository: Path,
) -> None:
    """⛔ A misspelled branch and an unmerged branch both return empty from a grep.

    ⭐ **So existence is checked as its OWN command**, and a row whose claim
    resolves to nothing is refuted on the assertion rather than passed over.
    """
    _board(repository, "| `W42` | Dev | `wt/x`, `fix/Wtypo` | **+3** | in flight |\n")
    lines, code = corroborate(repository, RELEASE)
    printed = "\n".join(lines)
    assert code == REFUTED
    assert "unresolved ['wt/x', 'fix/Wtypo']" in printed, "⛔ BOTH tokens, in order"
    assert "names no branch this checkout has" in printed


def test_planted_a_HELD_checkout_is_CORROBORATED_and_is_the_positive_row(
    repository: Path,
) -> None:
    """⭐ Ruling 191(c): a synthesised control owes its own POSITIVE row.

    ⛔ **Without one, every assertion below is *"the instrument said no"* and
    nothing shows it can say yes.**
    """
    _board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    lines, code = corroborate(repository, RELEASE)
    printed = "\n".join(lines)
    assert code == CORROBORATED, printed
    assert "CORROBORATED: feat/held is checked out at held" in printed
    assert "0 of 1 rows REFUTED" in printed


def test_planted_a_BARE_branch_at_the_release_tip_is_refuted_and_says_why(
    repository: Path,
) -> None:
    """⚠️ Ruling 130: a branch with no commit is invisible to `--no-merged`.

    ⛔ **So `--no-merged` alone would have read this row as fine**, which is the
    lower bound Ruling 171 measured and the reason the board is the total
    instrument.
    """
    _board(repository, "| `W42` | Dev | `wt/x`, `feat/bare` | 0 | in flight |\n")
    lines, code = corroborate(repository, RELEASE)
    printed = "\n".join(lines)
    assert code == REFUTED
    assert "BY CONSTRUCTION (Ruling 130)" in printed
    assert git(repository, "branch", "--no-merged", RELEASE).stdout.find("feat/bare") == -1


def test_planted_the_OTHER_direction_work_git_sees_and_the_board_does_not_name(
    repository: Path,
) -> None:
    """⛔ The measured failure was BIDIRECTIONAL — stale rows present, live rows absent."""
    _board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    lines, _code = corroborate(repository, RELEASE)
    printed = "\n".join(lines)
    assert "dispatched and UNNAMED by any row: feat/live" not in printed, (
        "feat/live has no checkout, so `worktree list` cannot see it either"
    )
    assert git(repository, "worktree", "add", "-q", str(repository.parent / "two"), "feat/live")
    lines, _code = corroborate(repository, RELEASE)
    assert "dispatched and UNNAMED by any row: feat/live" in "\n".join(lines)


def test_planted_a_spent_trial_branch_is_the_reading_no_board_cell_carries(
    repository: Path,
) -> None:
    """⭐ The standing form, measured by the CTO at `0285a92` and `c3e2919`.

    ⛔ **Such a branch carries nothing unique and is invisible to `--no-merged` by
    construction** — ⚠️ **its only remaining effect is to read as dispatched work
    to a human, which is Ruling 189's subject with no cell to print it in.**
    """
    _board(repository, "")
    lines, _code = corroborate(repository, RELEASE)
    printed = "\n".join(lines)
    assert "spent and deletable (1): trial/spent" in printed
    assert "ancestor of" in printed


def test_planted_an_EMPTY_observation_table_is_not_a_pass(repository: Path) -> None:
    """⛔ Ruling 191(a): `0` is a MISSING READING, and the verdict says which case it was."""
    _board(repository, "")
    lines, code = corroborate(repository, RELEASE)
    printed = "\n".join(lines)
    assert code == CORROBORATED
    assert "the observation table is EMPTY — nothing was read" in printed
    assert "0 observation rows" in printed


def test_the_blind_spot_is_COUNTED_AND_NAMED_rather_than_judged(repository: Path) -> None:
    """⚠️ *Just dispatched* and *an office checkout* are the same bytes to `git`.

    ⛔ **So a 0-commit checkout is named as UNREADABLE here** rather than reported
    as a defect — ⭐ the board is the only instrument that can tell them apart,
    which is the whole of Ruling 171.
    """
    assert git(repository, "worktree", "add", "-q", str(repository.parent / "office"), "feat/bare")
    _board(repository, "")
    lines, _code = corroborate(repository, RELEASE)
    printed = "\n".join(lines)
    assert "invisible to git BY CONSTRUCTION (Ruling 130), 0 commits ahead" in printed
    assert "office" in printed, "the directory BASENAME, which is what identifies it"


def test_no_reading_prints_an_absolute_path(repository: Path) -> None:
    """⛔ R7: `git worktree list` answers in absolute paths and an absolute path is personal data.

    ⭐ Asserted against the fixture's own root, so the test needs no home
    directory of its own to compare against.
    """
    assert git(repository, "worktree", "add", "-q", str(repository.parent / "held2"), "trial/spent")
    _board(repository, "| `W42` | Dev | `held`, `feat/held` | 1 | in flight |\n")
    lines, _code = corroborate(repository, RELEASE)
    for line in lines:
        assert str(repository) not in line
        assert str(repository.parent) not in line


# --------------------------------------------------------------------------
# Reading 2 — Ruling 189(d)'s two instruments, one of them RECORDED AS WRONG
# --------------------------------------------------------------------------


def test_the_row_id_grep_is_a_LOWER_BOUND_and_the_branch_derivation_is_not(
    repository: Path,
) -> None:
    """⛔ Measured: `--grep '<row id>'` reads `0` for every row that shared a branch.

    ⚠️ **All three of `W85`, `W86` and `W87` returned nothing**, and `W86` is named
    in no commit message on its own branch at all. ⭐ **This fixture reproduces the
    shape rather than citing it**: one branch, one merge message, and a row id the
    message never mentions.
    """
    by_row = git(repository, "log", "--merges", "--first-parent", "--grep=W42", RELEASE)
    assert by_row.stdout.strip() == "", "⛔ the lower bound, reading 0 on a real close"
    assert merge_of(repository, "fix/Wmerged", RELEASE), "⭐ the branch derivation finds it"


def test_existence_is_its_OWN_command_and_a_sha_is_not_a_branch(repository: Path) -> None:
    """⛔ `$?` after a pipeline is the pipeline's last command, and `rev-parse` echoes.

    ⚠️ **An unknown name comes back looking like an answer**, so this asks
    `refs/heads/<name>` and reads the EXIT CODE — ⭐ and a full sha, which resolves
    as a commit, is correctly NOT a branch.
    """
    head = git(repository, "rev-parse", "HEAD").stdout.strip()
    assert branch_exists(repository, RELEASE)
    assert not branch_exists(repository, head)
    assert not branch_exists(repository, "fix/Wtypo")


def test_tokens_reads_the_code_spans_and_not_the_prose() -> None:
    """⭐ The board's own idiom for a carrier is a code span."""
    assert tokens("`wt/dev2`, `fix/W95-shared-origin-fixture`") == (
        "wt/dev2",
        "fix/W95-shared-origin-fixture",
    )
    assert tokens("none") == ()
    assert tokens("`wt/x`, `wt/x`") == ("wt/x",)


# --------------------------------------------------------------------------
# Reading 3 — IMPOSSIBLE, and it must DIFFER: exit 2, not exit 0
# --------------------------------------------------------------------------


def test_impossible_a_release_branch_that_cannot_exist_is_NOT_AUTHORITATIVE(
    repository: Path,
) -> None:
    """⛔ Ruling 53's fourth state, and Ruling 191's reason for needing it.

    ⚠️ **A check that shelled into git and found nothing would return the PASS
    reading from an empty population.** ⭐ **Here it exits `2`**, which is neither
    *the board is right* nor *the board is wrong*.
    """
    _board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n")
    lines, code = corroborate(repository, "release/no-such-branch-60713")
    assert code == NOT_AUTHORITATIVE
    assert code not in (CORROBORATED, REFUTED), "⛔ it must DIFFER from both verdicts"
    assert "NOT AUTHORITATIVE" in lines[0] and "not a pass" in lines[0]


def test_impossible_a_checkout_with_no_board_is_NOT_AUTHORITATIVE(tmp_path: Path) -> None:
    """⚠️ A tree that is not this repository has nothing to corroborate, and says so."""
    lines, code = corroborate(tmp_path, RELEASE)
    assert code == NOT_AUTHORITATIVE
    assert "nothing to corroborate" in lines[0]


def test_the_command_line_returns_the_code_and_prints_every_step(
    repository: Path, capsys: pytest.CaptureFixture[str]
) -> None:
    """⭐ The entry point a wave's close runs, asserted rather than assumed."""
    _board(repository, "| `W42` | Dev | `wt/x`, `fix/Wmerged` | 0 | in flight |\n")
    code = main(["--root", str(repository), "--release", RELEASE])
    printed = capsys.readouterr().out
    assert code == REFUTED
    assert "row -> branch (ASSERTION, Ruling 189(c))" in printed
    assert "observations (" in printed, "the population comes before the verdict (Ruling 128)"


def test_checkouts_maps_a_branch_to_its_checkout_and_skips_a_detached_one(
    repository: Path,
) -> None:
    """⚠️ *Nobody is on that branch* and *that checkout has no branch* are different answers."""
    live = checkouts(repository)
    assert live[RELEASE].endswith("repo")
    assert "feat/held" in live
    assert (
        git(
            repository, "worktree", "add", "-q", "--detach", str(repository.parent / "loose")
        ).returncode
        == 0
    )
    assert sorted(checkouts(repository)) == sorted(live), "a detached checkout has no branch row"
