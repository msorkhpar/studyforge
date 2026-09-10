"""Where the knowledge index is, and whether it can be trusted.

**What it does.** Finds `graphify-out/graph.json`, reads the commit it was
built at, and answers *"is this index current?"* by asking **git what
changed**, never by asking the filesystem what time it is.

**How you use it.** `index_path(root)`, `read_graph(path)`,
`built_at_commit(graph)`, `freshness(root, commit)` → one of `FRESH`,
`STALE`, `UNVERIFIABLE`.

**Depends on.** `json`, `pathlib`, `shutil`, `subprocess`. Nothing from
`studyforge`, so a tree whose framework does not import still gets a verdict.

## ⛔ Why there is no `mtime` anywhere in this module (Ruling 18)

**Measured 2026-09-09, and it is the reason this module exists in this shape:**

- A reviewer read the index's mtime as **stale** and was wrong; the same index
  was measured stale **by content**, 15 commits behind. ⛔ Both signals were
  wrong at once, in opposite directions.
- Re-measured 33 minutes later, ⛔ **the mtime verdict flipped FAIL→PASS while
  the content signal did not move.** Nothing about the tree had changed.
- ⛔ **`git worktree add` resets every mtime**, so an mtime check would fail in
  every trial-merge worktree — breaking the one gate the rubric added to catch
  C5.

⭐ **And the right signal was already in the file.** `graph.json` carries
`built_at_commit`; it existed and nobody read it.

⚠️ **`git diff <built> HEAD -- src tools docs`, never `built != HEAD`.** A
commit comparison fails after *every* commit, including one that touched only
a handoff; the diff fails only when something the index describes has actually
moved.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

#: The generated index directory, in every repository this project touches.
INDEX_DIR = "graphify-out"

#: The file inside it that carries the graph and its provenance.
GRAPH_FILE = "graph.json"

#: The key `graphify` writes recording the commit the index was built at.
COMMIT_KEY = "built_at_commit"

#: ⛔ The trees an index claims to describe. A change anywhere else — a board
#: row, a handoff, a `.gitignore` — does not make the index wrong, and a
#: freshness rule that fired on one would be a rule people rebuild past
#: without reading.
DESCRIBED_TREES = ("src", "tools", "docs")

#: The three verdicts, and they are three rather than two on purpose.
FRESH = "fresh"
STALE = "stale"
#: ⚠️ *"I cannot answer"* is not *"the answer is no"*. No git on the path, or a
#: checkout that does not contain the commit the index names, are both states
#: where the honest report is that the question could not be put — and R6's
#: "fail loud" means say which, not guess.
UNVERIFIABLE = "unverifiable"


def index_path(root: Path) -> Path:
    """Where the graph would be, whether or not it is there."""
    return Path(root) / INDEX_DIR / GRAPH_FILE


def read_graph(path: Path) -> dict | None:
    """Return the decoded graph, or `None` when there is none to read.

    ⚠️ A malformed graph reads as absent rather than raising. An index is a
    local, derived, rebuildable artifact; a half-written one is a rebuild the
    reader needs to be told about, not a crash in the quality floor.
    """
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except OSError, ValueError:
        return None


def built_at_commit(graph: dict) -> str | None:
    """Return the commit the index was built at, or `None` if it does not say."""
    value = graph.get(COMMIT_KEY)
    return value if isinstance(value, str) and value else None


def _git() -> str | None:
    return shutil.which("git")


def _run(git: str, arguments: list[str], root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(  # noqa: S603 - fixed argv, no shell
        [git, *arguments],
        cwd=root,
        capture_output=True,
        text=True,
        check=False,
    )


def freshness(root: Path, commit: str | None) -> str:
    """`FRESH`, `STALE` or `UNVERIFIABLE` for an index built at `commit`.

    ⛔ **The comparison is a diff over `DESCRIBED_TREES`, not `commit != HEAD`.**
    Every commit changes `HEAD`; only some of them change what the index
    describes, and a check that fired on the rest would be rebuilt past
    reflexively — which is how a check stops being read.
    """
    if commit is None:
        return UNVERIFIABLE
    git = _git()
    if git is None:
        return UNVERIFIABLE
    known = _run(git, ["cat-file", "-e", f"{commit}^{{commit}}"], root)
    if known.returncode != 0:
        # ⚠️ Not `STALE`. The index may be perfectly current and simply built
        # in a clone this one cannot see — a shallow checkout, a fresh worktree
        # of a branch that never had it. Saying "stale" would be a verdict the
        # evidence does not support.
        return UNVERIFIABLE
    changed = _run(git, ["diff", "--quiet", commit, "HEAD", "--", *DESCRIBED_TREES], root)
    if changed.returncode == 0:
        return FRESH
    if changed.returncode == 1:
        return STALE
    return UNVERIFIABLE
