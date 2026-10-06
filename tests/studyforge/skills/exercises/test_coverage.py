"""Mirror of `src/studyforge/skills/exercises/coverage.py` (R12) — one report, still true or stale.

**What it asserts.** `stale_of` answers `None` for a report that still
describes its unit and names each of the four reasons otherwise, in
`REASONS` order; a changed contract has no plan to compare; a stale unit
names its practice counterpart; and the summary line is said only when
something is stale.
"""

from __future__ import annotations

import pytest

from studyforge.skills.exercises import (
    COVERAGE_API,
    REASONS,
    STALE_COMMAND,
    Stale,
    stale_of,
    stale_summary,
)
from studyforge.skills.exercises.coverage import CONTRACT, PAGE, PLAN, SOURCES, TESTS

UNIT = "exercises/kata/python/unit-03"
PAGE_PATH = "lessons/three.md"
TESTS_PATH = "tests/test_three.py"
DIGESTS = {PAGE_PATH: "sha256:aa", TESTS_PATH: "sha256:bb"}
PLAN_DOCUMENT = {"plan_api": 2, "tier": "core", "count": 0, "aspects": [], "exercises": []}


def _recorded(**changes) -> dict:
    recorded = {
        "coverage_api": COVERAGE_API,
        "page": PAGE_PATH,
        "kind": "code",
        "quiz": None,
        "digests": dict(DIGESTS),
        "plan": dict(PLAN_DOCUMENT),
    }
    recorded.update(changes)
    return recorded


def _stale(recorded=None, digests=None, planned=None):
    return stale_of(
        UNIT,
        _recorded() if recorded is None else recorded,
        PAGE_PATH,
        DIGESTS if digests is None else digests,
        {"plan": PLAN_DOCUMENT} if planned is None else planned,
    )


def test_a_report_that_still_describes_its_unit_is_not_stale():
    assert _stale() is None


@pytest.mark.parametrize(
    ("digests", "reason"),
    [
        ({PAGE_PATH: "sha256:moved", TESTS_PATH: "sha256:bb"}, PAGE),
        ({PAGE_PATH: None, TESTS_PATH: "sha256:bb"}, PAGE),
        ({PAGE_PATH: "sha256:aa", TESTS_PATH: "sha256:moved"}, TESTS),
        ({PAGE_PATH: "sha256:aa", TESTS_PATH: None}, TESTS),
        ({PAGE_PATH: "sha256:aa"}, TESTS),
        ({**DIGESTS, "tests/test_new.py": "sha256:cc"}, TESTS),
    ],
    ids=["page-edited", "page-gone", "tests-edited", "tests-gone", "tests-dropped", "tests-added"],
)
def test_a_moved_file_is_named_by_what_it_was_to_the_unit(digests, reason):
    stale = _stale(digests=digests)
    assert stale is not None and stale.reasons == (reason,), stale


def test_a_page_the_report_never_digested_is_a_moved_page():
    recorded = _recorded(digests={TESTS_PATH: "sha256:bb"})
    assert _stale(recorded, digests={PAGE_PATH: "sha256:aa", TESTS_PATH: "sha256:bb"}).reasons == (
        PAGE,
    )


@pytest.mark.parametrize(
    "planned",
    [
        {"plan": {**PLAN_DOCUMENT, "tier": "advanced"}},
        {"plan": None},
        {"plan": PLAN_DOCUMENT, "quiz": "check"},
        {"plan": PLAN_DOCUMENT, "kind": "quiz"},
    ],
    ids=["replanned", "no-longer-plans", "quiz-named", "kind-changed"],
)
def test_a_plan_that_is_not_the_plan_now_is_a_moved_plan(planned):
    assert _stale(planned=planned).reasons == (PLAN,)


@pytest.mark.parametrize(
    ("recorded", "says"),
    [
        (_recorded(coverage_api=3), "coverage_api 3"),
        (_recorded(coverage_api=None), "no coverage_api"),
        (_recorded(plan={**PLAN_DOCUMENT, "plan_api": 1}), "plan_api 1"),
    ],
    ids=["coverage-3", "coverage-absent", "plan-1"],
)
def test_a_contract_this_build_does_not_keep_is_named_with_its_version(recorded, says):
    # ⛔ A plan written under another `plan_api` has no plan to compare: the
    # contract is the reason, never a plan that "moved".
    stale = _stale(recorded, planned={"plan": {"something": "else"}})
    assert stale.reasons == (CONTRACT,) and says in stale.detail, stale
    assert says in stale.says


def test_a_version_one_report_is_still_kept():
    assert _stale(_recorded(coverage_api=1)) is None


def test_every_reason_is_named_once_in_reasons_order():
    stale = _stale(
        _recorded(coverage_api=3),
        digests={PAGE_PATH: "sha256:moved", TESTS_PATH: None},
    )
    assert stale.reasons == (PAGE, TESTS, CONTRACT)
    assert list(REASONS) == [PAGE, TESTS, SOURCES, PLAN, CONTRACT]
    assert stale.says.startswith(f"{REASONS[PAGE]}; {REASONS[TESTS]}; {REASONS[CONTRACT]}")


def test_a_stale_unit_names_its_practice_counterpart_as_the_second_folder():
    stale = Stale(UNIT, (PAGE,))
    assert stale.practice == "practice/kata/python/unit-03"
    assert stale.folders == (UNIT, "practice/kata/python/unit-03")


def test_the_summary_line_is_said_only_when_something_is_stale():
    one = Stale(UNIT, (PAGE,))
    assert stale_summary(()) == ""
    assert stale_summary([one]) == f"1 authored unit is stale; run `{STALE_COMMAND}`"
    assert (
        stale_summary([one, one]) == "2 authored units are stale; run `studyforge exercises stale`"
    )
