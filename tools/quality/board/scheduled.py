"""`W100`: the `## Scheduled` table's STATE, read by the instrument that reads the register.

**What it does.** Locates `BOARD.md`'s `## Scheduled` table by its OWN delimiter, reads
each row ACROSS, and reports a row whose state cell DECLARES no state from the trigger
vocabulary — ⭐ **plus a declared block this module could not read**, which is `W111`'s
refusal one table over.

**How you use it.** `scheduled_findings(text)` returns findings and is called from
`check_board`; `scheduled_reading(text)` is the population line `board_state` prints
every run. ⛔ **It reads no `git` at all** — `W100` is a PURE TREE property and may not
inherit a git dependency to get built (`board.md`, ruled round 49).

**Depends on.** `register` for the cell parser, the markup normaliser and the ONE
word-boundary rule; `contradiction` for `RULE_UNREADABLE`, because *a declared block
that did not parse* is ONE concept and a second spelling of its code would be
`CTO-47/3` a second time. ⛔ **Nothing else, ever.**

## ⛔ The defect: a cell that carried an obligation and could not say what had happened to it

⚠️ **MEASURED by the PO at `c18df98c`, over the 6 rows `## Scheduled` then carried:**

```text
cells whose Trigger names an EVENT THAT HAS ALREADY PASSED   : 1
   "before M1's wave opens"  — M1 CLOSED at 2fe56a4
the 23 findings that first cell scheduled, re-read one by one : 23 of 23 carry a
   marker AND a disposition                                  -> THE WORK WAS DONE
```

⛔ **The work discharged itself round by round while the only record of the obligation
sat in a cell with no state, so nothing could report that it was owed and nothing could
report that it was met.** ⚠️ **That cell read *before M1's wave opens* through the close
of M1 and all four steps of M2.**

⭐ **A `Trigger` cell IS an asserted state wearing another column name** (Ruling 189's
family, ruled round 49): it declares *not yet* and has no observer, ⛔ **so the remedy is
the one this project applies to every status — make the illegal value unrepresentable:
the cell declares its state as its FIRST WORD, from a closed set.**

## ⛔ What this deliberately does NOT do

⚠️ **It never decides whether a trigger's EVENT has occurred.** ⭐ **An event trigger is
the section's own prescribed form** — *"a trigger that is an EVENT rather than a date"* —
⛔ **so the predicate reads the STATE cell and never the trigger's prose.** ⚠️ **A check
that tried to decide whether six different events had happened would be reading the tree
for six subjects, which is `W49`'s class: an acceptance naming no instrument that can
return `no`.**

⛔ **And it reads NO table the board has not DECLARED.** ⚠️ **Every table an instrument
can FIND is an inferred boundary, and this document has already paid for one: the first
register check inferred its boundary, an ordinary `In flight` table was read as four
duplicate register rows, and `board-duplicate` fired on the author of
`board-duplicate`.** ⭐ **A board carrying no `<!-- scheduled -->` marker has nothing
scheduled as far as this is concerned, and the reading SAYS so** (Ruling 191) — ⛔ which
is also what lets the floor run over a corpus repository's own board.

## ⛔ THE HAZARD THE BOARD EDIT CREATED, and its pass condition was handed over in advance

⭐ **MEASURED by the PO at `0ba512d`: the board MENTIONS `<!-- scheduled -->` in a table
cell as well as DECLARING it** — 3 lines contain the marker and 2 of them ARE one.
⛔ **So the locator tests `line.strip() == SCHEDULED_OPEN` and never `in line`**, exactly
as `observation.py`'s `_delimited` does. ⚠️ **An `in` test would read a cell that names
the marker as a block opener, and the same property has held for the `<!-- inflight -->`
pair since round 40 only because the equality was right by construction.** ⭐ **Both
numbers are PRINTED by `scheduled_reading`, with their units, so the hazard is visible
on every run rather than remembered.**

## ⭐ There is NO fifth state, and the answer arrived before the question did (Ruling 233)

⚠️ **`PO-42/4`: the `Effort` row's trigger fires again and never discharges — *as each
computation-shaped task is assigned* — and the closed set has no word for a STANDING
trigger.** ⛔ **The CTO ruled that a fifth word would be WRONG rather than merely
unauthorised:** the four words are points on one lifecycle and are mutually exclusive,
⭐ **and a standing trigger is `fired` (it has fired) AND `pending` (it will fire again)
at once, so `standing` would make the set non-exclusive — the one property a closed
vocabulary must keep.** ⚠️ **If a genuine standing trigger that is NOT a convention ever
appears, the answer is a `once`/`standing` KIND column beside the state, never a fifth
state.** ⛔ **So this module's vocabulary is four words and the `fired` cell is accepted
as correct, not tolerated.**
"""

from __future__ import annotations

from dataclasses import dataclass

from tools.quality.board.contradiction import RULE_UNREADABLE
from tools.quality.board.register import BOARD, cells, declared, normalised
from tools.quality.report import Finding

#: ⛔ The `## Scheduled` table is DELIMITED, and these are its markers — the
#: `<!-- register -->` / `<!-- inflight -->` pattern reused rather than reinvented
#: (ruled round 49, and `W96`'s handoff is explicit that `W100` adds no second pattern).
SCHEDULED_OPEN = "<!-- scheduled -->"
SCHEDULED_CLOSE = "<!-- /scheduled -->"

#: ⛔ **The closed vocabulary of a trigger's state, declared as the cell's FIRST WORD**
#: (Ruling 189's family, clause (c), ruled CTO round 49). ⭐ **`expired` is the member the
#: whole row is about: the trigger that expired could not say so.**
#:
#: ⚠️ **The value is whether the item OWES NOTHING FURTHER, and it is used by the printed
#: READING alone — never by the gate.** ⛔ **Only `discharged` is settled**, and `expired`
#: deliberately is not: an expired trigger is the DEFECT this column exists to make
#: sayable, not a disposition. ⭐ **Stated because it is this module's reading of the
#: ruling rather than the ruling's own words** (Ruling 195): the ruling gives the four
#: words and says EXPIRED becomes representable; which of them still owe work is a
#: reading, so it decides nothing that could fail the build.
TRIGGER_STATES: dict[str, bool] = {
    "pending": False,
    "fired": False,
    "expired": False,
    "discharged": True,
}

#: ⛔ A row whose state cell declares nothing from `TRIGGER_STATES`. ⚠️ It is a SECOND
#: code rather than `board-state` widened, and the reason is diagnostic: the two tables
#: have different vocabularies, so a reader who meets the code must know which closed set
#: the cell failed against. ⭐ **The INSTRUMENT is one — `tools/quality/board/` reads both
#: delimited tables and nothing else, which is what round 49 ruled.**
RULE_TRIGGER = "board-trigger"

#: ⭐ The locator readings, the same three words `observation.py` uses, so a reader of the
#: `board:` lines meets one vocabulary and not two.
DELIMITED = "delimited"
NONE_FOUND = "NONE FOUND"


@dataclass(frozen=True)
class Item:
    """One row of the `## Scheduled` table, read ACROSS rather than down."""

    line: int
    subject: str
    trigger: str
    cell: str
    declared: str | None

    @property
    def settled(self) -> bool:
        """Whether the declared state says nothing further is owed. ⛔ READING only."""
        return TRIGGER_STATES.get(self.declared or "", False)


@dataclass(frozen=True)
class Schedule:
    """What the `## Scheduled` table is, INCLUDING what could not be read of it.

    ⛔ **`unreadable` is `W111`'s clause one table over**: the line of every
    `<!-- scheduled -->` marker whose block declares none of the roles. ⭐ **A DECLARED
    block that did not parse is a refusal, and `rows == ()` is not the only thing a
    caller can see.**
    """

    rows: tuple[Item, ...]
    unreadable: tuple[int, ...]
    blocks: int
    mentions: int
    locator: str


def _columns(line: str) -> dict[str, int] | None:
    """Return `{role: index}` if this header DECLARES the scheduled columns.

    ⛔ **The roles are read FROM the header, never from a position**, so the PO may
    rename, reorder, emphasise or prefix a column and this still reads it — ⚠️ **and the
    refusal fires on a header that declares NO role, never on one that declares them
    differently** (Ruling 189(b)'s own prohibition, and `W111`'s).

    ⭐ **A `State` column AND a trigger column, because those two are what make this
    table the one the contract describes**: an ordinary two-column table cannot satisfy
    that by accident.
    """
    roles: dict[str, int] = {}
    for index, cell in enumerate(cells(line)):
        plain = normalised(cell)
        if plain.startswith("state") or plain.startswith("status"):
            roles.setdefault("state", index)
        elif "trigger" in plain or plain.startswith("when"):
            roles.setdefault("trigger", index)
        elif plain in {"item", "what", "subject", "thing"}:
            roles.setdefault("subject", index)
    if not {"state", "trigger"} <= roles.keys():
        return None
    roles.setdefault("subject", 0)
    return roles


def _item(number: int, line: str, roles: dict[str, int]) -> Item | None:
    """One data row against an already-declared header, or `None` if it is not one."""
    columns = cells(line)
    if len(columns) <= max(roles.values()) or set(columns[0]) <= set("-: "):
        return None
    cell = columns[roles["state"]]
    return Item(
        line=number,
        subject=columns[roles["subject"]],
        trigger=columns[roles["trigger"]],
        cell=cell,
        declared=declared(cell, TRIGGER_STATES),
    )


def read(text: str) -> Schedule:
    """Read ONLY inside `<!-- scheduled -->` blocks, and report the ones that did not read.

    ⛔ **The marker is matched as the WHOLE LINE** — `line.strip() == SCHEDULED_OPEN` —
    ⚠️ **because the board MENTIONS the marker inside a table cell as well as declaring
    it, and an `in` test would read that cell as a block opener.** ⭐ **The mentions are
    COUNTED and printed beside the declarations** rather than merely avoided.

    ⚠️ **An unclosed block still counts as declared and is judged at end of file**, the
    same way `observation.py` judges its own: ⛔ **otherwise deleting ONE line restores
    the `NONE FOUND` answer to a table the author declared.**
    """
    rows: list[Item] = []
    unreadable: list[int] = []
    blocks = mentions = opened = 0
    roles: dict[str, int] | None = None
    read_any = False
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if stripped not in {SCHEDULED_OPEN, SCHEDULED_CLOSE} and (
            SCHEDULED_OPEN in line or SCHEDULED_CLOSE in line
        ):
            mentions += 1
        if stripped == SCHEDULED_OPEN:
            if opened and not read_any:
                unreadable.append(opened)
            blocks += 1
            opened, roles, read_any = number, None, False
            continue
        if stripped == SCHEDULED_CLOSE:
            if opened and not read_any:
                unreadable.append(opened)
            opened, roles, read_any = 0, None, False
            continue
        if not opened:
            continue
        if not line.startswith("|"):
            roles = None
            continue
        if roles is None:
            roles = _columns(line)
            read_any = read_any or roles is not None
            continue
        found = _item(number, line, roles)
        if found is not None:
            rows.append(found)
    if opened and not read_any:
        unreadable.append(opened)
    return Schedule(
        tuple(rows), tuple(unreadable), blocks, mentions, DELIMITED if blocks else NONE_FOUND
    )


def scheduled_findings(text: str) -> list[Finding]:
    """Every `## Scheduled` row that declares no state, and every block that did not read.

    ⛔ **A board with NO marker yields NOTHING**, and that is deliberate rather than
    lenient: ⭐ **the floor runs over ARBITRARY ROOTS** — a temp tree, a corpus
    repository — ⚠️ **so a refusal there would be asserting *which repository you are
    in***. ⛔ **In THIS repository the table is declared, and `test_scheduled.py` says
    so against the live board.**
    """
    schedule = read(text)
    findings = [_unreadable(line) for line in schedule.unreadable]
    for row in schedule.rows:
        if row.declared is not None:
            continue
        findings.append(
            Finding(
                BOARD,
                row.line,
                RULE_TRIGGER,
                f"this scheduled row declares no state. Begin its state cell with one of "
                f"{', '.join(sorted(TRIGGER_STATES))} — ⛔ a `Trigger` cell IS an asserted "
                f"state wearing another column name (Ruling 189's family), and a scheduled "
                f"item whose state no instrument can read is one that cannot report that it "
                f"is owed OR that it was met. ⚠️ MEASURED: one such cell read `before M1's "
                f"wave opens` through the close of M1 and all four steps of M2 while the work "
                f"behind it was being done. ⭐ `expired` is in the set precisely so a trigger "
                f"whose event has passed can SAY so.",
            )
        )
    return findings


def _unreadable(line: int) -> Finding:
    """`W111`'s refusal, one table over: the board DECLARED a block and this did not read it."""
    return Finding(
        BOARD,
        line,
        RULE_UNREADABLE,
        f"this {SCHEDULED_OPEN} block declares a scheduled table and NO table inside it "
        f"declares a state column and a trigger column. ⛔ A DECLARED block that did not "
        f"read is a FINDING and not a `{NONE_FOUND}` notice (`W111`'s clause, one table "
        f"over): the author has said a table is here, so *I could not read it* is no longer "
        f"indistinguishable from *there is none*. ⭐ The roles are read FROM the header and "
        f"never from a position, so rename, reorder, emphasise or prefix the columns freely "
        f"— ⛔ but one of them must still be the state and one must be the trigger.",
    )


def scheduled_reading(text: str) -> str:
    """Return the population, printed before any verdict (Ruling 128, Ruling 191).

    ⭐ **Every state in the vocabulary is printed WITH ITS COUNT, the uninhabited ones
    included and NAMED** — ⚠️ **`expired` was inhabited only as a trigger DESCRIPTION and
    not as a STATE on the day the column landed, which is a real gap in the inhabitation
    and is stated rather than hidden** (Ruling 191).

    ⛔ **And both marker numbers, each with its UNIT** (Ruling 224): the lines that ARE a
    declaration and the lines that merely MENTION the marker inside a cell.
    """
    schedule = read(text)
    if schedule.locator != DELIMITED:
        return (
            f"scheduled ({NONE_FOUND}, Ruling 189's family, no git): 0 {SCHEDULED_OPEN} "
            f"blocks declared, so nothing here is read — ⛔ which is not the same answer as "
            f"*nothing is scheduled* (Ruling 191(a))."
        )
    counted = {
        word: sum(1 for row in schedule.rows if row.declared == word) for word in TRIGGER_STATES
    }
    uninhabited = sorted(word for word, count in counted.items() if not count)
    refused = (
        f"⛔ {len(schedule.unreadable)} UNREADABLE at "
        + " ".join(f"line {line}" for line in schedule.unreadable)
        + f" ({RULE_UNREADABLE})"
        if schedule.unreadable
        else "0 unreadable"
    )
    return (
        f"scheduled ({schedule.locator}, Ruling 189's family, no git): {len(schedule.rows)} rows, "
        f"{sum(1 for row in schedule.rows if row.declared)} declaring a state, "
        f"{sum(1 for row in schedule.rows if row.declared is None)} declaring none "
        f"({RULE_TRIGGER}), {sum(1 for row in schedule.rows if row.settled)} settled; by state — "
        + ", ".join(f"{word} {counted[word]}" for word in sorted(TRIGGER_STATES))
        + "; states with no row at all: "
        + (" ".join(uninhabited) if uninhabited else "none")
        + f"; {schedule.blocks} {SCHEDULED_OPEN} declaration line(s), {refused}, "
        f"{schedule.mentions} line(s) MENTIONING the marker inside a cell and declaring "
        f"nothing."
    )
