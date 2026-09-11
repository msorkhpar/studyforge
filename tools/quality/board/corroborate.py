"""Ruling 189(c) and (d): the corroborating reading, which is `git` and is NOT the floor.

**What it does.** Takes every row the board asserts is started and corroborates it
against git in **two printed steps** — row → branch, which is an ASSERTION, and
branch → merge, which is an OBSERVATION — then names the rows git refutes, the
checkouts the board does not name, and the `trial/*` and `tmp-*` branches that
now carry nothing.

**How you use it.** `python3 -m tools.quality.board.corroborate` from any
checkout of this repository, at a wave's close. ⛔ **Exit `0` corroborated, `1`
refuted, and `2` NOT AUTHORITATIVE** — Ruling 53's fourth state, because *"git
could not answer"* and *"nothing is wrong"* must never arrive as the same answer.

**Depends on.** `board.observation` for the population, `board.contradiction` for
the reading it prints, `board.graph` for every git answer, and `argparse`.
⛔ **Nothing in `tools.quality.CHECKS` imports this**, and that is the design answer
below.

## ⛔ May the floor shell out? NO — and the reason is measured, not stylistic

⚠️ **`W96`'s row owed this answer before it owed code** (its argument is now in
`docs/tasks/BOARD-ARCHIVE.md`). ⭐ **The answer is that Ruling 189(b)'s reading
belongs on the floor and 189(c)'s cannot:**

- ⛔ **Ruling 80 — a floor check's verdict may not depend on untracked state.**
  ⭐ A branch position is the purest untracked state there is: the same tree reads
  green in the main checkout and red in a worktree that has not fetched.
- ⛔ **R10 — byte-for-byte reproducible.** ⚠️ `git worktree list` answers
  differently on every machine, and the floor runs over **arbitrary roots** — a
  temp tree, a corpus repository — where there is no release branch at all.
- ⛔ **Ruling 191 — and this is the decisive one.** A check that shelled into git
  and found nothing would return **the PASS reading from an empty population**,
  which is the failure Ruling 191 exists to forbid. ⭐ **Here that is impossible
  by construction: an unanswerable run exits `2`.**

## ⛔ Ruling 189(d) — the ref comes from the BRANCH, never from the ROW

⚠️ **Measured, and it is why this is two steps rather than one:** a branch carries
N rows and a merge message names one thing, **itself**. ⛔ **`--grep '<row id>'`
over merge messages is a LOWER BOUND and reads `0` for every row that shared a
branch** — all three of `W85`, `W86` and `W87` returned nothing, and `W86` is
named in no commit message on its own branch at all.

⛔ **So existence is checked as its OWN command** — `git rev-parse --verify`,
never behind a pipeline — ⚠️ **because `$?` after a pipeline is the pipeline's
last command and `rev-parse` echoes an unknown name back at you as if it were an
answer.** ⭐ **And `--ancestry-path | tail -1` is RECORDED AS WRONG and is not
reused: it returned a different branch's merge, and the error was caught only
because both forms were run.**

## ⛔ `W110` — the per-branch verdict is `verdict.py`, and TERMINALITY decides it

⚠️ **The defect it closes:** ⛔ **the verdict was a DISJUNCTION whose first arm was
`if branch in live:`, so a leaked worktree kept a spent row green.** ⭐ **The shipped
predicate is Ruling 199's shape `C`, read off the COMMIT GRAPH** — ⛔ **the ruling is
`docs/conventions/board.md`, `RULED ROUND 51` clause (a), and it is POINTED AT rather
than paraphrased** (Ruling 195). ⭐ **The measurement, the refuted remedy and
`PO-40/2`'s comparison are all in `verdict.py`'s own docstring.**

## ⛔ `W111`'s half that lives here — exit `2` for a table that did not READ

⚠️ **`PO-40/4`: this command returned the PASS code `0` for a board whose
observation table it could not read, while printing Ruling 191(a)'s own sentence
saying that is not the same answer as nothing being in flight.** ⭐ **So the
unreadable and unlocated cases now exit `NOT_AUTHORITATIVE`, refusing at the first
declared block that did not parse**, which is Ruling 196(a)'s third state inhabited
by a third producer.

## ⛔ `W115` — Ruling 216: the exit code is a FOLD OF THE ROWS, and the third state survives it

⚠️ **Three process codes and a TWO-valued row verdict: *git could not answer about this
branch* had nowhere to land.** ⛔ **MEASURED at `6c4e3d0` in the pinned container with a
planted branch git genuinely cannot count — a ref file written to a sha no object carries,
so `rev-parse --verify` answers and `rev-list --count` does not:**

```text
the row's branch, no checkout     ->  ⛔ REFUTED "is 0 ahead"    exit 1  a FALSE REFUTATION
the row's branch, checked out     ->  ⭐ CORROBORATED "is None"  exit 0  a FAILED reading, PASSED
a live checkout named by no row   ->  filed under "invisible to git BY CONSTRUCTION"
```

⭐ **Now: `Answer.NOT_ANSWERABLE` per branch, which is `verdict.py`'s business; and HERE the
fold — one unanswerable row, or one live checkout whose count did not read, makes the RUN
exit `NOT_AUTHORITATIVE`.** ⛔ **`_unnamed()`'s `ahead(branch) or 0` is gone: a failed
reading gets its OWN line, because the line it used to land on is the one whose whole job is
to say *this is unreadable BY CONSTRUCTION*, where a failure cannot be told from a real `0`.**

⚠️ **What this row is NOT: a rule that every unreadable thing exits `2`.** ⭐ **A DECLARED,
READABLE, EMPTY `<!-- inflight -->` block is still exit `0` and still says so in its own
sentence** — *nothing is in flight* is a real answer, and a refusal there would fire on
every wave the PO closed correctly (`board.md`, ruled round 50).

## ⛔ `W132` — Ruling 265, and the FOURTH printed line, are `unclaimed.py`'s

⚠️ **Ruling 130's exemption was gated on `0` commits ahead, and an office's own round
branch stops satisfying that the moment it records anything** — ⛔ **so the
`dispatched and UNNAMED` line named a `chore/{po,cto}-round*` branch in every wave,
forever, and Ruling 264(c) had just made that line the project's ONE pre-merge gate.**
⭐ **The predicate, the measurement in both states, and the split this row took are all
in `unclaimed.py`** — one home, not two.

"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from tools.quality.board.contradiction import observation_reading
from tools.quality.board.graph import Graph
from tools.quality.board.observation import (
    DELIMITED,
    INFLIGHT_OPEN,
    Observation,
    Table,
    asserted,
    read,
)
from tools.quality.board.register import BOARD
from tools.quality.board.unclaimed import spent, unnamed
from tools.quality.board.verdict import Answer, Verdict, claim, tokens, verdict

#: The branch every *commits ahead* cell on this board counts against. ⭐ A
#: default rather than a constant: `--release` overrides it, because a milestone
#: branch is a fact about this month and not about the instrument.
RELEASE = "release/m0-foundations"

CORROBORATED = 0
REFUTED = 1
#: ⛔ **Ruling 53's fourth state, as a number** — not *"the board is right"* and
#: not *"the board is wrong"*: this run could not tell. ⚠️ A check that cannot be
#: authoritative where it is running says so and refuses.
NOT_AUTHORITATIVE = 2


def corroborate(root: Path, release: str = RELEASE) -> tuple[list[str], int]:
    """Every asserted row against git, as printed steps and one exit code.

    ⛔ **The population is printed in full before any verdict** (Ruling 128), and
    ⚠️ **an EMPTY population is not automatically a pass**: a board that DECLARED an
    observation table this instrument could not read exits `NOT_AUTHORITATIVE`, and
    a board declaring no table at all does too. ⭐ **Only a DECLARED and READABLE
    block with no rows in it means *nothing is in flight*, and the verdict says
    which case it was** (`W111`, `PO-40/4`).
    """
    board = root / BOARD
    if not board.is_file():
        return [f"corroborate: no {BOARD} in this checkout — nothing to corroborate."], (
            NOT_AUTHORITATIVE
        )
    graph = Graph.read(root, release)
    if not graph.exists(release):
        return [
            f"corroborate: NOT AUTHORITATIVE — no branch {release!r} in this checkout, so "
            f"every *commits ahead* cell on this board counts against nothing. ⛔ This is "
            f"exit {NOT_AUTHORITATIVE} and not a pass (Ruling 191)."
        ], NOT_AUTHORITATIVE

    text = board.read_text(encoding="utf-8")
    table = read(text)
    live = graph.checkouts()
    lines = [
        f"corroborate: release {release}, {len(table.rows)} observation rows, "
        f"{len(live)} checkouts on a branch, {len(asserted(text))} started register cells.",
        observation_reading(text),
    ]
    refused = _refusal(table)
    if refused is not None:
        return [*lines, refused], NOT_AUTHORITATIVE

    refuted = unanswerable = 0
    for row in table.rows:
        asserted_by = claim(row, graph, live)
        lines.append(
            f"  row -> branch (ASSERTION, Ruling 189(c)): {row.subject} claims "
            f"{', '.join(tokens(row.checkout)) or 'nothing'} — branches "
            f"{list(asserted_by.branches)}, checkouts {list(asserted_by.checkouts)}, "
            f"unresolved {list(asserted_by.unresolved)}"
        )
        if not row.started:
            lines.append("    not a started state; no carrier is owed.")
            continue
        verdicts = [
            verdict(asserted_by, branch, graph, live) for branch in asserted_by.branches
        ] or [
            Verdict(
                Answer.REFUTED,
                (
                    "    ⛔ REFUTED: the row names no branch this checkout has. An assertion "
                    "owes its own observation (Ruling 189(c)).",
                ),
            )
        ]
        for answer in verdicts:
            lines.extend(answer.lines)
        answers = {answer.answer for answer in verdicts}
        # ⛔ `NOT_ANSWERABLE` DOMINATES within a row too (Ruling 216): a row one of whose
        # branches git could not read is a row this run cannot judge, and folding it onto
        # `REFUTED` is the FALSE REFUTATION the row exists to close.
        if Answer.NOT_ANSWERABLE in answers:
            unanswerable += 1
        elif Answer.REFUTED in answers:
            refuted += 1
    unread_lines, unread = unnamed(table.rows, live, graph)
    lines.extend(unread_lines)
    lines.extend(spent(graph, live))
    lines.append(
        f"corroborate: {refuted} of {len(table.rows)} rows REFUTED by git, "
        f"{unanswerable} NOT ANSWERABLE and {unread} live checkout(s) git could not "
        f"count (Ruling 216's third answer)."
        if table.rows
        else f"corroborate: the {INFLIGHT_OPEN} block is DECLARED, READ, and carries no row — "
        f"⭐ that is *nothing is in flight*, which is a real answer and not an empty "
        f"population (Ruling 191(a), and `W111` is why the two can now be told apart)."
    )
    if unanswerable or unread:
        # ⛔ Its OWN sentence, appended only when the third state is inhabited, so the four
        # `W111` populations keep the four distinct closing sentences they are asserted on.
        lines.append(
            f"corroborate: NOT AUTHORITATIVE — exit {NOT_AUTHORITATIVE}, not "
            f"{CORROBORATED} and not {REFUTED}. ⛔ {unanswerable} row(s) and {unread} live "
            f"checkout(s) have NO git reading at all, and *git could not answer* is neither "
            f"*the board is right* nor *the board is wrong* (Ruling 216, Ruling 53's fourth "
            f"state). ⚠️ The coerced form folded these onto a number and exited 0 or 1."
        )
        return lines, NOT_AUTHORITATIVE
    return lines, REFUTED if refuted else CORROBORATED


def _refusal(table: Table) -> str | None:
    """`W111`: the sentence for a table that did not READ, or `None` when it did.

    ⛔ **Refuses at the FIRST declared block that did not parse** (`rows/W111.md`),
    and treats *no table located at all* the same way — ⚠️ **because the board's
    contract has carried the `<!-- inflight -->` markers since the PO's round-40
    edit, so their total absence is this instrument failing to read THIS board
    rather than a board that has nothing to say.**
    """
    if table.unreadable:
        return (
            f"corroborate: NOT AUTHORITATIVE — the board DECLARES an observation table at "
            f"line {table.unreadable[0]} and no table inside it declares the observation "
            f"columns. ⛔ Exit {NOT_AUTHORITATIVE}, not {CORROBORATED}: a DECLARED block that "
            f"did not read is *I could not answer*, and this command used to return the PASS "
            f"code for it while printing Ruling 191(a)'s own sentence (`PO-40/4`, `W111`). "
            f"⭐ The floor says the same thing as `board-unreadable`."
        )
    if table.locator != DELIMITED:
        return (
            f"corroborate: NOT AUTHORITATIVE — no {INFLIGHT_OPEN} block on this board, so the "
            f"population was located by the Ruling 196(b) header RAMP and read "
            f"{len(table.rows)} rows. ⛔ Exit {NOT_AUTHORITATIVE}: the markers are this "
            f"board's contract (`board.md`, ruled round 50), so their absence is this "
            f"instrument failing to read THIS board — ⚠️ which is not the same answer as "
            f"nothing being in flight (Ruling 191(a))."
        )
    return None


def main(argv: list[str] | None = None) -> int:
    """Print every step and return the exit code. ⛔ Three answers, never two."""
    parser = argparse.ArgumentParser(description="Corroborate the board's asserted states.")
    parser.add_argument("--root", default=".", help="the checkout to read")
    parser.add_argument("--release", default=RELEASE, help="the branch cells count against")
    arguments = parser.parse_args(argv)
    lines, code = corroborate(Path(arguments.root), arguments.release)
    for line in lines:
        print(line)
    return code


if __name__ == "__main__":  # pragma: no cover - the CLI's one line
    sys.exit(main())
