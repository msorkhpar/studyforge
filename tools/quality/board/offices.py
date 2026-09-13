"""`W96/5`, landed by `W125`: which checkouts are OFFICES and not rows, as data the board declares.

**What it does.** Reads the board's `<!-- offices -->` block — a table whose `Checkout`
column carries code spans — and says which of the `0`-ahead checkouts no row names are
DECLARED offices. ⛔ **It answers ABSENT or UNREADABLE instead of answering when there is no
declaration to read, and an EMPTY declaration is printed as EMPTY.**

**How you use it.** `read(text)` returns a `Declaration`. `judged(declaration, blind)` takes
`{basename: path}` for the checkouts `unclaimed.unnamed()` found invisible BY CONSTRUCTION and
returns `(the basenames still named, the one line that reports the declaration)`.

**Depends on.** `board.register` for `cells` and `normalised`, and `board.verdict` for
`tokens` and `designates` — ⭐ the board's ONE definition of a carrier span and of *this name
designates that checkout*. ⛔ **Nothing in `tools.quality.CHECKS` imports this.**

## ⛔ Why the names are DATA and never code

⚠️ **`W96/5`:** the board declared its office checkouts in PROSE, so every wave printed them
*with no judgement available*. ⛔ **Copying the names into this module would give the fact a
second home, and that copy goes stale the next time an office opens a worktree.** ⭐ **So the
declaration is a DELIMITED block like `<!-- inflight -->`**, because a population grows by a
delimiter and never by inference (`board.md`, ruled round 49).

## ⛔ What the declaration may NOT narrow

⭐ **Only the `invisible … BY CONSTRUCTION` population**: checkouts `0` ahead that no row
names, where *just dispatched* and *office checkout* are the same bytes to git (Ruling 130,
Ruling 171). ⛔ **Never the `dispatched and unnamed` gate and never the `held by no checkout,
named by no row` notice.** An office checkout carrying unmerged work is still work, and
Ruling 319 refuses a widening that empties the gate's population.

⚠️ **A declaration nobody wrote is not a declaration that nothing is an office** (Ruling
191): ABSENT and UNREADABLE take nothing off, and every checkout stays named.
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.quality.board.register import cells, normalised
from tools.quality.board.verdict import designates, tokens

OFFICES_OPEN = "<!-- offices -->"
OFFICES_CLOSE = "<!-- /offices -->"

#: ⭐ The three states a declaration can be in. ⛔ Only `DECLARED` answers.
ABSENT = "ABSENT"
UNREADABLE = "UNREADABLE"
DECLARED = "DECLARED"


@dataclass(frozen=True)
class Declaration:
    """What the board's `<!-- offices -->` block declares, INCLUDING that it did not read."""

    state: str
    entries: tuple[str, ...] = ()
    #: The line of the first declared block whose table has no `Checkout` column, else `0`.
    line: int = 0


def read(text: str) -> Declaration:
    """Return the declaration: ⛔ ABSENT with no block, UNREADABLE when a block did not parse.

    ⭐ **The marker is matched as the WHOLE LINE**, as `observation.py` and `scheduled.py`
    match theirs, so prose that MENTIONS the marker declares nothing. ⚠️ **An unclosed block
    is judged at end-of-file**, because a missing close marker must not make a declared
    block vanish.
    """
    entries: list[str] = []
    declared, unreadable, opened = False, 0, 0
    column: int | None = None
    header = False
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if stripped in (OFFICES_OPEN, OFFICES_CLOSE):
            if opened and column is None and not unreadable:
                unreadable = opened
            opened = number if stripped == OFFICES_OPEN else 0
            declared = declared or bool(opened)
            column, header = None, False
            continue
        if not opened or not line.startswith("|"):
            continue
        row = cells(line)
        if not header:
            header = True
            found = [index for index, cell in enumerate(row) if "checkout" in normalised(cell)]
            column = found[0] if found else None
            continue
        if column is None or len(row) <= column:
            continue
        for name in tokens(row[column]):
            if name not in entries:
                entries.append(name)
    if opened and column is None and not unreadable:
        unreadable = opened
    if not declared:
        return Declaration(ABSENT)
    if unreadable:
        return Declaration(UNREADABLE, tuple(entries), unreadable)
    return Declaration(DECLARED, tuple(entries))


def judged(declaration: Declaration, blind: dict[str, str]) -> tuple[list[str], str]:
    """Split the invisible population by the declaration, and return the line reporting it.

    ⛔ **Only a DECLARED block with entries takes anything off.** ABSENT, UNREADABLE and EMPTY
    return the whole population, so a missing declaration can never make the line above
    read clean.

    ⚠️ **This line carries no other line's anchor** — not `BY CONSTRUCTION`, not `dispatched
    and`, not `held by no checkout` — because `W170`'s note records a decoy anchor choosing
    the wrong line from this instrument's own output.
    """
    label = f"  office checkouts ({OFFICES_OPEN}):"
    everyone = sorted(blind)
    if declaration.state == ABSENT:
        return everyone, (
            f"{label} ABSENT — this board declares no such block, so which checkouts on the "
            f"line above are offices and not rows is NOT ANSWERED (`W96/5`). ⛔ Not a clean "
            f"answer: every one of them stays named there."
        )
    if declaration.state == UNREADABLE:
        return everyone, (
            f"{label} UNREADABLE — the block at line {declaration.line} has no `Checkout` "
            f"column, so this is NOT ANSWERED and every checkout stays named on the line "
            f"above. ⛔ A declared block that did not read is not an empty one."
        )
    if not declaration.entries:
        return everyone, (
            f"{label} DECLARED and EMPTY — no entry, so nothing on the line above is taken "
            f"off. ⚠️ An empty declaration is not a clean answer."
        )
    entries = declaration.entries
    offices = sorted(n for n, where in blind.items() if any(designates(e, where) for e in entries))
    unmatched = [e for e in entries if not any(designates(e, where) for where in blind.values())]
    return [name for name in everyone if name not in offices], (
        f"{label} DECLARED with {len(entries)} entries; taken off the line above "
        f"({len(offices)}): {' '.join(offices) or 'none.'} — entries matching none of those "
        f"checkouts: {' '.join(unmatched) or 'none.'} ⛔ The declaration narrows THAT line "
        f"alone, never the gate."
    )
