"""The SYNTHESISED repository every git-reading board test is measured against.

⛔ **The subject is a synthesised repository, and that is Ruling 191(b) rather than
convenience.** ⚠️ **Between waves every population these modules read is empty** —
the observation table is replaced at a close, `--no-merged` is empty, and a
just-dispatched checkout carries no commit — ⭐ **so a control drawn from the live
tree is born vacuous exactly when a close run is taken.**

⭐ **It carries one branch of every shape Ruling 199 separates, because the three
candidate predicates DISAGREE and a fixture with only the agreeing cases would have
measured nothing:**

| branch | `A` merged∧0 | `B` message | `C` graph | what it is for |
|---|---|---|---|---|
| `fix/Wmerged` | 1 | 1 | 1 | the ordinary spent branch, both shapes agree |
| `fix/Wsilent` | 1 | 0 | 1 | ⛔ `B`'s false-NEGATIVE: absorbed, never named |
| `fix/Wff` | 1 | 0 | 0 | ⚠️ `C`'s NAMED blind spot: a fast-forward leaves no merge |
| `fix/Wmoved` | 0 | 1 | 0 | ⭐ named by a merge and its TIP MOVED PAST it |
| `fix/W4` | 0 | 0 | 0 | ⛔ the PREFIX control: `Merge fix/W40:` must not claim it |
| `fix/Wleak` | 1 | 1 | 1 | ⛔ **`W110` itself: absorbed AND STILL CHECKED OUT** |
| `feat/held` | 0 | 0 | 0 | ⭐ the POSITIVE row: ahead and held (Ruling 191(c)) |
| `feat/live` | 0 | 0 | 0 | ahead and nobody's |
| `feat/bare` | 1 | 0 | 0 | Ruling 130: no commit, invisible to `--no-merged` |
| `trial/spent` | 1 | 0 | 0 | the spent-namespace reading no board cell carries |

⭐ **The identity the fixture commits with is a PLACEHOLDER** (R7): a real name or
address in a test is personal data in a file, and a commit does not need one to be a
commit.
"""

from __future__ import annotations

from pathlib import Path

import pytest

from tests.support import git as git_binary
from tools.quality.board.observation import INFLIGHT_CLOSE, INFLIGHT_OPEN
from tools.quality.board.register import BOARD
from tools.workspace import git

RELEASE = "release/m0-foundations"

#: ⛔ A placeholder identity, never the user's (R7). ⭐ `Example` and `.invalid`
#: are the reserved forms, so a reader cannot mistake either for a real address.
AUTHOR = ("-c", "user.name=Example Author", "-c", "user.email=author@example.invalid")

HEADER = "| Row | Owner | Checkout | Commits ahead | State |\n|---|---|---|---|---|\n"

#: ⛔ A well-formed sha that NO OBJECT CARRIES. ⭐ `git update-ref` REFUSES to write one
#: ("trying to write non-commit object"), so the plant below writes the ref FILE — which
#: is the shape a pruned object or a truncated `refs/heads/` write leaves behind.
MISSING_OBJECT = "0" * 39 + "1"


def unreadable(root: Path, branch: str) -> str:
    """⛔ Plant a branch git CANNOT count — ⭐ a GENUINE failure, never a stubbed `None`.

    ⚠️ **MEASURED at `6c4e3d0` in the pinned container, git 2.47.3, BEFORE any test was
    written** — the point being that `Graph.ahead()` returns `None` only when git
    declines, so a mocked `None` would certify nothing (`rows/W115.md`):

    ```text
    rev-parse --verify --quiet refs/heads/<b>            -> rc 0, echoes the missing sha
    rev-parse --verify --quiet refs/heads/<b>^{commit}   -> rc 1      (tip() -> "")
    rev-list --count <release>..<b>                      -> rc 128    (ahead() -> None)
    merge-base --is-ancestor <b> <release>               -> rc 128
    worktree list --porcelain / for-each-ref / log --merges -> rc 0, unaffected
    ```

    ⭐ **So `exists()` is TRUE and `ahead()` is `None`** — exactly `W115`'s state: the
    row's carrier resolves as a branch and git will not count it.
    """
    ref = root / ".git" / "refs" / "heads" / branch
    ref.parent.mkdir(parents=True, exist_ok=True)
    ref.write_text(f"{MISSING_OBJECT}\n", encoding="utf-8")
    return branch


def commit(root: Path, name: str, body: str = "x\n") -> None:
    """Write and commit one file, ⛔ asserting each git command's own exit code."""
    (root / name).write_text(body, encoding="utf-8")
    assert git(root, "add", name).returncode == 0
    assert git(root, *AUTHOR, "commit", "-q", "-m", f"add {name}").returncode == 0


def _branch_then_merge(root: Path, branch: str, subject: str | None) -> None:
    """Cut `branch`, commit on it, and absorb it — ⛔ `--no-ff` unless `subject` is `None`."""
    assert git(root, "checkout", "-q", "-b", branch).returncode == 0
    commit(root, f"{branch.replace('/', '-')}.txt")
    assert git(root, "checkout", "-q", RELEASE).returncode == 0
    if subject is None:
        assert git(root, *AUTHOR, "merge", "--ff-only", "-q", branch).returncode == 0
        return
    assert git(root, *AUTHOR, "merge", "--no-ff", "-q", branch, "-m", subject).returncode == 0


def write_board(root: Path, rows: str, register: str = "", delimited: bool = True) -> None:
    """Write a board whose observation table is DELIMITED, as the contract requires.

    ⚠️ **`delimited=False` writes the Ruling 196(b) RAMP**, which `W111` made a
    `NOT_AUTHORITATIVE` reading rather than a silent fallback.
    """
    table = HEADER + rows
    if delimited:
        table = f"{INFLIGHT_OPEN}\n{table}{INFLIGHT_CLOSE}\n"
    (root / BOARD).parent.mkdir(parents=True, exist_ok=True)
    (root / BOARD).write_text(
        "# Board\n\n## In flight\n\n"
        + table
        + "\n<!-- register -->\n| # | Row | Owner | State | Detail |\n|---|---|---|---|---|\n"
        + register
        + "<!-- /register -->\n",
        encoding="utf-8",
    )


@pytest.fixture
def repository(tmp_path: Path) -> Path:
    """One repository with one branch of every shape the module docstring tabulates."""
    assert git_binary()
    root = tmp_path / "repo"
    root.mkdir()
    assert git(root, "init", "-q", "-b", RELEASE).returncode == 0
    commit(root, "first.txt")

    # ⛔ The verdict convention's own shape: `Merge <branch>: <line> (CTO: …)`.
    _branch_then_merge(
        root, "fix/Wmerged", "Merge fix/Wmerged: the naming of one row (CTO: APPROVE)"
    )
    # ⛔ `B`'s false-NEGATIVE population: the pre-convention tail, 25 branches at `2d0cfe7`.
    _branch_then_merge(root, "fix/Wsilent", "a merge whose subject names no branch")
    # ⛔ The PREFIX control — the shipped `merge_of()`'s `if branch in subject:` defect.
    _branch_then_merge(root, "fix/W40", "Merge fix/W40: a neighbouring id (CTO: APPROVE)")
    # ⚠️ `C`'s NAMED blind spot: a fast-forward leaves no merge commit at all.
    _branch_then_merge(root, "fix/Wff", None)
    # ⭐ Named by a merge, and then its TIP MOVED PAST it — `chore/cto-round17`'s shape.
    _branch_then_merge(root, "fix/Wmoved", "Merge fix/Wmoved: a row that continued (CTO: APPROVE)")
    assert git(root, "checkout", "-q", "fix/Wmoved").returncode == 0
    commit(root, "moved-again.txt")
    assert git(root, "checkout", "-q", RELEASE).returncode == 0
    # ⛔ `W110` itself: absorbed by a merge AND still held by a checkout.
    _branch_then_merge(root, "fix/Wleak", "Merge fix/Wleak: the leaked worktree (CTO: APPROVE)")

    assert git(root, "branch", "fix/W4", "fix/Wmoved").returncode == 0
    for branch, name in (("feat/live", "live.txt"), ("feat/held", "held.txt")):
        assert git(root, "checkout", "-q", "-b", branch).returncode == 0
        commit(root, name, "ahead\n")
        assert git(root, "checkout", "-q", RELEASE).returncode == 0

    assert git(root, "branch", "trial/spent").returncode == 0
    assert git(root, "branch", "feat/bare").returncode == 0
    assert git(root, "worktree", "add", "-q", str(tmp_path / "held"), "feat/held").returncode == 0
    assert git(root, "worktree", "add", "-q", str(tmp_path / "leak"), "fix/Wleak").returncode == 0
    return root
