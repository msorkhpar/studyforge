"""The arm that reads the board AS A REGISTER — one argument, one home, one state.

**What it does.** Asserts the bijection between the register's live rows and the
files in `docs/tasks/rows/`, in BOTH directions; that every register row DECLARES
a state from the closed vocabulary; and that every row file carries its frame.
⭐ **And Ruling 270's one narrow exception: a CLOSED row's detail file MAY be a
REDIRECT STUB.**

**How you use it.** `bijection_findings(root, text)` returns the findings and is
called from `check_board`; `bijection_reading(root, text)` is the population it was
over, printed by `board_state` (`W161`). ⛔ **It is handed the board's text rather than reading
it**, so the four arms read one string and cannot disagree about what the file said.

**Depends on.** `register` for the parsers and the frame, `vocabulary` for the
In-flight table's subjects (moved there by `W262`, `W161/5`), `config` for
`relative`/`read_text`, and `report` for the answer. Nothing else.
⭐ **`rows_on_disk` is DEFINED here and `notice` imports it** (`W161`): the files on
disk are this arm's other half, and the notice now prints this arm's reading, so the
old direction of that import would have been a cycle.

## ⛔ Why this is its own module, and it is a STANDING DECISION rather than taste

⚠️ **`docs/tasks/BOARD.md` carries a standing decision that the NEXT row touching
`tools/quality/board/__init__.py` SPLITS IT** — ⭐ **the same form that split
`notice.py` off (`W96`), `observation.py` off (`W96/3`, by `W111`) and `bounds.py`
and `scheduled.py` off (`W100`).** ⛔ **`W129`, `W130` and `W132` are all that row,
so the split is discharged once and named here.**

⭐ **The seam is the one the package's own table already drew, and this is the arm
that had never been given a module:** ⛔ **every other arm reads the board as a
FILE (`bounds.py`), as an OBSERVATION TABLE (`contradiction.py`) or as a SCHEDULE
(`scheduled.py`); this one reads it as a REGISTER.** ⚠️ **It stayed in
`__init__.py` only because it was there first** — ⭐ **and `__init__.py` is now what
its name says: the package surface and the composition of four arms, nothing that
judges anything itself.**

## ⛔ Ruling 270 — a close REPLACES the row file with a stub, and the clause is NARROW

⚠️ **Three rules were jointly unsatisfiable and three closes stood behind the
collision:** ⛔ **Ruling 201 DEFINES a close as DELETING the row's detail file;
Rulings 106 and 174 forbid editing a frozen record; and frozen records point at
row files.** ⭐ **A close therefore had to break a pointer NO OFFICE MAY REPAIR.**

⭐ **The PO measured all four states at `6c4e3d0` and the stub wins on stage 4
against stage 3** (`rows/W129.md`): performing Ruling 201's delete left **3 FROZEN
pointers unresolved** in `BOARD-ARCHIVE.md`, while the stub leaves **2 findings
from ONE arm of ONE instrument** — this one — and **0 unresolved pointers**.

⛔ **So the clause is *a CLOSED row's detail file MAY be a stub*, and never *a file
under `rows/` may be anything*.** ⚠️ **A stub is STILL JUDGED:**

| the file | ⛔ what this arm answers |
|---|---|
| a stub whose id has a CLOSED register row | ⭐ **clean** — Ruling 270's exception |
| a FULL argument file left behind by a close | ⛔ `board-orphan` — the close did not happen |
| a stub whose id has NO register row | ⛔ `board-orphan` — the register lost it |
| a stub whose id has a LIVE register row | ⛔ `board-detail` — ⚠️ **a live argument is
  AMENDED, so it may not live in the archive**, which is what that finding's message
  has said since it was written |
| a stub with no frame phrase | ⛔ `board-frame` **and** `board-orphan`, measured |
| a stub whose archive pointer does not resolve | ⛔ the POINTER FLOOR, one instrument over |

⭐ **The predicate is CLOSED and carries NO byte threshold** (`repeats_its_naming`'s
own remedy, Ruling 186): ⛔ **a stub's ARGUMENT *is* one pointer into the archive,
rather than *contains* one.** ⚠️ **MEASURED at `51dee3b`, role `wt/dev1`: of the **83**
live row files, **50** carry an anchored `BOARD-ARCHIVE.md#` pointer somewhere and
**42** END with one** — `rows/W129.md`, `rows/W130.md` and `rows/W132.md` among them —
⭐ **so a `contains` form would have read FIFTY full argument files as stubs and
silenced `board-orphan` on exactly the files it guards.** ⛔ **I caught myself writing
*"every full argument file"* here and corrected it to the count: the shape of the
argument survives, and the number it rests on was wrong.**

⚠️ **NOTICE (`W78`) — the reading above stays TRUE OF `51dee3b`, and its three named
WITNESSES no longer inhabit it.** ⛔ `W129`, `W130` and `W132` are REDIRECT STUBS
today, so they are no longer the full argument files the claim cites them for.
⭐ **RE-TAKEN at `fc56011`, role `wt/dev1`: of the **97** live row files, **65** carry
an anchored `BOARD-ARCHIVE.md#` pointer somewhere, **59** END with one and **16** are
stubs by the predicate — so **43** FULL argument files END with an archive pointer,
and `rows/W105.md`, `rows/W106.md` and `rows/W114.md` are three that do.**
⚠️ **Annotated, never reworded** (Ruling 183's form; Ruling 97 — a measurement is
true of the ref it was taken at).

## ⚠️ What this arm deliberately does NOT assert, DECLARED rather than implied

⛔ **Nothing about a row's NAMING** — whether a naming is a good one is the PO's
judgement and check 4's job. ⭐ This arm asserts SHAPE.

⛔ **And it does not read whether a stub's pointer RESOLVES.** ⚠️ **That is
`tools/quality/pointers.py`'s reading and it stays there**: this arm would need to
open another file to answer it, and a second resolver is a second answer.

## ⛔ `W185` — A CLOSE MAY NOT GROW THE BOARD, and this is the arm that clause was owed

⭐ **The clause is `docs/conventions/board.md`'s** (PO round 59): ⛔ **a close leaves
the Detail cell exactly as it was born, and does not re-point it at an archive
anchor.** ⚠️ **An archive anchor is the row's whole NAMING slugified, so the old
edit made the board PERMANENTLY LONGER by an amount proportional to how well the row
was named** — ⛔ **`PO-58/10` measured a round overrunning `board-size` by 257 bytes
before one word of STATE was written.**

⛔ **THE CLAUSE SHIPPED WITH ONE DIRECTION ASSERTED AND ONE OWED, and this is the
owed one.** ⭐ **The *reader still lands on the argument* half was already held by
Ruling 270's exception above and by the pointer floor** — a closed row's file must
EXIST and must BE an anchored stub — ⚠️ **but NOTHING read the register CELL, so the
next close could have quietly re-pointed it and grown the board with every gate
green.**

⭐ **THE PREDICATE IS AN EQUALITY, and that is Ruling 186's and Ruling 270's own
remedy reused rather than a stricter taste:** ⛔ **a closed predicate retires a
disagreement instead of settling it.** ⚠️ **The alternative — *the cell does not
mention the archive* — is satisfied by a cell pointing anywhere at all, which is the
direction a bijection check fails toward.** ⛔ **MEASURED at `a606033`: all **87**
closed register rows already carry the born form exactly, so the equality is
inhabited by the whole population rather than by a hopeful majority.**

⚠️ **The cell is read off `register()`'s OWN line numbers** rather than by a second
walk of the `<!-- register -->` markers. ⛔ **A second walk is a second answer to
*what is a register row*, and this package already paid for that once: an inferred
boundary read an *In flight* table as four duplicate register rows.**

## ⛔ `W161` — this arm is over `W` ids ONLY, and it SAYS which population it read

⭐ **The SUBJECT VOCABULARY is `docs/conventions/board.md`'s:** a `W` id is argued in
`rows/<ID>.md`, an EPIC TASK (`NS-03`) in its EPIC — ⛔ so an epic task's row file is
`board-orphan`. ⚠️ **At `a2ae2c4` an In-flight `W` id with no register row and no file
read CLEAN; it is `board-detail` now.** ⛔ **`0 findings` over a `W`-only population is
not a claim about every row** (Ruling 48, Ruling 331), so `bijection_reading` prints it,
the epic tasks outside it, and the residue — read, never refused (`NS-01/2`).
"""

from __future__ import annotations

import posixpath
from pathlib import Path

from tools.quality.board.register import (
    ARCHIVE,
    BOARD,
    ROW_FRAME,
    ROWS,
    STATES,
    cells,
    is_closed,
    redirects_to_the_archive,
    register,
    state,
    table_lines,
)
from tools.quality.board.vocabulary import EPIC_HOME, EPIC_TASK, subjects
from tools.quality.config import read_text, relative
from tools.quality.report import Finding

RULE_DETAIL = "board-detail"
RULE_ORPHAN = "board-orphan"
RULE_DUPLICATE = "board-duplicate"
RULE_STATE = "board-state"
RULE_FRAME = "board-frame"

#: ⛔ How `ROWS` is spelled FROM THE BOARD, which is the only place a Detail cell is
#: ever written. ⭐ Derived from the two locations this package already answers for
#: rather than typed: a third spelling of `rows` is a fact with three homes, and the
#: one nobody re-measures is the one that goes stale.
ROWS_FROM_BOARD = posixpath.relpath(ROWS, posixpath.dirname(BOARD))


def rows_on_disk(root: Path) -> dict[str, Path]:
    """`{"W96": <path>}` for every row file beside the board, in sorted order (R10)."""
    directory = root / ROWS
    if not directory.is_dir():
        return {}
    return {path.stem: path for path in sorted(directory.glob("*.md"))}


def bijection_reading(root: Path, text: str) -> str:
    """Name the population `board-detail` and `board-orphan` were over (`W161`).

    ⛔ **Printed on a CLEAN run too**, because a silence over a `W`-only population
    reads as a claim about every row (Ruling 48, Ruling 331).
    """
    ids = {identifier for _n, row_ids, _cell in register(text) for identifier in row_ids}
    vocabulary = subjects(text)
    return (
        f"bijection ({RULE_DETAIL}, {RULE_ORPHAN} — `W161`) over `W` ids ONLY: "
        f"{len(ids)} register ids and {len(vocabulary.w_rows)} observation `W` ids against "
        f"{len(rows_on_disk(root))} files in {ROWS}/; epic tasks OUTSIDE it by rule, "
        f"argued in {EPIC_HOME}: {' '.join(vocabulary.epic_tasks) or 'none'}; "
        f"observation subjects in NEITHER vocabulary, read and not judged: "
        f"{' | '.join(vocabulary.unclassified) or 'none'}."
    )


def born_detail(identifier: str) -> str:
    """Return the Detail cell a row is born with — ⛔ the one `W185` says a close LEAVES.

    ⭐ **One function, called by the arm AND by its test**, so the expected cell has
    a single home. ⚠️ A test that spelled the cell out for itself would agree with a
    typo here and report nothing.
    """
    return f"[`{ROWS_FROM_BOARD}/{identifier}.md`]({ROWS_FROM_BOARD}/{identifier}.md)"


def bijection_findings(root: Path, text: str) -> list[Finding]:
    """Report every way this register has stopped being one.

    ⛔ **The bijection is asserted in BOTH directions**, and that is deliberate: a
    live row with no detail file is an argument with no home, and a detail file with
    no row is a file nobody will ever be sent to. ⭐ One of the two always survives a
    careless edit, which is exactly why the check that only looks one way is the one
    that misses.
    """
    findings: list[Finding] = []
    on_disk = rows_on_disk(root)
    bodies = {name: read_text(path) or "" for name, path in on_disk.items()}
    seen: dict[str, int] = {}
    expected: set[str] = set()
    closed: set[str] = set()
    # ⛔ `W185`: the raw line behind each register row, so the Detail cell is read at
    # `register()`'s OWN line numbers and never by a second walk of the markers.
    lines = dict(table_lines(text))

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
            # ⭐ Ruling 270: this row's file may be a REDIRECT STUB, and only this row's.
            closed.update(ids)
            # ⛔ `W185`: and its Detail cell STOPS MOVING. A close that re-points the
            # cell at an archive anchor grows the board permanently, by the length of
            # the row's own naming — see this module's docstring for the measurement.
            detail = cells(lines[number])[4].strip()
            if detail != born_detail(ids[0]):
                findings.append(
                    Finding(
                        BOARD,
                        number,
                        RULE_DETAIL,
                        f"{ids[0]} is closed and its Detail cell is {detail!r}. ⛔ A close "
                        f"LEAVES the cell as it was born — {born_detail(ids[0])!r} — and "
                        f"never re-points it"
                        f"{f' at a {ARCHIVE} anchor' if ARCHIVE in detail else ''}. "
                        f"⚠️ An archive anchor is the row's whole NAMING slugified, so "
                        f"re-pointing grows the board permanently and `board-size` pays "
                        f"for it every round after. ⭐ Ruling 270 already makes "
                        f"{ROWS}/{ids[0]}.md a REDIRECT STUB, so the reader still lands "
                        f"on the argument — in two hops, at zero cost to the register. "
                        f"See docs/conventions/board.md.",
                    )
                )
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
        elif redirects_to_the_archive(bodies[ids[0]]):
            findings.append(
                Finding(
                    relative(on_disk[ids[0]], root),
                    1,
                    RULE_DETAIL,
                    f"{ids[0]} is not closed and its detail file is a Ruling 270 REDIRECT STUB — "
                    f"its whole argument is one pointer into BOARD-ARCHIVE.md. ⛔ A live row's "
                    f"argument is AMENDED, so it may not live in the archive. ⭐ The stub is what "
                    f"a CLOSED row's file may be, and this row's state cell does not say closed.",
                )
            )

    # ⛔ `W161`: an observation `W` id owes its row file too — it read CLEAN with no
    # register row and no file. ⭐ An EPIC TASK owes none: its argument is its epic.
    for number, identifier in subjects(text).w_rows:
        if identifier not in on_disk:
            findings.append(
                Finding(
                    BOARD,
                    number,
                    RULE_DETAIL,
                    f"{identifier} is named in the In-flight table and has no "
                    f"{ROWS}/{identifier}.md. ⛔ A `W` subject's argument lives in its row "
                    f"file (the subject vocabulary, docs/conventions/board.md); only an "
                    f"EPIC TASK's lives elsewhere, in {EPIC_HOME}.",
                )
            )

    for identifier, path in on_disk.items():
        body = bodies[identifier]
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
        if identifier in expected:
            continue
        if identifier in closed and redirects_to_the_archive(body):
            # ⭐ Ruling 270, and the ONE exception this arm grants.
            continue
        findings.append(
            Finding(
                relative(path, root),
                1,
                RULE_ORPHAN,
                f"{identifier} has a detail file and no live register row. ⛔ Either the row "
                f"closed — in which case Ruling 270 replaces this file with a REDIRECT STUB "
                f"whose whole argument is one pointer into BOARD-ARCHIVE.md, and its argument "
                f"moves there — or the register lost it. ⚠️ A file still carrying its FULL "
                f"argument is a close that did not happen; see docs/conventions/board.md."
                + (
                    f" ⛔ {identifier} is an EPIC TASK (`W161`): its argument lives in "
                    f"{EPIC_HOME}, and a row file is a SECOND home for it."
                    if EPIC_TASK.fullmatch(identifier)
                    else ""
                ),
            )
        )
    return findings
