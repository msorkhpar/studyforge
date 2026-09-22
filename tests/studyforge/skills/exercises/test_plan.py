"""Mirror of `src/studyforge/skills/exercises/plan.py` (R12) — `AX-07`'s second half.

**What it asserts.** That a page's count stays inside the band its length sets,
that **every movement is recorded as a reason**, that a plan of zero says why,
and that the same three readings always produce the same plan (R10). ⛔ **And
the half R6 turns on:** a page cannot ship past its ceiling, and a gap that
ships fewer is named with a gate `exercise.gates` actually declares.

⚠️ **The band table is read from `BANDS` and the counts are asserted as
PROPERTIES** — inside the band, moved by a recorded reason — rather than by
typing today's numbers in. ⛔ A test spelling `3` would pin the convention
instead of the rule, and the convention is the part that is allowed to move.

**Depends on.** `studyforge.exercise.gates` for the one gate registry, and the
package under test.
"""

from __future__ import annotations

import pytest

from studyforge.exercise.gates import G1, G3, registered
from studyforge.skills.exercises.plan import (
    ADVANCED,
    BANDS,
    CORE,
    INTRODUCTORY,
    PLAN_API,
    TIERS,
    Plan,
    PlanError,
    Refusal,
    band_for,
    plan_document,
    plan_for,
    shortfall,
    shortfall_document,
)

#: A length inside every band above the stub, so a case is not silently a stub.
LENGTHS = tuple(band.words for band in BANDS if band.ceiling)

#: What a gate said when it refused. A sentence, because a reader is shown it.
SAID = "the starter passed one of the tests, so that test is vacuous"


def every_case():
    """Every (words, skills, tier) this module's own vocabulary admits, bounded."""
    return [
        (words, skills, tier)
        for words in (0, 1, *LENGTHS, 10_000)
        for skills in (0, 1, 2, 5, 40)
        for tier in TIERS
    ]


def test_a_plans_count_never_leaves_its_bands_bounds():
    """⛔ The property, over the whole vocabulary — not one worked example."""
    for words, skills, tier in every_case():
        plan = plan_for(words, skills, tier, "the plan")
        assert plan.band is band_for(words), "the band is the page's length's"
        assert 0 <= plan.count <= plan.band.ceiling, (
            f"{(words, skills, tier)} planned {plan.count} past {plan.band}"
        )
        if skills:
            assert plan.count >= plan.band.floor, "a page with work starts at the floor"
        else:
            assert plan.count == 0, "a page with no checkable skill plans none"


def test_every_movement_is_recorded_and_the_reasons_add_up_to_the_count():
    """⭐ A recorded reason is checkable arithmetic, not a note beside the number."""
    for words, skills, tier in every_case():
        plan = plan_for(words, skills, tier, "the plan")
        moved = plan.band.floor + sum(reason.moves for reason in plan.reasons)
        assert moved == plan.count, f"{(words, skills, tier)}: the reasons do not add up"
        assert plan.reasons, "a plan with no recorded reason is a number nobody can argue with"
        assert all(reason.says.strip() for reason in plan.reasons)


def test_the_first_reason_is_always_the_band_the_length_set():
    plan = plan_for(900, 3, CORE, "the plan")
    assert plan.band.name in plan.reasons[0].says
    assert str(plan.words) in plan.reasons[0].says


def test_a_page_whose_plan_is_zero_says_why():
    short = plan_for(0, 5, ADVANCED, "the plan")
    assert short.count == 0
    assert any("too short" in reason.says for reason in short.reasons)
    unteachable = plan_for(max(LENGTHS), 0, ADVANCED, "the plan")
    assert unteachable.count == 0
    assert any("no distinct checkable skill" in reason.says for reason in unteachable.reasons)


def test_the_clamp_is_itself_a_recorded_reason():
    """⛔ A ceiling that silently ate a movement is a ceiling nobody can see working."""
    plan = plan_for(max(LENGTHS), 40, ADVANCED, "the plan")
    clamps = [reason for reason in plan.reasons if "permits" in reason.says and reason.moves]
    assert clamps, "the movements overran the band and nothing recorded the clamp"
    assert plan.count == plan.band.ceiling


def test_the_tier_moves_the_count_and_the_three_tiers_do_not_agree():
    counts = {
        tier: plan_for(max(LENGTHS), 2, tier, "the plan").count
        for tier in (INTRODUCTORY, CORE, ADVANCED)
    }
    assert counts[INTRODUCTORY] < counts[CORE] < counts[ADVANCED], counts


def test_more_distinct_checkable_skills_never_plan_fewer_exercises():
    for words in LENGTHS:
        counts = [plan_for(words, skills, CORE, "the plan").count for skills in range(0, 12)]
        assert counts == sorted(counts), f"{words} words: more skills planned fewer"


def test_a_tier_this_build_does_not_define_is_refused_rather_than_defaulted():
    for bad in ("middling", "", None, 2):
        with pytest.raises(PlanError) as refusal:
            plan_for(500, 2, bad, "the plan")
        assert "tier" in str(refusal.value)


def test_a_reading_that_is_not_a_count_of_things_is_refused():
    for bad in (-1, 1.5, "3", None, True):
        with pytest.raises(PlanError):
            plan_for(bad, 2, CORE, "the plan")
        with pytest.raises(PlanError):
            plan_for(500, bad, CORE, "the plan")


def test_re_planning_the_same_page_writes_the_same_document(tmp_path):
    """⛔ R10: the plan is an input to a build that must be byte-reproducible."""
    first = plan_document(plan_for(900, 3, CORE, "the plan"))
    second = plan_document(plan_for(900, 3, CORE, "a different where"))
    assert first == second
    assert first["plan_api"] == PLAN_API
    assert first["band"] == band_for(900).name


def test_the_document_carries_every_reading_the_count_came_from():
    document = plan_document(plan_for(900, 3, CORE, "the plan"))
    assert document["words"] == 900 and document["skills"] == 3 and document["tier"] == CORE
    assert [set(reason) for reason in document["reasons"]] == [
        {"moves", "says"} for _ in document["reasons"]
    ]


def test_shipping_everything_the_plan_allowed_needs_no_shortfall():
    plan = plan_for(900, 3, CORE, "the plan")
    assert shortfall(plan, plan.count, (), "the report") == ()


def test_shipping_past_the_ceiling_is_refused_because_a_plan_is_not_a_quota():
    plan = plan_for(900, 3, CORE, "the plan")
    with pytest.raises(PlanError) as refusal:
        shortfall(plan, plan.count + 1, (), "the report")
    assert "ceiling, never a quota" in str(refusal.value)


def test_a_gap_with_nothing_said_about_it_is_refused():
    plan = plan_for(900, 3, CORE, "the plan")
    with pytest.raises(PlanError) as refusal:
        shortfall(plan, plan.count - 1, (), "the report")
    assert "unaccounted for" in str(refusal.value)


def test_a_gap_named_with_the_gate_that_refused_it_is_accepted():
    """⭐ The positive control beside the two refusals above."""
    plan = plan_for(900, 3, CORE, "the plan")
    refusals = (Refusal(G3, SAID),)
    assert shortfall(plan, plan.count - 1, refusals, "the report") == refusals
    assert shortfall_document(refusals) == [{"gate": G3, "says": SAID}]


def test_a_shortfall_citing_a_gate_no_family_declares_is_refused():
    plan = plan_for(900, 3, CORE, "the plan")
    declared = {gate for family in registered() for gate in family.gates}
    unknown = next(f"G{n}" for n in range(6, 99) if f"G{n}" not in declared)
    for bad in (unknown, "", None, 1):
        with pytest.raises(PlanError) as refusal:
            shortfall(plan, plan.count - 1, (Refusal(bad, SAID),), "the report")
        assert "gate" in str(refusal.value)


def test_a_shortfall_with_nothing_the_gate_said_is_refused():
    plan = plan_for(900, 3, CORE, "the plan")
    for bad in ("", "   ", None):
        with pytest.raises(PlanError):
            shortfall(plan, plan.count - 1, (Refusal(G1, bad),), "the report")


def test_the_bands_are_ordered_and_reach_every_length():
    assert [band.words for band in BANDS] == sorted(band.words for band in BANDS)
    assert BANDS[0].words == 0, "every length must fall in a band"
    assert all(band.floor <= band.ceiling for band in BANDS)
    assert band_for(0) is BANDS[0] and band_for(10**9) is BANDS[-1]


def test_a_plan_is_frozen_so_a_recorded_reason_cannot_be_edited_after_the_fact():
    plan = plan_for(900, 3, CORE, "the plan")
    assert isinstance(plan, Plan)
    with pytest.raises(AttributeError):
        plan.count = 99
