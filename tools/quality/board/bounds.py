"""The board's three SIZE bounds — ⛔ and not one of them is a line count.

**What it does.** Measures `BOARD.md` against the three bounds that keep a register from
turning back into a document: bytes of narrative, bytes of one row, and the whole file
against what its register indexes.

**How you use it.** `size_findings(text)` returns the findings and is called from
`check_board`. ⛔ **It derives its own denominator from the register** rather than being
handed one, so the bound and the count it divides by cannot drift apart.

**Depends on.** `register` for the parsers, the locations and the three ceilings, and
`report` for the answer. ⛔ **Nothing else, ever.**

## ⛔ Why this is its own module, and it is a standing decision rather than taste

⚠️ **`docs/tasks/BOARD.md` carries a standing decision that the NEXT row touching
`tools/quality/board/__init__.py` SPLITS IT** — ⭐ **the same form the CTO used for
`observation.py` (`W96/3`, split by `W111`) and for the package surface itself (split by
`W96` into `notice.py`)** — ⛔ **and `W100` is that row: it adds a fourth arm to
`check_board`.** ⚠️ **The seam is not a line count either: the other three arms each read
the board AS A REGISTER — a row's argument, a state, an observation — ⭐ and this one reads
it AS A FILE.**

## ⭐ The three bounds, and why none is a line count

⛔ **Ruling 149 retired a line-count governor on `review-rubric.md`** because it *"alarmed
seven times while the property improved seven times"* — the document was growing because
it had more to say, and the governor could not tell that from accretion. ⚠️ **A line
ceiling on the board would fail the same way**: a backlog with more rows in it is a longer
board and a *better* one.

⭐ **So all three bounds here are invariant to the number of rows.**

| Bound | What it measures | Why adding rows cannot trip it |
|---|---|---|
| `BOARD_NARRATIVE_CEILING` | bytes **not inside a table** | the frame is fixed; a new
  row is a table line and contributes **nothing** to it |
| `BOARD_ROW_CEILING` | bytes of **one table row** | a row's width is a property of
  that row, not of how many there are |
| `BOARD_FRAME` + `BOARD_PER_ROW` | the **whole file**, against what its register
  indexes | a row raises the allowance by more than it costs |

⛔ **The second bound is not decoration, and the measurement says so.** At `bfb8c8c` the
board's table rows carried **388,649 bytes** against **382,194** of prose — ⭐ **the cells
were as fat as the narrative**, and a governor watching only prose would have called that
board half-clean. ⚠️ **The widest single row was 3,485 bytes.** ⛔ **A cell that needs more
than `BOARD_ROW_CEILING` is an argument, and an argument goes behind a pointer.**

## ⚠️ The evasion this is built against (Ruling 140)

⛔ **The adversarial move is not more prose; it is prose written as a table**, so that a
narrative-blind byte count reads it as rows. ⚠️ **That plant was run against the first two
bounds before this shipped and IT GOT THROUGH:** ⛔ **320 lines of round 33's narrative,
pasted one line per table row, moved the narrative reading by ZERO and tripped the width
rule exactly ONCE.**

⭐ **`board-size` is the answer, and it is a third bound rather than a tweak to the other
two**, because the property it measures is different: not *how much prose* but *how much
file per row of state a reader gets for it*. ⛔ **Text that indexes nothing raises the
numerator and not the denominator**, which is the whole of the evasion and the whole of
the bound.

⚠️ **The other two are kept, and they are kept as DIAGNOSIS.** `board-size` says the board
is too big; ⭐ **`board-narrative` and `board-row-width` say WHERE**, and a governor that
only says *too big* is one somebody raises rather than obeys.

⛔ **And nothing here bounds `BOARD-ARCHIVE.md` or `docs/tasks/rows/`.** ⭐ **A record is
*supposed* to grow monotonically, and a bound on a row file would forbid the amendment
those files exist for** — ⚠️ **so `board_state` prints their bytes instead** (Ruling 183: a
bound removed because its subject became editable is replaced by a NOTICE, never by
nothing).
"""

from __future__ import annotations

from tools.quality.board.register import (
    BOARD,
    BOARD_FRAME,
    BOARD_NARRATIVE_CEILING,
    BOARD_PER_ROW,
    BOARD_ROW_CEILING,
    ROWS,
    narrative_bytes,
    register,
    table_lines,
)
from tools.quality.report import Finding

RULE_NARRATIVE = "board-narrative"
RULE_WIDTH = "board-row-width"
RULE_SIZE = "board-size"


def size_findings(text: str) -> list[Finding]:
    """Measure the board against all three bounds — narrative, then whole file, then row.

    ⛔ **The denominator is DERIVED here** — every id the register names — ⚠️ **because a
    count passed in from the caller is a second reading of the same population, and the
    two can disagree the moment either loop changes.**
    """
    findings: list[Finding] = []
    narrative = narrative_bytes(text)
    if narrative > BOARD_NARRATIVE_CEILING:
        findings.append(
            Finding(
                BOARD,
                1,
                RULE_NARRATIVE,
                f"{narrative} bytes of narrative against a ceiling of "
                f"{BOARD_NARRATIVE_CEILING}. The board is a register: a round's reasoning "
                f"goes to BOARD-ARCHIVE.md and a row's goes to {ROWS}/. See "
                f"docs/conventions/board.md.",
            )
        )

    indexed = {identifier for _number, ids, _cell in register(text) for identifier in ids}
    allowed = BOARD_FRAME + BOARD_PER_ROW * len(indexed)
    size = len(text.encode())
    if size > allowed:
        findings.append(
            Finding(
                BOARD,
                1,
                RULE_SIZE,
                f"{size} bytes against {allowed} allowed — {BOARD_FRAME} of frame plus "
                f"{BOARD_PER_ROW} for each of {len(indexed)} register rows. ⛔ The board grew "
                f"without indexing anything more. See docs/conventions/board.md.",
            )
        )

    for number, line in table_lines(text):
        width = len(line.encode())
        if width > BOARD_ROW_CEILING:
            findings.append(
                Finding(
                    BOARD,
                    number,
                    RULE_WIDTH,
                    f"row is {width} bytes against a ceiling of {BOARD_ROW_CEILING}. A cell "
                    f"that long is an argument, and an argument goes behind a pointer.",
                )
            )
    return findings
