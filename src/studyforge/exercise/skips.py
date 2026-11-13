"""A case that may skip: the capability it names, and how a report says it skipped.

**What it does.** Reads a case's one optional key, `skips_without`, the name
of a capability (`gpu`) whose absence makes the case's test skip itself, and
says whether a JUnit testcase was skipped and nothing else.

**How you use it.** `cases` reads the key with `skips_without_of(value, kind,
where)`; `report` asks `skipped_only(element, passing)` of each testcase of a
case that carries it.

**Depends on.** `errors` for the one exception, `describe` for naming a value
without reproducing it (R7), and the standard library.

## ⛔ Opt-in, per case, and never the ask

⭐ **A practice whose test runs only where a GPU is present declares it**:
`"skips_without": "gpu"` on that case. A report that marks such a case skipped
leaves it out of the count, and the grade is carried by the rest
(`report.Breakdown.skipped_ids`). ⛔ **Strict by default**: a case without the
key that is skipped did not pass, exactly as before; a skippable case that
failed failed; and the main ask may never carry the key, because a grade with
no ask is no grade.

⚠️ **The test decides when it skips**, and this module trusts nothing else: a
test that declares `skips_without` skips itself only when that capability is
absent (`pytest.mark.skipif(not gpu_available(), ...)`). A case skipped for any
reason reads the same in a report.

⚠️ **The gates say what they could not prove.** `G1`, `G2` and `G4` leave a
skipped case out and say how many; `G3` cannot prove an edge whose test did not
run, says which, and refuses when no edge at all was proven. Run the gates where
the capability is present to prove every case.

⭐ The key is written only when set, so every record written without it is
unchanged.
"""

from __future__ import annotations

import re
from collections.abc import Collection
from xml.etree import ElementTree

from studyforge.describe import describe
from studyforge.exercise.errors import ExerciseError

#: The one optional key of a case: the capability whose absence lets its test skip.
SKIPS_WITHOUT = "skips_without"

#: What a capability's name may be: a short lowercase token, such as `gpu`.
CAPABILITY = re.compile(r"\A[a-z][a-z0-9-]{0,31}\Z")

#: The child a testcase its test tool skipped carries.
SKIPPED = "skipped"

#: The case kind that may never skip. ⚠️ Spelled here as `cases.MAIN` spells it, since
#: `cases` imports this module.
_MAIN = "main"


def skips_without_of(value: dict, kind: str, where: str) -> str | None:
    """Read the capability a case may skip without, or `None`; refuse it on the main ask."""
    if SKIPS_WITHOUT not in value:
        return None
    named = value[SKIPS_WITHOUT]
    if not isinstance(named, str) or not CAPABILITY.match(named):
        raise ExerciseError(
            f"{where}: a case's {SKIPS_WITHOUT!r} names a capability, a lowercase token "
            f"of letters, digits and '-' up to 32 characters, such as 'gpu'. The value "
            f"is {describe(named)}."
        )
    if kind == _MAIN:
        raise ExerciseError(
            f"{where}: the {_MAIN!r} case carries {SKIPS_WITHOUT!r}. The main ask is "
            f"what a grade is of, so it always runs; only an edge or a kept case may skip."
        )
    return named


def skipped_only(element: ElementTree.Element, passing: Collection[str]) -> bool:
    """Was this testcase skipped and nothing else? ⛔ A skip beside a failure is a failure."""
    tags = [child.tag for child in element]
    return SKIPPED in tags and all(tag == SKIPPED or tag in passing for tag in tags)
