"""Rubric §1f, made behavioural: no refusal reproduces what it refused.

**What it does.** Poisons a synthetic absolute path into every string-shaped
parameter of every public callable in `studyforge`, and reports each one whose
exception message reproduces it. A second pass hands every `Path` parameter a
real absolute path and asserts no refusal reproduces a directory from it.

**How you use it.** `census("studyforge")` returns a `Census`;
`tests/test_emission.py` is what fails the build on it. Run it alone with
`python3 -m pytest tests/test_emission.py -q`.

**Depends on.** `fillers`, `probe`, and the standard library. It imports the
package under test by name and knows nothing else about it.

## ⛔ Why this replaces a reviewer reading raise-lines (Ruling 13)

§1f asks a reviewer to read every message a diff adds and ask whether the value
being formatted *could* be a path. ⚠️ **That rule has now missed a site twice**
— once in round 15, two lines from the defect it did catch. ⭐ A rule a machine
can check should not be a rule a person checks: this has no AST, no heuristic
and **no false positives by construction**, because it fails only when a
refusal really does reproduce what it was handed.

## ⛔ Where it lives, and why not in `tools/quality`

`handoffs/SF-03.md` proposed this beside the R7 sweep. ⚠️ Two reasons it is
here instead, and the second is a collision:

1. `tools/quality` declares it depends on **the standard library and nothing
   else, ever**, and is deliberately independent of the framework so that a
   broken `studyforge` still lints. This check must *import and call*
   `studyforge`, so filing it there would make the lint tool fail on any
   import error in the tree it is linting.
2. ⛔ `FND-07` is registering in `tools.quality.CHECKS` — the same five-entry
   tuple — and two agents in one tuple is C5 with a contract instead of a line
   length. Nothing here touches that tuple.

⭐ The gate is unchanged either way: `tests/test_quality_floor.py` shows the
suite is already how the floor fails a build, so `pytest` alone still catches
this and no contributor has a second command to remember.

## ⭐ What the check does **not** claim, said here rather than discovered later

⚠️ **It sees what a public callable emits when called directly.** A refusal
raised deep inside a document reader, reached only by a whole valid document
with one bad field, is not probed — the framework has roughly forty-five such
`{value!r}` sites left and they are recorded as a finding in
`docs/tasks/handoffs/W1-W2.md`, not held here. ⛔ **A check that overstated its
coverage would be worse than this one**; `Census.report` prints what it
reached, and a lower bound on that count is asserted so a refactor cannot
quietly shrink it to nothing.
"""

from __future__ import annotations

from tests.emission.fillers import UNFILLABLE, filler_for
from tests.emission.probe import (
    LABEL_PARAMETERS,
    POISON,
    POISON_DIRECTORY,
    Census,
    Echo,
    Unreached,
    census,
    probe_callable,
    public_callables,
)

__all__ = [
    "LABEL_PARAMETERS",
    "POISON",
    "POISON_DIRECTORY",
    "UNFILLABLE",
    "Census",
    "Echo",
    "Unreached",
    "census",
    "filler_for",
    "probe_callable",
    "public_callables",
]
