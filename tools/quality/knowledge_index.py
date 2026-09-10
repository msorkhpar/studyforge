"""FND-07's tripwire — is there a knowledge index here, and can it be trusted.

**What it does.** Turns the three states of a local index into the floor's
answer — absence into a printed notice, staleness and an unbridged graph into
findings.

**How you use it.** `check_knowledge_index(root)` is registered in
`tools.quality.CHECKS`; `notices(root)` is registered in `NOTICES`.

**Depends on.** `tools.knowledge` for what the index says about itself, and
this package's `report`. ⛔ Never the other direction: `tools.knowledge` must
stay importable by anything, including a tree whose floor will not import.

## ⛔ Three states, and the third had never been checked

**absent** → ⚠️ report the rebuild command and **exit 0**. A fresh clone
legitimately has none, and ⛔ a red suite on clone is hostile and gets muted,
which is how a check stops being read.

**stale** → ⛔ **FAIL.** ⭐ Worse than absent, because absence is *visible*: a
stale index answers confidently, with yesterday's tree.

**present, current, unbridged** → ⛔ **FAIL.** The worst of the three: every
green light is on and the one question that matters — *which ruling does this
code implement?* — returns silence.

## ⭐ Why the task exists at all

`FND-02` was marked done for an artifact that never reached the repository.
Its acceptance — *"the graph is rebuilt at the M0 close"* — was **true in the
worktree where it ran and false everywhere else**, because `graphify-out/` is
git-ignored and ⛔ **an ignored artifact cannot travel on a branch.** Measured:
33 worktrees, 2 with a graph.

⛔ **That is not a criticism of `FND-02`**, which did the work and recorded
what it saw. The defect is that **the acceptance was unverifiable from the
repository** — so the fix is a rule and a check, never a rebuild.
"""

from __future__ import annotations

from pathlib import Path

from tools.knowledge import (
    BRIDGE_FLOOR,
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


def how_to_rebuild() -> str:
    """Return the two commands, in order, as one line a reader can paste."""
    return "; ".join(REBUILD_COMMANDS)


def notices(root: Path) -> list[str]:
    """Lines to print that are **not** failures.

    ⛔ The absent case lives here rather than in `check_knowledge_index`, and
    that separation is the whole of the first state above: a check that can
    only fail cannot tell somebody how to obtain the thing they are missing
    without also failing them for missing it.
    """
    graph = read_graph(index_path(root))
    if graph is None:
        return [
            f"knowledge index: none in this checkout. R14's budgets assume one; "
            f"build it with `{how_to_rebuild()}`. This is not a failure — a fresh "
            f"clone legitimately has no index."
        ]
    if freshness(root, built_at_commit(graph)) == UNVERIFIABLE:
        return [
            "knowledge index: present, and its freshness could not be checked — "
            "either git is not on the path or this checkout does not contain the "
            f"commit it names. Rebuild with `{how_to_rebuild()}` if in doubt."
        ]
    return []


def check_knowledge_index(root: Path) -> list[Finding]:
    """Every way the index present in `root` cannot be trusted.

    ⛔ Returns nothing when there is no index, and nothing when freshness could
    not be established. Both are reported by `notices`, and neither is a
    finding: *"I cannot answer"* must never arrive as *"the answer is no"*.
    """
    graph = read_graph(index_path(root))
    if graph is None:
        return []

    commit = built_at_commit(graph)
    verdict = freshness(root, commit)
    if verdict == STALE:
        return [_stale(commit)]
    if verdict == UNVERIFIABLE:
        return []

    counted = census(graph)
    if counted["bridged"] < BRIDGE_FLOOR:
        return [_unbridged(counted["bridged"])]
    return []


def _stale(commit: str) -> Finding:
    return Finding(
        path=WHERE,
        line=0,
        rule=RULE,
        message=(
            f"stale: built at {commit[:8]}, and src/, tools/ or docs/ has changed "
            f"since. A stale index is worse than an absent one — it answers "
            f"confidently with yesterday's tree (R14). Rebuild: {how_to_rebuild()}"
        ),
    )


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
