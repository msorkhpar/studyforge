"""`W125`, Ruling 231(c): GENERATE the In flight table's checkout half and `n @ tip` from git.

**What it does.** Reads the board's `<!-- inflight -->` block and prints it back with two
halves re-derived from git: which checkout holds each row's branch, and how many commits that
branch is ahead of the release branch, at its tip. ⛔ **Row, Owner, State and the BRANCH half
of `Checkout` are copied VERBATIM: they are the board's ASSERTION.**

**How you use it.** `python3 -m tools.quality.board.inflight` from any checkout, then paste
the printed block over the board's. ⛔ **It prints and never writes: `docs/tasks/BOARD.md` is
the register's.** Exit `0` generated, and `2` NOT AUTHORITATIVE, `corroborate`'s third state.

**Depends on.** `board.observation` for the table, `board.verdict` for `claim`, `board.graph`
for every git answer, and `board.corroborate` for the release default and the meaning of exit
`2`. ⛔ **Nothing in `tools.quality.CHECKS` imports this.**

## ⛔ Why the WHOLE table is not generated

⭐ **`docs/tasks/handoffs/W125.md` carries the argument, and this is its outcome.** ⚠️ **Ruling
231(c): `corroborate` derives the row↔branch correspondence FROM the table, so a table
generated whole would assert git against itself** (Ruling 48). ⛔ **So the branch half stays
asserted. Every refuting arm reads that half, and nothing this module writes reaches it.**
`test_inflight.py` compares the verdicts before and after generation, over inhabited
populations, and a control that generates the branch half too turns that comparison RED.

⚠️ **A row naming NOT exactly one branch git has is copied verbatim and listed.** Generating
it would invent the correspondence, and leaving it as written keeps Ruling 189(b)'s floor
contradiction reading the cells a human wrote.

⛔ **The checkout is written as its directory BASENAME in the board's `wt/<name>` idiom,
never as a path** (R7).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.quality.board.corroborate import NOT_AUTHORITATIVE, RELEASE
from tools.quality.board.graph import Graph
from tools.quality.board.observation import (
    DELIMITED,
    INFLIGHT_CLOSE,
    INFLIGHT_OPEN,
    Observation,
    _columns,
    read,
)
from tools.quality.board.register import BOARD, cells
from tools.quality.board.verdict import claim

GENERATED = 0

#: ⭐ The board's own spelling of a checkout cell (`` `wt/dev1` ``), written about a BASENAME.
#: ⛔ `verdict.designates` is what reads it back, so the two must agree.
CHECKOUT = "`wt/{name}`"

#: The short-sha length every `@ <tip>` on this board is written with.
SHORT = 7


def generate(root: Path, release: str = RELEASE) -> tuple[list[str], int]:
    """Print the `<!-- inflight -->` block with the two git halves regenerated, and an exit code.

    ⛔ **Refuses before generating anything** when there is no board, no release branch, or a
    table that did not read: with no readable assertion there is nothing to generate FROM.
    ⚠️ **A row whose one branch git cannot count is left verbatim and makes the run exit
    `2`** (Ruling 216): a generated table missing a count is not a generated table.
    """
    board = root / BOARD
    if not board.is_file():
        return [f"inflight: no {BOARD} in this checkout — nothing to generate."], NOT_AUTHORITATIVE
    graph = Graph.read(root, release)
    if not graph.exists(release):
        return [
            f"inflight: NOT AUTHORITATIVE — no branch {release!r} in this checkout, so no count "
            f"can be generated (exit {NOT_AUTHORITATIVE})."
        ], NOT_AUTHORITATIVE
    text = board.read_text(encoding="utf-8")
    table = read(text)
    if table.unreadable or table.locator != DELIMITED:
        return [
            f"inflight: NOT AUTHORITATIVE — the board's {INFLIGHT_OPEN} block did not read "
            f"(`W111`), so there is no asserted branch to generate from. ⛔ `corroborate` "
            f"prints the reason (exit {NOT_AUTHORITATIVE})."
        ], NOT_AUTHORITATIVE
    lines = text.split("\n")
    live = graph.checkouts()
    generated: dict[int, str] = {}
    verbatim: list[str] = []
    unread: list[str] = []
    for row in table.rows:
        branches = claim(row, graph, live).branches
        if len(branches) != 1:
            verbatim.append(
                f"  left verbatim: {row.subject} names {len(branches)} branch(es) git has — a "
                f"checkout half and a count are generated only for a row naming exactly ONE, "
                f"because anything else would invent the correspondence."
            )
            continue
        count = graph.ahead(branches[0])
        if count is None:
            unread.append(
                f"  ⛔ NOT GENERATED: git could not count {release}..{branches[0]} for "
                f"{row.subject}, so the row is copied verbatim."
            )
            continue
        generated[row.line] = _row(lines, row, branches[0], count, graph, live)
    out = [
        f"inflight: generated from git against {release} — the checkout half and `n @ tip` "
        f"for {len(generated)} of {len(table.rows)} row(s). Row, Owner, State and the branch "
        f"half are the board's ASSERTION, copied verbatim (Ruling 231(c), `W125`).",
        *_block(lines, generated),
        *(verbatim or ["  rows left verbatim: none."]),
    ]
    if unread:
        out.extend(unread)
        out.append(
            f"inflight: NOT AUTHORITATIVE — exit {NOT_AUTHORITATIVE}: {len(unread)} row(s) have "
            f"no git count (Ruling 216)."
        )
        return out, NOT_AUTHORITATIVE
    return out, GENERATED


def _block(lines: list[str], generated: dict[int, str]) -> list[str]:
    """Every line from each `<!-- inflight -->` to its close, generated rows substituted."""
    out, inside = [], False
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        inside = inside or stripped == INFLIGHT_OPEN
        if inside:
            out.append(generated.get(number, line))
        if stripped == INFLIGHT_CLOSE:
            inside = False
    return out


def _row(
    lines: list[str],
    row: Observation,
    branch: str,
    count: int,
    graph: Graph,
    live: dict[str, str],
) -> str:
    """One row with ONLY its checkout cell and commits-ahead cell rewritten from git."""
    header = row.line - 1
    while header > 0 and lines[header - 1].startswith("|"):
        header -= 1
    roles = _columns(lines[header])
    assert roles is not None, "a row observation.read returned has a declaring header"
    columns = cells(lines[row.line - 1])
    where = live.get(branch)
    held = CHECKOUT.format(name=Path(where).name) if where else "none"
    columns[roles["checkout"]] = f"`{branch}` @ {held}"
    columns[roles["ahead"]] = f"{count} @ `{graph.tip(branch)[:SHORT]}`"
    return "| " + " | ".join(columns) + " |"


def main(argv: list[str] | None = None) -> int:
    """Print the generated block and return the exit code."""
    parser = argparse.ArgumentParser(description="Generate the In flight table's git halves.")
    parser.add_argument("--root", default=".", help="the checkout to read")
    parser.add_argument("--release", default=RELEASE, help="the branch counts are taken against")
    arguments = parser.parse_args(argv)
    lines, code = generate(Path(arguments.root), arguments.release)
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":  # pragma: no cover - the CLI's one line
    sys.exit(main())
