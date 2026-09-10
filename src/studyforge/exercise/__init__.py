"""What a practice is: the workspace it runs in, and how much its verdict is trusted.

**What it does.** Defines the three states an exercise can be in, the workspace
a reader works in, and the trust attached to whatever checks their answer.

**How you use it.** Read an exercise from a practice archive document; ask what
state it is in before rendering anything that implies a grade.

    from studyforge.exercise import of, state_of, completes_practice

    state_of(None)                       # 'none' — the unit sets no work
    state_of(practice_document)          # 'ungraded' or 'graded'
    exercise = of(practice_document, where)   # an Exercise, or None
    completes_practice(state, "test", passed=True)

**Depends on.** `unit.trust`, which owns R5's rule and whose own contract says
*"SF-23 consumes it"*. ⛔ Not on `execute` — running a grader is a separate
concern from saying what a grader's word is worth. ⛔ Not on `render`: this
says what may be claimed, never how it is drawn.

⛔ **Three states, not two** (C5). *No exercise*; an **ungraded** exercise — a
prompt the reader works, with nothing to check it; and a **graded** exercise,
whose verdict is then `authoritative` or `advisory` (R5). Only the third can
complete a practice. Collapsing the middle state into "no exercise" discards
real teaching content: one surveyed corpus has an exercise in every one of its
19 lessons and a test for none of them.

⭐ **The three states are read off the structure and there is no `state` field**
— none to set, none to forget. **none** is no practice document at all;
**ungraded** is a practice document with no `exercise` key; **graded** is the
key being present. ⛔ A corpus that must declare its own emptiness is a contract
fitted to the one source that ships 168 graders (§11.0), and the common case
here writes nothing.

⛔ **Nothing generated is presented as more authoritative than it is** (R5). A
grader written by us against a hidden upstream grader is `advisory`. A grader
that shipped with the material and passes the gates is `authoritative`. The
framework refuses to render the first as the second — and it refuses in code,
at the point the record is read, so no consumer has to remember.

⛔ **Run and Submit are different acts, and the distinction is in the data.**
The record carries two commands, and only a passing `test` run completes a
practice. A unit document with one command could not stop a program that merely
printed from completing one.

⭐ **A corpus with no graders is complete, not short.** It finishes at the
reading floor, which is a whole product for prose material.

## What is in the package

| Module | Owns |
|---|---|
| `states` | the three states, the two acts, and what may complete a practice |
| `record` | `Exercise`, and reading one out of a practice document |
| `safety` | what a path and a command may be, checked before either reaches a file |
| `errors` | `ExerciseError`, the only exception any of it raises |

**Skeleton at FND-01.** Filled by SF-23 (E06).
"""

from __future__ import annotations

from studyforge.exercise.errors import ExerciseError
from studyforge.exercise.record import (
    DEFAULTED_KEYS,
    EXERCISE_KEYS,
    Exercise,
    from_document,
    of,
    to_document,
)
from studyforge.exercise.safety import (
    ARGUMENT_PERMITTED,
    PATH_PERMITTED,
    SAFE_ARGUMENT,
    SAFE_SEGMENT,
    require_command,
    require_path,
)
from studyforge.exercise.states import (
    COMMANDS,
    EXERCISE_KEY,
    GRADED,
    NONE,
    RUN,
    STATES,
    TEST,
    UNGRADED,
    completes_practice,
    state_of,
)

#: ⛔ The package's whole public surface. A consumer that has to import
#: `studyforge.exercise.record` directly is a consumer this contract failed —
#: `docs/conventions/module-structure.md` calls `__init__.py` the contract, and
#: this is what it says.
__all__ = [
    "ARGUMENT_PERMITTED",
    "COMMANDS",
    "DEFAULTED_KEYS",
    "EXERCISE_KEY",
    "EXERCISE_KEYS",
    "GRADED",
    "NONE",
    "PATH_PERMITTED",
    "RUN",
    "SAFE_ARGUMENT",
    "SAFE_SEGMENT",
    "STATES",
    "TEST",
    "UNGRADED",
    "Exercise",
    "ExerciseError",
    "completes_practice",
    "from_document",
    "of",
    "require_command",
    "require_path",
    "state_of",
    "to_document",
]
