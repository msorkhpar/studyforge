"""A repository of material with no manifest, which is what onboarding starts from.

⛔ Synthetic on purpose. A fixture that depends on a sibling repository being
checked out is a fixture that skips, and a skipped check is not evidence.

⚠️ **There is no `corpus.json` here, and that is the difference from the
adapter's fixture.** The adapter scaffold starts from a manifest somebody already wrote;
this skill is what writes one, so its fixture has to stop before that.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

#: The commit a pin records (the operator's statement of what the
#: installed library was built from, checked for shape only). ⭐ The sha of an
#: empty tree committed with placeholder identities at a fixed date, so it is
#: the same on every machine. ⛔ Never a real commit from this one (R7).
COMMIT = "cdfb352da949393dd56a58ac37d1f43d5970d659"

#: How a synthetic repository is made: no user or system config, placeholders only.
SYNTHETIC_GIT = {
    "GIT_CONFIG_GLOBAL": os.devnull,
    "GIT_CONFIG_NOSYSTEM": "1",
    "GIT_AUTHOR_NAME": "framework",
    "GIT_AUTHOR_EMAIL": "framework@example.invalid",
    "GIT_COMMITTER_NAME": "framework",
    "GIT_COMMITTER_EMAIL": "framework@example.invalid",
    "GIT_AUTHOR_DATE": "2000-01-01T00:00:00+0000",
    "GIT_COMMITTER_DATE": "2000-01-01T00:00:00+0000",
}

#: What reconnaissance hands over: a draft, not a manifest. ⚠️ `corpus_api: 1`
#: and no `not_material`, exactly as `proposal.draft` writes it.
DRAFT = {
    "corpus_api": 1,
    "source": "walkthrough",
    "title": "A Walkthrough Corpus",
    "levels": ["course"],
    "variants": ["prose"],
    "exercises": False,
    "placement": "tree",
    "content": {"include": ["src/*.md", "README.md"]},
}


#: ⭐ `W266`: the draft a PERSON settled before onboarding. The README records the units and no
#: unit reads it, so it is `not_material` (`docs/authoring/corpus.md`), never an include.
SETTLED = {
    **DRAFT,
    "content": {
        "include": ["src/*.md"],
        "not_material": [
            {
                "glob": "README.md",
                "why": "navigation that records the units; no unit reads it (W266)",
            }
        ],
    },
}


#: A `not_material` block a PERSON settled in the draft (INT06-1's shape): a
#: directory of notes about the material, which no generator writes and so no
#: generator can declare. ⚠️ Not written by `material` — a test that needs the
#: file on disk writes it, so every other test's tree is unchanged.
NOTES = {"glob": "notes/**", "why": "the integrator's notes about the material, never a unit"}


def material(root: Path) -> Path:
    """Write the material, and nothing else — no manifest, no adapter, no tests.

    ⛔ **And nothing beside it**: the framework is the library the
    test's Python imports, never a checkout next to the corpus.
    """
    root.mkdir(parents=True, exist_ok=True)
    (root / "README.md").write_text(
        "# A Walkthrough Corpus\n\n- [1. First](src/01.md)\n- [2. Second](src/02.md)\n",
        encoding="utf-8",
    )
    (root / "src").mkdir(exist_ok=True)
    (root / "src/01.md").write_text("# First\n\nProse.\n", encoding="utf-8")
    (root / "src/02.md").write_text("# Second\n\nProse.\n", encoding="utf-8")
    return root


def git(where: Path, *arguments: str) -> None:
    """Run git in `where` with no user config and placeholder identities only (R7)."""
    env = {"PATH": os.environ.get("PATH", ""), "HOME": str(where), **SYNTHETIC_GIT}
    done = subprocess.run(
        [shutil.which("git"), "-C", str(where), *arguments], capture_output=True, env=env
    )
    assert done.returncode == 0, done.stderr.decode()


def linked_worktree(parent: Path, *, main: str = "corpus") -> Path:
    """A corpus repository under `parent`, and a linked worktree of it one level deeper.

    ⛔ Nothing beside either: the framework is the installed library.
    """
    checkout = parent / main
    checkout.mkdir(parents=True)
    git(checkout, "init", "-q")
    git(checkout, "commit", "-q", "--allow-empty", "-m", "a synthetic corpus commit")
    worktree = parent / f"{main}-worktrees" / "one"
    git(checkout, "worktree", "add", "-q", str(worktree))
    return worktree


def draft(**changes) -> dict:
    """The draft with fields replaced, so a test says only what it varies."""
    return {**DRAFT, **changes}
