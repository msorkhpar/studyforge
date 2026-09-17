"""`W306`: the MINT RUNS Ruling 244(e)'s own command, and the floor BRANCHES on its exit.

**What it does.** Reads the row files beside the board and refuses one that carries
no ANCHORED pointer back to the argument that minted it — ⛔ **using the predicate
parsed out of Ruling 244(e)'s own fenced command in `docs/conventions/board.md`,
never a second spelling of it.** ⭐ **A clause it cannot read is a FINDING**, because
an instrument that lost its predicate must not return the pass reading (Ruling 191).

**How you use it.** `born_findings(root)` returns the findings and is composed into
`check_board`; `born_reading(root)` is the population it was over, printed by
`board_state`. `clause_pattern(text)` is the parser both are built on, and
`refused(pattern, body)` is the `-L` predicate itself.

**Depends on.** `bijection` for `rows_on_disk` — the one definition of *which files
sit beside the board* — `register` for `ROWS`, `config` for `read_text`/`relative`,
`report` for the answer, and `re`. Nothing else.

## ⛔ THE DEFECT, AND BOTH STATEMENTS ABOUT IT ARE TRUE AT ONCE

⚠️ **`W305` was minted in round 93 WITHOUT the anchored pointer Ruling 244(e)
requires, and round 93's record was NOT FALSE.** ⭐ **It says *"pointers verified"*,
and `W302`'s parallel entry gives the sense in full — *"pointers verified TO RESOLVE
from `docs/tasks/rows/`"*.** ⛔ **`W305`'s links DID resolve.**

⭐ **A CHECK THAT VERIFIES THE POINTERS *PRESENT* CAN NEVER SEE THE POINTER THAT IS
*ABSENT*: a resolution check has nothing to resolve when the pointer is missing.**
⚠️ **MEASURED at `93a7795`, HOST, main checkout, with the clause's OWN command:** it
NAMED `rows/W305.md` and was SILENT on `rows/W302.md`. ⛔ **That instance is
discharged; the GAP is this module.**

## ⛔ WHY THE PREDICATE IS PARSED AND NOT TYPED HERE

⭐ **The row's own clause: *the command in `docs/conventions/board.md` is the
authority; this makes the mint path RUN it, never restate it*.** ⛔ **A regular
expression re-typed here would be a SECOND SPELLING of the clause** — the defect
`W306` exists to close, arriving one layer down — ⚠️ **and the two would be free to
disagree, with the convention's copy being the one nobody re-measures.**

⭐ **So the pattern is read from the clause's own fenced block at run time.** ⛔ **An
amendment to the clause changes this arm's verdict in the same commit, which is the
property a restatement cannot have.**

⚠️ **The match is taken PER LINE, because `grep` matches per line.** ⛔ Searching the
whole file at once would let `[^)]*` run across a newline and admit a pointer no
`grep -LE` would accept — ⭐ **a predicate that is WIDER than the clause it claims to
run is the same defect as a narrower one, pointing the other way.**

## ⛔ WHAT THIS IS NOT: A RETROACTIVE SWEEP OF `rows/`

⛔ **Ruling 244(e) says in terms that it BINDS THE MINT and is *not* a retroactive
sweep of `rows/`, and the backlog is `W88`'s.** ⚠️ **It measured, at `6c4e3d0`, role
`wt/dev1`, **33** of **80** row
files carrying no anchored pointer on the day it landed — ⛔ reading THAT as the
clause's pass condition would have made the clause UNSATISFIABLE ON THE DAY IT
LANDED**, which is Ruling 185(a)'s defect and Ruling 223's worked example.

⭐ **So the population is NARROWED IN THE INSTRUMENT and the excluded name is
PRINTED — Ruling 185's form, and `observation.STAND_INS`'s shape one module over.**
⛔ **The PREDICATE is never widened**: there is no *contains a pointer somewhere*
escape and no byte threshold, because either would release every future mint too.

⚠️ **`PRE_CLAUSE` is NOT `observation.STAND_INS` and is deliberately not imported
from it.** ⭐ **That tuple's ground is a CARRIER IN A REPOSITORY THIS ONE DOES NOT
OWN (`CTO-49/4`, R20); this one's ground is a MINT THAT PREDATES THE CLAUSE.**
⛔ **Two exemptions sharing one list would retire together and neither reason would
be readable** — ⚠️ **they coincide on `W73` today, and the coincidence is not the
reason.**

## ⭐ WHAT A GREEN RUN HERE DOES AND DOES NOT SAY (Ruling 48, Ruling 331)

⛔ **It says every row file outside `PRE_CLAUSE` carries an anchored pointer.**
⚠️ **It does NOT say the pointer RESOLVES** — that is `tools/quality/pointers.py`'s
reading and it stays there, for `bijection.py`'s own stated reason: ⭐ **this arm
would have to open another file to answer it, and a second resolver is a second
answer.** ⛔ **The two are complements and `W306` is the half that was missing:
this one sees an ABSENCE, and only that one sees a WRONG ADDRESS.**
"""

from __future__ import annotations

import re
from pathlib import Path

from tools.quality.board.bijection import rows_on_disk
from tools.quality.board.register import ROWS, row_order
from tools.quality.config import read_text, relative
from tools.quality.report import Finding

#: ⛔ A row file born with no anchored pointer to the argument that minted it.
RULE_BORN = "board-born"

#: ⛔ The clause itself could not be read, so NOTHING was judged (Ruling 191): an
#: empty population is never the pass reading, and a missing predicate is the
#: emptiest population there is.
RULE_CLAUSE = "board-clause"

#: ⛔ **The clause's home, and the AUTHORITY this arm runs rather than restates.**
CLAUSE = "docs/conventions/board.md"

#: ⛔ **Ruling 244(e)'s command, as the two literals that identify its fenced line:
#: `-L` (the pass condition is a SILENCE) and the row files it is run over.**
#: ⭐ Both are required, so an unrelated `grep` example elsewhere in the convention
#: cannot be mistaken for the clause — ⚠️ **and neither literal is the PATTERN**,
#: which is the byte string this module refuses to hold a copy of.
CLAUSE_COMMAND = "grep -LE"
CLAUSE_SUBJECT = "../tasks/rows/"

#: ⛔ **ROWS MINTED BEFORE THE CLAUSE EXISTED, EXCLUDED BY NAME** — Ruling 185's
#: form: the POPULATION is narrowed in the instrument and the name is PRINTED; the
#: PREDICATE is never widened.
#:
#: ⭐ **`W73` was minted in PO round 33 and Ruling 244(e) landed at CTO round 56, so
#: the clause NEVER BOUND that mint.** ⛔ **That backlog is `W88`'s and it is not
#: this arm's to clear** — ⚠️ **a gate that reddened the tree over it would BE the
#: retroactive sweep the clause says in terms it is not.**
#:
#: ⚠️ **MEASURED at `b58a120`, HOST, role `wt/dev2`, clean worktree: of the **304**
#: files in `docs/tasks/rows/`, `W73.md` ALONE is refused by the clause's own
#: command.** ⭐ **So this tuple is INHABITED and exactly inhabited — the day it
#: names a row the clause DID bind, `test_born.py` reddens.**
PRE_CLAUSE = ("W73",)

#: The single-quoted ERE in the clause's command line, and nothing else on it.
_QUOTED = re.compile(r"'(?P<pattern>[^']+)'")


def clause_pattern(text: str) -> str | None:
    """Return Ruling 244(e)'s own ERE, read out of the clause, or None if absent.

    ⛔ **The line is identified by BOTH of the clause's literals** — `grep -LE` and
    the row files it runs over — ⭐ so the parser cannot bind to some other fenced
    `grep` the convention happens to carry.

    ⚠️ **A comment line is skipped**: the clause's block opens with two of them, and
    one names the command it is about to show.
    """
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("#"):
            continue
        if CLAUSE_COMMAND not in stripped or CLAUSE_SUBJECT not in stripped:
            continue
        found = _QUOTED.search(stripped)
        if found is not None:
            return found.group("pattern")
    return None


def refused(pattern: re.Pattern[str], body: str) -> bool:
    """Say whether `grep -LE` would NAME this file — ⛔ a name is the REFUSAL.

    ⭐ **`-L` lists the files with NO match, so the pass condition is a SILENCE**
    (the clause's own sentence). ⛔ **Matched PER LINE, because that is what `grep`
    does**: a whole-file search would let the clause's `[^)]*` cross a newline and
    admit a pointer the command itself refuses.
    """
    return not any(pattern.search(line) for line in body.splitlines())


def _population(root: Path) -> tuple[list[str], list[str]]:
    """Return the row ids this arm judges and the ones `PRE_CLAUSE` excludes."""
    on_disk = sorted(rows_on_disk(root), key=row_order)
    judged = [name for name in on_disk if name not in PRE_CLAUSE]
    excluded = [name for name in on_disk if name in PRE_CLAUSE]
    return judged, excluded


def born_findings(root: Path) -> list[Finding]:
    """Report every row file born with no anchored pointer to its own argument.

    ⛔ **A tree with no row files at all yields NOTHING, and that is the floor's
    standing split rather than a pass**: the floor runs over arbitrary roots (R10),
    where a finding would be asserting *which repository you are in*. ⭐ **The
    presence half is asserted by `test_born.py` against the live tree, which is the
    only place that knows the answer should be yes.**

    ⛔ **THREE STATES, and the middle one is the whole of `W306`:**

    | the tree | ⛔ the answer |
    |---|---|
    | no row files | ⭐ nothing — there is no mint to bind |
    | row files, and NO convention in the tree at all | ⭐ nothing — ⚠️ **not this
      repository**, and a finding would assert WHICH repository you are in |
    | row files, the convention PRESENT, its command UNREADABLE | ⛔ **`board-clause`** |
    | row files and a readable clause | ⭐ **the clause's own verdict, per file** |

    ⚠️ **The middle two are different questions and collapsing them was a real
    defect in this arm's first draft**: it raised `board-clause` over every tree that
    had rows and no conventions directory, which reddened the floor on synthetic
    fixtures and would redden it on an arbitrary root (R10). ⭐ **An ABSENT document
    is a different fact from a document whose CLAUSE HAS BEEN REMOVED**, and only the
    second is somebody deleting the predicate out from under the gate.
    """
    on_disk = rows_on_disk(root)
    if not on_disk:
        return []

    text = read_text(root / CLAUSE)
    if text is None:
        # ⛔ The convention is not in this tree AT ALL, so this is not this repository
        # and the arm asserts nothing (R10, and `check_board`'s own standing split).
        # ⭐ The presence half is asserted against the LIVE tree in `test_born.py`,
        # which is the only place that knows the answer here should be yes.
        return []
    pattern = clause_pattern(text)
    if pattern is None:
        return [
            Finding(
                CLAUSE,
                1,
                RULE_CLAUSE,
                f"Ruling 244(e)'s command is not readable here, so {len(on_disk)} row "
                f"file(s) in {ROWS}/ were judged by NOTHING. ⛔ An empty population is "
                f"never the pass reading (Ruling 191). ⭐ This arm RUNS the clause's own "
                f"`{CLAUSE_COMMAND} '<pattern>' {CLAUSE_SUBJECT}<ID>.md` rather than "
                f"restating it, so the fenced block in {CLAUSE} is its predicate — "
                f"restore it, or the mint is unguarded.",
            )
        ]

    compiled = re.compile(pattern)
    judged, _excluded = _population(root)
    return [
        Finding(
            relative(on_disk[name], root),
            1,
            RULE_BORN,
            f"{name} carries no ANCHORED pointer to the argument that minted it. "
            f"⛔ Ruling 244(e): a row is BORN with one, and the clause's own command "
            f"NAMES this file — `{CLAUSE_COMMAND}` lists the files with NO match, so "
            f"the pass condition is a SILENCE. ⚠️ An UNANCHORED pointer is not a pass: "
            f"the address has to resolve to the ARGUMENT, not to the document that "
            f"contains it. ⭐ Add a link into ../BOARD-ARCHIVE.md#<anchor> or "
            f"../handoffs/<file>.md#<anchor>. See {CLAUSE}.",
        )
        for name in judged
        if refused(compiled, read_text(on_disk[name]) or "")
    ]


def born_reading(root: Path) -> str:
    """Name the population Ruling 244(e)'s command was run over (Ruling 48).

    ⛔ **Printed on a CLEAN run too**, and it prints the EXCLUDED NAMES: an exemption
    that is not printed is an exemption nobody re-reads (Ruling 185's form).
    """
    judged, excluded = _population(root)
    text = read_text(root / CLAUSE)
    if text is None:
        predicate = f"⚠️ ABSENT — no {CLAUSE} in this tree, so nothing was judged"
    elif clause_pattern(text) is None:
        predicate = f"⛔ NOT READABLE in {CLAUSE}"
    else:
        predicate = f"READ from {CLAUSE}"
    return (
        f"born ({RULE_BORN} — `W306`, Ruling 244(e)) over {ROWS}/: {len(judged)} row "
        f"file(s) judged by the clause's OWN command ({predicate}); "
        f"{len(excluded)} excluded BY NAME as minted before the clause "
        f"(`W88`'s backlog, never this arm's): {' '.join(excluded) or 'none'}. "
        f"⚠️ This says the pointer is PRESENT and ANCHORED, never that it RESOLVES — "
        f"that reading is tools/quality/pointers.py's."
    )
