"""Ruling 189(b): an ASSERTED state owes a corroborating OBSERVATION, read ACROSS the row.

**What it does.** Reads the board's own observation table — the one whose header
declares a `Checkout` column and a commits-ahead column — and reports the three
ways the board refutes itself **without git being consulted at all**: a started
row that admits no observation, a started register cell no observation table
names, and two tables disagreeing about one row.

**How you use it.** `observation_findings(text)` returns findings and is called
from `check_board`; `observation_reading(text)` is the population line
`board_state` prints every run. ⛔ **Neither shells out**, and that is the point
of the split — `W100` is a pure tree property and may not inherit a git
dependency to get built (`board.md`, ruled round 49).

**Depends on.** `register` for the parser and the state vocabulary, and `report`
for the answer. ⛔ **Nothing else, ever** — the corroborating git reading is
`corroborate.py`, which the floor does not import.

## ⛔ The board printed its own refutation, on ONE ROW, for 350 commits

⚠️ **Measured at `cae114e^`, and these are this module's founding bytes:**

```text
| `W14` + `W18` | Developer 1 | none | 0 | in flight |
| `W27` | Developer 2 | none | 0 | ◐ in-review @ `655b527` |
```

⛔ **Both rows declare a started state, name no checkout, and count no commit.**
⭐ **Every git instrument read CORRECTLY at the same moment** — `worktree list`
saw no checkout, which was true because the work had finished, and `--no-merged`
saw nothing, which was true because it had merged — ⚠️ **so every instrument
read DOWN A COLUMN and the contradiction was printed ACROSS THE ROW.**

⭐ **That is why the primary reading is internal and needs no git**, and why it is
cheap enough to run on every floor rather than at a wave's close.

## ⛔ What this module CANNOT see, and it is named rather than implied

⚠️ **A cell that LIES is invisible here.** Measured at `679a6c5^`: the In-flight
table named `` `wt/dev1`, `feat/SF-34-chrome` `` and `` `wt/dev2`,
`fix/board-instrument` `` — ⛔ **both checkouts gone and both branches merged, and
both cells read as an observation to this module because an observation is what
they claim to be.** ⭐ **The complement is `corroborate.py`**: this module catches a
cell that ADMITS no observation, and that one catches a cell that CLAIMS one
falsely. ⛔ **Neither is the other's test, and the division is stated here so the
next reader does not widen one into the other.**
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from tools.quality.board.register import BOARD, cells, identifiers, normalised, register, state
from tools.quality.report import Finding

#: ⛔ The observation table is DELIMITED when the board says so, and these are
#: the markers — the `<!-- register -->` pattern, reused rather than reinvented.
#: ⚠️ **Ruled round 49 (`board.md`): a population grows BY A DELIMITER, never by
#: inference**, because an inferred boundary moves the moment somebody writes an
#: ordinary table — measured, at the cost of `board-duplicate` firing on the
#: author of `board-duplicate`.
INFLIGHT_OPEN = "<!-- inflight -->"
INFLIGHT_CLOSE = "<!-- /inflight -->"

#: ⛔ **The three words that mean *started and not finished*, and the closed set
#: has NO HOLE.** ⚠️ `in-progress` was nearly left out, and leaving it out would
#: have been the defect this module exists to close.
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

#: ⛔ The states that mean NO WORK IS PENDING. ⭐ **A row cannot be both terminal
#: and started, and that is the only cross-table disagreement this module reports
#: as a FINDING.**
#:
#: ⚠️ **`todo` is deliberately NOT here, and the reason is measured.** ⭐ **This
#: board's current practice dispatches a row by naming it in the observation table
#: and leaving its register cell at `` `todo` `` — `W95` and `W96` both, round
#: 38** — so a rule that read `todo` against a started row would have fired on two
#: rows the PO had just written correctly. ⛔ **A notice whose first wave fires on
#: work its author just did is a notice nobody reads twice** (Ruling 179). ⭐ **So
#: that pairing is PRINTED by `observation_reading` instead**, where a reader can
#: see it without the floor crying wolf — ⚠️ **and it is `corroborate.py` that
#: refutes such a row, because only `git` can tell *just dispatched* from *closed
#: five waves ago*.**
TERMINAL = frozenset({"done", "accepted", "routed"})

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

RULE_INFLIGHT = "board-inflight"
RULE_UNOBSERVED = "board-unobserved"
RULE_DISAGREEMENT = "board-disagreement"


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
    def commits(self) -> int | None:
        """The commits the row counts ahead, or `None` when it counts none at all.

        ⛔ `None` is not `0`: a cell reading `—` declares no ahead observation,
        and a cell reading `0` declares one whose value refutes the row.
        """
        found = _COUNT.search(normalised(self.ahead))
        return int(found.group()) if found else None


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


def observations(text: str) -> list[Observation]:
    """Every row of every observation table on this board, in file order.

    ⛔ **Two locators and the reading says which answered.** ⭐ The delimited form
    is the ruled one; the header declaration is what lets this instrument read a
    board it is forbidden to edit — ⚠️ **and a board carrying neither is reported
    by `observation_reading`, never passed over in silence** (Ruling 191).
    """
    found: list[Observation] = []
    roles: dict[str, int] | None = None
    delimited = False
    for number, line in enumerate(text.split("\n"), 1):
        stripped = line.strip()
        if stripped == INFLIGHT_OPEN:
            delimited = True
            continue
        if stripped == INFLIGHT_CLOSE:
            delimited, roles = False, None
            continue
        if not line.startswith("|"):
            roles = None
            continue
        if roles is None:
            roles = _columns(line)
            continue
        columns = cells(line)
        if len(columns) <= max(roles.values()) or set(columns[0]) <= set("-: "):
            continue
        subject = columns[roles["subject"]]
        found.append(
            Observation(
                line=number,
                subject=subject,
                ids=tuple(identifiers(subject)),
                declared=state(columns[roles["state"]]),
                checkout=columns[roles["checkout"]],
                ahead=columns[roles["ahead"]],
                delimited=delimited,
            )
        )
    return found


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


def observation_findings(text: str) -> list[Finding]:
    """Ruling 189(b)'s three readings, each with a MEASURED founding case.

    ⭐ **One row, three shapes, and no two of them catch each other's case** —
    which is why this is three rule codes rather than one:

    | Rule | The board says | Measured at |
    |---|---|---|
    | `board-inflight` | started, **no** checkout, **0** ahead — on one row |
      `cae114e^`, `W14`+`W18` and `W27`, for 350 commits |
    | `board-unobserved` | a started register cell **no** table observes |
      the absent half of the bidirectional failure, `c18df98c` |
    | `board-disagreement` | the register and the table declare **opposite sides**
      of started | `7559398`, `W95`: `` `todo` `` against `in flight` |
    """
    findings: list[Finding] = []
    rows = observations(text)
    for row in rows:
        if not row.started or row.observes_a_checkout or (row.commits or 0) > 0:
            continue
        counted = "counts no commit at all" if row.commits is None else "counts 0 commits ahead"
        findings.append(
            Finding(
                BOARD,
                row.line,
                RULE_INFLIGHT,
                f"{row.subject} declares {row.declared!r}, names no checkout, and {counted}. "
                f"⛔ That is a CONTRADICTION PRINTED ON ONE ROW (Ruling 189(b)): a started row "
                f"owes a live checkout OR a branch ahead of the release branch, and this row "
                f"offers neither. ⚠️ Every git instrument reads correctly while this stands — "
                f"`worktree list` sees no checkout because the work FINISHED, and `--no-merged` "
                f"sees nothing because it MERGED. Re-take the row or close it.",
            )
        )
    named = {identifier for row in rows for identifier in row.ids}
    for number, identifier, word in asserted(text):
        if identifier not in named:
            findings.append(
                Finding(
                    BOARD,
                    number,
                    RULE_UNOBSERVED,
                    f"{identifier}'s register cell declares {word!r} and NO observation row "
                    f"names it. ⛔ An asserted state owes a corroborating observation "
                    f"(Ruling 189): the board is the only instrument that ASSERTS in-flight "
                    f"rather than OBSERVING it, so a started cell with no observer can only be "
                    f"kept freshly wrong. ⭐ Name the row in the In-flight table with its "
                    f"checkout and its commits ahead, or change the state cell.",
                )
            )
    # ⛔ EVERY id of a multi-id register row, not only the owning one: `W14 + W18`
    # is one register row and the observation table named BOTH, so a map keyed on
    # the owner alone would have missed the half the founding case turned on.
    declared = {identifier: state(cell) for _n, ids, cell in register(text) for identifier in ids}
    for row, identifier, other in _disagreements(rows, declared):
        findings.append(
            Finding(
                BOARD,
                row.line,
                RULE_DISAGREEMENT,
                f"this row declares {row.declared!r} for {identifier} and the register cell "
                f"declares {other!r} — ⛔ one of the two says the work is STARTED and the other "
                f"says it is FINISHED, and both cannot be true of one row. ⚠️ A state has ONE "
                f"home (`docs/conventions/board.md`); when one file carries two of them a reader "
                f"cannot tell which is stale. ⭐ Replace the stale cell — ⛔ never append the new "
                f"reading beneath the old one, which is how a status comes to disagree with "
                f"itself.",
            )
        )
    return findings


def _disagreements(
    rows: list[Observation], declared: dict[str, str | None]
) -> list[tuple[Observation, str, str]]:
    """Rows where one table says STARTED and the other says FINISHED.

    ⛔ **`TERMINAL`, never `NOT_STARTED`** — see `TERMINAL` for the measurement
    that narrowed this, and `observation_reading` for where the softer pairing is
    printed instead of flagged.
    """
    found = []
    for row in rows:
        for identifier in row.ids:
            other = declared.get(identifier)
            if other is None:
                continue
            if (row.started and other in TERMINAL) or (not row.started and other in STARTED):
                if row.started or row.declared in TERMINAL:
                    found.append((row, identifier, other))
    return found


def observation_reading(text: str) -> str:
    """Return the population, printed before any verdict (Ruling 128, Ruling 191).

    ⛔ **Three numbers that can each be `0`, and `0` here is a MISSING READING
    rather than a pass** — which is why the locator, the stand-ins and the
    unmatched rows are all named in the same line. ⚠️ **Between waves the
    observation table is empty and the started register population is empty too**,
    so a reader who sees `0` must be able to tell *nothing is in flight* from
    *nothing was read*.
    """
    rows = observations(text)
    locator = "delimited" if any(row.delimited for row in rows) else "header-declared"
    if not rows:
        locator = "NONE FOUND"
    with_ids = sum(1 for row in rows if row.ids)
    started = [identifier for _n, identifier, _w in asserted(text)]
    declared = {identifier: state(cell) for _n, ids, cell in register(text) for identifier in ids}
    # ⛔ The pairing that is PRINTED rather than flagged — see `TERMINAL`. ⭐ It is
    # named, not counted, because `0` would read the same as *"nobody checked"*.
    unstarted = sorted(
        identifier
        for row in rows
        if row.started
        for identifier in row.ids
        if declared.get(identifier) == "todo"
    )
    return (
        f"observations ({locator}, Ruling 189(b), no git): {len(rows)} rows, "
        f"{with_ids} naming a `W` row id, "
        f"{sum(1 for row in rows if row.started)} declaring a started state, "
        f"{sum(1 for row in rows if row.started and row.observes_a_checkout)} with a checkout, "
        f"{sum(1 for row in rows if row.started and (row.commits or 0) > 0)} ahead; "
        f"register cells declaring a started state: {len(started)}"
        + (f" — {' '.join(sorted(started))}" if started else "")
        + "; started here and `todo` in the register (printed, not flagged — Ruling 179): "
        + (" ".join(unstarted) if unstarted else "none")
        + f"; stand-ins excluded by name (`CTO-49/4`): {' '.join(STAND_INS)}."
    )
