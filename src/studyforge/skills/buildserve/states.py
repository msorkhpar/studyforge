"""The honest partial states: each one says what is missing and what still works.

**What it does.** Names the five states a site can be served in short of
everything, and derives which of them hold from the verbs' own answers: the
narration run's exit code and report, the plan's narration creations, the
manifest's `exercises` flag, and the namespaces the serving process offers.

**How you use it.** `narration_states(code, said, has_record=...)` and
`exercise_states(declared, namespaces)` each return a tuple of `PartialState`;
`recorded(plan)` answers whether a narration record names any clip.
`PartialState.lines()` is what the skill prints.

**Depends on.** `cli.narrate.report.NO_SERVICE`, imported so the no-service
sentence is never respelled, and `validate.report.OK`. ⛔ It reads answers and
opens nothing.

## ⛔ None of these is an error (R6, R8)

⭐ Each state is data with a stated consequence, and none of them changes an exit
code. The reading floor still works in every one of them.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass

from studyforge.cli.narrate.report import NO_SERVICE
from studyforge.validate.report import OK

#: What works in every partial state. ⭐ R8: a built site opens with nothing running.
READING_FLOOR = (
    "reading pages, navigation, contents and progress; the site also opens "
    "from its index.html with nothing running"
)

#: The namespace a serving process offers once it can run a reader's code.
#: ⚠️ No framework module names it yet: `SF-22` registers `run` beside `state`
#: (`SF-19b`'s handoff), so this is the one spelling this package holds (`SK-03/2`).
EXECUTION_NAMESPACE = "run"


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


NO_NARRATION = PartialState(
    "narration",
    "no narration record exists, so every page is silent",
    READING_FLOOR,
    "start the narration service and run again with --voice <voice>",
)

NO_NARRATION_SERVICE = PartialState(
    "narration-service",
    "no narration service answered, so nothing was synthesised",
    f"{READING_FLOOR}; clips recorded by an earlier run still play",
    "start the narration service and run again",
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
KNOWN = (NO_NARRATION, NO_NARRATION_SERVICE, NARRATION_INCOMPLETE, NO_EXERCISES, NO_TOOLCHAIN)


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
    """The narration states, from the narration run's exit code and report.

    `code` is `None` when no narration was asked for. ⛔ A run that did not
    finish is reported, never raised: the build that follows still reads.
    """
    if code is None or code == OK:
        return () if has_record else (NO_NARRATION,)
    if NO_SERVICE in said:
        return (NO_NARRATION_SERVICE,)
    return (NARRATION_INCOMPLETE,)


def exercise_states(declared: bool, namespaces: Iterable[str]) -> tuple[PartialState, ...]:
    """The exercise states, from the manifest's flag and what the serving process offers."""
    if not declared:
        return (NO_EXERCISES,)
    if EXECUTION_NAMESPACE not in set(namespaces):
        return (NO_TOOLCHAIN,)
    return ()
