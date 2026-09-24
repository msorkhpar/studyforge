"""Mirror of `src/studyforge/skills/exercises/plan.py` (R12) — the plan, by aspects.

**What it asserts.** That a page is planned by its ASPECTS and not by its
length: one planned exercise per distinct name
the aspects give, each carrying the aspects it checks, with no ceiling; that a
plan of zero says why; and that the same aspects always produce the same plan
(R10). ⛔ **And the half R6 turns on:** a page cannot ship past its plan, and a
gap that ships fewer is named with a gate `exercise.gates` actually declares.

⭐ **The positive control is a real page**, planned through `plan_page` over a
ledger taken on disk: the code-dense `DENSE` page and the runnable fixture's
greeting page, both of which the withdrawn length band planned at zero.

**Depends on.** `studyforge.exercise.gates` for the one gate registry, the
package under test, and the shared pages.
"""

from __future__ import annotations

import pytest

from studyforge.address import Address
from studyforge.exercise import CODE
from studyforge.exercise.gates import G1, G3, registered
from studyforge.skills.exercises import (
    ADVANCED,
    CORE,
    PLAN_API,
    PLAN_KEYS,
    PLANNED_KEYS,
    TIERS,
    Aspect,
    AspectError,
    AuthoringError,
    Page,
    Plan,
    PlanError,
    Refusal,
    plan_document,
    plan_for,
    plan_page,
    shortfall,
    shortfall_document,
    take,
)
from tests.studyforge.skills.exercises.pages import DENSE, fixture_corpus, written

#: What a gate said when it refused. A sentence, because a reader is shown it.
SAID = "the starter passed one of the tests, so that test is vacuous"

#: A written reason an aspect is not checked, worded as a minor aspect's is.
MINOR = "incidental detail, not practised"


def aspect(ident, exercise=None, reason=None, says=None):
    """An aspect with a sentence of its own, read from a heading."""
    return Aspect(ident, says or f"the reader can do {ident}", ("section:Body",), exercise, reason)


#: Three aspects, two of which one exercise checks together.
THREE = (aspect("b", "second"), aspect("a", "first"), aspect("c", "first"))


def dense_page(aspects, nothing_checkable=None, path="dense.md"):
    return Page(path, Address(["kata"]), "python", 1, CODE, aspects, CORE, (), nothing_checkable)


#: ⭐ What an author reads off `DENSE`: four ideas, two practised together, and
#: the setup snippet carried by a short reason — never an exercise per fence.
DENSE_ASPECTS = (
    Aspect("reads-a-field", "a field is read by its position", ("example:dense.md:1",), "field"),
    Aspect("missing", "a missing field is an error", ("example:dense.md:2",), "field"),
    Aspect("numbers", "a numeric field is converted", ("example:dense.md:3",), "number"),
    Aspect("trims", "a field's padding is trimmed", ("example:dense.md:4",), "trim"),
    Aspect("setup", "the environment is set up", ("example:dense.md:5",), reason=MINOR),
)


def test_one_planned_exercise_per_distinct_name_each_carrying_its_aspects():
    plan = plan_for(THREE, CORE, "the plan")
    assert [(p.slot, p.name, p.aspects) for p in plan.exercises] == [
        (1, "first", ("a", "c")),
        (2, "second", ("b",)),
    ]
    assert plan.count == 2
    assert [a.id for a in plan.checked_by(plan.exercises[0])] == ["a", "c"]


def test_there_is_no_length_ceiling_the_count_is_the_aspects():
    many = tuple(aspect(f"idea-{n:02d}", f"exercise-{n:02d}") for n in range(40))
    assert plan_for(many, CORE, "the plan").count == 40


def test_every_aspect_reasoned_plans_zero_and_each_reason_is_visible():
    plan = plan_for((aspect("a", reason=MINOR), aspect("b", reason=MINOR)), CORE, "the plan")
    assert plan.count == 0
    assert [a.id for a in plan.reasoned] == ["a", "b"]
    assert all(row["reason"] == MINOR for row in plan_document(plan)["aspects"])


def test_a_page_teaching_nothing_checkable_plans_zero_and_says_why():
    plan = plan_for((), CORE, "the plan", nothing_checkable="the page is a list of links")
    assert plan.count == 0
    assert plan_document(plan)["nothing_checkable"] == "the page is a list of links"
    with pytest.raises(AspectError, match="says nothing about why"):
        plan_for((), CORE, "the plan")


def test_an_aspect_left_neither_covered_nor_reasoned_is_refused():
    with pytest.raises(AspectError, match="checked by no exercise and carries no"):
        plan_for((*THREE, aspect("d")), CORE, "the plan")


def test_the_tier_is_recorded_and_never_moves_the_count():
    counts = {tier: plan_for(THREE, tier, "the plan").count for tier in TIERS}
    assert set(counts.values()) == {2}, counts
    assert plan_document(plan_for(THREE, ADVANCED, "the plan"))["tier"] == ADVANCED


def test_a_tier_this_build_does_not_define_is_refused_rather_than_defaulted():
    for bad in ("middling", "", None, 2):
        with pytest.raises(PlanError) as refusal:
            plan_for(THREE, bad, "the plan")
        assert "tier" in str(refusal.value)


def test_re_planning_the_same_aspects_in_any_order_writes_the_same_document():
    """⛔ R10: the plan is an input to a build that must be byte-reproducible."""
    first = plan_document(plan_for(THREE, CORE, "the plan"))
    second = plan_document(plan_for(tuple(reversed(THREE)), CORE, "a different where"))
    assert first == second
    assert first["plan_api"] == PLAN_API == 2
    assert tuple(first) == PLAN_KEYS
    assert all(tuple(row) == PLANNED_KEYS for row in first["exercises"])


def test_shipping_everything_the_plan_allowed_needs_no_shortfall():
    plan = plan_for(THREE, CORE, "the plan")
    assert shortfall(plan, plan.count, (), "the report") == ()


def test_shipping_past_the_plan_is_refused_because_a_plan_is_not_a_quota():
    plan = plan_for(THREE, CORE, "the plan")
    with pytest.raises(PlanError) as refusal:
        shortfall(plan, plan.count + 1, (), "the report")
    assert "ceiling, never a quota" in str(refusal.value)


def test_a_gap_with_nothing_said_about_it_is_refused():
    plan = plan_for(THREE, CORE, "the plan")
    with pytest.raises(PlanError) as refusal:
        shortfall(plan, plan.count - 1, (), "the report")
    assert "unaccounted for" in str(refusal.value)


def test_a_gap_named_with_the_gate_that_refused_it_is_accepted():
    """⭐ The positive control beside the two refusals above."""
    plan = plan_for(THREE, CORE, "the plan")
    refusals = (Refusal(G3, SAID),)
    assert shortfall(plan, plan.count - 1, refusals, "the report") == refusals
    assert shortfall_document(refusals) == [{"gate": G3, "says": SAID}]


def test_a_shortfall_citing_a_gate_no_family_declares_is_refused():
    plan = plan_for(THREE, CORE, "the plan")
    declared = {gate for family in registered() for gate in family.gates}
    unknown = next(f"G{n}" for n in range(6, 99) if f"G{n}" not in declared)
    for bad in (unknown, "", None, 1):
        with pytest.raises(PlanError) as refusal:
            shortfall(plan, plan.count - 1, (Refusal(bad, SAID),), "the report")
        assert "gate" in str(refusal.value)


def test_a_shortfall_with_nothing_the_gate_said_is_refused():
    plan = plan_for(THREE, CORE, "the plan")
    for bad in ("", "   ", None):
        with pytest.raises(PlanError):
            shortfall(plan, plan.count - 1, (Refusal(G1, bad),), "the report")


def test_a_plan_is_frozen_so_a_recorded_aspect_cannot_be_edited_after_the_fact():
    plan = plan_for(THREE, CORE, "the plan")
    assert isinstance(plan, Plan)
    with pytest.raises(AttributeError):
        plan.exercises = ()


# --- the positive control, on real pages ------------------------------------


def test_a_code_dense_page_the_band_planned_at_zero_is_planned_by_its_aspects(tmp_path):
    """⭐ The positive control: little prose, five fences, three exercises."""
    ledger = take(tmp_path, (written(tmp_path, "dense.md", DENSE),), (), "the ledger")
    plan = plan_page(dense_page(DENSE_ASPECTS), ledger, "the plan")
    assert [(p.name, p.aspects) for p in plan.exercises] == [
        ("field", ("missing", "reads-a-field")),
        ("number", ("numbers",)),
        ("trim", ("trims",)),
    ]
    assert [a.id for a in plan.reasoned] == ["setup"]


def test_the_runnable_fixtures_greeting_is_planned_by_the_code_it_carries():
    root = fixture_corpus()
    path = "kata/01-greeting.md"
    ledger = take(root, (path,), (), "the ledger")
    greets = Aspect(
        "greets", "greet returns the greeting for a name", (f"example:{path}:1",), "greet"
    )
    starts = Aspect("script", "the module runs as a script", (f"example:{path}:2",), "greet")
    plan = plan_page(dense_page((greets, starts), path=path), ledger, "the plan")
    assert plan.count == 1 and plan.exercises[0].aspects == ("greets", "script")


def test_a_basis_the_page_does_not_carry_is_refused_when_the_page_is_planned(tmp_path):
    ledger = take(tmp_path, (written(tmp_path, "dense.md", DENSE),), (), "the ledger")
    for basis in ("example:dense.md:9", "section:Absent", "tests:dense.md"):
        stray = Aspect("stray", "a stray idea", (basis,), "field")
        with pytest.raises(AuthoringError, match="stray"):
            plan_page(dense_page((*DENSE_ASPECTS, stray)), ledger, "the plan")
