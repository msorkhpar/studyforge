"""The board's POPULATION, printed every run before anything is reduced to a verdict.

**What it does.** Counts the register, the row files beside it and the board's
own observation table, and prints all of it with every limit beside it
(Ruling 128). ⛔ **It forbids nothing**: two of its readings exist precisely
because their gates were retired, and a bound REMOVED because its subject became
editable is replaced by a NOTICE, never by nothing (Ruling 183).

**How you use it.** `board_state(root)` is registered in `tools.quality.NOTICES`;
`rows_on_disk(root)` is the one definition of *which files sit beside the board*
and `check_board` reads it from here.

**Depends on.** `register` for the parsers and the locations, `observation` for
Ruling 189(b)'s population, and `config` for the tree. Nothing else.

## ⛔ Why this is its own module, and it is an R11 reading rather than taste

⚠️ **`tools/quality/board/__init__.py` measured 388 of 400 lines** when `W85`
landed, and the CTO left a standing condition rather than forcing an unforced
split mid-review: ⭐ **the next row that needs the room splits at the named seam —
`check_board` / `board_state`.** ⛔ **`W96` is that row**, because Ruling 189(b)
adds a third reading to the notice and a rule to the check in one commit.

⭐ **And the seam is a real one, not a line-count convenience:** the verdict half
answers *what is wrong*, and this half answers *what there was to be wrong* —
⛔ **which is the half that must never be silent, because `0 = 0` is not a pass**
(Ruling 48).
"""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

from tools.quality.board.observation import observation_reading
from tools.quality.board.register import (
    BOARD,
    BOARD_FRAME,
    BOARD_NARRATIVE_CEILING,
    BOARD_PER_ROW,
    BOARD_ROW_CEILING,
    ROWS,
    duplicates_a_state,
    is_closed,
    namings,
    narrative_bytes,
    register,
    repeats_its_naming,
    row_order,
    table_lines,
)
from tools.quality.config import read_text


def rows_on_disk(root: Path) -> dict[str, Path]:
    """`{"W96": <path>}` for every row file beside the board, in sorted order (R10)."""
    directory = root / ROWS
    if not directory.is_dir():
        return {}
    return {path.stem: path for path in sorted(directory.glob("*.md"))}


def board_state(root: Path) -> list[str]:
    """Print the population before it is reduced to a verdict (Ruling 128).

    ⛔ Where there is no board this SAYS SO rather than returning nothing: a
    silent notice about an absent register is the `0 = 0` this exists to stop
    (Ruling 48), and the honest line names who does enforce presence.

    ## ⛔ Three readings here forbid nothing, and that is what they are for

    ⭐ **`rows/`'s BYTES — Ruling 183.** ⛔ **A bound on a row file would forbid
    the thing the file exists for**, and nothing can tell *"the PO re-scoped a
    row"* from *"the PO pasted a fragment"*. ⚠️ **That retires the GATE and not
    the MEASUREMENT** — ⛔ **measured by the CTO, pinned: `rows/` inflated 112×,
    to 3.2 MB, with this line BYTE-IDENTICAL and the floor clean**, because it
    printed a COUNT.

    ⭐ **The files whose ARGUMENT IS THEIR NAMING — Ruling 186.** ⛔ **A CLOSED
    PREDICATE, not a threshold**: see `repeats_its_naming` for what it compares
    and `argument` for why the span is never the file.

    ⭐ **The OBSERVATION population — Ruling 189(b), and it is the one that can
    be legitimately `0`.** ⚠️ **Between waves nothing is in flight and nothing
    is asserted started**, so a reader must be able to tell *nothing was
    dispatched* from *nothing was read* — ⛔ **which is why the locator is named
    in the line and a board with no observation table reads `NONE FOUND` rather
    than `0 rows`** (Ruling 191(a)).

    ⛔ **A cutoff appearing in this function is the signal a gate has been
    rebuilt.** ⭐ **The contract all three readings answer to is
    `docs/conventions/board.md`**, and it is not restated here.
    """
    text = read_text(root / BOARD)
    if text is None:
        return [
            f"board: none — no {BOARD} in this checkout. This is not a failure: the floor "
            f"runs over trees that are not this repository. ⛔ In THIS repository its "
            f"absence is a build failure, and tools/tests/quality/board/test_init.py says so."
        ]
    rows = register(text)
    identifiers = {i for _n, ids, _s in rows for i in ids}
    live = [row for row in rows if not is_closed(row[2])]
    on_disk = rows_on_disk(root)
    # ⛔ Ruling 183, and `st_size` rather than a clock or an enumeration order,
    # over a SORTED population, so the reading is reproducible (R10).
    rows_bytes = sum(path.stat().st_size for path in sorted(on_disk.values()))
    # ⛔ Ruling 186(b)'s two closed predicates, over ONE declared population.
    named = namings(text)
    bodies = {name: read_text(path) or "" for name, path in on_disk.items()}
    faults = (
        ("repeat their own naming", repeats_its_naming),
        ("duplicate a state", lambda body, name: duplicates_a_state(body)),
    )
    table = table_lines(text)
    widest = max((len(line.encode()) for _n, line in table), default=0)
    return [
        f"board: {len(rows)} register rows, {len(live)} live, "
        f"{len(on_disk)} detail files in {ROWS}/ holding {rows_bytes} bytes "
        f"(no bound — Ruling 183); "
        f"{narrative_bytes(text)} bytes narrative of {BOARD_NARRATIVE_CEILING}, "
        f"widest row {widest} of {BOARD_ROW_CEILING}, "
        f"{len(text.encode())} bytes total of "
        f"{BOARD_FRAME + BOARD_PER_ROW * len(identifiers)} allowed.",
        f"row arguments in {ROWS}/ (Ruling 186, no bound): "
        + "; ".join(_fault_reading(name, bodies, named, holds) for name, holds in faults)
        + ".",
        observation_reading(text),
    ]


def _fault_reading(
    what: str,
    bodies: dict[str, str],
    named: dict[str, str],
    holds: Callable[[str, str], bool],
) -> str:
    """One of Ruling 186(b)'s clauses, as a count AND the files it names.

    ⭐ **The files, not only the count** — Ruling 184's reason, reused: a reader
    who can see WHICH row can dismiss a false positive with one `git show`.
    ⛔ Ordered by `row_order`, never by the filesystem (R10).
    """
    found = sorted(
        (n for n, body in bodies.items() if holds(body, named.get(n, ""))), key=row_order
    )
    return f"{len(found)} {what}" + (f" — {' '.join(found)}" if found else "")
