"""The doc↔code bridge — which ruling does this code implement.

**What it does.** Joins each ruling the spec defines to the code that **cites
it by name**, and counts the resulting bridge.

**How you use it.** `rulings(root)` for the rulings the spec defines;
`bridge(root, graph)` for the nodes and edges to add; `census(graph)` for the
count the tripwire compares against a floor.

**Depends on.** `re`, `pathlib`, and this package's `index`. ⛔ Never a model:
the recipe FND-02 established and proved on the corpus is **deterministic,
literal symbol occurrence**, and a bridge a reader cannot re-derive by hand is
one nobody can check.

## ⛔ What was actually wrong, and my first answer to it was wrong too

**Measured 2026-09-09** on the index rebuilt at `dc4686c`:

```text
edges                                   7749
edges joining prose to code, cross-file    6      ⛔ 0.08%
```

⚠️ **The 7.9% in circulation is a different measurement.** 510 edges have
exactly one code endpoint, but **495 of them are a docstring pointing at the
code in its own file** — that is not a bridge between layers, and counting it
is what made an unbridged graph look eight per cent bridged. Same file, same
author, same edit: the cross-file rule below is what separates the two.

⛔ **And I got the diagnosis wrong first, which is worth recording.** I
reported that `graphify path "R7 …" "assert_clean()"` fails because *there is
no `R7` node*. There is. All twenty-one are in the graph — typed `rationale`
rather than `document`, which is why a search filtered on document types found
nothing. ⭐ **The hole is edges, not endpoints**, and the first version of this
module minted twenty-one duplicate nodes on the strength of a search I had run
badly. It now **finds** them.

## ⭐ The rule, and why it is this one

**An edge joins the spec's `Rn` node to every code node whose own docstring
cites `Rn`.**

⛔ **Enumerate the legal, never the illegal.** The alternative considered and
rejected was matching backticked symbols in prose: it produced 63 edges over
24 sections and needed a stop-list of English words (`check`, `parse`, `load`)
to stay useful — an **open** set, wrong the moment it is written. A citation
is a **closed** form: `R` followed by digits, in a docstring, in a repository
whose authors already write it everywhere.

⚠️ **The bridge is only as good as the citing.** Code that implements a ruling
and does not name it stays unbridged — visibly, as a number — which is a
better failure than a heuristic that guesses.
"""

from __future__ import annotations

import ast
import re
from pathlib import Path

from tools.knowledge.index import DESCRIBED_TREES

#: Where the rulings are defined. ⛔ A **directory**, never a filename: the
#: spec is dated, and a check pinned to `2026-09-08-…` breaks silently on the
#: day somebody supersedes it.
SPEC_DIR = "docs/specs"

#: How the spec spells a ruling. ⚠️ `re.S` is load-bearing — five of the
#: twenty-one wrap onto a second line, and a line-anchored pattern finds
#: sixteen and looks like it worked.
RULING = re.compile(r"^\*\*(R\d{1,2}) — (.*?)\*\*", re.M | re.S)

#: How code cites one. Word-bounded so `R7` matches and `R7X`, `CR7` and a
#: version like `1.R7` do not.
CITATION = re.compile(r"\bR(\d{1,2})\b")

#: The relation a bridge edge carries, and the direction. ⭐ Ruling → code
#: reads as the question people actually ask: *what enforces this?*
RELATION = "implemented_by"

#: ⛔ How every artifact this module adds is identifiable afterwards. Without
#: it the census cannot tell a bridge it built from an incidental edge, and a
#: second run cannot tell what to replace.
ORIGIN = "bridge"

#: ⭐ The one closed set in this module: a node is **code** or it is prose.
#: ⛔ Listing the prose types instead would be an open set — `image` was
#: already in this graph and in nobody's list.
CODE_TYPE = "code"

#: How a ruling node identifies itself, wherever `graphify` files it.
RULING_LABEL = re.compile(r"^(R\d{1,2}) — ")


def rulings(root: Path) -> dict[str, str]:
    """`{"R7": "No personal data reaches disk or the wire"}`, from the spec.

    ⚠️ Every `.md` under `docs/specs/` is read, so superseding the spec is
    adding a file rather than editing this module.
    """
    found: dict[str, str] = {}
    for path in sorted((Path(root) / SPEC_DIR).glob("*.md")):
        for name, title in RULING.findall(path.read_text(encoding="utf-8")):
            found.setdefault(name, " ".join(title.split()).rstrip("."))
    return found


def ruling_nodes(graph: dict) -> dict[str, str]:
    """`{"R7": "<node id>"}` — the ruling nodes already in `graph`.

    ⛔ **Found, never minted.** The first version of this module created its
    own `R1`–`R21` nodes because a badly filtered search reported none; the
    graph had all twenty-one, and a duplicate endpoint is worse than a missing
    one — every query then answers twice, half-connected each time.

    ⚠️ Matched on the **label**, not on a node type: `graphify` files these as
    `rationale` today and that is its business, not this module's.
    """
    found: dict[str, str] = {}
    for node in graph.get("nodes", []):
        if node.get("_origin") == ORIGIN:
            continue
        if not str(node.get("source_file") or "").startswith(SPEC_DIR):
            continue
        match = RULING_LABEL.match(node.get("label") or "")
        if match:
            found.setdefault(match.group(1), node["id"])
    return found


def citations(root: Path) -> dict[tuple[str, int], set[str]]:
    """`{("src/studyforge/archive/scrub.py", 261): {"R7"}}` — who cites what, where.

    ⭐ **Keyed by the line a definition starts on**, because that is what a
    code node records, so a citation lands on the function that made it and
    not on its file. ⚠️ The first version of this attached a file's citations
    to every node in that file: `R7` alone reached **215** code nodes and
    **969** edges, which is a bridge so wide it answers *"what implements
    R7?"* with *"most of the tree"*.

    ⛔ Read from the source, not from the graph's node labels, which are
    truncated at eighty characters — a citation past the truncation would
    simply not exist and nothing would say so.
    """
    found: dict[tuple[str, int], set[str]] = {}
    for tree in DESCRIBED_TREES:
        directory = Path(root) / tree
        if not directory.is_dir():
            continue
        for path in sorted(directory.rglob("*.py")):
            relative = str(path.relative_to(Path(root)))
            for line, text in _docstrings(path):
                cited = {f"R{number}" for number in CITATION.findall(text)}
                if cited:
                    found.setdefault((relative, line), set()).update(cited)
    return found


def _docstrings(path: Path) -> list[tuple[int, str]]:
    """`(line, docstring)` for the module and every class and function in it.

    The module's docstring is reported at line 1 — where `graphify` puts a
    file's own node — so a module-level citation bridges the module.
    """
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"))
    except OSError, SyntaxError:
        return []
    found: list[tuple[int, str]] = []
    module_doc = ast.get_docstring(tree)
    if module_doc:
        found.append((1, module_doc))
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            text = ast.get_docstring(node)
            if text:
                found.append((node.lineno, text))
    return found


def _code_nodes(graph: dict) -> dict[tuple[str, int], list[str]]:
    """`{(source_file, line): [node id, ...]}` for every code node."""
    by_site: dict[tuple[str, int], list[str]] = {}
    for node in graph.get("nodes", []):
        location = node.get("source_location") or ""
        if node.get("file_type") == "code" and location.startswith("L"):
            key = (node["source_file"], int(location[1:]))
            by_site.setdefault(key, []).append(node["id"])
    return by_site


def bridge(root: Path, graph: dict) -> tuple[list[dict], list[dict]]:
    """Return the `(nodes, edges)` this bridge adds to `graph`.

    ⚠️ **A citation with no code node at that line adds nothing, silently by
    count rather than silently by omission** — `census` reports what landed,
    so a drift between the graph's line numbers and the tree's shows up as a
    number falling rather than as an edge nobody misses.
    """
    minted = ruling_nodes(graph)
    nodes: list[dict] = []
    by_site = _code_nodes(graph)

    edges: list[dict] = []
    for (source_file, line), cited in sorted(citations(root).items()):
        for name in sorted(cited, key=lambda value: int(value[1:])):
            for target in by_site.get((source_file, line), []):
                if name in minted:
                    edges.append(
                        {
                            "source": minted[name],
                            "target": target,
                            "relation": RELATION,
                            "confidence": "EXTRACTED",
                            "confidence_score": 1.0,
                            "weight": 1.0,
                            "source_file": source_file,
                            "source_location": f"L{line}",
                            "_origin": ORIGIN,
                        }
                    )
    return nodes, edges


def applied(root: Path, graph: dict) -> dict:
    """`graph` with the bridge applied, idempotently.

    ⭐ Everything this module added last time is removed first, so running it
    twice is running it once. ⛔ R10's argument, applied to a derived artifact:
    a pass whose second run differs from its first cannot be checked by
    re-running it.
    """
    nodes = [node for node in graph.get("nodes", []) if node.get("_origin") != ORIGIN]
    links = [link for link in graph.get("links", []) if link.get("_origin") != ORIGIN]
    added_nodes, added_links = bridge(root, {**graph, "nodes": nodes, "links": links})
    return {**graph, "nodes": nodes + added_nodes, "links": links + added_links}


def census(graph: dict) -> dict[str, int]:
    """How many edges actually join prose to code, and how many are the bridge.

    ⛔ **Cross-file, and that is the whole of the definition.** A docstring
    edge to the function it sits above is same-file by construction, and
    counting it is what let an unbridged graph report 7.9% — 495 of those 510
    edges never left their own file.
    """
    kinds = {node["id"]: node.get("file_type") for node in graph.get("nodes", [])}
    files = {node["id"]: node.get("source_file") for node in graph.get("nodes", [])}
    links = graph.get("links", [])
    bridged = 0
    ours = 0
    for link in links:
        source, target = link.get("source"), link.get("target")
        if (kinds.get(source) == CODE_TYPE) == (kinds.get(target) == CODE_TYPE):
            continue
        if files.get(source) == files.get(target):
            continue
        bridged += 1
        if link.get("_origin") == ORIGIN:
            ours += 1
    return {"edges": len(links), "bridged": bridged, "from_bridge": ours}


def unbridged_rulings(root: Path, graph: dict) -> list[str]:
    """Rulings the spec defines that the graph has no node for.

    ⚠️ Reported rather than repaired. A missing endpoint is `graphify`'s
    extraction changing shape, and inventing a replacement here is how this
    module's first version came to duplicate all twenty-one.
    """
    present = ruling_nodes(graph)
    return [name for name in rulings(root) if name not in present]
