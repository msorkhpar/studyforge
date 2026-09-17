"""The board's POPULATION, printed every run before anything is reduced to a verdict.

**What it does.** Counts the register, the row files beside it and the board's
own observation table, and prints all of it with every limit beside it
(Ruling 128). ⛔ **It forbids nothing**: two of its readings exist precisely
because their gates were retired, and a bound REMOVED because its subject became
editable is replaced by a NOTICE, never by nothing (Ruling 183).

**How you use it.** `board_state(root)` is registered in `tools.quality.NOTICES`;
`rows_on_disk(root)` is the one definition of *which files sit beside the board*;
⭐ **it is defined in `bijection.py` since `W161` and re-exported from here**, so the
notice can print that arm's population without an import cycle.

**Depends on.** `register` for the parsers and the locations, ⭐ **`bounds` for the
five size bounds and `W130`'s three-term `allowance`**, `observation` for
Ruling 189(b)'s population, `scheduled` for `W100`'s, `bijection` for the files on
disk and `W161`'s population, ⭐ **`born` for `W306`'s — the row files the MINT
clause was run over, and the ones excluded from it BY NAME** — and `config` for the
tree. Nothing else.

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

from tools.quality.board.bijection import bijection_reading, rows_on_disk
from tools.quality.board.born import born_reading
from tools.quality.board.bounds import (
    BOARD_FRAME,
    BOARD_NARRATIVE_CEILING,
    BOARD_PER_OBSERVATION_ROW,
    BOARD_PER_ROW,
    BOARD_PER_SCHEDULED_ROW,
    BOARD_ROW_CEILING,
    allowance,
)
from tools.quality.board.contradiction import observation_reading
from tools.quality.board.register import (
    BOARD,
    ROWS,
    duplicates_a_state,
    is_closed,
    namings,
    narrative_bytes,
    redirects_to_the_archive,
    register,
    repeats_its_naming,
    row_order,
    table_lines,
)
from tools.quality.board.scheduled import scheduled_reading
from tools.quality.config import read_text


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

    ⭐ **And the FOURTH line, `W100`'s: the `## Scheduled` table, by state.**
    ⛔ **It prints every word of the trigger vocabulary with its count, the
    UNINHABITED ones named** — ⚠️ **`expired` was inhabited only as a trigger's
    prose and not as a STATE on the day the column landed** (Ruling 191) — ⭐ **and
    both marker numbers with their units: the lines that ARE a declaration, and the
    lines that merely MENTION the marker inside a cell** (Ruling 224).

    ⭐ **And `W306`'s line, which prints an EXEMPTION rather than a bound.** ⛔ **The
    rows Ruling 244(e)'s mint clause never bound are excluded BY NAME inside `born.py`
    and NAMED here** (Ruling 185's form) — ⚠️ **an exemption nobody prints is an
    exemption nobody re-reads, and the day its population empties, the line says so.**

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
    live = [row for row in rows if not is_closed(row[2])]
    closed_ids = {i for _n, ids, cell in rows if is_closed(cell) for i in ids}
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
    # ⛔ `W130`: the allowance's THREE terms, derived in `bounds.allowance` and printed
    # with each term's own count — ⭐ a total with one denominator hid the slope defect
    # Ruling 271 found, and a reader who cannot see which term grew cannot see it either.
    allowed, indexed, observations, scheduled = allowance(text)
    # ⭐ `W129`, Ruling 270: the stub population, PRINTED rather than bounded — the
    # clause's denominator is every CLOSED id with a file still on disk (Ruling 48).
    stubs = sorted(
        (n for n, body in bodies.items() if n in closed_ids and redirects_to_the_archive(body)),
        key=row_order,
    )
    closed_on_disk = sorted((n for n in bodies if n in closed_ids), key=row_order)
    # ⛔ `W144`: TWO populations, TWO labels. `register lines` counts table LINES and
    # `register ids` counts the distinct ID SET the allowance is indexed to, so a
    # `W17 + W19` line is one of the first and two of the second. ⭐ Neither is labelled
    # `register rows`, the phrase that named both until the numbers disagreed.
    return [
        f"board: {len(rows)} register lines, {len(live)} live, "
        f"{len(on_disk)} detail files in {ROWS}/ holding {rows_bytes} bytes "
        f"(no bound — Ruling 183); "
        f"{narrative_bytes(text)} bytes narrative of {BOARD_NARRATIVE_CEILING}, "
        f"widest row {widest} of {BOARD_ROW_CEILING}, "
        f"{len(text.encode())} bytes total of {allowed} allowed "
        f"({BOARD_FRAME} frame + {BOARD_PER_ROW}×{indexed} register ids "
        f"+ {BOARD_PER_OBSERVATION_ROW}×{observations} observation "
        f"+ {BOARD_PER_SCHEDULED_ROW}×{scheduled} scheduled).",
        f"closed rows with a detail file still in {ROWS}/ (Ruling 270, no bound): "
        f"{len(closed_on_disk)}"
        + (f" — {' '.join(closed_on_disk)}" if closed_on_disk else "")
        + f"; of those, {len(stubs)} are REDIRECT STUBS"
        + (f" — {' '.join(stubs)}" if stubs else "")
        + ".",
        f"row arguments in {ROWS}/ (Ruling 186, no bound): "
        + "; ".join(_fault_reading(name, bodies, named, holds) for name, holds in faults)
        + ".",
        bijection_reading(root, text),
        born_reading(root),
        observation_reading(text),
        scheduled_reading(text),
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
