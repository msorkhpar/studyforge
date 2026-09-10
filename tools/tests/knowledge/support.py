"""A throwaway repository for the index tests. Imported, never copied.

**What it does.** Builds a git repository with the three trees an index claims
to describe, so freshness can be exercised without touching this checkout.

**How you use it.** `make_repository(tmp_path)` returns `(root, head)`;
`commit_all(root, message)` adds a commit.

**Depends on.** `subprocess` and `pathlib`.

⛔ **The identity is fabricated and local to the repository being made** (R7).
A test that committed as the person running it would write their git identity
into a fixture, which is the datum this project refuses to record anywhere.
"""

from __future__ import annotations

import shutil
import subprocess
from pathlib import Path

#: ⛔ Fabricated, and `.invalid` is reserved by RFC 2606 so it can reach
#: nobody. Never the identity of whoever runs the suite.
AUTHOR = ("Example Author", "author@example.invalid")


def _git(root: Path, *arguments: str) -> str:
    tool = shutil.which("git")
    assert tool is not None, "git is not installed; this test cannot answer"
    done = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [tool, *arguments], cwd=root, capture_output=True, text=True, check=False
    )
    assert done.returncode == 0, done.stdout + done.stderr
    return done.stdout.strip()


def commit_all(root: Path, message: str) -> str:
    """Stage everything and commit it, returning the new commit."""
    _git(root, "add", "-A")
    _git(root, "commit", "-q", "-m", message)
    return _git(root, "rev-parse", "HEAD")


def make_repository(tmp_path: Path) -> tuple[Path, str]:
    """A repository with `src/`, `tools/` and `docs/`, and one commit."""
    root = tmp_path / "repository"
    (root / "src").mkdir(parents=True)
    (root / "tools").mkdir()
    (root / "docs").mkdir()
    (root / "src" / "thing.py").write_text("VALUE = 1\n", encoding="utf-8")
    (root / "docs" / "note.md").write_text("# note\n", encoding="utf-8")
    (root / "README.md").write_text("readme\n", encoding="utf-8")
    _git(root, "init", "-q", "-b", "main")
    _git(root, "config", "user.name", AUTHOR[0])
    _git(root, "config", "user.email", AUTHOR[1])
    return root, commit_all(root, "first")
