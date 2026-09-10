"""The two index commands the conventions document names.

**What it does.** `census` prints how much of the local graph joins prose to
code; `bridge` adds the ruling→code edges and writes the graph back.

**How you use it.**

    python3 -m tools.knowledge census     # read-only, prints the numbers
    python3 -m tools.knowledge bridge     # rewrites graphify-out/graph.json

**Depends on.** `argparse`, `json`, and this package.

⛔ **`bridge` writes only to `graphify-out/`, which is git-ignored.** The index
is local, derived and rebuilt — never committed, never merged (R14), and the
answer to an untracked artifact is never *"track it"*.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from tools.knowledge import BRIDGE_FLOOR, applied_graph, census, index_path, read_graph


def main(argv: list[str] | None = None) -> int:
    """Run one index command and return the process exit code."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.knowledge",
        description="Report or repair the doc-to-code bridge in the local knowledge index.",
    )
    parser.add_argument("command", choices=("census", "bridge"))
    parser.add_argument("--root", type=Path, default=Path("."))
    arguments = parser.parse_args(argv)

    path = index_path(arguments.root)
    graph = read_graph(path)
    if graph is None:
        print(f"no knowledge index at {path.as_posix()}; build it first (see graphify.md)")
        return 1

    if arguments.command == "bridge":
        graph = applied_graph(arguments.root, graph)
        path.write_text(json.dumps(graph), encoding="utf-8")

    counted = census(graph)
    print(
        f"edges {counted['edges']}; prose-to-code {counted['bridged']} "
        f"({counted['from_bridge']} from the bridge); floor {BRIDGE_FLOOR}"
    )
    return 0 if counted["bridged"] >= BRIDGE_FLOOR else 1


if __name__ == "__main__":
    sys.exit(main())
