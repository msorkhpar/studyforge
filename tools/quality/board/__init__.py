"""The board is a register, and this is what keeps it one.

**What it does.** Reads `docs/tasks/BOARD.md` and the per-row files beside it in
`docs/tasks/rows/`, and fails the build on the four ways a register stops being
one: a row whose argument has no home, a detail file with no row, one id written
twice, and **narrative** — prose or a fat cell — accreting in a file every agent
in this project is told to read.

**How you use it.** `check_board(root)` is registered in `tools.quality.CHECKS`;
`board_state(root)` is registered in `NOTICES` and prints the population every
run, because a `0` with no denominator is `0 = 0` (Ruling 48).

**Depends on.** `config` for the tree and `report` for the answer. Nothing else.

## ⛔ Why this exists, and the number is the argument

⚠️ **`BOARD.md` was split once already, in round 25, for being 1,615 lines and
~180KB.** ⛔ **Twelve rounds later it was 8,545 lines and 753KB — four times the
size that triggered the split — and the paragraph announcing the split still
said the live board was "~56KB".** ⭐ **Nothing noticed, because nothing was
measuring.**

⛔ **The rule was never missing.** `docs/conventions/delivery-flow.md` has said
since it was written that *"a status change is one cell"* and that an event goes
to the Log rather than into the tables. ⚠️ **A rule recorded only in prose has
not landed** — this project's own most-repeated finding, committed by the
document that governs the board.

## ⭐ The two bounds, and why neither is a line count

⛔ **Ruling 149 retired a line-count governor on `review-rubric.md`** because it
*"alarmed seven times while the property improved seven times"* — the document
was growing because it had more to say, and the governor could not tell that
from accretion. ⚠️ **A line ceiling on this file would fail the same way**: a
backlog with more rows in it is a longer board and a *better* one.

⭐ **So both bounds here are invariant to the number of rows.**

| Bound | What it measures | Why adding rows cannot trip it |
|---|---|---|
| `BOARD_NARRATIVE_CEILING` | bytes **not inside a table** | the frame is fixed; a new
  row is a table line and contributes **nothing** to it |
| `BOARD_ROW_CEILING` | bytes of **one table row** | a row's width is a property of
  that row, not of how many there are |
| `BOARD_FRAME` + `BOARD_PER_ROW` | the **whole file**, against what its register
  indexes | a row raises the allowance by more than it costs |

⛔ **The second bound is not decoration, and the measurement says so.** At
`bfb8c8c` the board's table rows carried **388,649 bytes** against **382,194**
of prose — ⭐ **the cells were as fat as the narrative**, and a governor watching
only prose would have called that board half-clean. ⚠️ **The widest single row
was 3,485 bytes.** ⛔ **A cell that needs more than `BOARD_ROW_CEILING` is an
argument, and an argument goes behind a pointer.**

## ⚠️ The evasion this is built against (Ruling 140)

⛔ **The adversarial move is not more prose; it is prose written as a table**, so
that a narrative-blind byte count reads it as rows. ⚠️ **That plant was run
against the first two bounds before this module shipped and IT GOT THROUGH:**
⛔ **320 lines of round 33's narrative, pasted one line per table row, moved the
narrative reading by ZERO and tripped the width rule exactly ONCE.**

⭐ **`board-size` is the answer, and it is the third bound rather than a tweak to
the other two**, because the property it measures is different: not *how much
prose* but *how much file per row of state a reader gets for it*. ⛔ **Text that
indexes nothing raises the numerator and not the denominator**, which is the
whole of the evasion and the whole of the bound.

⚠️ **The other two are kept, and they are kept as DIAGNOSIS.** `board-size` says
the board is too big; ⭐ **`board-narrative` and `board-row-width` say WHERE**,
and a governor that only says *too big* is one somebody raises rather than
obeys.

## ⛔ What this deliberately does NOT assert

⚠️ **Nothing about a row's *content*.** Whether a naming is a good naming, an
owner right, or a state current, is the PO's judgement and check 4's job. ⭐ This
module asserts **shape**: that every fact has exactly one home, and that the
home a reader is told to load stays loadable.

⛔ **And nothing about `BOARD-ARCHIVE.md`'s size.** A record is *supposed* to
grow monotonically; that is what makes it a record. ⭐ **Bounding it would push
the reasoning back onto the board**, which is the defect, not the remedy.

⛔ **Nor anything about `docs/tasks/rows/`'s size**, and for a different reason:
a bound there would forbid the amendment those files exist for. ⭐ **So
`board_state` prints their bytes instead — Ruling 183: a bound REMOVED because
its subject became editable is replaced by a NOTICE, never by nothing.**
"""

from pathlib import Path

from tools.quality.board.register import (
    BOARD_FRAME,
    BOARD_NARRATIVE_CEILING,
    BOARD_PER_ROW,
    BOARD_ROW_CEILING,
    REGISTER_CLOSE,
    REGISTER_OPEN,
    ROW_FRAME,
    STATES,
    argument_bytes,
    is_closed,
    narrative_bytes,
    register,
    state,
    table_lines,
)
from tools.quality.config import read_text, relative
from tools.quality.report import Finding

#: The register itself. ⛔ One file, named here rather than discovered, because
#: a check that hunts for the board would pass on a repository that had lost it.
BOARD = "docs/tasks/BOARD.md"

#: The directory holding one file per live row.
ROWS = "docs/tasks/rows"

RULE_DETAIL = "board-detail"
RULE_ORPHAN = "board-orphan"
RULE_DUPLICATE = "board-duplicate"
RULE_NARRATIVE = "board-narrative"
RULE_WIDTH = "board-row-width"
RULE_SIZE = "board-size"
RULE_STATE = "board-state"
RULE_FRAME = "board-frame"

__all__ = [
    "BOARD",
    "BOARD_FRAME",
    "BOARD_NARRATIVE_CEILING",
    "BOARD_PER_ROW",
    "BOARD_ROW_CEILING",
    "REGISTER_CLOSE",
    "REGISTER_OPEN",
    "ROWS",
    "ROW_FRAME",
    "RULE_DETAIL",
    "RULE_DUPLICATE",
    "RULE_FRAME",
    "RULE_NARRATIVE",
    "RULE_ORPHAN",
    "RULE_SIZE",
    "RULE_STATE",
    "RULE_WIDTH",
    "STATES",
    "board_state",
    "check_board",
]


def _rows_on_disk(root: Path) -> dict[str, Path]:
    directory = root / ROWS
    if not directory.is_dir():
        return {}
    return {path.stem: path for path in sorted(directory.glob("*.md"))}


def check_board(root: Path) -> list[Finding]:
    """Report every way this board has stopped being a register.

    ⛔ **The bijection is asserted in BOTH directions**, and that is deliberate:
    a live row with no detail file is an argument with no home, and a detail
    file with no row is a file nobody will ever be sent to. ⭐ One of the two
    always survives a careless edit, which is exactly why the check that only
    looks one way is the one that misses.
    """
    text = read_text(root / BOARD)
    if text is None:
        # ⛔ Not a finding, and this is `check_knowledge_index`'s split, reused.
        # The floor runs over ARBITRARY roots — a temp tree, a corpus
        # repository — and a check that failed every tree that is not this one
        # would be asserting *which repository you are in*. ⭐ Absence is
        # reported by `board_state` and enforced by
        # `test_this_repository_has_a_board`, which is the only place that
        # knows the answer should be yes.
        return []

    findings: list[Finding] = []
    on_disk = _rows_on_disk(root)
    seen: dict[str, int] = {}
    expected: set[str] = set()

    for number, ids, cell_state in register(text):
        for identifier in ids:
            if identifier in seen:
                findings.append(
                    Finding(
                        BOARD,
                        number,
                        RULE_DUPLICATE,
                        f"{identifier} already has a register row at line {seen[identifier]}. "
                        f"An id gets ONE row; a second one is how a status disagrees with itself.",
                    )
                )
            else:
                seen[identifier] = number
        if state(cell_state) is None:
            findings.append(
                Finding(
                    BOARD,
                    number,
                    RULE_STATE,
                    f"{ids[0]}'s state cell declares no state. Begin it with one of "
                    f"{', '.join(sorted(STATES))} — ⛔ a cell that merely MENTIONS a "
                    f"state word is how a live row silently leaves the register.",
                )
            )
        if is_closed(cell_state):
            continue
        # The first id of a multi-id row owns the file; the rest ride with it.
        expected.add(ids[0])
        if ids[0] not in on_disk:
            findings.append(
                Finding(
                    BOARD,
                    number,
                    RULE_DETAIL,
                    f"{ids[0]} is not closed and has no {ROWS}/{ids[0]}.md. A live row's argument "
                    f"is AMENDED, so it may not live in the archive, and it may not live in this "
                    f"cell either.",
                )
            )

    for identifier, path in on_disk.items():
        body = read_text(path) or ""
        if not body.startswith(f"# {identifier}\n") or ROW_FRAME not in body:
            findings.append(
                Finding(
                    relative(path, root),
                    1,
                    RULE_FRAME,
                    # ⛔ `CTO-47/4`: the message used to claim the file "states
                    # which row it argues and that the naming, owner and state
                    # are the board's". ⚠️ **The predicate is TWO SUBSTRINGS and
                    # cannot read any of that.** ⭐ A weak predicate is the RIGHT
                    # trade for amendment-proofness (R3's reading, round 47) —
                    # the message must describe what is CHECKED, not what is
                    # hoped, or the next reader debugs the wrong claim.
                    f"does not begin with the line `# {identifier}`, or does not contain "
                    f"the phrase {ROW_FRAME!r}. ⚠️ Those TWO SUBSTRINGS are the whole "
                    f"predicate: it does not read what the file SAYS about its naming, "
                    f"owner or state. ⭐ That weakness is deliberate — a frame survives "
                    f"every amendment, which is what lets anything at all be required of "
                    f"a file the PO is told to edit freely. ⛔ Open `# {identifier}` and "
                    f"state that the row's naming, owner and state are the board's.",
                )
            )
        if identifier not in expected:
            findings.append(
                Finding(
                    relative(path, root),
                    1,
                    RULE_ORPHAN,
                    f"{identifier} has a detail file and no live register row. Either the row "
                    f"closed — in which case its argument belongs in BOARD-ARCHIVE.md — or the "
                    f"register lost it.",
                )
            )

    narrative = narrative_bytes(text)
    if narrative > BOARD_NARRATIVE_CEILING:
        findings.append(
            Finding(
                BOARD,
                1,
                RULE_NARRATIVE,
                f"{narrative} bytes of narrative against a ceiling of {BOARD_NARRATIVE_CEILING}. "
                f"The board is a register: a round's reasoning goes to BOARD-ARCHIVE.md and a "
                f"row's goes to {ROWS}/. See docs/conventions/board.md.",
            )
        )

    allowed = BOARD_FRAME + BOARD_PER_ROW * len(seen)
    size = len(text.encode())
    if size > allowed:
        findings.append(
            Finding(
                BOARD,
                1,
                RULE_SIZE,
                f"{size} bytes against {allowed} allowed — {BOARD_FRAME} of frame plus "
                f"{BOARD_PER_ROW} for each of {len(seen)} register rows. ⛔ The board grew "
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
                    f"row is {width} bytes against a ceiling of {BOARD_ROW_CEILING}. A cell that "
                    f"long is an argument, and an argument goes behind a pointer.",
                )
            )

    return findings


def board_state(root: Path) -> list[str]:
    """Print the population before it is reduced to a verdict (Ruling 128).

    ⛔ Where there is no board this SAYS SO rather than returning nothing: a
    silent notice about an absent register is the `0 = 0` this exists to stop
    (Ruling 48), and the honest line names who does enforce presence.

    ## ⛔ `docs/tasks/rows/` is printed with its BYTES, and that is Ruling 183

    ⚠️ **A bound on a row file would forbid the thing the file exists for** —
    appending to a live row's argument is the contract's own prescribed action,
    and nothing can tell *"the PO re-scoped a row"* from *"the PO pasted a
    fragment"*. ⭐ **That argument retires the GATE. It does not retire the
    MEASUREMENT.**

    ⛔ **Measured by the CTO at round 47, pinned: `rows/` inflated from 28,787
    bytes to 3,231,307 — 3.2 MB, 112× — and this line came back BYTE-IDENTICAL
    with the floor clean**, because it printed the files' COUNT and not one byte
    of their size. ⚠️ **That is the module's own founding defect under a new
    carrier:** `BOARD.md` was split once for being 1,615 lines, grew to four
    times that, *"and nothing noticed, because nothing was measuring."*

    ⭐ **A notice forbids nothing, cannot fire on a correct edit, and restores
    the only property whose absence caused the defect: somebody is measuring.**

    ## ⛔ The THINNEST ARGUMENT is printed beside the widest row — Ruling 186

    ⚠️ **`board-frame` is the right instrument asked the wrong question.** ⛔ A
    row file can carry its frame and argue nothing — 19 of them were measured
    doing it, three ending on a dangling *"round 22's mint block above"* that
    used to point into `BOARD.md` and now points at the frame — ⭐ **but widening
    `board-frame` to judge whether an argument is PRESENT restores exactly the
    gate Ruling 180 removed**, because nothing can tell a thin argument from one
    the PO has not finished writing.

    ⛔ **So the property re-homes to the notice, and NO THRESHOLD is chosen.**
    ⭐ **Printing the thinnest argument needs none** — ⚠️ **and if a cutoff ever
    appears here, that is the signal a gate has been rebuilt.** ⛔ **Measure the
    ARGUMENT, not the file**: see `argument_bytes`.
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
    rows_on_disk = _rows_on_disk(root)
    # ⛔ Ruling 183, and `st_size` rather than a clock or an enumeration order,
    # over a SORTED population, so the reading is reproducible (R10).
    rows_bytes = sum(path.stat().st_size for path in sorted(rows_on_disk.values()))
    # ⛔ Ruling 186, and the tuple's second member is the TIE-BREAK: the thinnest
    # argument is named deterministically, never by enumeration order (R10).
    thinnest = min(
        ((argument_bytes(read_text(path) or ""), name) for name, path in rows_on_disk.items()),
        default=None,
    )
    thin = (
        f"thinnest argument {thinnest[0]} bytes in {thinnest[1]}"
        if thinnest
        else "no row arguments"
    )
    table = table_lines(text)
    widest = max((len(line.encode()) for _n, line in table), default=0)
    return [
        f"board: {len(rows)} register rows, {len(live)} live, "
        f"{len(rows_on_disk)} detail files in {ROWS}/ holding {rows_bytes} bytes "
        f"(no bound — Ruling 183); "
        f"{narrative_bytes(text)} bytes narrative of {BOARD_NARRATIVE_CEILING}, "
        f"widest row {widest} of {BOARD_ROW_CEILING}, {thin}, "
        f"{len(text.encode())} bytes total of "
        f"{BOARD_FRAME + BOARD_PER_ROW * len(identifiers)} allowed."
    ]
