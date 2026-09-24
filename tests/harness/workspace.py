r"""Where a sibling checkout is, when a run was TOLD where: `STUDYFORGE_WORKSPACE`.

**What it does.** Answers one question for a product test that reads another repository —
the runner image's component, the narration service, a real corpus: *which directory is that
checkout, if this run named one?* ⭐ The answer comes from ONE environment variable,
`STUDYFORGE_WORKSPACE`, naming the directory the checkouts sit in, each under its own name.
⛔ Nothing is guessed: no pin file is read, and no parent directory is searched.

**How you use it.** `sibling(name)` is that checkout's directory, or `None`; `absence(name)` is
the sentence a caller skips with when it is `None`. `workspace_root()` is the named directory
itself, or `None`. `git` and `holds` ask a checkout one question each, and `head` is the commit
it has checked out. `DEV_CONTAINER` names the variable the pinned image sets.
`tests.harness.sibling` reads one file out of a checkout at that commit.

**Depends on.** `git` on `PATH`, and the standard library.

## ⛔ Absent is an answer, and the default

A clean clone of this repository holds the framework and its tests and nothing else, and the
pinned image mounts that one checkout. ⭐ So with the variable unset, every sibling is ABSENT,
and a test that needs one SKIPS saying which checkout and which variable — never a crash, and
never a reach for a file that is not part of this repository.

## ⛔ No path is ever put in a sentence (R7)

The directory the variable names sits under somebody's home. A sentence names the
**component** and the **variable**, both of which every checkout of this repository agrees on,
and never where either sits on this disk.
"""

from __future__ import annotations

import os
import re
import subprocess
from collections.abc import Mapping
from pathlib import Path

#: ⭐ The one way a run names where the sibling checkouts are.
WORKSPACE_ENV = "STUDYFORGE_WORKSPACE"

#: ⛔ A component's name is **one path component**, and the shape is closed: no
#: separator, no `..`, no leading dot — so a name can never resolve outside the
#: named directory, and there is nothing a refusal would have to quote.
SAFE_NAME = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9._-]*[A-Za-z0-9])?$")

#: Set by `docker/dev/Dockerfile`. ⭐ Its presence means *"this run is the one
#: that certifies a result"* — the same marker the grammar tests read.
DEV_CONTAINER = "STUDYFORGE_DEV_CONTAINER"


def workspace_root(environ: Mapping[str, str] | None = None) -> Path | None:
    """Return the directory `STUDYFORGE_WORKSPACE` names, or `None` when it names none."""
    named = (os.environ if environ is None else environ).get(WORKSPACE_ENV)
    return Path(named).expanduser() if named else None


def sibling(name: str, environ: Mapping[str, str] | None = None) -> Path | None:
    """Return the checkout called `name` in the named workspace, or `None`.

    ⛔ `name` is framework data, never corpus data, and it must be one path component.
    """
    if not SAFE_NAME.match(name):
        raise ValueError("a sibling's name must be a single path component")
    root = workspace_root(environ)
    if root is None:
        return None
    directory = root / name
    return directory if directory.is_dir() else None


def absence(name: str, environ: Mapping[str, str] | None = None) -> str:
    """Say why `name` is not reachable here, naming the variable and never a path."""
    if workspace_root(environ) is None:
        return f"{WORKSPACE_ENV} is not set, so no checkout of {name} is named"
    return f"the workspace {WORKSPACE_ENV} names holds no checkout of {name}"


def git(directory: Path, *arguments: str) -> subprocess.CompletedProcess:
    """Run one git command in `directory`. ⛔ Never `--work-tree`, never a URL."""
    return subprocess.run(
        ["git", "-C", str(directory), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )


def holds(directory: Path, commit: str) -> bool:
    """Say whether this checkout holds that commit at all."""
    return git(directory, "cat-file", "-e", f"{commit}^{{commit}}").returncode == 0


def head(directory: Path) -> str | None:
    """Return the commit this checkout has checked out, or `None` when it is no checkout."""
    result = git(directory, "rev-parse", "--verify", "--quiet", "HEAD^{commit}")
    commit = result.stdout.strip()
    return commit if result.returncode == 0 and commit else None
