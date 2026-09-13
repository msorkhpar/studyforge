"""`W168`: a reading of a trial merge declares the one fact only the trial tree has.

**What it does.** Reads the tree it is run in and asserts that its `HEAD` is the trial
merge the reviewer made. ⛔ `docker/dev/check` mounts the tree the SCRIPT sits in, never
the caller's `cwd`, so a reviewer's own wrapper run from inside a trial worktree
measures the reviewer's own tree, and that run looks exactly like a correct one
(`CTO-67/11`). ⭐ The trial merge's sha is a positive discriminator: the merge commit
was made in the trial worktree, so no other checkout is at it. Exit `0` means the
mounted tree is the trial merge. Exit `1` means it is not, and the output names the
tree's own `HEAD` as ANOTHER tree, or names a `HEAD` that is no merge commit (a merge
that made no commit leaves the trial at a sha another checkout can hold). Exit `2`
means nothing was read: the sha is not hexadecimal, or git cannot answer in the tree.
An empty reading is never the pass reading (Ruling 191).

**How you use it.** It runs INSIDE the container, first, through the trial tree's own
wrapper, and a refusal stops the run before any gate prints a figure:

    M=$(git -C "$TRIAL" rev-parse HEAD)
    cd "$TRIAL" && ./docker/dev/check sh -c 'python3 -m tools.quality.trial "$1" || exit' trial "$M"

⭐ The gates follow `|| exit` inside the same `sh -c`. The whole invocation, and its pass
condition, live in `docs/conventions/review-rubric.md` under the `W168` heading in
section 0a. `read_tree(tree, expected)` returns the `Reading` the command prints.

**Depends on.** `argparse`, `re`, `subprocess`, `sys`, `dataclasses` and `pathlib`, and
a `git` on the path. ⛔ It never calls docker: it is taken inside the container, and the
wrapper is the reviewer's to invoke. ⛔ It is not in `CHECKS` or `NOTICES`.

## ⚠️ DECLARED, NOT DECIDED (Ruling 292)

1. A checkout deliberately detached at the trial merge's sha passes. Nothing makes one.
2. Uncommitted edits in the trial tree are not read. A trial worktree is made fresh.
3. It prints shas and never a path, because a path here is a home directory (R7).
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path

#: Exit codes: `0` the trial tree, `1` refused, `2` nothing read.
PASSED, REFUSED, UNREAD = 0, 1, 2

_SHA = re.compile(r"[0-9a-f]{7,40}")
_RULE = "review-rubric.md, W168; CTO-67/11"


@dataclass(frozen=True)
class Reading:
    """What the mounted tree declared: its `HEAD`, that commit's parents, and the sha expected."""

    expected: str
    head: str = ""
    parents: tuple[str, ...] = ()
    unread: str = ""

    @property
    def verdict(self) -> int:
        """Return the exit code: the trial tree, refused, or unread when nothing was read."""
        if self.unread:
            return UNREAD
        is_trial = self.head.startswith(self.expected) and len(self.parents) >= 2
        return PASSED if is_trial else REFUSED


def _git(tree: Path, *arguments: str) -> str | None:
    """Return git's stdout for `arguments` in `tree`, or None when git cannot answer."""
    try:
        result = subprocess.run(  # noqa: S603 - fixed argv, no shell
            ["git", "-C", str(tree), *arguments],  # noqa: S607 - git from the path, by design
            capture_output=True,
            text=True,
            check=False,
        )
    except OSError:
        return None
    return result.stdout.strip() if result.returncode == 0 else None


def read_tree(tree: Path, expected: str) -> Reading:
    """Read `HEAD` and its parents in `tree`, against the trial merge's sha `expected`."""
    expected = expected.strip().lower()
    if not _SHA.fullmatch(expected):
        return Reading(expected, unread="the trial merge's sha is not 7 to 40 hex digits")
    line = _git(tree, "rev-list", "--parents", "-n", "1", "HEAD")
    if not line:
        return Reading(expected, unread="git cannot read a HEAD in the mounted tree")
    head, *parents = line.split()
    return Reading(expected, head=head, parents=tuple(parents))


def render(reading: Reading) -> list[str]:
    """Return the lines the command prints: what the tree declared, then the answer."""
    if reading.unread:
        return [f"⛔ UNREAD: {reading.unread}, so no tree was read (exit 2)"]
    lines = [
        f"mounted tree: HEAD {reading.head}, {len(reading.parents)} parent(s); "
        f"trial merge expected: {reading.expected}"
    ]
    if not reading.head.startswith(reading.expected):
        lines.append(
            f"⛔ REFUSED: the mounted tree is ANOTHER tree, at {reading.head[:12]}, and not "
            f"the trial merge {reading.expected[:12]}. Run the TRIAL tree's own wrapper ({_RULE})"
        )
    elif len(reading.parents) < 2:
        lines.append(
            f"⛔ REFUSED: HEAD {reading.head[:12]} is NOT A MERGE COMMIT, so the trial made no "
            f"commit and its sha is one another checkout can hold ({_RULE})"
        )
    else:
        merged = " + ".join(parent[:12] for parent in reading.parents)
        lines.append(f"⭐ PASSED: the mounted tree is the trial merge of {merged}")
    return lines


def main(argv: list[str] | None = None) -> int:
    """Read the tree the command runs in against the trial merge's sha, print, return the exit."""
    parser = argparse.ArgumentParser(
        prog="python3 -m tools.quality.trial",
        description="Assert the mounted tree is the trial merge, by its sha (W168).",
    )
    parser.add_argument("expected", help="the trial merge's sha, taken on the host")
    parser.add_argument("--tree", type=Path, default=Path(), help="the tree to read")
    arguments = parser.parse_args(argv)
    reading = read_tree(arguments.tree, arguments.expected)
    print("\n".join(render(reading)))
    return reading.verdict


if __name__ == "__main__":  # pragma: no cover - the CLI's one line
    sys.exit(main())
