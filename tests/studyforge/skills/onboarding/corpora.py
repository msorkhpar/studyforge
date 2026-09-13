"""A repository of material with no manifest, which is what onboarding starts from (SK-07).

⛔ Synthetic on purpose. A fixture that depends on a sibling repository being
checked out is a fixture that skips, and a skipped check is not evidence.

⚠️ **There is no `corpus.json` here, and that is the difference from the
adapter's fixture.** `SK-02` starts from a manifest somebody already wrote;
this skill is what writes one, so its fixture has to stop before that.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

from studyforge.skills.onboarding.pin import FRAMEWORK

#: The one commit of the synthetic framework `framework_beside` makes (`W270`).
#: ⭐ Deterministic: an empty tree, placeholder identities and a fixed date, so
#: the sha is the same on every machine. ⛔ Never a real commit from this one (R7).
COMMIT = "cdfb352da949393dd56a58ac37d1f43d5970d659"

#: How the synthetic commit is made: no user or system config, placeholders only.
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


#: A `not_material` block a PERSON settled in the draft (INT06-1's shape): a
#: directory of notes about the material, which no generator writes and so no
#: generator can declare. ⚠️ Not written by `material` — a test that needs the
#: file on disk writes it, so every other test's tree is unchanged.
NOTES = {"glob": "notes/**", "why": "the integrator's notes about the material, never a unit"}


def framework_beside(root: Path) -> Path:
    """Make the synthetic framework checkout beside `root`, holding `COMMIT`, once.

    ⭐ Where the pin looks (`pin.framework_of`): a sibling of the corpus root. A
    test that means the checkout is absent simply never calls this.
    """
    framework = root.parent / FRAMEWORK
    if (framework / ".git").exists():
        return framework
    git = shutil.which("git")
    assert git is not None, "git is not installed; the pin cannot be checked without it"
    framework.mkdir(parents=True, exist_ok=True)
    env = {"PATH": os.environ.get("PATH", ""), "HOME": str(root.parent), **SYNTHETIC_GIT}

    def run(*arguments: str, stdin: bytes = b"") -> str:
        done = subprocess.run(
            [git, "-C", str(framework), *arguments], input=stdin, capture_output=True, env=env
        )
        assert done.returncode == 0, done.stderr.decode()
        return done.stdout.decode().strip()

    run("init", "-q")
    tree = run("hash-object", "-w", "-t", "tree", "--stdin")
    made = run("commit-tree", tree, "-m", "a synthetic framework commit")
    assert made == COMMIT, "the synthetic framework commit is not the pinned one"
    return framework


def material(root: Path) -> Path:
    """Write the material, and nothing else — no manifest, no adapter, no tests.

    ⚠️ Plus the framework checkout beside it (`W270`), which is outside `root`.
    """
    root.mkdir(parents=True, exist_ok=True)
    framework_beside(root)
    (root / "README.md").write_text(
        "# A Walkthrough Corpus\n\n- [1. First](src/01.md)\n- [2. Second](src/02.md)\n",
        encoding="utf-8",
    )
    (root / "src").mkdir(exist_ok=True)
    (root / "src/01.md").write_text("# First\n\nProse.\n", encoding="utf-8")
    (root / "src/02.md").write_text("# Second\n\nProse.\n", encoding="utf-8")
    return root


def draft(**changes) -> dict:
    """The draft with fields replaced, so a test says only what it varies."""
    return {**DRAFT, **changes}
