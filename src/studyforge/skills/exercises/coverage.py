r"""A unit's coverage report: its name, the versions it is read at, and whether it went stale.

**What it does.** Names the report each authored unit carries beside its
bundles, and answers one question about a committed one: ⭐ **does it still
describe its unit?** A unit whose report no longer does is *stale*, and
`stale_of` says why, by one of four reasons: its page moved, a test file it
was authored from moved, its plan moved, or its report is at a contract
version this build does not keep.

**How you use it.**

    found = stale_of(unit, recorded, page, digests, {"plan": plan_document(plan)})
    found.reasons                   # ('page',) — in `REASONS` order
    found.folders                   # the unit's folder and its practice counterpart
    stale_summary(stale)            # '2 authored units are stale; run …', or ''

**Depends on.** `drafts` for the refusal, `plan` for `PLAN_API`,
`exercise.bundle` for the bundles' root, `corpus.placement` for the
workspaces' root, and `studyforge.version`. Standard library only. ⛔ No read
and no write: the caller hands over what it read.

## ⭐ ONE ANSWER, ASKED BY THE PASS AND BY THE COMMAND

⭐ **The pass and `studyforge exercises stale` ask the same function**, so the
two cannot disagree about whether a unit is stale. The pass hands over what
it read for the page now — its digests and its plan from the author's
aspects. The command holds only the corpus, so it hands over the digests of
the files the report names and the plan its own aspects give.

## ⛔ A STALE UNIT IS TWO FOLDERS, AND BOTH GO

⚠️ **The pass refuses a workspace file that exists with other bytes**, so a
unit's bundles removed without its workspace files leave the next pass
refused on the reader's starter. ⭐ `Stale.folders` names both.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass

from studyforge.corpus.placement import PRACTICE_DIRNAME
from studyforge.exercise.bundle import BUNDLES_DIRNAME
from studyforge.skills.exercises.drafts import AuthoringError
from studyforge.skills.exercises.plan import PLAN_API
from studyforge.version import check

#: Each unit's coverage report, beside its bundles and never inside one.
COVERAGE_FILENAME = "coverage.json"

#: The coverage report's version, and its key order (R10). ⚠️ **2** added
#: `quiz`, the planned exercise a quiz checks on a code page. ⭐ A version-1
#: report is still read, as a page that named no quiz, so a unit authored
#: before it is kept rather than authored again (`COVERAGE_READ`).
COVERAGE_API = 2
COVERAGE_KEYS = (
    "coverage_api",
    "page",
    "kind",
    "quiz",
    "case",
    "digests",
    "sources",
    "plan",
    "shipped",
    "accounts",
    "shortfalls",
)

#: ⭐ The coverage reports this build reads back: every one it has written.
COVERAGE_READ = (1, COVERAGE_API)

#: The keys of one named shortfall in a coverage report, in write order.
SHORTFALL_REPORT_KEYS = ("slot", "gate", "says", "output")

#: The unit's page no longer digests to what its report recorded, or is gone.
PAGE = "page"

#: A test file the unit was authored from no longer digests to what was recorded.
TESTS = "tests"

#: A file the unit's exercises were copied from (a try-it file, a starter, a reference, a
#: statement, a check script) no longer digests to what was recorded, or is gone.
SOURCES = "sources"

#: The plan the unit was authored against is not the plan its page gets now.
PLAN = "plan"

#: The report is at a `coverage_api` or `plan_api` this build does not keep.
CONTRACT = "contract"

#: ⛔ Closed, and in the order a unit's reasons are listed. Each says why.
REASONS = {
    PAGE: "its page has since moved",
    TESTS: "a test file it was authored from has since moved",
    SOURCES: "a file its exercises were copied from (try-it, starter, reference, statement) has since moved",
    PLAN: "its plan has since moved",
    CONTRACT: "its coverage report is at a contract version this build does not keep",
}

#: The command that lists every stale unit, named by the summary line.
STALE_COMMAND = "studyforge exercises stale"


@dataclass(frozen=True, slots=True)
class Stale:
    """One authored unit whose report no longer describes it, and every reason why.

    ⭐ `detail` is the version refusal when a contract changed, else empty.
    """

    unit: str
    reasons: tuple[str, ...]
    detail: str = ""

    @property
    def practice(self) -> str:
        """The unit's practice counterpart: the reader's workspace files, which go with it."""
        return PRACTICE_DIRNAME + self.unit.removeprefix(BUNDLES_DIRNAME)

    @property
    def folders(self) -> tuple[str, str]:
        """The two folders a stale unit is removed by, relative to the corpus root."""
        return (self.unit, self.practice)

    @property
    def says(self) -> str:
        """Every reason in one clause, with the version refusal where there is one."""
        said = "; ".join(REASONS[reason] for reason in self.reasons)
        return f"{said} ({self.detail})" if self.detail else said


def stale_of(
    unit: str,
    recorded: dict,
    page: str,
    digests: Mapping[str, str | None],
    planned: Mapping[str, object],
    sources: Mapping[str, str | None] | None = None,
) -> Stale | None:
    """Return why `recorded` no longer describes its unit, or `None` when it still does.

    `digests` is what the page and its test files digest to now, by path,
    `None` for one that will not read. `planned` holds the report's keys the
    plan is compared on — `plan`, and `kind` and `quiz` where the caller
    knows them. ⛔ A report at another version has no plan to compare.
    `sources` is what the files the unit is copied from digest to now, by
    path. ⭐ A report that recorded no `sources` key was authored before they
    were tracked: it is never stale for them (`untracked`), and `sources` is
    then ignored.
    """
    detail = _contract(recorded)
    written = recorded.get("digests")
    written = written if isinstance(written, dict) else {}
    found = []
    if recorded.get("page") != page or page not in written or written[page] != digests.get(page):
        found.append(PAGE)
    if _tests(written, page) != _tests(digests, page):
        found.append(TESTS)
    tracked = recorded.get("sources")
    if isinstance(tracked, dict) and sources is not None and tracked != dict(sources):
        found.append(SOURCES)
    if not detail and any(recorded.get(key) != value for key, value in planned.items()):
        found.append(PLAN)
    if detail:
        found.append(CONTRACT)
    return Stale(unit, tuple(found), detail) if found else None


def untracked(recorded: dict) -> bool:
    """Whether a code unit was authored before the files it is copied from were tracked.

    ⭐ Its report has no `sources` key, so a change to a try-it file cannot be seen
    for it. A quiz copies nothing, so it is never untracked.
    """
    return recorded.get("kind") == "code" and "sources" not in recorded


def untracked_summary(count: int) -> str:
    """Return the one line that says how many units are not tracked, or `''`."""
    if count <= 0:
        return ""
    return f"{count} unit(s) authored before try-it tracking; re-author to track them"


def stale_summary(stale: Sequence[Stale]) -> str:
    """Return the one line the pass and the build say up front, or `''` when nothing is stale."""
    if not stale:
        return ""
    count = (
        f"{len(stale)} authored unit is" if len(stale) == 1 else f"{len(stale)} authored units are"
    )
    return f"{count} stale; run `{STALE_COMMAND}`"


def _tests(digests: Mapping[str, object], page: str) -> dict[str, object]:
    """Every file but the page, by path: the test files a unit was authored from."""
    return {path: digest for path, digest in digests.items() if path != page}


def _contract(recorded: dict) -> str:
    """Return the version refusal for a report this build does not keep, or `''`."""
    written = recorded.get("plan")
    versions = (
        ("coverage_api", recorded.get("coverage_api"), COVERAGE_READ),
        ("plan_api", written.get("plan_api") if isinstance(written, dict) else None, (PLAN_API,)),
    )
    for contract, declared, speaks in versions:
        try:
            check(contract, declared, speaks, where="its coverage report", error=AuthoringError)
        except AuthoringError as refused:
            return str(refused)
    return ""
