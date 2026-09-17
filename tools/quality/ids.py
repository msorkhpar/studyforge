"""Ruling 218's MULTI-ID CELL — ⛔ ONE grammar, ONE home, read the same by every instrument.

**What it does.** Answers two questions about a cell that may name several rows:
which `W` row ids it names, and which PARTS it names at all. ⛔ **It is the one
home for that spelling** (`W192`): three instruments read a multi-id cell and NO
TWO AGREED, so a comma-form cell silently observed the WRONG ROW with exit `0`.

**How you use it.** `row_ids(cell)` for the row ids a board cell names, in the
order the cell names them. `parts(cell)` for every part it names whatever the
part's shape, which is what a reader that must REFUSE an unknown id wants.
`is_row_id` and `order` for the SHAPE itself.

**Depends on.** `re`. ⛔ **Nothing else, ever.** ⭐ It is read by
`tools/quality/board/register.py` and by `tools/quality/handoffs/__init__.py`,
and a grammar importing either of those would have to be imported by the other.

## ⛔ THE GRAMMAR, AND IT IS DECLARED RATHER THAN INFERRED

⭐ **A cell naming several rows separates them with `+` or `,`.** Markup is not
part of an id, and the order the cell writes them in is the order they come back
in. ⛔ **The DECLARATION is a convention's** — `docs/conventions/board.md`, beside
what a register row may carry — ⭐ **and this module is its INSTRUMENT.** ⚠️ The
two are not two spellings of it: the convention says what the grammar is, and
nothing else in `tools/` respells it.

## ⛔ THE DEFECT, AND WHY IT SURVIVED BEING WRITTEN DOWN

⚠️ **Measured at `35bf14e` and re-measured at `19c7224`, role `wt/dev1`, HOST:**

```text
`W14` + `W18`     parses as TWO ids     ⭐ the form the board happens to use
`W20`, `W21`      parses as ONE id      ⛔ and it takes the LAST
```

⛔ **Not the second-best row and not no row — the WRONG one, with no notice and
exit `0`.** ⚠️ **And the handoff reader was the exact INVERSE**: it split on the
comma alone, so `W188 + W183` was ONE id there while the title check demanded
that very spelling. ⭐ **Closing two rows in PO round 60 therefore required
writing BOTH spellings into one file, and no instrument could see it.**

## ⛔ WHY THE TWO READERS ASK DIFFERENT QUESTIONS OF THE SAME PARSE

⚠️ **A board cell's subject may be an epic task, or free text, and refusing one
re-opens `NS-01/2` as a build failure** — the subject vocabulary is the
convention's. ⭐ **So `row_ids` KEEPS the parts that are row ids and drops the
rest.** ⛔ **A handoff's `**Kind:**` line is the opposite**: every part of it
CLAIMS to be a task id, so `parts` returns all of them and the handoff package's
own `TASK_ID` refuses the ones that are not — loudly, by name.

⭐ **The two read the SAME PARTS, and that is the whole of `W192`.** ⚠️ **A
joiner this grammar does not declare is therefore never SILENTLY WRONG in either
direction:** the board's readers name every id in such a cell and never take the
last, and the handoff reader refuses the part by name.

## ⛔ `W181` — THE SHAPE IS A STATED PROPERTY, SO ORDERING IS SAFE BY CONSTRUCTION

⚠️ **`tools/quality/handoffs/existence.py` ordered a closed row by slicing the
leading character off its id and calling `int()` on the rest.** ⛔ **`int()`
RAISES, and it raised inside a FLOOR CHECK** — so a malformed id would have been
a traceback where the contract is a finding, and the whole tree would have read
as unreadable rather than one arm going red.

⭐ **Both halves are closed here, and they are not the same half.** ⛔ `order`
returns `None` instead of raising, so a caller REPORTS rather than dies; and
`row_ids` can only ever return `ROW_ID`, ⚠️ **which its mirror asserts over
planted garbage** — so the arithmetic downstream is safe BY A STATED PROPERTY
rather than by luck.
"""

from __future__ import annotations

import re

#: ⛔ **The DECLARED separators of a multi-id cell, and the whole of the grammar.**
#: ⚠️ `+` alone was what the board happened to use and `,` alone was what the
#: handoff reader split on; ⭐ **neither reader declared anything, so each was the
#: other's undeclared form.**
SEPARATORS = re.compile(r"[,+]")

#: Emphasis and code spans a cell may wear. ⛔ **Markup is not part of an id** —
#: `` `W17` `` and `**W17**` name the row `W17`, as they do everywhere else in
#: this package (`board.register.normalised` strips the same three).
_MARKUP = re.compile(r"[*`~]")

#: ⛔ **The register's own id shape, and `W181`'s STATED PROPERTY.** ⭐ It is
#: spelled ONCE, here, because it is what `order` promises and what `row_ids`
#: guarantees — ⚠️ **and a second copy of it is the defect that would make the
#: guarantee true in one module and a hope in the other.**
ROW_ID = re.compile(r"W\d+")


def parts(cell: str) -> list[str]:
    """Every part a cell names under the grammar — markup stripped, in file order.

    ⛔ **The parts, and never only the ones that parsed**: a reader whose parts
    all CLAIM to be ids needs the unreadable one so it can refuse it by name.
    ⭐ That is the handoff `**Kind:**` line, and it is why this is public.
    """
    return [part.strip() for part in SEPARATORS.split(_MARKUP.sub("", cell)) if part.strip()]


def row_ids(cell: str) -> list[str]:
    """Every `W` row id a cell names, in the order it names them.

    ⛔ **A part that is not a row id is DROPPED and never refused here** — an
    In-flight subject may be an epic task or free text, and a parser that refused
    one would re-open `NS-01/2` as a build failure. ⚠️ **A part is still read
    ACROSS its own whitespace**, so an undeclared joiner names both of its ids
    rather than the last of them: the grammar reads MORE than it declares and
    never less, which is the direction that cannot be silently wrong.
    """
    return [token for part in parts(cell) for token in part.split() if ROW_ID.fullmatch(token)]


def is_row_id(text: str) -> bool:
    """Whether `text` IS a row id — ⛔ the shape, asserted where it is parsed (`W181`)."""
    return ROW_ID.fullmatch(text) is not None


def order(identifier: str) -> int | None:
    """The number a row id is ORDERED by, or `None` when `identifier` is not one.

    ⛔ **`None`, never a raise** (`W181`): the caller is a floor check, and a
    traceback out of one takes the whole tree's reading down where the contract
    is a single arm going red. ⭐ **Reporting is the caller's** — this says only
    that it cannot order it.
    """
    return int(identifier[1:]) if is_row_id(identifier) else None
