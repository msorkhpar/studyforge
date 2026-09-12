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
from tools.quality.report import Finding

RULE_MISSING = "handoff-missing"

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


def owing(rows: list[tuple[int, str, str]]) -> list[tuple[int, str, str]]:
    """Return the closed rows that OWE a task handoff, after both narrowings."""
    return [
        row for row in rows if int(row[1][1:]) > HANDOFF_OWED_FROM and row[2] not in OFFICE_OWNERS
    ]


def _board(root: Path) -> str | None:
    """Read the register's text, or `None` when this tree has no board at all."""
    path = root / BOARD
    return config.read_text(path) if path.is_file() else None


def existence_findings(root: Path, declared: set[str]) -> list[Finding]:
    """Every closed row that owes a task handoff and has none.

    ⛔ The finding is raised against `BOARD.md`, on the register row's own line,
    because the remedy is one of two things and neither is a file that exists:
    write the handoff, or stop declaring the row closed.
    """
    text = _board(root)
    if text is None:
        return []
    findings = []
    for line, identifier, _owner in owing(closed_rows(text)):
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


def existence_lines(root: Path, declared: set[str]) -> list[str]:
    """Print the population this arm read, whether or not anything is wrong.

    ⛔ Ruling 191, and it is the reason this notice ships WITH the check rather
    than after it: the denominator is empty today, and `0 = 0` over an empty
    population reads as a clean bill unless it says so out loud.
    """
    text = _board(root)
    if text is None:
        return [f"handoff existence: no {BOARD} in this checkout, so no row can owe one."]
    closed = closed_rows(text)
    above = [row for row in closed if int(row[1][1:]) > HANDOFF_OWED_FROM]
    offices = [row for row in above if row[2] in OFFICE_OWNERS]
    owed = owing(closed)
    missing = [row[1] for row in owed if row[1] not in declared]
    legacy = [
        row[1]
        for row in closed
        if int(row[1][1:]) <= HANDOFF_OWED_FROM
        and row[1] not in declared
        and row[2] not in OFFICE_OWNERS
    ]
    empty = " — the population is EMPTY, so this is 0 = 0 and not a clean bill" if not owed else ""
    return [
        f"handoff existence: {len(missing)} of {len(owed)} closed register rows owe a task "
        f"handoff and lack one{empty}. Population: {len(closed)} closed rows, "
        f"{len(above)} above the pinned bound W{HANDOFF_OWED_FROM}, "
        f"{len(offices)} of those excluded as an office round "
        f"({', '.join(sorted(OFFICE_OWNERS))}). "
        f"Below the bound and NOT chased (Rulings 106, 193): {len(legacy)}"
        + (f" — {' '.join(sorted(legacy, key=lambda name: int(name[1:])))}." if legacy else "."),
    ]


def check_handoff_existence(root: Path) -> list[Finding]:
    """`W167`: every closed register row that owes a task handoff and has none."""
    return existence_findings(root, declared_task_ids(root))


def handoff_existence(root: Path) -> list[str]:
    """`W167`'s population, printed every run whether or not anything is wrong."""
    return existence_lines(root, declared_task_ids(root))
