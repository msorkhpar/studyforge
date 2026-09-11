"""The board is a register, and this is what keeps it one.

**What it does.** Reads `docs/tasks/BOARD.md` and the per-row files beside it in
`docs/tasks/rows/`, and fails the build on the ways a register stops being one: a
row whose argument has no home, a detail file with no row, one id written twice,
**narrative** — prose or a fat cell — accreting in a file every agent in this
project is told to read, and ⭐ **a row whose state is ASSERTED with no
observation anywhere on the board to corroborate it** (Ruling 189(b)).

**How you use it.** `check_board(root)` is registered in `tools.quality.CHECKS`;
`board_state(root)` is registered in `NOTICES` and prints the population every
run, because a `0` with no denominator is `0 = 0` (Ruling 48).

**Depends on.** `register` for the parser, `notice` for the population,
`observation` for the observation table and `contradiction` for Ruling 189(b)'s
rules over it, `config` for the tree and `report` for the answer. Nothing else.

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

## ⭐ The four arms, and each one is a module rather than a paragraph of this one

⛔ **`docs/tasks/BOARD.md` carries a standing decision that the next row touching
this file SPLITS IT**, and `W100` is that row. ⭐ **The seam is the one the three
existing modules already drew: an arm reads the board AS A REGISTER or it reads it
AS A FILE.**

| Arm | Module | Its subject |
|---|---|---|
| the bijection, the states, the frames | ⭐ **here** | a row's argument has one home |
| the three SIZE bounds | `bounds.py` | ⛔ **the board as a FILE**, and no bound is a
  line count |
| the observation table | `contradiction.py` | Ruling 189(b), a contradiction on one row |
| ⭐ the `## Scheduled` table | `scheduled.py` | ⛔ **`W100`** — a trigger is an asserted
  state wearing another column name |

⚠️ **`notice.py` is the fifth and it forbids nothing**: it prints what there was to
be wrong (Ruling 48), and `W96` split it off at the seam the CTO named.

## ⛔ And the fourth subject, which is a STATE rather than a size (Ruling 189)

⭐ **Ruling 171 found that `git worktree list` can see a row `git log` cannot and
concluded the board is the only TOTAL instrument.** ⛔ **It did not say the board
is RELIABLE** — ⚠️ **and the board is the only instrument that ASSERTS in-flight
rather than OBSERVING it, so it is the only one that can be stale in this
direction.** ⭐ **The rules live in `contradiction.py` with their founding bytes and
the table they judge is parsed by `observation.py`** — the `W96/3` seam, split at by
`W111` — and the reason they are here at all rather than in a wave-check script
is Ruling 189(b): ⛔ **the primary reading needs NO GIT** — it compares three
cells of one row with each other.

⛔ **And a FOURTH rule, which is a REFUSAL rather than a contradiction** (`W111`,
Ruling 196(b)'s expiry): ⭐ **a `<!-- inflight -->` block the board DECLARED and the
parser could not read is `board-unreadable`**, because a declared table that did not
parse used to read as *no table at all* — ⚠️ **measured by the CTO's round-50 plant:
two renamed column names, three rules silently inapplicable, and the floor clean.**

## ⛔ What this deliberately does NOT assert

⚠️ **Nothing about a row's *naming*.** Whether a naming is a good naming or an
owner right is the PO's judgement and check 4's job. ⭐ This module asserts
**shape**: that every fact has exactly one home, that the home a reader is told
to load stays loadable, and that a state the board asserts is a state the board
also observes.

⛔ **And nothing about `BOARD-ARCHIVE.md`'s or `docs/tasks/rows/`'s size**, for
two different reasons, both in `bounds.py`: a record is *supposed* to grow
monotonically, and a bound on a row file would forbid the amendment those files
exist for. ⭐ **`board_state` prints their bytes instead** (Ruling 183).

⛔ **Nor whether a trigger's EVENT has occurred**, which is `scheduled.py`'s own
refusal: ⭐ **the predicate reads the STATE cell and never the trigger's prose**,
because an event trigger is the contract's prescribed form and a check deciding
whether six events had happened would be `W49`'s class.

⛔ **Nor whether a branch the board names EXISTS**, which is Ruling 189(c) and
(d). ⭐ **That reading is `corroborate.py`'s, it shells out to `git`, and the
floor does not import it** — a floor check's verdict may not depend on untracked
state (Ruling 80), and a branch position is the purest untracked state there is.
"""

from pathlib import Path

from tools.quality.board.bounds import (
    RULE_NARRATIVE,
    RULE_SIZE,
    RULE_WIDTH,
    size_findings,
)
from tools.quality.board.contradiction import (
    RULE_DISAGREEMENT,
    RULE_INFLIGHT,
    RULE_UNOBSERVED,
    RULE_UNREADABLE,
    observation_findings,
)
from tools.quality.board.notice import board_state, rows_on_disk
from tools.quality.board.observation import (
    ABSENT,
    INFLIGHT_CLOSE,
    INFLIGHT_OPEN,
    NOT_STARTED,
    STAND_INS,
    STARTED,
)
from tools.quality.board.register import (
    BOARD,
    BOARD_FRAME,
    BOARD_NARRATIVE_CEILING,
    BOARD_PER_ROW,
    BOARD_ROW_CEILING,
    REGISTER_CLOSE,
    REGISTER_OPEN,
    ROW_FRAME,
    ROWS,
    STATES,
    is_closed,
    register,
    state,
)
from tools.quality.board.scheduled import (
    RULE_TRIGGER,
    SCHEDULED_CLOSE,
    SCHEDULED_OPEN,
    TRIGGER_STATES,
    scheduled_findings,
)
from tools.quality.config import read_text, relative
from tools.quality.report import Finding

RULE_DETAIL = "board-detail"
RULE_ORPHAN = "board-orphan"
RULE_DUPLICATE = "board-duplicate"
RULE_STATE = "board-state"
RULE_FRAME = "board-frame"

__all__ = [
    "ABSENT",
    "BOARD",
    "BOARD_FRAME",
    "BOARD_NARRATIVE_CEILING",
    "BOARD_PER_ROW",
    "BOARD_ROW_CEILING",
    "INFLIGHT_CLOSE",
    "INFLIGHT_OPEN",
    "NOT_STARTED",
    "REGISTER_CLOSE",
    "REGISTER_OPEN",
    "ROWS",
    "ROW_FRAME",
    "RULE_DETAIL",
    "RULE_DISAGREEMENT",
    "RULE_DUPLICATE",
    "RULE_FRAME",
    "RULE_INFLIGHT",
    "RULE_NARRATIVE",
    "RULE_ORPHAN",
    "RULE_SIZE",
    "RULE_STATE",
    "RULE_TRIGGER",
    "RULE_UNOBSERVED",
    "RULE_UNREADABLE",
    "RULE_WIDTH",
    "SCHEDULED_CLOSE",
    "SCHEDULED_OPEN",
    "STAND_INS",
    "STARTED",
    "STATES",
    "TRIGGER_STATES",
    "board_state",
    "check_board",
]


def check_board(root: Path) -> list[Finding]:
    """Report every way this board has stopped being a register.

    ⛔ **The bijection is asserted in BOTH directions**, and that is deliberate:
    a live row with no detail file is an argument with no home, and a detail
    file with no row is a file nobody will ever be sent to. ⭐ One of the two
    always survives a careless edit, which is exactly why the check that only
    looks one way is the one that misses.

    ⚠️ **Ruling 189(b)'s three rules are asserted in both directions for the same
    reason** — ⛔ **a stale row PRESENT and a live row ABSENT are one defect with
    two shapes, and the measured failure showed both at once.**
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
    on_disk = rows_on_disk(root)
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

    # ⛔ The board as a FILE rather than as a register — `bounds.py`, and the
    # denominator is derived there rather than handed over (see `size_findings`).
    findings.extend(size_findings(text))
    # ⛔ Ruling 189(b), and the two table arms are LAST because they are the only
    # rules here that read a table against another rather than a cell against a bound.
    findings.extend(observation_findings(text))
    # ⛔ `W100` — Ruling 189's family ONE TABLE OVER, and a board declaring no
    # `<!-- scheduled -->` marker yields nothing: the floor runs over arbitrary roots.
    findings.extend(scheduled_findings(text))
    return findings
