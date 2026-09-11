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
from tools.quality.board.verdict import Verdict, claim, tokens, verdict

#: The branch every *commits ahead* cell on this board counts against. ⭐ A
#: default rather than a constant: `--release` overrides it, because a milestone
#: branch is a fact about this month and not about the instrument.
RELEASE = "release/m0-foundations"

#: ⛔ Branch namespaces whose members are DELETED once they are ancestors of the
#: release branch. ⚠️ **The standing form, measured by the CTO at `0285a92` and
#: `c3e2919`:** such a branch carries nothing unique, is invisible to
#: `--no-merged` by construction, and its only remaining effect is ⭐ **to read as
#: dispatched work to a human — which is Ruling 189's subject with no board cell
#: to print it in.** ⛔ **So this instrument is where it gets printed.**
SPENT = ("trial/", "tmp-")

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

    refuted = 0
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
                True,
                (
                    "    ⛔ REFUTED: the row names no branch this checkout has. An assertion "
                    "owes its own observation (Ruling 189(c)).",
                ),
            )
        ]
        for answer in verdicts:
            lines.extend(answer.lines)
        if any(answer.refuted for answer in verdicts):
            refuted += 1
    lines.extend(_unnamed(table.rows, live, graph))
    lines.extend(_spent(graph, live))
    lines.append(
        f"corroborate: {refuted} of {len(table.rows)} rows REFUTED by git."
        if table.rows
        else f"corroborate: the {INFLIGHT_OPEN} block is DECLARED, READ, and carries no row — "
        f"⭐ that is *nothing is in flight*, which is a real answer and not an empty "
        f"population (Ruling 191(a), and `W111` is why the two can now be told apart)."
    )
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


def _unnamed(rows: tuple[Observation, ...], live: dict[str, str], graph: Graph) -> list[str]:
    """Report the other direction: work git can see that the board does not name.

    ⛔ **The measured failure was BIDIRECTIONAL** — stale rows present and live
    rows absent, in the same table — ⚠️ **and a check that only read the rows the
    board printed would have passed the half where the board printed nothing.**

    ⛔ **And the BLIND SPOT is printed rather than implied.** ⚠️ **A checkout with
    no commit is invisible to every git instrument BY CONSTRUCTION** (Ruling 130,
    and Ruling 171's founding case): *just dispatched* and *office checkout* are
    the same bytes to `git`. ⭐ **So those are COUNTED AND NAMED as unreadable
    here, never silently dropped and never judged** — the board is the only
    instrument that can tell them apart, which is the whole of Ruling 171.

    ⛔ **Directory BASENAMES, never the path** (R7): `git worktree list` answers
    in absolute paths, and an absolute path carries the user's home directory.
    """
    claimed = {name for row in rows for name in tokens(row.checkout)}
    counts = {branch: graph.ahead(branch) or 0 for branch in live if branch != graph.release}
    missing = sorted(b for b, n in counts.items() if n > 0 and b not in claimed)
    blind = sorted(Path(live[b]).name for b, n in counts.items() if n == 0 and b not in claimed)
    lines = (
        [f"  ⛔ dispatched and UNNAMED by any row: {' '.join(missing)}"]
        if missing
        else ["  dispatched and unnamed: none."]
    )
    lines.append(
        f"  invisible to git BY CONSTRUCTION (Ruling 130), 0 commits ahead and named by no "
        f"row: {len(blind)}" + (f" — {' '.join(blind)}" if blind else "")
    )
    return lines


def _spent(graph: Graph, live: dict[str, str]) -> list[str]:
    """`trial/*` and `tmp-*` branches that are now ancestors of the release branch.

    ⚠️ **Ruling 206(ii) named this line's own blind spot and routed it here:** a
    trial worktree that is STILL CHECKED OUT is excluded by `name not in live`, so
    the one shape that keeps a spent row green is the one shape this line cannot
    print. ⭐ **It is printed now, separately and as a NOTICE**, because removing a
    worktree you did not cut is always wrong and reporting one never is.
    """
    names = [name for name in graph.heads() if name.startswith(SPENT)]
    spent = sorted(name for name in names if name not in live and graph.merged(name))
    standing = sorted(name for name in names if name in live)
    lines = (
        [
            f"  ⚠️ spent and deletable ({len(spent)}): {' '.join(spent)} — each is an ancestor "
            f"of {graph.release}, checked out nowhere, and reads as dispatched work to a human."
        ]
        if spent
        else ["  spent trial/tmp branches: none."]
    )
    lines.append(
        f"  ⚠️ trial/tmp branches STILL CHECKED OUT ({len(standing)}): {' '.join(standing)} — "
        f"⛔ report, never remove one you did not cut (Ruling 206(ii))."
        if standing
        else "  trial/tmp branches still checked out: none."
    )
    return lines


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
