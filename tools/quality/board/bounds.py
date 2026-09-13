"""The board's three SIZE bounds — ⛔ and not one of them is a line count.

**What it does.** Measures `BOARD.md` against the three bounds that keep a register from
turning back into a document: bytes of narrative, bytes of one row, and the whole file
against ⭐ **everything its DELIMITED tables index** (`W130`).

**How you use it.** `size_findings(text)` returns the findings and is called from
`check_board`. ⛔ **It derives its own denominator from the board's own delimited
tables** rather than being handed one, so the bound and the counts it divides by cannot
drift apart.

**Depends on.** `register` for the parsers and the locations; ⭐ **`W130` adds
`observation` and `scheduled` for the two row counts the new denominator terms need**;
and `report` for the answer. ⛔ **Nothing else.** ⭐ **And it DECLARES all five size
bounds itself** — see below.

⚠️ **TWO things about this module changed with `W130` and both are stated rather than
quietly edited.** ⛔ **(1) The dependency line used to read *"`register` … and `report`.
Nothing else, EVER."*:** Ruling 271 found the allowance indexed to a population that
cannot see its own numerator, and the two counts that fix it are parsed in
`observation.py` and `scheduled.py`. ⭐ **The alternative was a THIRD parser for two
tables this package already reads, which is the defect this package exists to forbid one
layer down.** ⚠️ **Neither import can cycle: both depend on `register` and on nothing
here.**

⛔ **(2) The five bound CONSTANTS moved here from `register.py`, and they moved for a
stated reason rather than taste:** ⭐ **this module is the one named for them and the
only one that spends them, so a bound and its derivation now have ONE home** (Ruling 277:
the figure is binding wherever it is written, so it is written once). ⚠️ **`W130` doubled
their number from three to five, and `register.py` — a PARSER, whose docstring opens on
the two parsing defects it exists for — would have gone past R11's 400-line ceiling
carrying derivations for bounds it never reads.** ⛔ **The ceiling is not the argument;
it is what made an already-wrong home untenable** (Ruling 261: a ceiling, not a budget).

## ⛔ Why this is its own module, and it is a standing decision rather than taste

⚠️ **`docs/tasks/BOARD.md` carries a standing decision that the NEXT row touching
`tools/quality/board/__init__.py` SPLITS IT** — ⭐ **the same form the CTO used for
`observation.py` (`W96/3`, split by `W111`) and for the package surface itself (split by
`W96` into `notice.py`)** — ⛔ **`W100` was that row when this module was cut, and
`W129`/`W130`/`W132` are that row now: they cut `bijection.py`, the LAST arm still living
in the package surface.** ⚠️ **The seam is not a line count either: the other three arms each read
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
| `BOARD_FRAME` + `BOARD_PER_ROW` + ⭐ `BOARD_PER_OBSERVATION_ROW` +
  `BOARD_PER_SCHEDULED_ROW` | the **whole file**, against what **all three** of its
  DELIMITED tables index | a row of ANY of the three raises the allowance by more
  than it costs |

## ⛔ `W130` — the SLOPE was the defect, not the size, and the denominator now counts three things

⚠️ **MEASURED by the PO at `6c4e3d0`: `42707 of 42784`, **77** bytes of headroom,
**99.82 %** consumed — ⛔ and the round that had to record FOUR MINTS owed more than the
`4 × 224 = 896` those mints earned.** ⭐ **The register's own round could not be recorded
inside the bound that governs the register.**

⛔ **What grew was `## In flight` (+1 880 B) and `## Scheduled`, and NEITHER is a register
row.** ⚠️ **So the allowance was indexed to a population that cannot see its own
numerator** — ⭐ **which is why the obvious remedies all fail, and Ruling 271 refuses all
three by measurement: raising `BOARD_PER_ROW` rewards minting, which was never the cause;
archiving closed register lines has slope ~ZERO; raising `BOARD_NARRATIVE_CEILING` is the
same defect one bound over.**

⭐ **Both tables are DELIMITED and this package ALREADY PARSES BOTH** — `observation.py`
and `scheduled.py` — ⛔ **so the fix is a denominator term per table and never a bigger
number.** ⚠️ **The two constants, the RULE that derives them and the populations it was
measured over are below, beside `BOARD_PER_ROW`** — ⭐ **and the rule RE-DERIVES `224`
from today's register, which is what makes it a derivation rather than a preference.**

⛔ **And the evasion still fails, which is the half that had to be asserted in BOTH
directions:** ⚠️ **a data row is only counted when the table's own parser reads it, and
both parsers require a row to carry at least as many cells as their DECLARED HEADER has
roles** — ⭐ **so 320 lines of prose pasted one line per table row raise the numerator
and leave all three denominators where they were, exactly as before.** ⛔ **Only
DELIMITED rows count: an inferred population in a denominator would be the evasion with
a header on it.**

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

from tools.quality.board.observation import DELIMITED as OBSERVATION_DELIMITED
from tools.quality.board.observation import read as read_observations
from tools.quality.board.register import (
    BOARD,
    ROWS,
    narrative_bytes,
    register,
    table_lines,
)
from tools.quality.board.scheduled import read as read_schedule
from tools.quality.report import Finding

#: ⛔ Bytes of `BOARD.md` outside any table. Measured **3,811** at the split;
#: this is 2.1× that, which is room for the frame to gain a section and not
#: room for a round's narrative — ⛔ **the largest round section in the record
#: is `ROUND 35` at 1,151 lines.**
#:
#: ⚠️ **This line read *"round 33's alone was 833 lines"* and the number was
#: WRONG TWICE OVER** — round 33's section is **31** lines, and `833` was a
#: real reading from somewhere else entirely (CTO round 43's `117 files /
#: 833 lines` of findings). ⭐ **A wrong citation that is a real number
#: survives a re-read**, which is why `CTO-45/5` had to be measured rather
#: than eyeballed.
BOARD_NARRATIVE_CEILING = 8192

#: ⛔ Bytes of one table row. Measured widest **415** at the split against
#: **3,485** before it. ⭐ 600 is the project's own test-file ceiling, reused so
#: a reader has one number to remember rather than two.
BOARD_ROW_CEILING = 600

#: ⛔ The board's whole size is bounded as `BOARD_FRAME + BOARD_PER_ROW × register
#: ids` — the distinct ids, not the table lines (`W144`). ⭐ **This is the bound that has no gap**, and it exists because the
#: Ruling 140 plant found one in the other two before this shipped: 320 lines of
#: a round's narrative, pasted as one-cell table rows, moved the narrative count
#: by ZERO and tripped the width rule ONCE.
#:
#: ⚠️ Measured at the split: **23,839 B** total over **78** register rows, of
#: which the register itself is the majority — **~170 B a row**. ⭐ A ratio
#: rather than a ceiling is Ruling 149's own
#: remedy for a governor that alarms while the property improves: adding rows
#: raises the allowance by more than a row costs, so a longer backlog can never
#: trip this, and only text that indexes nothing can.
BOARD_FRAME = 14336
BOARD_PER_ROW = 224

#: ⛔ **`W130`, Ruling 271's two new denominator terms. THE RULE, and it is the same rule
#: for all three populations: a per-row term is its population's MEASURED MEAN LINE,
#: rounded UP to the next multiple of 32, plus one further 32.**
#:
#: ⭐ **Its property is a STATED, UNIFORM slope: the allowance a row earns exceeds what the
#: MEAN row of its own population costs, by between 32 and 64 bytes — for every population
#: and not just the register.**
#:
#: ⚠️ **MEASURED at `51dee3b`, role `wt/dev1`, in the pinned container; every population
#: printed in full in `docs/tasks/handoffs/W130.md`:**
#:
#: ```text
#: population              rows   mean B   ceil32   +32   the term
#: register lines, LIVE       83    169.8      192   224   BOARD_PER_ROW       (unchanged)
#: register lines, ALL       130    191.4      192   224   ⭐ the SAME answer
#: observation rows            2     97.5      128   160   BOARD_PER_OBSERVATION_ROW
#: scheduled rows              8    418.4      448   480   BOARD_PER_SCHEDULED_ROW
#: ```
#:
#: ⛔ **THAT IS WHY THE RULE IS NOT NUMEROLOGY: applied to the register it returns `224`,
#: the constant that has shipped since the split** — ⭐ **from today's mean AND from the
#: `~170 B` measured at the split itself, so the rule was validated against a figure
#: nobody chose for it** (Ruling 277: the figure is DERIVED, and written down ONCE).
#:
#: ⚠️ **The two populations are kept APART rather than averaged, because they are not one
#: population:** a scheduled row carries a TRIGGER — prose describing an event — and an
#: observation row carries three short cells. ⛔ **One constant sized for the first would
#: hand every row of the second a 4.8× gift, and a gift in a denominator is the evasion
#: this bound exists to refuse.**
BOARD_PER_OBSERVATION_ROW = 160
BOARD_PER_SCHEDULED_ROW = 480

RULE_NARRATIVE = "board-narrative"
RULE_WIDTH = "board-row-width"
RULE_SIZE = "board-size"


def allowance(text: str) -> tuple[int, int, int, int]:
    """Return `(allowed, register ids, delimited observation rows, delimited scheduled rows)`.

    ⛔ **`W130`, Ruling 271: the denominator counts the things the board actually holds**
    — ⚠️ **and all three counts are DERIVED here rather than passed in, because a count
    handed over by a caller is a second reading of the same population and the two
    disagree the moment either loop changes.**

    ⛔ **Only DELIMITED rows count, in BOTH tables.** ⭐ `observation.read` still answers
    for a board carrying no marker through Ruling 196(b)'s header RAMP, and that reading
    is right for its own purpose and WRONG in a denominator: ⚠️ **an inferred population
    here would let an ordinary five-column table declaring `Checkout` and `State` earn
    the allowance, which is the Ruling 140 evasion with a header on it.**
    ⛔ **`scheduled.read` is delimited-only by construction and has no ramp at all.**
    """
    indexed = {identifier for _number, ids, _cell in register(text) for identifier in ids}
    observed = read_observations(text)
    observations = (
        len([row for row in observed.rows if row.delimited])
        if observed.locator == OBSERVATION_DELIMITED
        else 0
    )
    scheduled = len(read_schedule(text).rows)
    allowed = (
        BOARD_FRAME
        + BOARD_PER_ROW * len(indexed)
        + BOARD_PER_OBSERVATION_ROW * observations
        + BOARD_PER_SCHEDULED_ROW * scheduled
    )
    return allowed, len(indexed), observations, scheduled


def size_findings(text: str) -> list[Finding]:
    """Measure the board against all three bounds — narrative, then whole file, then row.

    ⛔ **The denominator is DERIVED in `allowance`** — every id the register names, plus
    the rows of the two DELIMITED tables the board also holds (`W130`, Ruling 271).
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

    allowed, indexed, observations, scheduled = allowance(text)
    size = len(text.encode())
    if size > allowed:
        findings.append(
            Finding(
                BOARD,
                1,
                RULE_SIZE,
                f"{size} bytes against {allowed} allowed — {BOARD_FRAME} of frame, plus "
                f"{BOARD_PER_ROW} for each of {indexed} register ids, plus "
                f"{BOARD_PER_OBSERVATION_ROW} for each of {observations} delimited "
                f"observation rows, plus {BOARD_PER_SCHEDULED_ROW} for each of {scheduled} "
                f"delimited scheduled rows. ⛔ The board grew without indexing anything more. "
                f"⚠️ Raising a term is NOT the remedy — Ruling 271 refuses all three of the "
                f"obvious ones by measurement; see docs/conventions/board.md.",
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
