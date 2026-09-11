"""Write the rulings index, or say that the one on disk is stale.

**What it does.** `python3 -m tools.quality.rulings` regenerates
`docs/tasks/rulings-index.md` from the ruling records. `--check` writes nothing
and exits `1` when the document on disk differs from what the records say.

**How you use it.**

    python3 -m tools.quality.rulings                 # regenerate, in place
    python3 -m tools.quality.rulings --check         # exit 1 when stale
    python3 -m tools.quality.rulings --root <tree>   # explicit root

**Depends on.** `argparse`, `sys`, and this package. ⛔ Nothing else, ever: the
index must be rebuildable on a clean checkout with no network and no installs.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.quality.rulings import REBUILD_COMMAND as COMMAND
from tools.quality.rulings.derive import INDEX_PATH, entries
from tools.quality.rulings.document import text


def main(argv: list[str] | None = None) -> int:
    """Regenerate the index, or report its staleness, and return the exit code."""
    parser = argparse.ArgumentParser(prog="python3 -m tools.quality.rulings", description=__doc__)
    parser.add_argument("--root", default=".", help="repository root (default: .)")
    parser.add_argument(
        "--check",
        action="store_true",
        help="write nothing; exit 1 when the document on disk is stale",
    )
    arguments = parser.parse_args(argv)
    root = Path(arguments.root)
    document = text(root)
    target = root / INDEX_PATH
    rows = len(entries(root))
    if arguments.check:
        current = target.read_text(encoding="utf-8") if target.exists() else None
        if current == document:
            print(f"rulings index: fresh, {rows} rulings.")
            return 0
        print(f"rulings index: STALE — {rows} rulings derived. Run `{COMMAND}`.")
        return 1
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(document, encoding="utf-8")
    print(f"rulings index: written, {rows} rulings, {target.as_posix()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
