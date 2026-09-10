"""FND-07's tripwire — is there a knowledge index here, and can it be trusted.

**What it does.** Turns the state of a local index into **one line the floor
always prints** — `none`, `unverifiable`, `stale` or `fresh`, with the commit
it was built at — and into a finding only where the answer does not depend on
`graphify-out/` at all.

**How you use it.** `verdict(root)` is the word; `notices(root)` is the line,
registered in `tools.quality.NOTICES`; `check_knowledge_index(root)` is
registered in `CHECKS`.

**Depends on.** `tools.knowledge` for what the index says about itself, and
this package's `report`. ⛔ Never the other direction: `tools.knowledge` must
stay importable by anything, including a tree whose floor will not import.

## ⛔ Ruling 96, part 2 — `stale` is a NOTICE, and the notice is load-bearing by QUOTATION

⚠️ **`stale` used to be a `Finding`, and the argument for that was correct as
far as it went:** *"worse than absent, because absence is visible — a stale
index answers confidently, with yesterday's tree."* ⛔ **What it could not
answer is Ruling 80:** `graphify-out/` is git-ignored, so the same commit read
**clean** on a fresh clone and **exit 1** on a machine that had built an index.
⭐ **A verdict that depends on untracked state is a report on the reviewer's
disk, not on the commit.**

⛔ **So the exit code goes and the sentence stays**, carried by the mechanism
this project already uses to make a line load-bearing: ⭐ **the review rubric
requires the index line to be QUOTED, beside the lint line (Ruling 79).** ⚠️ An
exit code makes the machine refuse; a quoted line makes the reviewer
accountable — ⛔ **and only the second survives `graphify-out/` being
untracked**, which is why this is not the weaker half of a trade.

⭐ **That is why `notices` returns a line in all four states**, including
`fresh`. A reviewer cannot quote a verdict a tool declines to print, and a
vocabulary with a silent member is one a reader fills in from memory.

## ⭐ Why the task exists at all

`FND-02` was marked done for an artifact that never reached the repository.
Its acceptance — *"the graph is rebuilt at the M0 close"* — was **true in the
worktree where it ran and false everywhere else**, because `graphify-out/` is
git-ignored and ⛔ **an ignored artifact cannot travel on a branch.** Measured:
33 worktrees, 2 with a graph.

⛔ **That is not a criticism of `FND-02`**, which did the work and recorded
what it saw. The defect is that **the acceptance was unverifiable from the
repository** — so the fix is a rule and a line, never a rebuild.
"""

from __future__ import annotations

from pathlib import Path

from tools.knowledge import (
    BRIDGE_FLOOR,
    FRESH,
    GRAPH_FILE,
    INDEX_DIR,
    REBUILD_COMMANDS,
    STALE,
    UNVERIFIABLE,
    built_at_commit,
    census,
    freshness,
    index_path,
    read_graph,
)
from tools.quality.report import Finding

#: The rule name every finding here carries.
RULE = "index"

#: Where a finding points. ⛔ Repo-relative: an absolute path in a build log
#: carries the user's home directory (R7).
WHERE = f"{INDEX_DIR}/{GRAPH_FILE}"

#: ⛔ The fourth word in the rubric's index-line vocabulary, and it lives here
#: rather than beside `FRESH`/`STALE`/`UNVERIFIABLE`: absence is a state of the
#: **checkout**, not a verdict about an index, and `freshness()` is right to
#: have three answers rather than four.
ABSENT = "none"

#: ⛔ Every line this module prints opens with it, so a reviewer can find the
#: line to quote with `grep`, and `W39`'s rubric clause can name that grep.
PREFIX = "knowledge index: "

#: The commit is quoted short. ⚠️ The rubric asks for the built-at commit, and
#: a full object name in a review line is noise nobody diffs.
ABBREVIATED = 8


def how_to_rebuild() -> str:
    """Return the two commands, in order, as one line a reader can paste."""
    return "; ".join(REBUILD_COMMANDS)


def verdict(root: Path) -> str:
    """`ABSENT`, `UNVERIFIABLE`, `STALE` or `FRESH` for the index in `root`.

    ⭐ The rubric's four-state vocabulary, single-sourced. A malformed graph
    reads as `ABSENT`, because a half-written local artifact is a rebuild the
    reader needs to be told about, not a fourth state to reason about.
    """
    return _verdict(root, read_graph(index_path(root)))


def _verdict(root: Path, graph: dict | None) -> str:
    """`verdict`, for a caller that has already read the graph."""
    if graph is None:
        return ABSENT
    return freshness(root, built_at_commit(graph))


def notices(root: Path) -> list[str]:
    """Return the one line the floor prints about the index. ⛔ Never a failure.

    ⛔ **All four states print**, `fresh` included — see the module docstring.
    The line is the review's evidence (Ruling 79's clause), and a state the
    tool declines to print is a state the reviewer supplies from memory.
    """
    graph = read_graph(index_path(root))
    if graph is None:
        return [
            f"{PREFIX}{ABSENT} — none in this checkout. R14's budgets assume one; "
            f"build it with `{how_to_rebuild()}`. This is not a failure — a fresh "
            f"clone legitimately has no index."
        ]
    commit = built_at_commit(graph)
    said = _verdict(root, graph)
    if said == UNVERIFIABLE:
        return [
            f"{PREFIX}{UNVERIFIABLE} — present, and its freshness could not be checked "
            "— either git is not on the path or this checkout does not contain the "
            f"commit it names. Rebuild with `{how_to_rebuild()}` if in doubt."
        ]
    at = _at(commit)
    if said == STALE:
        return [
            f"{PREFIX}{STALE} — {at}, and src/, tools/ or docs/ has changed since "
            "(the board, its archive and the handoffs excluded). A stale index is "
            "worse than an absent one — it answers confidently with yesterday's "
            f"tree (R14). ⛔ Not a failure, and not a licence: Ruling 96 requires "
            f"this line in the review. Rebuild: {how_to_rebuild()}"
        ]
    return [f"{PREFIX}{FRESH} — {at}, and nothing it describes has moved since."]


def _at(commit: str | None) -> str:
    """`built at <commit>`, abbreviated, or an honest sentence when it does not say."""
    if commit is None:
        return "built at an unrecorded commit"
    return f"built at {commit[:ABBREVIATED]}"


def check_knowledge_index(root: Path) -> list[Finding]:
    """Every untrustworthy index whose verdict does not depend on `graphify-out/`.

    ⛔ Returns nothing when there is no index, nothing when freshness could not
    be established, and — since Ruling 96 — nothing when it is stale. All three
    are reported by `notices`: *"I cannot answer"* must never arrive as *"the
    answer is no"*, and neither may *"your disk is behind"*.

    ⚠️ A stale index is not censused. ⭐ That is not new — `STALE` short-circuited
    the census before this change too — and it is right: a bridge count taken
    from yesterday's graph is a claim about yesterday's tree.
    """
    graph = read_graph(index_path(root))
    if graph is None:
        return []

    if _verdict(root, graph) != FRESH:
        return []

    counted = census(graph)
    if counted["bridged"] < BRIDGE_FLOOR:
        return [_unbridged(counted["bridged"])]
    return []


def _unbridged(bridged: int) -> Finding:
    return Finding(
        path=WHERE,
        line=0,
        rule=RULE,
        message=(
            f"unbridged: {bridged} edge(s) join prose to code across files, below "
            f"the recorded floor of {BRIDGE_FLOOR}. Present, current and unbridged "
            f"is the worst of the three states — every green light is on and "
            f"'which ruling does this code implement?' returns silence. "
            f"Bridge it: {REBUILD_COMMANDS[1]}"
        ),
    )
