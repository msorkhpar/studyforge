"""Ruling 189(b)'s RULES: the four ways the board refutes itself with no `git` consulted.

**What it does.** Judges what `observation.py` parsed. Three rules read a
CONTRADICTION — a started row that admits no observation, a started register cell no
observation row names, and two tables declaring opposite sides of started — and
⭐ **a fourth reads a REFUSAL: a `<!-- inflight -->` block the board DECLARED and the
parser could not read** (`W111`).

**How you use it.** `observation_findings(text)` returns findings and is called from
`check_board`; `observation_reading(text)` is the population line `board_state`
prints every run. ⛔ **Neither shells out**, and that is the point of the split —
`W100` is a pure tree property and may not inherit a git dependency to get built
(`board.md`, ruled round 49).

**Depends on.** `observation` for the parse, `register` for the state vocabulary,
and `report` for the answer. ⛔ **Nothing else, ever** — the corroborating git
reading is `corroborate.py`, which the floor does not import.

## ⛔ Why this is a module and not the bottom of `observation.py` (`W96/3`, `W111`)

⭐ **The seam was NAMED IN ADVANCE, in `W96`'s own handoff, while the module stood at
`386` of R11's `400`:** *the next row needing the room splits `observation.py` at
PARSER against RULES*. ⚠️ **`W111` is that row, and it split at the named seam rather
than spending the last fourteen lines** — which is the standing-decision form
`board.md` uses for exactly this.

## ⛔ `board-unreadable` — a DECLARED block that did not parse is a FINDING

⚠️ **Ruling 196(b) gave the header-declared locator an EXPIRY, and `rows/W111.md`
carries the clause that settles what replaces it:**

> ⭐ **A `<!-- inflight -->` block whose table does not declare the observation
> columns is a FINDING, not a `NONE FOUND` notice** — ⛔ **because the author has
> DECLARED that a table is there, so *"I could not read it"* is no longer
> indistinguishable from *"there is none"*.**

⛔ **And the markers ALONE did not fix it, which is the part this rule exists for:**
⚠️ **inside the markers the roles are still taken from `_columns`, and `_columns`
returns `None` for a header that declares none of the three roles** — ⭐ **so the
delimiter makes the refusal POSSIBLE; this rule is what makes it HAPPEN.**

⛔ **It does NOT pin the column names** (`W111`, and Ruling 189(b)): a header that
declares the roles differently still reads, and only a header declaring NONE of them
is refused.
"""

from __future__ import annotations

from tools.quality.board.observation import (
    DELIMITED,
    INFLIGHT_OPEN,
    NONE_FOUND,
    STAND_INS,
    STARTED,
    Observation,
    Table,
    asserted,
    read,
)
from tools.quality.board.register import BOARD, register, state
from tools.quality.report import Finding

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

RULE_INFLIGHT = "board-inflight"
RULE_UNOBSERVED = "board-unobserved"
RULE_DISAGREEMENT = "board-disagreement"
#: ⛔ **`W111`, and Ruling 196(b)'s expiry** — a block the board DECLARED and this
#: package could not READ. ⚠️ It is a fourth rule rather than a widening of the other
#: three, because its subject is the TABLE and theirs is a ROW.
RULE_UNREADABLE = "board-unreadable"


def observation_findings(text: str) -> list[Finding]:
    """Ruling 189(b)'s three readings and `W111`'s refusal, each with a MEASURED case.

    ⭐ **One table, four shapes, and no two of them catch each other's case** —
    which is why this is four rule codes rather than one:

    | Rule | The board says | Measured at |
    |---|---|---|
    | `board-unreadable` | a DECLARED `<!-- inflight -->` block with no
      role-declaring header | the CTO's round-50 plant: two column names renamed,
      `NONE FOUND, 0 rows`, floor clean, exit 0 |
    | `board-inflight` | started, **no** checkout, **0** ahead — on one row |
      `cae114e^`, `W14`+`W18` and `W27`, for 350 commits |
    | `board-unobserved` | a started register cell **no** table observes |
      the absent half of the bidirectional failure, `c18df98c` |
    | `board-disagreement` | the register and the table declare **opposite sides**
      of started | `7559398`, `W95`: `` `todo` `` against `in flight` |
    """
    table = read(text)
    findings = [_unreadable(line) for line in table.unreadable]
    findings.extend(_contradictions(table.rows))
    named = {identifier for row in table.rows for identifier in row.ids}
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
    for row, identifier, other in _disagreements(table.rows, declared):
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


def _unreadable(line: int) -> Finding:
    """`W111`: the board DECLARED a block here and this package could not read it."""
    return Finding(
        BOARD,
        line,
        RULE_UNREADABLE,
        f"this {INFLIGHT_OPEN} block declares an observation table and NO table inside it "
        f"declares the observation columns. ⛔ A DECLARED block that did not read is a "
        f"FINDING and not a `{NONE_FOUND}` notice (Ruling 196(b)'s expiry, `W111`): the "
        f"author has said a table is here, so *I could not read it* is no longer "
        f"indistinguishable from *there is none*. ⚠️ Ruling 189(b)'s three rules are "
        f"SILENTLY INAPPLICABLE while this stands, and the floor would otherwise print "
        f"clean. ⭐ The roles are read FROM the header and never from a position, so "
        f"rename, reorder, emphasise or prefix the columns freely — ⛔ but ONE of them "
        f"must still say `Checkout`, one must count commits ahead, and one must be the "
        f"state.",
    )


def _contradictions(rows: tuple[Observation, ...]) -> list[Finding]:
    """`board-inflight`: a started row that admits no observation at all."""
    findings = []
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
    return findings


def _disagreements(
    rows: tuple[Observation, ...], declared: dict[str, str | None]
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

    ⭐ **And `W111` adds the third case the locator could not distinguish:** a board
    that DECLARED a block this package could not read says so, by line, in the same
    sentence as the locator that answered.
    """
    table = read(text)
    rows = table.rows
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
        f"observations ({table.locator}, Ruling 189(b), no git): {len(rows)} rows, "
        f"{sum(1 for row in rows if row.ids)} naming a `W` row id, "
        f"{sum(1 for row in rows if row.started)} declaring a started state, "
        f"{sum(1 for row in rows if row.started and row.observes_a_checkout)} with a checkout, "
        f"{sum(1 for row in rows if row.started and (row.commits or 0) > 0)} ahead; "
        f"{locator_reading(table)}; "
        f"register cells declaring a started state: {len(started)}"
        + (f" — {' '.join(sorted(started))}" if started else "")
        + "; started here and `todo` in the register (printed, not flagged — Ruling 179): "
        + (" ".join(unstarted) if unstarted else "none")
        + f"; stand-ins excluded by name (`CTO-49/4`): {' '.join(STAND_INS)}."
    )


def locator_reading(table: Table) -> str:
    """How the table was located, and `W111`'s refusal count in the same breath.

    ⛔ **Ruling 196(b): the printed locator name is the whole of what keeps the
    header branch honest, and it is therefore not optional.**
    """
    if table.locator != DELIMITED:
        return f"0 {INFLIGHT_OPEN} blocks declared, so the locator is the Ruling 196(b) ramp"
    refused = (
        f"⛔ {len(table.unreadable)} UNREADABLE at "
        + " ".join(f"line {line}" for line in table.unreadable)
        + f" ({RULE_UNREADABLE})"
        if table.unreadable
        else "0 unreadable"
    )
    return f"{table.declared} {INFLIGHT_OPEN} blocks declared, {refused}"
