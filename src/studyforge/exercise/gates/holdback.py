"""The `holdback` family — `H1` — and what it asks of a project step that `G1`–`G5` do not.

**What it does.** Declares one gate, `H1`, and registers it, so a gate record that names the
`holdback` family is complete only when it carries `H1`. `H1` reads one run: the step's tests
over the **copied candidate**, the starter with every change the step's page shows applied to it.
It holds when at least one case fails on that candidate, and it refuses when every case passes,
because then a reader passes the practice by copying the page.

**How you use it.**

    from studyforge.exercise.gates.holdback import COPIED, check_holdback

    run = attempt(COPIED, 1) if shown else None   # one run, only when the page shows a change
    verdicts = (*check(exercise, evidence, origins, ledger, where),
                check_holdback(cases, run, shown, where))

**Depends on.** `families` to register, `record` for `Verdict`, `runs` for what one run is,
and `studyforge.exercise.cases` for `Case`. Standard library only.

## ⛔ `G1`–`G5` CANNOT SEE A PAGE THAT GIVES THE ANSWER AWAY

⚠️ **Measured on one course.** Three projects showed each step's full before and after on the
lesson page, and each step's practice graded exactly that change. Every practice cleared
`G1`–`G5`: the reference passed, the starter failed on an assertion, each plant failed only its
case. A learner judge found that copying the page passed them all. ⭐ So this gate asks the one
question those five never ask: what does a reader get who copies what the page shows?

## ⭐ WHAT THE CANDIDATE IS, AND WHOSE IT IS

⛔ Nothing here reads a page or builds a candidate: the authoring skill builds it
(`skills.exercises.holdback`) and runs it through the same `runs.Attempt` as every other role,
as `COPIED`. This module reads the run it is handed and names the files the page showed a change
to. ⭐ A page that shows none of the step's changes leaves the candidate equal to the starter,
which `G2` already proves fails, so `H1` holds without a run and says so.

## ⛔ A RUN THAT LEFT NO REPORT HOLDS ONLY WHEN IT FAILED

⭐ A candidate that misses a piece the page held back can fail before any test runs: a module
that names a helper the page never showed does not import, and pytest then leaves no report the
case map can fold. ⭐ That run exited non-zero, and it is read as a fail: copying the page did
not pass. ⛔ A run that left no report and exited zero was not read, and a gate that holds for
want of evidence is the defect these gates exist to stop, so `H1` answers **did not hold**.
⭐ The record's `G1` already refuses a runner that reads nothing, so a broken runner never
clears through this gate.
"""

from __future__ import annotations

from studyforge.exercise.cases import Case
from studyforge.exercise.gates.families import Family, register
from studyforge.exercise.gates.record import Verdict
from studyforge.exercise.gates.runs import Run, require_run

#: The one gate a project step clears beyond a code exercise's five.
H1 = "H1"

#: ⭐ Registered at import: a record naming this family is complete only with `H1`.
HOLDBACK = register(Family("holdback", (H1,)))

#: The role the copied candidate is run as, once.
COPIED = "copied"


def check_holdback(
    cases: tuple[Case, ...], run: Run | None, shown: tuple[str, ...], where: str
) -> Verdict:
    """Answer `H1` over the copied candidate's run; `shown` names each file the page changed.

    ⛔ `run` is `None` only when `shown` is empty: a page that shows a change is always run.
    """
    if not shown:
        return _verdict(
            True,
            "the page shows none of this step's changes to the files the reader edits, so a "
            "reader who copies it has the starter, which G2 proves fails",
        )
    read = require_run(run, COPIED, 1, where)
    if not read.reported:
        if read.exit_code != 0:
            return _verdict(
                True,
                f"the starter with the code the page shows for {', '.join(shown)} fails before "
                f"its tests report, so the page holds back a piece the tests need",
            )
        return _verdict(
            False,
            "the copied candidate's run left no report this build could fold and exited "
            "zero, so whether copying the page passes the practice was not read",
        )
    failing = [case for case in cases if not (read.passed(case) or read.skipped(case))]
    files = ", ".join(shown)
    if not failing:
        return _verdict(
            False,
            f"the page gives the answer away: the starter with the code the page shows for "
            f"{files} passes every case. Hold back at least one piece the tests grade: "
            f"describe it in prose or a stub on the page, and do not show its code",
        )
    return _verdict(
        True,
        f"{len(failing)} of {len(cases)} case(s) fail on the starter with the code the page "
        f"shows for {files}, so the page holds back a piece the tests grade",
    )


def _verdict(held: bool, says: str) -> Verdict:
    """Return `H1`'s verdict with the sentence saying what was read."""
    return Verdict(id=H1, family=HOLDBACK.name, held=held, says=says)
