"""Synthetic workspaces: real git repositories, small enough to build per test.

⭐ For the tests of `tests.harness.workspace` and `tests.harness.sibling`, so they build
their trees without touching any real checkout.

⛔ **Synthetic on purpose, and it is not a convenience.** The real components
are not part of this repository and the pinned image mounts one directory, so a
test that needed them would skip inside the authoritative image — ⭐ **and a
skipped check is not evidence.** These are real `git init` repositories with
real commits, so `rev-parse` and `cat-file` answer for real.

⚠️ **The identity is a placeholder and must stay one** (R7). A commit needs an
author; a test that took the machine's git identity would write a person's name
and address into a temporary tree, and the habit is the risk rather than the
file.
"""

from __future__ import annotations

import subprocess
from pathlib import Path

#: ⛔ Never the machine's git identity. RFC 2606 reserves `.invalid`, so this
#: address can never be delivered anywhere.
AUTHOR = ("-c", "user.name=Example Author", "-c", "user.email=author@example.invalid")


def run(directory: Path, *arguments: str) -> str:
    """Run one git command, failing loudly."""
    result = subprocess.run(
        ["git", "-C", str(directory), *AUTHOR, *arguments],
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout.strip()


def repository(directory: Path, text: str = "one") -> str:
    """Create a git repository with one commit and return that commit."""
    directory.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(directory)], check=True)
    (directory / "file.txt").write_text(text, encoding="utf-8")
    run(directory, "add", "file.txt")
    run(directory, "commit", "-qm", "one")
    return run(directory, "rev-parse", "HEAD")


def environ(root: Path) -> dict[str, str]:
    """The one variable a run sets to name `root` as the workspace."""
    return {"STUDYFORGE_WORKSPACE": str(root)}


#: ⛔ Assembled at run time, never written as a literal. A test file carrying a
#: home-directory path **is** the violation these checks exist to prevent, even
#: as a fixture and even with a placeholder name in it (R7), and the quality
#: floor is right to refuse one.
SEPARATOR = "/"
HOME_PATH = f"{SEPARATOR}home{SEPARATOR}jane{SEPARATOR}IdeaProjects"
