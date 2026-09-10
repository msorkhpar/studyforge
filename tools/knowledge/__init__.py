"""R14's index, checked rather than assumed: present, current, and bridged.

**What it does.** Answers *"is there a knowledge index here and can it be
trusted?"* — and, when there is one, whether it can connect a **ruling** to
the code that enforces it.

**How you use it.** `python3 -m tools.knowledge census` and
`python3 -m tools.knowledge bridge` are the two commands the conventions
document names. `BRIDGE_FLOOR` and `REBUILD_COMMANDS` are what the tripwire in
`tools/quality/knowledge_index.py` compares against and prints.

**Depends on.** `index`, `bridge`, and the standard library. ⛔ Nothing from
`studyforge`, and ⛔ nothing from `tools.quality` — the floor imports *this*,
so an import in the other direction is the cycle that shape always is.

## ⛔ Three states, and the third is the one that had never been checked

**absent** → ⚠️ report the rebuild command and **exit 0**. A fresh clone
legitimately has none, and ⛔ a red suite on clone is hostile and gets muted,
which is how a check stops being read.

**stale** → ⛔ **FAIL.** ⭐ Worse than absent, because absence is *visible*: a
stale index answers confidently, with yesterday's tree.

**present, current, unbridged** → ⛔ **FAIL.** The worst of the three: every
green light is on and the one question that matters returns silence.

## ⭐ Why this task exists at all

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

from tools.knowledge.bridge import applied as applied_graph
from tools.knowledge.bridge import bridge, census, rulings, unbridged_rulings
from tools.knowledge.index import (
    FRESH,
    GRAPH_FILE,
    INDEX_DIR,
    STALE,
    UNVERIFIABLE,
    built_at_commit,
    freshness,
    index_path,
    read_graph,
)

#: ⛔ The floor the prose↔code census must clear — a **recorded measurement**,
#: not a target. Measured 2026-09-09 on the graph rebuilt at `dc4686c`:
#:
#:     unbridged   15 edges     ⛔ the state this refuses
#:     bridged    222 edges     ⭐ 207 of them from `tools.knowledge bridge`
#:
#: The floor sits an order of magnitude above the first and comfortably below
#: the second, so an ordinary week of edits cannot trip it and an unbridged
#: rebuild cannot pass it.
#:
#: ⚠️ **A floor, never a ceiling, and never an exact match.** Pinning 222 would
#: make every merge a failing test and teach people to edit the constant, which
#: is muting the check by another route.
BRIDGE_FLOOR = 100

#: What a reader is told to run. ⛔ Both commands, in order: rebuilding without
#: bridging produces the third state in the table above, which is the one that
#: lies.
REBUILD_COMMANDS = (
    "graphify update .",
    "python3 -m tools.knowledge bridge",
)

__all__ = [
    "BRIDGE_FLOOR",
    "FRESH",
    "GRAPH_FILE",
    "INDEX_DIR",
    "REBUILD_COMMANDS",
    "STALE",
    "UNVERIFIABLE",
    "applied_graph",
    "bridge",
    "built_at_commit",
    "census",
    "freshness",
    "index_path",
    "read_graph",
    "rulings",
    "unbridged_rulings",
]
