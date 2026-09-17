r"""`W167`: the arm whose population is the tasks that OWE a handoff.

**What it does.** Compares the rows `docs/tasks/BOARD.md`'s register DECLARES
CLOSED against the task handoffs that exist, and fails the build on a row that
closed without one. ⛔ **It is the half `check_handoffs` cannot reach:** that
function iterates `rglob("*.md")`, so its population is *documents that exist*
and *the handoff is missing* is unreachable by construction (`CTO-67/10` — the
reviewer measured it on a live branch shipping no handoff at all, floor green).

**How you use it.** `check_handoff_existence(root)` is registered in
`tools.quality.CHECKS` and `handoff_existence(root)` in `NOTICES`. Both are one
line over `existence_findings(root, declared)` and `existence_lines(root,
declared)`, where `declared` is the set of task ids the directory's documents
declare. ⛔ **The set is a PARAMETER rather than a second walk**, so the finding
and the denominator can never describe different readings — `pointers.py`'s
rule, applied here.

**Depends on.** `board.register` for every board reading, this package's own
surface for what a document declares, `config` for the tree, `report` for the
answer. ⛔ **Nothing else, and no `git`:** a floor check's verdict may not depend
on untracked state (Ruling 80), and a branch position is the purest untracked
state there is.

⚠️ **Why this module is imported by the floor DIRECTLY and not re-exported by
`handoffs/__init__.py`:** it reads that package's `declared_kind`, so a
re-export would be a cycle. ⭐ The direction is the useful one — the arm depends
on the contract, and the contract knows nothing about the board.

## ⛔ The denominator is the hard part, and the population the rule NAMES is not decidable

⚠️ **`agent-protocol.md` binds the obligation to DEPENDENTS** — *"A task with
dependents and no handoff is not done."* ⛔ **A dependent can be minted after the
branch is gone**, so *has dependents* is not a property of the tree at the
moment the obligation falls due: `W167` was placed at PO round 54 and the
sentence making `W64` a task with a dependent is attributed to `PO-55/2`, a
round later — ⭐ **at the moment `W64`'s handoff fell due, `W64` had no declared
dependent at all.** ⚠️ **Nor is it readable:** `**Depends on**` is an EPIC
document's field, and measured at `4b48e6d` none of `docs/tasks/rows/`'s 122
files carries it.

⭐ **So this arm reads the CONTAINING population and bounds it: a row the
register DECLARES CLOSED.** ⛔ **The close is the first TRACKED statement that
the obligation fell due**, which is what makes it readable at all — and it is
one step later than the reviewer who caught `fix/W146-observation-verdict`.
⚠️ **This does not replace that reviewer; it makes the miss REACHABLE.**

## ⛔ Why the containing population is narrowed TWICE, and both narrowings are measured

⚠️ **`closed → owes` fires on correct work, which Ruling 179 forbids.**
⭐ **Measured at `4b48e6d`, role `wt/dev3`, HOST, over this module's own
readers:** 169 register rows, **73 closed**, and **11 of the 73 have no document
declaring `**Kind:** task handoff — <that id>`** — `W4`, `W6`, `W9`, `W22`,
`W23`, `W24`, `W84`, `W102`, `W147`, `W152`, `W166`.

- ⭐ **Five are office rounds** (`W4`, `W22`, `W24`, `W84`, `W166`, owner `PO`),
  ⛔ **and an office round records in the archive as a `ruling record`** — the
  row's own *WHAT IT MUST NOT BECOME*. That narrowing is `OFFICE_OWNERS`, read
  off the board's own owner cell as DATA.
- ⭐ **Six are landed work whose repair does not exist** (`W6`, `W9`, `W23`,
  `W102`, `W147`, `W152`): writing a handoff today for a branch that finished
  days ago fabricates a record (Ruling 106), and demanding it chases the corpus
  (Ruling 193). That narrowing is `HANDOFF_OWED_FROM`, ⛔ **pinned from the
  measurement above and not from a ruling** — the same construction, in the same
  package, as `contract.LEGACY_GLOBAL_MAX`.

## ⛔ An owner nobody has seen before OWES, and that direction is chosen

⭐ **This arm exists because a check could not FIRE.** ⚠️ So where the two
directions trade off, it defaults to REACHABLE: `OFFICE_OWNERS` enumerates the
owners that owe NOTHING, and every other spelling owes. ⛔ **A new office that
genuinely records elsewhere adds one entry here, with its sentence, where a
reviewer reads it** — it does not escape by being unrecognised.

## ⚠️ What it deliberately does NOT have, and the absence is argued rather than forgotten

⛔ **There is no *this row owed nothing* escape**, so `a row with no dependents
owes nothing` is honoured only by the two narrowings above. ⚠️ **Every site
available for such a declaration today is wrong:** a closed row's argument lives
in `BOARD-ARCHIVE.md`, a frozen record (Ruling 106); a register cell carries *no
measurement, no ref other than a merge ref, and no reasoning* by the board's own
sentence; and minting a NEW declaration site is a contract change that wants the
CTO before it is written (Ruling 176's form). ⭐ **Measured to be unexercised:
of 73 closed rows, 62 shipped a handoff, 5 were office rounds, and none of the
remaining 6 is a row where writing one would have been wrong.**

⛔ **`HANDOFF_OWED_FROM` IS A PIN, NOT A KNOB.** ⚠️ Raising it to turn a red arm
green is the one move it must never be used for; the repair for a red arm is the
handoff, or not declaring the row closed.

## ⛔ `W181` — AN ID THE PIN CANNOT ORDER IS REPORTED, NEVER RAISED

⚠️ **This module ordered a closed row by slicing the leading character off its id
and calling `int()` on the rest.** ⛔ **`int()` RAISES, and it raised INSIDE A
FLOOR CHECK** — so a register id the pin could not order would have been a
traceback where the contract is a finding, and the whole tree would have read as
unreadable rather than one arm going red.

⭐ **`ids.order` returns `None` instead**, so such a row is EXCLUDED from the
owed population, REPORTED by name under `RULE_UNORDERABLE`, and NAMED in the
notice beside the populations it sits outside.

⛔ **AND THE SHAPE IS ASSERTED WHERE IT IS PARSED, which is the OTHER half and
not the same one** (`W181`'s second clause): `register.identifiers` can only ever
return `ids.ROW_ID`, so this module's arithmetic is safe BY A STATED PROPERTY
rather than by luck. ⚠️ **The consequence is that the reporting arm is
UNREACHABLE from `check_handoff_existence` on any board the parser reads** —
⭐ **which is why the judging half is `findings_for` and `lines_for`, PURE
FUNCTIONS OF THE ROWS THEY ARE HANDED** (`module-structure.md`: a gate that is
part of a contract is a pure function of its input). ⛔ **An arm asserted only
through a walk that cannot produce its input is a check that could not fire,
which is the exact defect this module exists to close.**
"""

from __future__ import annotations

from pathlib import Path

from tools.quality import config
from tools.quality.board.register import (
    BOARD,
    REGISTER_CLOSE,
    REGISTER_OPEN,
    cells,
    identifiers,
    is_closed,
)
from tools.quality.handoffs import HANDOFF_DIR, TASK_HANDOFF, declared_kind
from tools.quality.ids import ROW_ID, order
from tools.quality.report import Finding

RULE_MISSING = "handoff-missing"

#: ⛔ **`W181`: a closed register id this arm cannot ORDER against the pin.**
#: ⭐ It is a finding with the id IN it and never a traceback, and it is a rule
#: of its own because the remedy is a different one: the id is not the
#: register's shape, so no handoff can discharge it.
RULE_UNORDERABLE = "handoff-row-id"

#: ⛔ The pinned legacy bound: a row numbered at or below this is NOT held to
#: the existence contract. ⭐ **Pinned from a MEASUREMENT and not from a
#: ruling** — the highest closed register row with a non-office owner and no
#: task handoff declaring it, read at `4b48e6d` in the `wt/dev3` worktree on the
#: host: `W152`. ⛔ **Ruling 193: the corpus is never chased**, and Ruling 106
#: forbids the only other repair — a record written today about work somebody
#: else finished.
#:
#: ⛔ **A PIN, NOT A KNOB.** ⚠️ Raising it to make a firing arm quiet is the one
#: use it must never have.
HANDOFF_OWED_FROM = 152

#: ⛔ The owners whose close is an OFFICE ROUND, and what each records instead.
#: ⭐ Read off the board's own owner cell, so this is a vocabulary rather than a
#: list of exempted rows — the distinction `DOCUMENT_KINDS` already turns on.
#: ⚠️ **An owner that is not here OWES**, deliberately: the defect this arm
#: repairs is a check that could not fire.
OFFICE_OWNERS: dict[str, str] = {
    "PO": "a PO round records in `BOARD-ARCHIVE.md` and in its own `ruling record`",
    "CTO": "a CTO round records in its own `ruling record`, which owes a SCOPE instead",
}

#: The register's columns, named rather than indexed at the call site.
_ID_CELL, _OWNER_CELL, _STATE_CELL = 0, 2, 3


def declared_task_ids(root: Path) -> set[str]:
    """Every task id a document in `HANDOFF_DIR` DECLARES itself the handoff for.

    ⛔ The DECLARATION and never the filename: both are free text, and measured
    2026-09-10, 8 of the 10 documents in that directory that were not task
    handoffs already carried `— handoff` in their own title.
    """
    directory = root / HANDOFF_DIR
    ids: set[str] = set()
    if not directory.is_dir():
        return ids
    for path in sorted(directory.rglob("*.md")):
        text = config.read_text(path)
        if text is None:
            continue
        kind, declared, _line = declared_kind(text)
        if kind == TASK_HANDOFF:
            ids.update(declared)
    return ids


def closed_rows(text: str) -> list[tuple[int, str, str]]:
    """`(line number, row id, owner)` for every register row DECLARED closed.

    ⛔ Only between the register's own delimiters, and only through
    `register.cells` — a naive `split("|")` tore three register rows apart at a
    pipe inside a code span, and that defect is paid for once, there.

    ⚠️ A cell may name two ids (`W17 + W19` are one commit and one row); each is
    returned separately, because a handoff covering both DECLARES both.
    """
    rows: list[tuple[int, str, str]] = []
    inside = False
    for number, line in enumerate(text.split("\n"), 1):
        if line.strip() == REGISTER_OPEN:
            inside = True
            continue
        if line.strip() == REGISTER_CLOSE:
            inside = False
            continue
        if not inside or not line.startswith("|"):
            continue
        columns = cells(line)
        if len(columns) < 5 or not is_closed(columns[_STATE_CELL]):
            continue
        for identifier in identifiers(columns[_ID_CELL]):
            rows.append((number, identifier, columns[_OWNER_CELL]))
    return rows


def unorderable(rows: list[tuple[int, str, str]]) -> list[tuple[int, str]]:
    """`(line, id)` for every row id the pin cannot ORDER — ⛔ reported, never raised.

    ⭐ **The population the two narrowings cannot speak about**: a bound is an
    ordering, and an id outside the register's shape has no place in one.
    """
    return [(line, identifier) for line, identifier, _owner in rows if order(identifier) is None]


def owing(rows: list[tuple[int, str, str]]) -> list[tuple[int, str, str]]:
    """Return the closed rows that OWE a task handoff, after both narrowings.

    ⛔ **A row the pin cannot ORDER is EXCLUDED here and REPORTED by
    `findings_for`** (`W181`) — ⚠️ it is not silently owed and not silently
    excused, and it is never an `int()` raised out of a floor check.
    """
    return [
        row
        for row in rows
        if (number := order(row[1])) is not None
        and number > HANDOFF_OWED_FROM
        and row[2] not in OFFICE_OWNERS
    ]


def _board(root: Path) -> str | None:
    """Read the register's text, or `None` when this tree has no board at all."""
    path = root / BOARD
    return config.read_text(path) if path.is_file() else None


def findings_for(rows: list[tuple[int, str, str]], declared: set[str]) -> list[Finding]:
    """Every closed row that owes a task handoff and has none, and every id that will not order.

    ⛔ **A PURE FUNCTION OF THE ROWS IT IS HANDED**, which is what makes `W181`'s
    arm reachable at all: the parser cannot hand `check_handoff_existence` a
    malformed id, so an arm asserted only through that walk could never fire.
    """
    findings = [
        Finding(
            BOARD,
            line,
            RULE_UNORDERABLE,
            f"the register declares {identifier!r} CLOSED and it is not a row id: the "
            f"register's own shape is `{ROW_ID.pattern}` (`docs/conventions/board.md`), "
            f"and this arm ORDERS every closed row against the pinned bound "
            f"W{HANDOFF_OWED_FROM}. ⛔ Reported and never raised: an id the pin cannot "
            f"order is a FINDING with the id in it, not a traceback out of a floor check "
            f"that takes every other reading down with it. ⭐ Spell the id `W<digits>`.",
        )
        for line, identifier in unorderable(rows)
    ]
    for line, identifier, _owner in owing(rows):
        if identifier in declared:
            continue
        findings.append(
            Finding(
                BOARD,
                line,
                RULE_MISSING,
                f"the register declares {identifier} CLOSED and no document in "
                f"`docs/tasks/handoffs/` declares `**Kind:** task handoff — {identifier}`. "
                f"`agent-protocol.md`: a task with dependents and no handoff is not done. "
                f"Land the handoff, or do not declare the row closed — "
                f"never raise `HANDOFF_OWED_FROM`.",
            )
        )
    return findings


def existence_findings(root: Path, declared: set[str]) -> list[Finding]:
    """Every closed row that owes a task handoff and has none.

    ⛔ The finding is raised against `BOARD.md`, on the register row's own line,
    because the remedy is one of two things and neither is a file that exists:
    write the handoff, or stop declaring the row closed.
    """
    text = _board(root)
    return [] if text is None else findings_for(closed_rows(text), declared)


def lines_for(rows: list[tuple[int, str, str]], declared: set[str]) -> list[str]:
    """The population `rows` carry — ⛔ a pure function of them, as `findings_for` is.

    ⚠️ **`W181`'s unorderable population is NAMED here even when it is empty**,
    for the same reason the owed one is: this arm's denominators are empty on the
    tree that minted it, and `0 = 0` reads as a clean bill unless it says so.
    """
    above = [row for row in rows if (n := order(row[1])) is not None and n > HANDOFF_OWED_FROM]
    offices = [row for row in above if row[2] in OFFICE_OWNERS]
    owed = owing(rows)
    missing = [row[1] for row in owed if row[1] not in declared]
    legacy = [
        row[1]
        for row in rows
        if (n := order(row[1])) is not None
        and n <= HANDOFF_OWED_FROM
        and row[1] not in declared
        and row[2] not in OFFICE_OWNERS
    ]
    unread = [identifier for _line, identifier in unorderable(rows)]
    empty = " — the population is EMPTY, so this is 0 = 0 and not a clean bill" if not owed else ""
    return [
        f"handoff existence: {len(missing)} of {len(owed)} closed register rows owe a task "
        f"handoff and lack one{empty}. Population: {len(rows)} closed rows, "
        f"{len(above)} above the pinned bound W{HANDOFF_OWED_FROM}, "
        f"{len(offices)} of those excluded as an office round "
        f"({', '.join(sorted(OFFICE_OWNERS))}). "
        f"Below the bound and NOT chased (Rulings 106, 193): {len(legacy)}"
        + (f" — {' '.join(sorted(legacy, key=lambda name: order(name) or 0))}." if legacy else ".")
        + " Closed ids this arm cannot ORDER (`W181`): "
        + (f"{len(unread)} — {' '.join(unread)}." if unread else "none."),
    ]


def existence_lines(root: Path, declared: set[str]) -> list[str]:
    """Print the population this arm read, whether or not anything is wrong.

    ⛔ Ruling 191, and it is the reason this notice ships WITH the check rather
    than after it: the denominator is empty today, and `0 = 0` over an empty
    population reads as a clean bill unless it says so out loud.
    """
    text = _board(root)
    if text is None:
        return [f"handoff existence: no {BOARD} in this checkout, so no row can owe one."]
    return lines_for(closed_rows(text), declared)


def check_handoff_existence(root: Path) -> list[Finding]:
    """`W167`: every closed register row that owes a task handoff and has none."""
    return existence_findings(root, declared_task_ids(root))


def handoff_existence(root: Path) -> list[str]:
    """`W167`'s population, printed every run whether or not anything is wrong."""
    return existence_lines(root, declared_task_ids(root))
