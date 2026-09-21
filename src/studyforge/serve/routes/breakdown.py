"""One Submit's breakdown: the record it folds through, and what a refusal says.

**What it does.** Turns a finished Submit into the per-case verdicts the
progress record keeps — `{case id: did it pass}` — or into no breakdown plus
the one sentence saying why none could be stated.

**How you use it.** `routes.runs.Outcome` holds the practice's workspace and
the clock read before the run, and calls `fold` once, just before it writes
the outcome:

    cases, said = fold(mode, workspace, root, started)

**Depends on.** `exercise` for the record and `breakdown_of`'s fold, and
`archive.scrub` for R7 on the wire. ⛔ Not on `progress`, `execute` or
`routes.runs`: this reads a file a run left behind, and the module that
records is the one that calls it.

## ⛔ Its own module, because `routes.runs` had no room and a trim is not a seam

⚠️ **MEASURED at `a821c32f`: `src/studyforge/serve/routes/runs.py` stood at
`378` of R11's `400`.** ⭐ The seam is the subject: that module is *what a
started run IS until it ends* — the slot, the stream, the write — and this one
is *what a grader's own report says about it*. ⛔ **Written here rather than
bought as a size exception or paid for by trimming four other rows' prose out
of a file three of them touched in one day** (`W422`'s second clause: a split
is its own act, never a passenger).

## ⛔ A breakdown is a REPORT, never a second definition of a pass (`AX-02`)

⭐ **`progress.is_pass` stays exactly what it is** — a test-mode run that
exited zero — so a practice still completes only when the grader itself
succeeded. ⛔ Nothing here is allowed to make a run pass or un-pass one, and a
reader shown *edge cases 2/3* is looking at an incomplete practice rather than
at a new kind of verdict.

⭐ **The per-case verdicts are what is recorded, and every count is derived.**
*Main ask*, *edge cases n/m* and each failed edge's sentence are all read off
this map joined with the practice's declared `cases`. ⛔ Recording the counts
as well would be two spellings of one claim, and the `says` is reader-facing
corpus text that goes stale the moment the corpus is regenerated — the id is
the stable key (`AX-01`, *For dependents*).

## ⛔ `started` is read BEFORE the run, and this module never reads a clock

⚠️ **The whole staleness clause is a comparison between the instant the run
started and the instant the report was written**, so a clock sampled after the
run makes every report look fresh — the previous run's included, which is the
one thing the clause exists to catch. ⭐ `routes.run` takes it immediately
before `Runs.claim` and it arrives here unchanged.

## ⚠️ A refusal is said on the stream, never swallowed

⛔ **`breakdown_of` raises for a report that is stale, malformed, unreadable,
or that names a test the case map does not**, and each means *this run's
breakdown cannot be stated honestly*. ⭐ **The outcome is still recorded** —
without a breakdown — because a run whose report cannot be read is still a run
that happened; ⛔ and the refusal's own sentence is returned for the stream to
say, scrubbed, so the reader is never left with a silently missing breakdown.

⚠️ **A workspace this reader cannot parse costs the breakdown and not the
run**, for the same reason: the archive accepted that record, `render.page.
practice` renders it, and a `500` here would take a working Submit away over a
report nobody was going to be shown.
"""

from __future__ import annotations

from pathlib import Path

from studyforge.archive.scrub import scrub
from studyforge.exercise import TEST, ExerciseError, breakdown_of, from_document

#: Said, just before the exit line, when this run's breakdown could not be
#: read. ⛔ NOT `routes.runs.NOT_RECORDED`: the outcome IS recorded, without a
#: breakdown, and the refusal's own sentence follows so the reason is stated.
NO_BREAKDOWN = "--- the case breakdown could not be read: {reason} ---"

#: What a refusal names itself after. ⛔ A constant and never a path: the
#: record's own sentences already name the declared report path, which
#: `exercise.safety` refused an absolute form of before the record was
#: accepted (R7).
WHERE = "this practice's exercise record"


def fold(
    mode: str, workspace: dict | None, root: Path, started: float | None
) -> tuple[dict[str, bool] | None, tuple[str, ...]]:
    """Return this run's per-case verdicts and the lines its refusal costs.

    ⭐ **`None` and no line is the ordinary answer**: a Run, a practice with no
    workspace, a record that declares no breakdown, and a run that wrote no
    report at all — a compile failure writes no surefire file.
    """
    if mode != TEST or workspace is None or started is None:
        return None, ()
    try:
        exercise = from_document(workspace, WHERE)
        folded = breakdown_of(exercise, root, WHERE, started=started)
    except ExerciseError as refusal:
        return None, (scrub(NO_BREAKDOWN.format(reason=refusal)),)
    if folded is None:
        return None, ()
    return {case.id: folded.passed(case) for case in folded.cases}, ()
