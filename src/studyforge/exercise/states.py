"""The three states, read off the structure, and what may complete a practice.

**What it does.** Answers "what state is this unit's practice in" from the
files that exist, and "may this run complete the practice" from the state and
the act.

**How you use it.** `state_of(document)` where `document` is the practice
archive document or `None`; `completes_practice(state, command, passed=...)`.

**Depends on.** Nothing.

## ⛔ There is no `state` field, and that is the design

⭐ **The three states fall out of the structure with no flag to remember**
(spec §7, C5):

| State | How it appears | The designed shape that is this |
|---|---|---|
| **none** | no `practice-M.json` at all | one shape: 38 units, none written |
| **ungraded** | a practice document, **no `exercise` key** | a second: 19 prompts, no workspace |
| **graded** | the `exercise` key is present | the first consumer — the **exception** |

⚠️ **The three shapes are named in `docs/tasks/E06-exercise-contract.md`, which
holds this table with its corpora attached.** ⛔ Not here: R1 binds framework
source and a document is the far end of the pointer, which is what lets the
measurement survive without the framework knowing whose it is.

⛔ **A corpus that must declare its own emptiness is a contract fitted to the
one source that ships 168 graders** (§11.0). The common case writes nothing:
one shape writes no practice document, another writes a prompt with no
workspace, and neither has a field to fill in or forget. ⚠️ A `state` field
would also be a second source of truth, and the day it disagreed with the files
the framework would have to decide which to believe.

⭐ **Ungraded is why three rather than two.** All 19 lessons of that second
shape end in an exercise and none ships a test. Recording those as "no
exercise" would delete real teaching content to satisfy a two-state model; they
are presented as work, marked unchecked, and they complete nothing.

## ⛔ Run and Submit are different acts, in the data

⚠️ **If a document carried one command, nothing downstream could stop a program
that merely printed from completing a practice.** So the record carries two,
and completion asks which act this was. Inherited verbatim from the extraction
source's progress rules and not negotiable: a program that printed successfully
has demonstrated nothing about its tests.
"""

from __future__ import annotations

#: The unit sets no work: there is no practice document.
NONE = "none"

#: A prompt the reader works, with nothing to check it.
UNGRADED = "ungraded"

#: A workspace plus a grader, `authoritative` or `advisory` (R5).
GRADED = "graded"

#: In increasing order of what the reader is offered.
STATES = (NONE, UNGRADED, GRADED)

#: The two acts. ⚠️ `TEST` is what the reader's page calls **Submit**; the
#: record's field is `test_command`, so the vocabulary follows the data rather
#: than the button.
RUN = "run"
TEST = "test"
COMMANDS = (RUN, TEST)

#: ⛔ The key whose presence *is* the graded state. Named once, here, so that
#: `archive.document` and this module cannot come to spell it differently.
EXERCISE_KEY = "exercise"


def state_of(document: object) -> str:
    """Return the state of a unit's practice, from what exists rather than a flag.

    `document` is the decoded practice archive document, or `None` when the
    unit has no practice document at all — which is the common case and the
    reason this function takes `None` rather than refusing it.
    """
    if document is None:
        return NONE
    if isinstance(document, dict) and EXERCISE_KEY in document:
        return GRADED
    return UNGRADED


def completes_practice(state: object, command: object, *, passed: object) -> bool:
    """May this run complete the practice? ⛔ Only a passing grader run, on a graded exercise.

    ⚠️ **Three conditions, and each one is a real failure mode.** An ungraded
    exercise has nothing that could pass (§7's table). A `run` has demonstrated
    that a program printed, not that it is right. And a failing grader run is
    the case the whole apparatus exists to report.

    ⭐ Returns `False` rather than raising for anything it does not recognise:
    this is asked on the completion path, and a caller that had to catch an
    exception to learn "no" is a caller that will eventually not catch it and
    complete a practice on an error.
    """
    return state == GRADED and command == TEST and passed is True
