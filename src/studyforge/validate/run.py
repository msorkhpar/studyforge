r"""One pass: read the corpus, run every check, drain them into one report.

**What it does.** Joins the walk to the checks. It is the only place that
knows the full list, so "which checks does `validate` run" has one answer.

**How you use it.** `validate(root) -> Report`. ⛔ It never raises for an
invalid corpus — an invalid corpus is a *result*, and a caller that had to
catch an exception to learn the verdict could not report ten problems at once.

**Depends on.** `validate.corpus`, `validate.structure`, `validate.source`,
`validate.report`.

⭐ **The check list is data, so it is assertable.** `tests` asserts that every
rule id the tool can emit appears in `RULES`, which means a check added without
a rule id, or a rule id nobody can produce, is a test failure rather than a
surprise in somebody's CI log.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from studyforge.validate import source, structure
from studyforge.validate.corpus import Walk, read
from studyforge.validate.report import Finding, Report, Unchecked

#: Every check, in the order a report reads best. ⛔ One list, so the answer to
#: "what does validate check" is not spread across four modules.
CHECKS = (*structure.CHECKS, *source.CHECKS)


def validate(root: Path | str) -> Report:
    """Run every check over one corpus root and return what they found."""
    return Report.of(_run(read(Path(root))))


def _run(walk: Walk) -> Iterator[Finding | Unchecked]:
    yield from walk.findings
    if walk.manifest is None:
        # ⛔ Without a manifest nothing else can be judged, and saying so is
        # not the same as saying the archive is fine (R6's sibling).
        yield Unchecked(
            "corpus", ".", "the manifest did not parse, so no other check could run"
        )
        return
    for item in walk.refused:
        if item.container is None:
            # ⛔ A container map that would not parse takes its documents with
            # it. Saying so is not the same as saying they are fine.
            yield Unchecked(
                "document",
                item.where,
                "this container map did not parse, so no document beneath it was read",
            )
    for check in CHECKS:
        yield from check(walk)
