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

**Depends on.** ⭐ **the four ARMS and nothing else** — `bijection`, `bounds`,
`contradiction` and `scheduled` — plus `notice` for the population, `register` and
`observation` for the names it re-exports, `config` for the tree and `report` for the
answer.

⛔ **THIS MODULE JUDGES NOTHING ITSELF, and that is how `W129`, `W130` and `W132`
discharge the standing SPLIT decision** (`docs/tasks/BOARD.md`, *Standing decisions*).
⚠️ **The bijection, the states and the frames were the one arm still living in the
package SURFACE, for no reason but that they were there first** — ⭐ **they are
`bijection.py` now, and `check_board` is one file read and the composition of four
arms.**

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
this file SPLITS IT.** ⚠️ **`W100` was that row once and split two arms out;
`W129`, `W130` and `W132` are that row now and they split the LAST one out.** ⭐ **The
seam is the one the existing modules already drew: an arm reads the board AS A REGISTER,
AS A FILE, AS AN OBSERVATION TABLE or AS A SCHEDULE — ⛔ and the package surface reads
it as NONE of those, because a surface composes.**

| Arm | Module | Its subject |
|---|---|---|
| the bijection, the states, the frames | ⭐ **`bijection.py`** | a row's argument has
  one home — ⛔ **and Ruling 270's STUB is its one exception** |
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

from tools.quality.board.bijection import (
    RULE_DETAIL,
    RULE_DUPLICATE,
    RULE_FRAME,
    RULE_ORPHAN,
    RULE_STATE,
    bijection_findings,
)
from tools.quality.board.bounds import (
    BOARD_FRAME,
    BOARD_NARRATIVE_CEILING,
    BOARD_PER_OBSERVATION_ROW,
    BOARD_PER_ROW,
    BOARD_PER_SCHEDULED_ROW,
    BOARD_ROW_CEILING,
    RULE_NARRATIVE,
    RULE_SIZE,
    RULE_WIDTH,
    allowance,
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
    ARCHIVE,
    BOARD,
    REGISTER_CLOSE,
    REGISTER_OPEN,
    ROW_FRAME,
    ROWS,
    STATES,
    is_closed,
    redirects_to_the_archive,
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
from tools.quality.config import read_text
from tools.quality.report import Finding

# ⛔ **Every name below is a RE-EXPORT and nothing here is defined twice.** ⚠️ **Four of
# them — `rows_on_disk`, `is_closed`, `register`, `state` — were CALLED here until `W129`
# moved `check_board`'s body into `bijection.py`; ⭐ they stay in `__all__` because the
# package surface is what callers import, and a name silently dropped from it is a
# breaking change nothing would have reported.**
#
# ⛔ **The five rule codes moved to `bijection.py` with the arm that RAISES them**, and
# that is `CTO-47/3`'s own rule applied rather than merely obeyed: ⭐ **a code is declared
# where its finding is raised — `bounds.py`, `contradiction.py` and `scheduled.py` have
# always done it that way — and this module RE-EXPORTS all thirteen so a caller still
# meets one surface.** ⚠️ **`register.py` once declared seven it never used, which is the
# defect that ruling is about; these are used at their new home.**

__all__ = [
    "ABSENT",
    "ARCHIVE",
    "BOARD",
    "BOARD_FRAME",
    "BOARD_NARRATIVE_CEILING",
    "BOARD_PER_OBSERVATION_ROW",
    "BOARD_PER_ROW",
    "BOARD_PER_SCHEDULED_ROW",
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
    "allowance",
    "bijection_findings",
    "board_state",
    "check_board",
    "is_closed",
    "redirects_to_the_archive",
    "register",
    "rows_on_disk",
    "state",
]


def check_board(root: Path) -> list[Finding]:
    """Report every way this board has stopped being a register — ⛔ FOUR ARMS, composed.

    ⭐ **This function decides nothing.** ⛔ **It reads the board ONCE and hands the same
    string to every arm**, which is what stops two arms disagreeing about what the file
    said — ⚠️ **the shape `size_findings` already refused for its denominator, applied to
    the text itself.**

    | the arm | its module | what it reads the board as |
    |---|---|---|
    | the bijection, the states, the frames | `bijection.py` | a REGISTER |
    | the three size bounds | `bounds.py` | a FILE |
    | Ruling 189(b)'s four rules | `contradiction.py` | an OBSERVATION TABLE |
    | `W100`'s trigger rule | `scheduled.py` | a SCHEDULE |
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

    # ⛔ The board as a REGISTER — `bijection.py`, and Ruling 270's stub is its one
    # exception. ⭐ It takes the ROOT as well as the text, because the other half of the
    # bijection is on disk.
    findings = bijection_findings(root, text)
    # ⛔ The board as a FILE rather than as a register — `bounds.py`, and the
    # denominator is derived there rather than handed over (see `allowance`).
    findings.extend(size_findings(text))
    # ⛔ Ruling 189(b), and the two table arms are LAST because they are the only
    # rules here that read a table against another rather than a cell against a bound.
    findings.extend(observation_findings(text))
    # ⛔ `W100` — Ruling 189's family ONE TABLE OVER, and a board declaring no
    # `<!-- scheduled -->` marker yields nothing: the floor runs over arbitrary roots.
    findings.extend(scheduled_findings(text))
    return findings
