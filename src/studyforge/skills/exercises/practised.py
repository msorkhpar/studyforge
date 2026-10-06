r"""What one shipped exercise practises, read back off its unit's coverage report.

**What it does.** Answers, for one committed exercise, the sentences of the
aspects its plan gave it to check — what a reader is told on its card before
opening it — by reading the unit's `coverage.json` against the rule that
shipped it.

**How you use it.** An adapter's join calls it for each bundle it emits, and
writes the answer into the exercise record's `concepts`:

    practised(root, places)          # ('a negative index counts back', …) or None

**Depends on.** `archive.scrub` for the personal-data gate every decoded
document passes (R7), this package's `coverage` for the report's name and the
versions it is read at, and `loop.quiz_last` for the drafting order;
`studyforge.version`.
Standard library otherwise. ⛔ No write.

## ⭐ THE REPORT NAMES WHAT SHIPPED, AND THE PLAN NAMES WHAT EACH CHECKS

⚠️ **The report does not pair a bundle with its planned exercise**: `shipped`
lists bundles in the order they shipped, and the plan lists exercises in plan
order. ⭐ The loop drafts in `quiz_last` order and a shortfall ships nothing,
so the planned exercises that shipped, in that order, pair with `shipped` one
for one. ⛔ **A count that does not match refuses** rather than pairing the
wrong sentences with a practice.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.archive.scrub import assert_clean
from studyforge.exercise.bundle import Places
from studyforge.skills.exercises.coverage import COVERAGE_FILENAME, COVERAGE_READ
from studyforge.skills.exercises.drafts import AuthoringError
from studyforge.skills.exercises.loop import quiz_last
from studyforge.skills.exercises.plan import PLAN_API
from studyforge.version import check


def practised(root: Path | str, places: Places) -> tuple[str, ...] | None:
    """Return what the exercise at `places` was planned to check, or `None` without a report.

    ⭐ The aspects' own sentences, in the plan's aspect order. ⛔ A report that
    will not read, at a version this build does not read, or whose shipped list
    does not pair with its plan, is refused naming the unit.
    """
    unit = places.bundle.rsplit("/", 1)[0]
    where = f"the coverage report of '{unit}'"
    path = Path(root) / unit / COVERAGE_FILENAME
    if not path.is_file():
        return None
    try:
        report = json.loads(path.read_text(encoding="utf-8"))
    except OSError, UnicodeDecodeError, ValueError:
        raise _unreadable(where) from None
    assert_clean(report, where)
    try:
        plan = report["plan"]
        check("coverage_api", report.get("coverage_api"), COVERAGE_READ, where=where,
              error=AuthoringError)  # fmt: skip
        check("plan_api", plan.get("plan_api"), (PLAN_API,), where=where, error=AuthoringError)
        says = {aspect["id"]: aspect["says"] for aspect in plan["aspects"]}
        missed = {entry["slot"] for entry in report.get("shortfalls", ())}
        drafted = quiz_last(plan["exercises"], report.get("quiz"), lambda one: one["name"])
        shipped = [one for one in drafted if one["slot"] not in missed]
        bundles = list(report["shipped"])
    except AuthoringError:
        raise
    except ValueError, KeyError, TypeError, AttributeError:
        raise _unreadable(where) from None
    if len(bundles) != len(shipped):
        raise AuthoringError(
            f"{where} lists {len(bundles)} shipped exercise(s) against {len(shipped)} its "
            f"plan shipped, so no practice can be paired with what it checks."
        )
    for bundle, planned in zip(bundles, shipped, strict=True):
        if bundle == places.bundle:
            return tuple(says[aspect] for aspect in planned["aspects"])
    return None


def _unreadable(where: str) -> AuthoringError:
    """Return the refusal of a report that will not read as one."""
    return AuthoringError(f"{where} will not read, so what it planned cannot be said.")
