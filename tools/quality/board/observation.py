"""Ruling 189(b)'s PARSER: locate the board's observation table and read it ACROSS the row.

**What it does.** Finds the board's observation table and returns its rows — and
⭐ **says which locator answered, and names every block the board DECLARED that
this module could not READ.** ⛔ **It reads no `git` at all**, and that is the point
of the split: `W100` is a pure tree property and may not inherit a git dependency
to get built (`board.md`, ruled round 49).

**How you use it.** `read(text)` returns a `Table`; `observations(text)` is its rows
alone, for a caller that does not care how they were found. ⭐ **The three RULES
that judge those rows are `contradiction.py`** — the seam named in advance by
`W96/3` (PARSER against RULES) and split at by `W111`, because this module stood at
`386` of R11's `400`.

**Depends on.** `register` for the parser and the state vocabulary. ⛔ **Nothing
else, ever** — not `report`, which is now the rules' dependency and not this
module's, and never the corroborating git reading in `corroborate.py`.

## ⛔ The board printed its own refutation, on ONE ROW, for 350 commits

⚠️ **Measured at `cae114e^`, and these are this package's founding bytes:**

```text
| `W14` + `W18` | Developer 1 | none | 0 | in flight |
| `W27` | Developer 2 | none | 0 | ◐ in-review @ `655b527` |
```

⛔ **Both rows declare a started state, name no checkout, and count no commit.**
⭐ **Every git instrument read CORRECTLY at the same moment** — `worktree list`
saw no checkout, which was true because the work had finished, and `--no-merged`
saw nothing, which was true because it had merged — ⚠️ **so every instrument
read DOWN A COLUMN and the contradiction was printed ACROSS THE ROW.**

## ⛔ Ruling 196(b) EXPIRED, and the header branch is now a RAMP WITH A FENCE

⭐ **The `<!-- inflight -->` markers landed in the PO's round-40 board edit, so the
condition Ruling 196(b) attached to the header locator has fired.** ⚠️ **The CTO's
own plant is the reason, quoted at its reading:**

```text
PLANTED: two column NAMES changed in the observation table header
  -> observations (NONE FOUND …): 0 rows     three rules silently inapplicable
  -> quality floor: clean, exit 0            corroborate: 0 of 0, exit 0
```

⛔ **A header is INFERRED, so an absent table was indistinguishable from a renamed
column and could only be ANNOUNCED.** ⭐ **A delimiter is DECLARED, so an absent
marker can be REFUSED** — and `W111`'s settling clause is the whole of the change
here:

> ⭐ **A `<!-- inflight -->` block whose table does not declare the observation
> columns is a FINDING, not a `NONE FOUND` notice** — ⛔ **because the author has
> DECLARED that a table is there, so *"I could not read it"* is no longer
> indistinguishable from *"there is none"*.**

⛔ **So the locator is chosen by the BOARD and not by what happened to parse:** a
board that declares one marker is read ONLY inside its markers, and a header
elsewhere on the file can no longer answer for it. ⭐ **The header branch SURVIVES,
narrowed to a board carrying NO marker at all** — ⚠️ which is R10's arbitrary roots,
and the form `W111`'s record in `BOARD-ARCHIVE.md` asked to be preferred — ⛔ **but a
board that HAS the delimiters and fails to declare its columns must not fall back to
it, or the ramp is permanent.**

⛔ **What this is NOT, and `W111` is explicit: a rule pinning the column NAMES.**
⭐ **Ruling 189(b)'s roles are read FROM the header precisely so the PO may rename,
reorder, emphasise or prefix a column** — ⚠️ **so the refusal fires on a header that
declares NO role, never on one that declares them differently.**

## ⛔ What this module CANNOT see, and it is named rather than implied

⚠️ **A cell that LIES is invisible here.** Measured at `679a6c5^`: the In-flight
table named `` `wt/dev1`, `feat/SF-34-chrome` `` and `` `wt/dev2`,
`fix/board-instrument` `` — ⛔ **both checkouts gone and both branches merged, and
both cells read as an observation to this module because an observation is what
they claim to be.** ⭐ **The complement is `corroborate.py`**: this half catches a
cell that ADMITS no observation, and that one catches a cell that CLAIMS one
falsely. ⛔ **Neither is the other's test, and the division is stated here so the
next reader does not widen one into the other.**
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tools.quality.board.register import cells, identifiers, normalised, register, state

#: ⛔ The observation table is DELIMITED, and these are the markers — the
#: `<!-- register -->` pattern, reused rather than reinvented. ⚠️ **Ruled round 49
#: (`board.md`): a population grows BY A DELIMITER, never by inference**, because an
#: inferred boundary moves the moment somebody writes an ordinary table — measured,
#: at the cost of `board-duplicate` firing on the author of `board-duplicate`.
INFLIGHT_OPEN = "<!-- inflight -->"
INFLIGHT_CLOSE = "<!-- /inflight -->"

#: ⭐ The three locator readings, and ⛔ **`NONE FOUND` is a MISSING READING rather
#: than a pass** (Ruling 191). ⚠️ `DELIMITED` is what the board declares; `RAMP` is
#: Ruling 196(b)'s header branch, now reachable only on a board with NO marker.
DELIMITED = "delimited"
RAMP = "header-declared"
NONE_FOUND = "NONE FOUND"

#: ⛔ **The three words that mean *started and not finished*, and the closed set
#: has NO HOLE.** ⚠️ `in-progress` was nearly left out, and leaving it out would
#: have been the defect this package exists to close.
#:
#: ⭐ The five excluded words are excluded for STATED reasons, and
#: `test_observation.py` asserts the partition is TOTAL against `STATES`, so a
#: tenth state word cannot join the vocabulary without being classified here:
#: `todo` is not started, so no carrier is owed; `done` carries a merge ref
#: instead; `accepted` and `routed` are terminal dispositions with no work
#: pending; `blocked` owes a named unblocking condition, which IS its carrier.
STARTED = frozenset({"in flight", "in-flight", "in-progress", "in-review"})

#: ⛔ The other side of the partition, DECLARED rather than derived by subtraction,
#: so that a tenth word joining `STATES` fails
#: `test_the_two_sides_of_the_vocabulary_are_a_TOTAL_partition` until somebody
#: classifies it. ⭐ **A closed set with a hole in it is the defect this row was
#: nearly shipped with**, and a subtraction would have swallowed the new word in
#: silence — which is `is_closed`'s founding defect one layer up.
NOT_STARTED = frozenset({"todo", "done", "accepted", "routed", "blocked"})

#: ⛔ **`CTO-49/4` — a row whose carrier lives in a repository this one does not
#: own is a STAND-IN, EXCLUDED BY NAME, and never observed across the seam**
#: (Ruling 173's form; R20 and Ruling 151 in one step).
#:
#: ⭐ **An exclusion BY NAME is still a TOTAL reading** — Ruling 185: an exemption
#: a clause declares is implemented in the POPULATION, never by widening the
#: PREDICATE. ⚠️ **The day a second cross-repo row appears this tuple names two,
#: which is a reading; a predicate quietly tolerant of unobservable carriers is
#: not.** ⛔ **And the alternative is worse than a gap: an instrument that shelled
#: into a sibling checkout would be GREEN whenever that sibling is absent —
#: which is every worktree in this project by construction (Ruling 159) — so it
#: would return the PASS reading from an empty population (Ruling 191).**
STAND_INS = ("W73",)

#: ⛔ The closed vocabulary of a cell that ADMITS no observation. ⚠️ Measured
#: across every In-flight table in this board's history: the positive form is a
#: code-spanned worktree and branch (`` `wt/dev1`, `feat/SF-14-index` ``) and the
#: negative form is the bare word `none`.
#:
#: ⭐ **A cell OUTSIDE this vocabulary is read as an observation, deliberately.**
#: ⚠️ The residual — a cell that claims a checkout which does not exist — is
#: `corroborate.py`'s, and it is the half that needs git. ⛔ **Narrowing this to
#: *looks like a path* would flag a correct cell somebody wrote without a slash,
#: and a notice that fires on correct work is one people learn to scroll past**
#: (Ruling 179).
ABSENT = frozenset({"", "none", "no", "na", "n/a", "-", "—", "–", "nothing", "gone", "not yet"})

#: The first integer a commits-ahead cell carries, sign and markup stripped.
_COUNT = re.compile(r"-?\d+")

#: ⛔ **Ruling 246's cell is `n @ <branch tip>`, and this is where the two halves
#: part.** ⚠️ **`PO-50/12`: the `@ <tip>` half reached NO READER AT ALL**, so a cell
#: that was TRUE WHEN IT WAS WRITTEN and a cell that was WRONG WHEN IT WAS WRITTEN
#: printed the same disagreement. ⭐ **ONE cell, ONE grammar, ONE reader**: the tip is
#: parsed here beside the count and never in `verdict.py`, because two halves of one
#: grammar in two modules is the seam `W139` paid to cut properly one package over.
_AS_OF = "@"


@dataclass(frozen=True)
class Observation:
    """One row of the board's observation table, read ACROSS rather than down."""

    line: int
    subject: str
    ids: tuple[str, ...]
    declared: str | None
    checkout: str
    ahead: str
    delimited: bool

    @property
    def started(self) -> bool:
        """Whether this row DECLARES a started state, from the closed set."""
        return self.declared in STARTED

    @property
    def observes_a_checkout(self) -> bool:
        """Whether the `Checkout` cell admits an observation at all."""
        return normalised(self.checkout) not in ABSENT

    @property
    def _halves(self) -> tuple[str, str]:
        """The cell's COUNT half and its AS-OF half, split at Ruling 246's `@`."""
        count, _, tip = normalised(self.ahead).partition(_AS_OF)
        return count, tip.strip()

    @property
    def commits(self) -> int | None:
        """The commits the row counts ahead, or `None` when it counts none at all.

        ⛔ `None` is not `0`: a cell reading `—` declares no ahead observation,
        and a cell reading `0` declares one whose value refutes the row.

        ⚠️ **The COUNT half only.** ⛔ Searching the WHOLE cell read a number out of
        the sha beside it — `— @ abc123` declared no count and answered `123`.
        """
        found = _COUNT.search(self._halves[0])
        return int(found.group()) if found else None

    @property
    def declared_tip(self) -> str | None:
        """The ref this cell declares as its AS-OF, or `None` when it declares none.

        ⛔ **A cell declaring NO tip is the form that predates Ruling 246 and it stays
        exactly as it is** — ⚠️ a remedy turning a missing tip into a finding would
        fire on correct historical work (Ruling 179, Ruling 185(a)).

        ⭐ **Whether the ref RESOLVES is git's answer and never this module's**: this
        module reads no git at all, which is the split `W100` paid for.
        """
        tip = self._halves[1].split()
        return tip[0] if tip else None


@dataclass(frozen=True)
class Table:
    """What the board's observation table is, INCLUDING what could not be read of it.

    ⛔ **`unreadable` is the whole of `W111`:** the line of every
    `<!-- inflight -->` marker whose block declares none of the observation roles.
    ⭐ **A DECLARED block that did not parse is a refusal, and `rows == ()` is no
    longer the only thing a caller can see.**
    """

    rows: tuple[Observation, ...]
    unreadable: tuple[int, ...]
    declared: int
    locator: str


def _columns(line: str) -> dict[str, int] | None:
    """Return `{role: index}` if this table header DECLARES the observation columns.

    ⛔ **The roles are read from the header, never from a position**, so the PO
    may reorder or rename the columns and this still reads them — which is
    Ruling 192's question asked of this module: *what can the board AUTHOR that
    the recogniser cannot see?* ⭐ **A header is a DECLARATION**: a table naming a
    `Checkout` column and a commits-ahead column says what it is, and an
    ordinary table cannot satisfy that by accident the way *five cells and a `W`
    id* could.
    """
    roles: dict[str, int] = {}
    for index, cell in enumerate(cells(line)):
        plain = normalised(cell)
        if "checkout" in plain:
            roles.setdefault("checkout", index)
        elif "ahead" in plain or "commit" in plain:
            roles.setdefault("ahead", index)
        elif plain.startswith("state") or plain.startswith("status"):
            roles.setdefault("state", index)
        elif plain in {"row", "id", "#", "task", "rows"}:
            roles.setdefault("subject", index)
    if not {"checkout", "ahead", "state"} <= roles.keys():
        return None
    roles.setdefault("subject", 0)
    return roles


def _observation(
    number: int, line: str, roles: dict[str, int], delimited: bool
) -> Observation | None:
    """One data row against an already-declared header, or `None` if it is not one."""
    columns = cells(line)
    if len(columns) <= max(roles.values()) or set(columns[0]) <= set("-: "):
        return None
    subject = columns[roles["subject"]]
    return Observation(
        line=number,
        subject=subject,
        ids=tuple(identifiers(subject)),
        declared=state(columns[roles["state"]]),
        checkout=columns[roles["checkout"]],
        ahead=columns[roles["ahead"]],
        delimited=delimited,
    )


def _delimited(lines: list[str]) -> tuple[int, list[Observation], list[int]]:
    """Read ONLY inside `<!-- inflight -->` blocks, and report the ones that did not read.

    ⛔ **Returns `(blocks declared, rows, the line of every block with no declaring
    header)`.** ⚠️ **An unclosed block still counts as declared and is judged at
    end-of-file**, because a missing close marker must not make the block vanish —
    that would be the `NONE FOUND` answer to a DECLARED table all over again.
    """
    rows: list[Observation] = []
    unreadable: list[int] = []
    declared = 0
    opened = 0
    roles: dict[str, int] | None = None
    read_any = False
    for number, line in enumerate(lines, 1):
        stripped = line.strip()
        if stripped == INFLIGHT_OPEN:
            if opened and not read_any:
                unreadable.append(opened)
            declared += 1
            opened, roles, read_any = number, None, False
            continue
        if stripped == INFLIGHT_CLOSE:
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
        found = _observation(number, line, roles, delimited=True)
        if found is not None:
            rows.append(found)
    if opened and not read_any:
        unreadable.append(opened)
    return declared, rows, unreadable


def _ramp(lines: list[str]) -> list[Observation]:
    """Ruling 196(b)'s HEADER-declared locator, reachable only on a board with NO marker.

    ⛔ **It is not removed, and `W111`'s record in `BOARD-ARCHIVE.md` states why:
    this instrument may be pointed at a corpus repository's own board** (R10's
    arbitrary roots) — ⭐ **but
    it can no longer answer for a board that declared a block, which is the half of
    Ruling 196(b) that expired.**
    """
    rows: list[Observation] = []
    roles: dict[str, int] | None = None
    for number, line in enumerate(lines, 1):
        if not line.startswith("|"):
            roles = None
            continue
        if roles is None:
            roles = _columns(line)
            continue
        found = _observation(number, line, roles, delimited=False)
        if found is not None:
            rows.append(found)
    return rows


def read(text: str) -> Table:
    """Return the table, the locator that answered, and every block that did NOT read.

    ⛔ **The BOARD chooses the locator, not the parse.** ⭐ A board declaring one
    `<!-- inflight -->` marker is `DELIMITED` even when nothing inside it parsed —
    which is exactly the reading `W111` exists to make possible.
    """
    lines = text.split("\n")
    declared, rows, unreadable = _delimited(lines)
    if declared:
        return Table(tuple(rows), tuple(unreadable), declared, DELIMITED)
    found = _ramp(lines)
    return Table(tuple(found), (), 0, RAMP if found else NONE_FOUND)


def observations(text: str) -> list[Observation]:
    """Every row of the board's observation table, in file order.

    ⚠️ **The rows ALONE**: a caller that must tell *"no rows"* from *"a declared
    block I could not read"* calls `read` instead (Ruling 191, and `W111`).
    """
    return list(read(text).rows)


def asserted(text: str) -> list[tuple[int, str, str]]:
    """Every register cell DECLARING a started state, stand-ins excluded BY NAME.

    ⛔ Returns `(line, id, state word)`, and the exclusion is Ruling 185's form:
    the POPULATION is narrowed, and `observation_reading` NAMES who was
    narrowed out.
    """
    out = []
    for number, ids, cell in register(text):
        word = state(cell)
        if word in STARTED and ids[0] not in STAND_INS:
            out.append((number, ids[0], word or ""))
    return out
