"""Ruling 199: every reading `corroborate` takes from the COMMIT GRAPH, in one place.

**What it does.** Resolves a release branch's merge history ONCE and answers four
questions about any branch against it: does it exist, how far is it ahead, is it an
ancestor, and ⭐ **is it TERMINAL** — which Ruling 199 defines off the graph rather
than off a merge message.

**How you use it.** `Graph.read(root, release)` once per run, then `exists`,
`ahead`, `merged`, `terminal` and `named` per branch. ⛔ **Nothing here decides a
verdict** — `corroborate` does that, and keeping the readings apart from the
decision is what lets the two shapes be PRINTED against each other.

**Depends on.** `tools.workspace.git` for the one definition of *run one git
command*. ⛔ **Nothing in `tools.quality.CHECKS` imports this, directly or
transitively** (`board.md`, ruled round 50): the floor may not shell out to git.

## ⛔ Ruling 199 — the TERMINAL predicate is shape `C`, and `A` and `B` are RECORDED AS REFUTED

⚠️ **The remedy first routed for `W110` was *MERGED ∧ 0-ahead refutes
unconditionally*.** ⛔ **It is DEAD, and the reason is measured rather than
argued:** `merged()` is `merge-base --is-ancestor`, and a branch cut AT the release
tip is an ancestor of it — ⭐ **measured at `2d0cfe7` in the `dev2` worktree, shape
`A` is true of ALL 124 local branches, `release/m0-foundations` itself and all four
live office branches included.** ⚠️ **`git branch --no-merged` is EMPTY at that
ref, which is the same reading from the other side.**

⭐ **Shape `B` — a merge subject NAMING the branch — is a CORROBORATOR and is
PRINTED, never the gate**, because the shipped `merge_of()` tested `if branch in
subject:` and ⛔ **`chore/cto-round3` therefore read terminal off
`Merge chore/cto-round39:`'s merge.** ⚠️ **A prefix, and as a predicate it is a
false-TERMINAL generator: `feat/SF-3` would be refuted by `feat/SF-30`'s merge.**

⭐ **So `terminal()` is shape `C`: is the branch's TIP a NON-FIRST PARENT of a merge
on the release branch's first-parent line.** ⛔ **Its own blind spot is NAMED rather
than hidden: a FAST-FORWARDED merge leaves no merge commit, so a genuinely spent
branch can read non-terminal** — ⚠️ **measured at `2d0cfe7`, 7 of them:
`chore/po-round18`, `chore/po-round21`, `chore/po-round22`, `feat/FND-09-sweep`,
`feat/QA-03-visual`, `feat/ruling-78-lint-notice`, `fix/W30-W31`.** ⭐ **That
failure mode is SAFE and it is the reason this shape ships: it can only MISS a
refutation, never invent one.**

⛔ **The residual risk, stated because nothing else states it:** a branch cut from
another branch's already-absorbed TIP reads terminal. ⚠️ **Such a branch is `0`
ahead of the release branch and carries nothing of its own, so refuting it is
correct — but it is the one way this predicate can surprise somebody**, and a
branch cut from the release tip cannot hit it, because the release tip is on the
FIRST-parent line by construction.

## ⛔ `W119` — what these readings DO and DO NOT license a caller to assert (Ruling 225)

⚠️ **A committed assertion may not take its POPULATION from `checkouts()` or `heads()`.**
⛔ **Both answer about the HOST**, and a test whose subject leaks out of the repository
reddens a correct commit: ⚠️ **one worktree opened on a branch absorbed many rounds ago
took a clean repository from `1 passed` to `1 FAILED`, with nothing merged.**

⭐ **And the property a caller may assert is NARROWER than the one this module's first
consumer asserted:** ⛔ **a branch carrying UNMERGED WORK must not read `terminal()`.**
⚠️ **The converse — *a live checkout never holds a terminal branch* — is FALSE, and it is
false of every worktree from the moment its branch merges until somebody retires it.**
⭐ **Ruling 225 is POINTED AT rather than paraphrased** (Ruling 195), and the predicate is
asserted over `conftest.py`'s constructed repository in `test_graph.py`.

## ⛔ The map is built with ONE git invocation, not one per merge

⚠️ **Ruling 199's own fenced command runs `git rev-list --parents -n1` once per
merge — 177 invocations at `2d0cfe7`.** ⭐ **One `log` with `%h%x09%s%x09%P` answers
the same question, the subject included**, and the two forms were COMPARED rather
than assumed: ⛔ **`diff` of the two absorbed-tip sets at `2d0cfe7` is EMPTY, 177
shas each.**
"""

from __future__ import annotations

import subprocess
from dataclasses import dataclass, field
from pathlib import Path

from tools.workspace import git

#: ⭐ The merge idiom, `Merge <branch>` then a BOUNDARY, as an EXACT branch rather than the
#: substring the shipped `merge_of()` used (Ruling 199). ⛔ `W274`: both forms merges carry read —
#: `Merge <branch>: <line>` and `Merge <branch> (<rows>): <line>` — and more branch never does.
MERGE_IDIOM = "Merge {branch}"

#: What may follow the branch in a subject that names it: a colon, a space, or nothing.
BOUNDARY = (":", " ")


@dataclass(frozen=True)
class Graph:
    """One release branch's merge history, read once and asked about many branches."""

    root: Path
    release: str
    #: ⭐ `{absorbed tip sha: the short ref of the merge that absorbed it}` — shape
    #: `C`, and it carries its OWN human-readable ref so that the gate never has to
    #: borrow one from shape `B`.
    absorbed: dict[str, str] = field(default_factory=dict)
    #: `(short ref, subject)` for every merge on the release branch's first-parent
    #: line, newest first. ⛔ Shape `B`'s whole population, and it is PRINTED.
    subjects: tuple[tuple[str, str], ...] = ()

    @classmethod
    def read(cls, root: Path, release: str) -> Graph:
        """Resolve the release branch's first-parent merge line. ⛔ ONE git command.

        ⚠️ **TAB-separated, because a merge subject contains spaces and a parent list
        does not** — and `%x09` is git's own spelling of a tab, so nothing here has
        to guess where the subject stopped.
        """
        told = git(root, "log", "--merges", "--first-parent", "--format=%h%x09%s%x09%P", release)
        absorbed: dict[str, str] = {}
        subjects: list[tuple[str, str]] = []
        for line in told.stdout.split("\n"):
            fields = line.split("\t")
            if len(fields) != 3:
                continue
            ref, subject, parents = fields
            subjects.append((ref, subject))
            # ⛔ `parents[0]` is the FIRST parent — the release line ITSELF, which is
            # never absorbed by its own merge. Shape `C` is the REST.
            for parent in parents.split()[1:]:
                absorbed.setdefault(parent, ref)
        return cls(root, release, absorbed, tuple(subjects))

    def exists(self, branch: str) -> bool:
        """Whether `refs/heads/<branch>` resolves. ⛔ Its OWN command, never a pipeline."""
        return self._git("rev-parse", "--verify", "--quiet", f"refs/heads/{branch}").returncode == 0

    def tip(self, branch: str) -> str:
        """Return the commit `branch` points at, or `""` when git cannot say."""
        result = self._git("rev-parse", "--verify", "--quiet", f"refs/heads/{branch}^{{commit}}")
        return result.stdout.strip() if result.returncode == 0 else ""

    def ahead(self, branch: str) -> int | None:
        """Count the commits on `branch` and not on the release branch; `None` if git cannot say."""
        result = self._git("rev-list", "--count", f"{self.release}..{branch}")
        return int(result.stdout.strip()) if result.returncode == 0 else None

    def merged(self, branch: str) -> bool:
        """Whether `branch` is an ancestor of the release branch. ⚠️ Equal counts, as git says."""
        return self._git("merge-base", "--is-ancestor", branch, self.release).returncode == 0

    def terminal(self, branch: str) -> str:
        """⭐ Shape `C`: the merge that ABSORBED this branch's tip, or `""`.

        ⛔ **The gate (Ruling 199).** ⚠️ A branch whose tip has MOVED past its own
        merge reads `""` here and is right to: the work continued.
        """
        return self.absorbed.get(self.tip(branch), "")

    def named(self, branch: str) -> str:
        """⭐ Shape `B`: the merge whose subject DECLARES this branch, or `""`.

        ⛔ **A corroborator that is PRINTED, never the gate** — and the match is an
        EXACT branch on `MERGE_IDIOM` then a `BOUNDARY`, because the substring form read
        `chore/cto-round3` as terminal off `Merge chore/cto-round39:`, and ⚠️ the colon-only
        prefix named no merge written `Merge <branch> (<rows>):` (`W274`).
        """
        idiom = MERGE_IDIOM.format(branch=branch)
        for ref, subject in self.subjects:
            rest = subject[len(idiom) :]
            if subject.startswith(idiom) and (not rest or rest[0] in BOUNDARY):
                return ref
        return ""

    def checkouts(self) -> dict[str, str]:
        """`{branch: checkout path}` for every live checkout, the MAIN one included.

        ⚠️ A detached checkout has no branch line and is not in this map: `detached()` reads
        it, because *"nobody is on that branch"* and *"that checkout has no branch"* are
        different answers (`W251`).
        """
        result = self._git("worktree", "list", "--porcelain")
        found: dict[str, str] = {}
        where = ""
        for line in result.stdout.split("\n"):
            if line.startswith("worktree "):
                where = line[len("worktree ") :].strip()
            elif line.startswith("branch refs/heads/"):
                found[line[len("branch refs/heads/") :].strip()] = where
        return found

    def detached(self) -> dict[str, str]:
        """`{checkout path: short head sha}` for every live checkout on NO branch (`W251`)."""
        result = self._git("worktree", "list", "--porcelain")
        found: dict[str, str] = {}
        where = head = ""
        for line in result.stdout.split("\n"):
            if line.startswith("worktree "):
                where, head = line[len("worktree ") :].strip(), ""
            elif line.startswith("HEAD "):
                head = line[len("HEAD ") :].strip()[:7]
            elif line.strip() == "detached":
                found[where] = head
        return found

    def heads(self) -> list[str]:
        """Every local branch name, in git's own order."""
        return self._git("for-each-ref", "--format=%(refname:short)", "refs/heads").stdout.split()

    def _git(self, *arguments: str) -> subprocess.CompletedProcess:
        return git(self.root, *arguments)
