"""Mirror of `src/studyforge/skills/exercises/practised.py` (R12).

⭐ What a card says a practice practises is read back off its unit's coverage
report, by the order that shipped it. ⛔ The pairing is the whole risk: a report
lists bundles in the order they SHIPPED, the plan lists exercises in PLAN order,
and a reader told the wrong practice's ideas is told something false.
"""

from __future__ import annotations

import json

import pytest

from studyforge.address import Address
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.exercise.bundle import Places
from studyforge.skills.exercises import AuthoringError, practised
from studyforge.skills.exercises.corpus import COVERAGE_API, COVERAGE_FILENAME
from studyforge.skills.exercises.plan import PLAN_API


def places(ordinal: int) -> Places:
    """Where the unit's practice number `ordinal` sits."""
    return Places(Address(["demo"]), "python", 1, ordinal)


#: The unit's report: three planned, the quiz planned FIRST and drafted last,
#: the middle code exercise refused — so plan order, drafting order and shipped
#: order are three different orders.
PLAN = {
    "plan_api": PLAN_API,
    "tier": "small",
    "count": 3,
    "aspects": [
        {"id": "a1", "says": "a negative index counts back"},
        {"id": "a2", "says": "a slice copies"},
        {"id": "a3", "says": "an empty list is falsy"},
    ],
    "exercises": [
        {"slot": 1, "name": "gauge", "aspects": ["a3"]},
        {"slot": 2, "name": "refused", "aspects": ["a2"]},
        {"slot": 3, "name": "count-back", "aspects": ["a1", "a2"]},
    ],
    "nothing_checkable": [],
}


def report(root, **over) -> None:
    """Write the unit's coverage report under `root`, overridable."""
    document = {
        "coverage_api": COVERAGE_API,
        "page": "lessons/lists.md",
        "kind": "code",
        "quiz": "gauge",
        "plan": PLAN,
        "shipped": [places(1).bundle, places(2).bundle],
        "shortfalls": [{"slot": 2, "gate": "G2", "says": "refused", "output": ""}],
        **over,
    }
    unit = places(1).bundle.rsplit("/", 1)[0]
    (root / unit).mkdir(parents=True, exist_ok=True)
    (root / unit / COVERAGE_FILENAME).write_text(json.dumps(document), encoding="utf-8")


def test_each_shipped_practice_is_paired_with_what_its_plan_checks(tmp_path):
    report(tmp_path)
    # ⭐ Code first, the quiz last, the refused slot skipped: the first bundle
    # is the plan's THIRD exercise and the second is its FIRST.
    assert practised(tmp_path, places(1)) == ("a negative index counts back", "a slice copies")
    assert practised(tmp_path, places(2)) == ("an empty list is falsy",)


def test_a_unit_with_no_report_says_nothing_and_a_bundle_it_did_not_ship_says_nothing(tmp_path):
    assert practised(tmp_path, places(1)) is None
    report(tmp_path)
    assert practised(tmp_path, places(3)) is None


def test_a_report_whose_shipped_list_does_not_pair_with_its_plan_is_refused(tmp_path):
    # ⛔ One bundle more than the plan shipped: pairing anyway would shift every
    # practice's ideas onto its neighbour.
    report(tmp_path, shipped=[places(1).bundle, places(2).bundle, places(3).bundle])
    with pytest.raises(AuthoringError, match="3 shipped exercise"):
        practised(tmp_path, places(1))


@pytest.mark.parametrize("over", [{"plan": {}}, {"coverage_api": 99}, {"shipped": None}])
def test_a_report_that_will_not_read_is_refused_naming_the_unit(tmp_path, over):
    report(tmp_path, **over)
    with pytest.raises(AuthoringError, match="coverage report of 'exercises/demo/python/unit-01'"):
        practised(tmp_path, places(1))


def test_a_report_carrying_personal_data_is_refused_by_the_gate_without_it(tmp_path):
    # ⛔ R7: every decoded document passes the gate, and what a card would say
    # is read straight off this one.
    leaky = "voicebox" + ".local"
    plan = {
        **PLAN,
        "aspects": [{**PLAN["aspects"][0], "says": f"ask {leaky}"}, *PLAN["aspects"][1:]],
    }
    report(tmp_path, plan=plan)
    with pytest.raises(PersonalDataLeak) as refused:
        practised(tmp_path, places(1))
    assert leaky not in str(refused.value)
