"""The honest partial states: each one says what is missing and what still works.

**What it does.** Names the six states a site can be served in short of
everything, and derives which of them hold from the verbs' own answers: the
narration run's exit code and report, the plan's narration creations, the
manifest's `exercises` flag, and the namespaces the serving process offers.

**How you use it.** `narration_states(code, said, has_record=...)` and
`exercise_states(declared, namespaces)` each return a tuple of `PartialState`;
`recorded(plan)` answers whether a narration record names any clip.
`PartialState.lines()` is what the skill prints.

**Depends on.** `cli.narrate.report.NO_SERVICE`, imported so the no-service
sentence is never respelled, `serve.routes.run.NAMESPACE` for the execution
namespace's one spelling, `validate.report.OK`, and this package's
`narration` for what provides narration and how to have it. ⛔ It reads answers
and opens nothing.

## ⛔ None of these is an error (R6, R8)

⭐ Each state is data with a stated consequence, and none of them changes an exit
code. The reading floor still works in every one of them.

## ⛔ *CANNOT NARRATE* AND *HAS NOT NARRATED* ARE TWO STATES, NOT ONE

⚠️ **They read as one state until this was split**, and the cost was measured: a
clean run of the skills produced a corpus with no narration at all and reported
it beside `exercises`, whose whole point is that it **is** a legitimate finished
state (C5).

⭐ **The two are told apart by the narration run's own answer, and by nothing
this module had to go and read:**

| what happened | the state | finished? |
|---|---|---|
| narration was never run | `narration` | ⛔ **no** — nor is it known whether it could speak |
| it ran and placed no clip | `narration-none` | ⭐ **yes**: there was nothing to say aloud |

⛔ So a corpus that could narrate and did not is never reported as complete, and
a corpus with nothing to narrate is never sent to start a service it does not
need.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

import studyforge.serve.routes.run as run
from studyforge.cli.narrate.report import NO_SERVICE
from studyforge.skills.buildserve import narration
from studyforge.validate.report import OK

#: What works in every partial state. ⭐ R8: a built site opens with nothing running.
READING_FLOOR = (
    "reading pages, navigation, contents and progress; the site also opens "
    "from its index.html with nothing running"
)

#: The namespace a serving process offers once it can run a reader's code. ⭐ The
#: framework's own `serve.routes.run.NAMESPACE`, the name `serve.instance.instance_of`
#: registers and `studyforge serve --site` registers too (`SK-03/3`, `SF-22`, `W371`):
#: this package holds no spelling of its own.
EXECUTION_NAMESPACE = run.NAMESPACE


@dataclass(frozen=True, slots=True)
class PartialState:
    """One known state short of everything: what is missing, what still works, what to do."""

    name: str
    missing: str
    works: str
    remedy: str

    def lines(self) -> list[str]:
        """Return the three greppable lines the skill prints for this state."""
        return [
            f"partial {self.name}  missing: {self.missing}",
            f"works {self.name}  {self.works}",
            f"remedy {self.name}  {self.remedy}",
        ]


NOT_NARRATED = PartialState(
    "narration",
    "narration has not been run, so every page is silent and it is not yet known "
    "whether this corpus could speak",
    READING_FLOOR,
    narration.REMEDY,
)

#: ⭐ The other half of the split: a corpus with nothing to say aloud is FINISHED.
#: ⛔ Read from what happened — a run against a service that placed no clip — and
#: never from a declaration, because no manifest declares narration.
NOTHING_TO_NARRATE = PartialState(
    "narration-none",
    "narration ran against a service and placed no clip, so this corpus has nothing to say aloud",
    "everything: a corpus with nothing to speak is complete at the reading floor, not short (C5)",
    "none needed",
)

NO_NARRATION_SERVICE = PartialState(
    "narration-service",
    "no narration service answered, so nothing was synthesised",
    f"{READING_FLOOR}; clips recorded by an earlier run still play",
    narration.REMEDY,
)

NARRATION_INCOMPLETE = PartialState(
    "narration-incomplete",
    "the narration run did not place every clip; its report above names what it did not",
    f"{READING_FLOOR}; every clip it placed plays",
    "read the narration report above, then run again",
)

NO_EXERCISES = PartialState(
    "exercises",
    "the corpus declares no exercises, so there is nothing to Run or Submit",
    "everything: a corpus with no graders is complete at the reading floor, not short (C5)",
    "none needed",
)

NO_TOOLCHAIN = PartialState(
    "toolchain",
    "the serving process offers no execution, so Run and Submit are unavailable",
    f"practice pages read; {READING_FLOOR}",
    "none from this skill: execution arrives with a toolchain container",
)

#: ⭐ Every state, in the order the skill prints them.
KNOWN = (
    NOT_NARRATED,
    NOTHING_TO_NARRATE,
    NO_NARRATION_SERVICE,
    NARRATION_INCOMPLETE,
    NO_EXERCISES,
    NO_TOOLCHAIN,
)


def recorded(plan: object) -> bool:
    """Whether the plan names any clip copy, which it does only when a record names clips.

    ⭐ The plan's own mark (`Creation.narration`) and its own printed distinction:
    a line ending in `/` is a directory, and a unit's audio directory is planned
    whether or not anything was ever narrated.
    """
    return any(
        creation.narration and not creation.path.endswith("/")
        for creation in getattr(plan, "creations", ())
    )


def narration_states(code: int | None, said: str, *, has_record: bool) -> tuple[PartialState, ...]:
    """Return the narration states, from the narration run's exit code and report.

    `code` is `None` when no narration was asked for. ⛔ A run that did not
    finish is reported, never raised: the build that follows still reads.

    ⭐ **The two silent corpora are told apart here and nowhere else.** No run
    at all leaves it unknown whether this corpus could speak, so it is reported
    as unfinished; a run that finished against a service and placed nothing is
    the answer that it could not, so it is reported as complete.
    """
    if code is None:
        return () if has_record else (NOT_NARRATED,)
    if code == OK:
        return () if has_record else (NOTHING_TO_NARRATE,)
    if NO_SERVICE in said:
        return (NO_NARRATION_SERVICE,)
    return (NARRATION_INCOMPLETE,)


def exercise_states(declared: bool, namespaces: Iterable[str]) -> tuple[PartialState, ...]:
    """Return the exercise states, from the manifest flag and what the server offers."""
    if not declared:
        return (NO_EXERCISES,)
    if EXECUTION_NAMESPACE not in set(namespaces):
        return (NO_TOOLCHAIN,)
    return ()
