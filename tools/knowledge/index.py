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

## ⛔ Ruling 96, part 1 — the trees are scoped, because the sentence above was not executable

⚠️ **Measured by `PO-23/3` and it is this module contradicting itself.** The
comment on `DESCRIBED_TREES` named *"a board row, a handoff, a `.gitignore`"* as
changes that do **not** make an index wrong — and ⛔ **two of those three live
under `docs/`, which the same line then described.** ⭐ **So every merge in this
project reddened the tip by construction**: each one writes a handoff and a
board row, and nothing else needed to change.

⭐ **The fix is the comment made executable**, as `:(exclude)` pathspecs passed
to the same diff. ⛔ **It is a scoping change, not a change of intent** — the
intent was already written down, three lines above the code that ignored it.
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

#: ⛔ **THE PRINCIPLE: THE BOARD AND ITS CARRIERS.** The paths **inside** those
#: trees whose content is this project's record of its own work — the board,
#: whatever files the board is currently spelled across, and the handoffs. It is
#: the comment above made executable (Ruling 96, part 1): a board row and a
#: handoff are that comment's own first two examples and both live under `docs/`.
#:
#: ⭐ **Ruling 175 (CTO round 45) — a NEW CARRIER IS ADMITTED BY THIS PRINCIPLE,
#: never by a fresh literal argued for on its own.** ⛔ A tuple that grows one
#: entry per restructure is a list of accepted shapes, which is the form this
#: project has refused; this one is a principle with its current spellings
#: beneath it. ⚠️ **Ask of any candidate: *is this a WIDENING, or the same
#: subject under a new carrier?*** — only the second is admissible here.
#:
#: ⚠️ **`docs/tasks/rows` is the second reading of that question and it is the
#: same subject.** Every byte in it was inside `docs/tasks/BOARD.md` the day
#: before, where it was already excluded; the board was decomposed into one file
#: per live row. **Measured by the Board Architect, 2026-09-10: the exclusion
#: saves a rebuild on 21 of 40 recent commits.** ⛔ Refusing it would make this
#: check fire on material it has always excluded, purely because the material
#: moved file — which is `CTO-25/9` returning, the stale-index defect `W39` was
#: minted to kill.
#:
#: ⚠️ `.gitignore`, the comment's third example, is already outside
#: `DESCRIBED_TREES` and is not a carrier — ⛔ **it gets no entry here.**
UNDESCRIBED_PATHS = (
    "docs/tasks/handoffs",
    "docs/tasks/BOARD.md",
    "docs/tasks/BOARD-ARCHIVE.md",
    "docs/tasks/rows",
)

#: Git's pathspec magic for *remove this from a diff already scoped to
#: something wider*. ⚠️ The long form rather than `:!`, because a reader can
#: look it up in `git help glossary` and a reader cannot look up punctuation.
EXCLUDE = ":(exclude)"

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


def described_pathspecs() -> list[str]:
    """Return the trees an index describes, minus the paths inside them it does not.

    ⭐ One list rather than two arguments, so the diff and every test that
    reasons about the scope read the same thing.
    """
    return [*DESCRIBED_TREES, *(f"{EXCLUDE}{path}" for path in UNDESCRIBED_PATHS)]


def freshness(root: Path, commit: str | None) -> str:
    """`FRESH`, `STALE` or `UNVERIFIABLE` for an index built at `commit`.

    ⛔ **The comparison is a diff over `described_pathspecs()`, not
    `commit != HEAD`.** Every commit changes `HEAD`; only some of them change
    what the index describes, and a check that fired on the rest would be
    rebuilt past reflexively — which is how a check stops being read.

    ⚠️ **And *some of them* is narrower than *anything under `docs/`*.** A
    handoff and a board row are excluded by name (Ruling 96, part 1), because a
    rule that fires on every merge is the same rule people rebuild past.
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
    changed = _run(git, ["diff", "--quiet", commit, "HEAD", "--", *described_pathspecs()], root)
    if changed.returncode == 0:
        return FRESH
    if changed.returncode == 1:
        return STALE
    return UNVERIFIABLE
