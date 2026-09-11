"""The arm that reads the board AS A REGISTER — one argument, one home, one state.

**What it does.** Asserts the bijection between the register's live rows and the
files in `docs/tasks/rows/`, in BOTH directions; that every register row DECLARES
a state from the closed vocabulary; and that every row file carries its frame.
⭐ **And Ruling 270's one narrow exception: a CLOSED row's detail file MAY be a
REDIRECT STUB.**

**How you use it.** `bijection_findings(root, text)` returns the findings and is
called from `check_board`. ⛔ **It is handed the board's text rather than reading
it**, so the four arms read one string and cannot disagree about what the file said.

**Depends on.** `register` for the parsers and the frame, `notice` for the files on
disk, `config` for `relative`/`read_text`, and `report` for the answer. Nothing else.

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
rather than *contains* one.** ⚠️ **`contains` would have passed every full argument
file this board has**, because a row file's last line is its archive pointer —
`rows/W129.md`, `rows/W130.md` and `rows/W132.md` all end with exactly that link.

## ⚠️ What this arm deliberately does NOT assert, DECLARED rather than implied

⛔ **Nothing about a row's NAMING** — whether a naming is a good one is the PO's
judgement and check 4's job. ⭐ This arm asserts SHAPE.

⛔ **And it does not read whether a stub's pointer RESOLVES.** ⚠️ **That is
`tools/quality/pointers.py`'s reading and it stays there**: this arm would need to
open another file to answer it, and a second resolver is a second answer.
"""

from __future__ import annotations

from pathlib import Path

from tools.quality.board.notice import rows_on_disk
from tools.quality.board.register import (
    BOARD,
    ROWS,
    ROW_FRAME,
    STATES,
    is_closed,
    redirects_to_the_archive,
    register,
    state,
)
from tools.quality.config import read_text, relative
from tools.quality.report import Finding

RULE_DETAIL = "board-detail"
RULE_ORPHAN = "board-orphan"
RULE_DUPLICATE = "board-duplicate"
RULE_STATE = "board-state"
RULE_FRAME = "board-frame"


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
                f"argument is a close that did not happen; see docs/conventions/board.md.",
            )
        )
    return findings
