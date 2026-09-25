"""The honest partial states: each one says what is missing and what still works.

**What it does.** Names the states a site can be served in short of
everything, and derives which of them hold from the verbs' own answers: the
narration run's exit code and report, the plan's narration creations, the
manifest's `exercises` flag, the namespaces the serving process offers, and
`execute`'s own answer to where a run would execute.

**How you use it.** `narration_states(code, said, has_record=...)` and
`exercise_states(declared, namespaces, probe)` each return a tuple of
`PartialState`; `probe_for(root, source)` is the probe to hand the second;
`recorded(plan)` answers whether a narration record names any clip.
`PartialState.lines()` is what the skill prints.

**Depends on.** `cli.narrate.report.NO_SERVICE`, imported so the no-service
sentence is never respelled, `serve.routes.run.NAMESPACE` for the execution
namespace's one spelling, `validate.report.OK`, and this package's
`narration` for what provides narration and how to have it, and
`studyforge.execute` for `ModeProbe`, `recorded` and `HOST` — the one
definition of where a run executes, imported and never copied. ⛔ It
reads answers and opens nothing; the one question it asks is that probe's, which
reads (`docker inspect`) and never starts, stops or enters a container.

## ⛔ None of these is an error (R6, R8)

⭐ Each state is data with a stated consequence, and none of them changes an exit
code. The reading floor still works in every one of them.

## ⛔ *CANNOT NARRATE* AND *HAS NOT NARRATED* ARE TWO STATES, NOT ONE

⚠️ **As one state, a clean run of the skills that produced a corpus with no
narration at all would be reported** beside `exercises`, whose whole point is
that it **is** a legitimate finished state (C5).

⭐ **The two are told apart by the narration run's own answer, and by nothing
this module had to go and read:**

| what happened | the state | finished? |
|---|---|---|
| narration was never run | `narration` | ⛔ **no** — nor is it known whether it could speak |
| it ran and placed no clip | `narration-none` | ⭐ **yes**: there was nothing to say aloud |

⛔ So a corpus that could narrate and did not is never reported as complete, and
a corpus with nothing to narrate is never sent to start a service it does not
need.

## ⭐ NARRATION OFF IS A CHOICE, AND A CHOICE IS NOT A PARTIAL STATE

⭐ Narration is optional: a reader may cover the course without voices. A run
with narration off — the
author's `corpus.json` answer or the operator's `--no-narration` — reports none
of the narration states above: `NARRATION_OFF` is one plain line saying what was
chosen and what was kept, and it is not a `partial` block. ⛔ **Nothing here
calls it short**; the reading floor is complete (C5).

## ⛔ WHERE A RUN EXECUTES IS A STATE OF ITS OWN (R15)

⭐ Every served form registers the `run` namespace (`serve.instance.namespaces_of`
builds it for both), so a site that declares exercises always answers Run and
Submit. ⚠️ **What varies is WHERE**: with no runner container up over this
corpus, `execute` runs a reader's code on the host, without the runner's
isolation. That is `host`, reported whenever the served instance offers
execution and `execute`'s probe answers `HOST`.

⛔ **There is no `toolchain` state**: it would name a serving process that
offers no execution, and no served form lacks the namespace.
"""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import studyforge.serve.routes.run as run
from studyforge.cli.narrate.report import NO_SERVICE
from studyforge.execute import HOST, ModeProbe, declares_runner
from studyforge.execute import recorded as recorded_names
from studyforge.skills.buildserve import narration
from studyforge.validate.report import OK

#: What works in every partial state. ⭐ R8: a built site opens with nothing running.
READING_FLOOR = (
    "reading pages, navigation, contents and progress; the site also opens "
    "from its index.html with nothing running"
)

#: The namespace a serving process offers once it can run a reader's code. ⭐ The
#: framework's own `serve.routes.run.NAMESPACE`, the name `serve.instance.instance_of`
#: registers and `studyforge serve --site` registers too:
#: this package holds no spelling of its own.
EXECUTION_NAMESPACE = run.NAMESPACE

#: ⭐ What a run with narration off says once the site is listening. ⛔ Not
#: a `partial` line: a choice is not a shortfall, and the reading floor is whole.
NARRATION_OFF = (
    "narration off  chosen: no page carries a player and no clip is served; every "
    "recorded clip stays on disk, and a run with --narration plays it again"
)

#: ⛔ Why a `--voice` with narration off is refused before anything runs.
VOICE_UNHEARD = (
    "narration is off for this run, so --voice would synthesise clips it does not "
    "serve; drop --voice, or run with --narration"
)


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
#: never from a declaration: `corpus.json`'s `narration` says whether to
#: voice a corpus, never whether it has anything to say.
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

#: Where a reader starts the containers: the corpus's own document, and the
#: section of it that holds the one command. ⭐ That command reads both tags
#: the execution skill recorded, so a remedy that pointed anywhere else would
#: start images the corpus never recorded.
START_DOCUMENT = "EXECUTION.md"
START_SECTION = "Bring it up"

#: ⭐ Its remedy points at the corpus's own command. ⛔ Not finished in the C5
#: sense — it has a remedy.
HOST_EXECUTION = PartialState(
    "host",
    "no runner container is up over this corpus, so Run and Submit execute on this "
    "host, without the runner's isolation",
    f"everything: Run and Submit answer on this host; {READING_FLOOR}",
    f'start the runner and the editor with the one command under "{START_SECTION}" in '
    f"this corpus's {START_DOCUMENT}, run from the corpus's root, then serve again",
)

#: ⛔ A corpus that DECLARES its runner never runs on the host
#: (`execute.Runner(required=True)`), so with that runner down nothing runs, and
#: the page offers no Run, Submit or Run tests. The remedy is the same command.
RUNNER_DOWN = PartialState(
    "runner",
    "this corpus declares its runner and it is not up over this corpus, so Run, Submit "
    "and an example's test run nowhere; each page hides them and says why",
    f"everything but running code: {READING_FLOOR}",
    HOST_EXECUTION.remedy,
)

#: ⭐ Every state, in the order the skill prints them.
KNOWN = (
    NOT_NARRATED,
    NOTHING_TO_NARRATE,
    NO_NARRATION_SERVICE,
    NARRATION_INCOMPLETE,
    NO_EXERCISES,
    HOST_EXECUTION,
    RUNNER_DOWN,
)


class Probe(Protocol):
    """What `exercise_states` asks: `execute`'s `ModeProbe`, or a test's stand-in."""

    def mode(self) -> str:
        """`CONTAINER` or `HOST`, as the next run would take it."""
        ...


def probe_for(root: Path | str, source: str) -> ModeProbe:
    """Return `execute`'s own probe for corpus `source` at `root`.

    ⭐ The same container name and root the served instance's runner is built
    from (`serve.routes.runs.runner_for`): the name THIS checkout recorded,
    so the skill asks the question a run asks. ⛔ Nothing is asked until `mode()`.
    """
    where = Path(root).absolute()
    return ModeProbe(where, recorded_names(where, source).runner)


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


def exercise_states(
    declared: bool, namespaces: Iterable[str], probe: Probe
) -> tuple[PartialState, ...]:
    """Return the exercise states, from the manifest flag, the server and the probe.

    ⭐ `host` holds when the served instance offers execution and the probe answers
    `HOST` for a corpus that declares no runner; `runner` holds instead for one
    that declares it, whose runs then go nowhere. ⛔ The probe is asked only then: a corpus with no exercises, or a
    server offering no execution, runs nothing, so where it would run is moot.
    """
    if not declared:
        return (NO_EXERCISES,)
    if EXECUTION_NAMESPACE in set(namespaces) and probe.mode() == HOST:
        root = getattr(probe, "source_root", None)
        return (RUNNER_DOWN,) if root is not None and declares_runner(root) else (HOST_EXECUTION,)
    return ()
