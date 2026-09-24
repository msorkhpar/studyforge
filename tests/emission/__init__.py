"""A refusal never echoes the value (R7), made behavioural: no refusal reproduces what it refused.

**What it does.** Poisons a synthetic absolute path into every string-shaped
parameter of every public callable in `studyforge`, and reports each one whose
exception message reproduces it. A second pass hands every `Path` parameter a
real absolute path and asserts no refusal reproduces a directory from it.

**How you use it.** `census("studyforge")` returns a `Census`;
`tests/test_emission.py` is what fails the build on it. Run it alone with
`python3 -m pytest tests/test_emission.py -q`.

**Depends on.** `fillers`, `probe`, and the standard library. It imports the
package under test by name and knows nothing else about it.

## ⛔ Why a sweep and not a reviewer reading raise-lines

A reviewer reading every message a diff adds, asking whether the value being
formatted *could* be a path, misses sites. ⭐ A rule a machine
can check should not be a rule a person checks: this has no AST, no heuristic
and **no false positives by construction**, because it fails only when a
refusal really does reproduce what it was handed.

## ⛔ Where it lives, and why not in the quality floor

The obvious home was beside the floor's R7 sweep. ⚠️ Two reasons it is
here instead, and the second is a collision:

1. The floor (`tests/floor/`) depends on **the standard library and nothing
   else, ever**, and is deliberately independent of the framework so that a
   broken `studyforge` still gets its floor read. This check must *import and
   call* `studyforge`, so filing it there would make the floor fail on any
   import error in the tree it is reading.
2. ⛔ `tests.floor.CHECKS` is the floor's own registration tuple, and two
   owners of one tuple is C5 with a contract instead of a line length. Nothing
   here touches that tuple.

⭐ The gate is unchanged either way: the suite is already how a build fails,
so `pytest` alone still catches this and no contributor has a second command
to remember.

## ⭐ What the check does **not** claim, said here rather than discovered later

⚠️ **It sees what a public callable emits when called directly.** A refusal
raised deep inside a document reader, reached only by a whole valid document
with one bad field, is not probed — the framework has roughly forty-five such
`{value!r}` sites left, and they are not held here. ⛔ **A check that overstated its
coverage would be worse than this one**; `Census.report` prints what it
reached, and `Census.walked` names it — ⭐ **asserted against the modules the
package ships on disk, so the coverage claim is measured against the tree and
never against a figure typed on a day that has passed**.
"""

from __future__ import annotations

from tests.emission.fillers import UNFILLABLE, filler_for
from tests.emission.probe import (
    LABEL_PARAMETERS,
    POISON,
    POISON_DIRECTORY,
    POISON_ROOT,
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
    "POISON_ROOT",
    "UNFILLABLE",
    "Census",
    "Echo",
    "Unreached",
    "census",
    "filler_for",
    "probe_callable",
    "public_callables",
]
