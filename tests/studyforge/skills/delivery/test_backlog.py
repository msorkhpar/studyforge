"""Mirror of `src/studyforge/skills/delivery/backlog.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.skills.delivery import Backlog, Finding, Milestone, PlanRefused, Question
from studyforge.skills.delivery.finding import Claim
from tests.studyforge.skills.delivery import plans


def milestone(**overrides: object) -> Milestone:
    fields: dict[str, object] = {
        "id": "C1",
        "name": "the material reads",
        "gated_by": "M1",
        "tasks": (plans.reading_task("C-01"),),
    }
    fields.update(overrides)
    return Milestone(**fields)  # type: ignore[arg-type]


def test_a_whole_plan_checks_against_the_index():
    plan = plans.backlog().checked(plans.index())
    assert [m.id for m in plan.milestones] == ["C1", "C2"]
    assert plan.effort == 5


# --- SK08-A: the gate is declared, and the declaration is checked ----------


def test_a_milestone_gated_on_framework_work_and_declaring_nothing_is_refused():
    # ⛔ A plan that slips because a framework milestone slipped is a plan that
    # slipped for a reason nobody wrote down.
    plan = Backlog(
        corpus="a corpus",
        milestones=(
            milestone(gated_by=None, tasks=(plans.reading_task("C-01", depends_on=("SF-01",)),)),
        ),
        terminal=plans.terminal(),
    )
    with pytest.raises(PlanRefused, match="declares no framework gate"):
        plan.checked(plans.index())


def test_a_milestone_reaching_past_its_declared_gate_is_refused_by_capability():
    plan = Backlog(
        corpus="a corpus",
        milestones=(
            milestone(gated_by="M1", tasks=(plans.reading_task("C-01", depends_on=("SF-02",)),)),
        ),
        terminal=plans.terminal(),
    )
    with pytest.raises(PlanRefused, match="waits on SF-02, which lands at M2"):
        plan.checked(plans.index())


def test_the_gate_is_compared_in_the_declared_order_and_never_by_id():
    # ⛔ W238. The fixture runs `M6` before `M5`. By id `M5` < `M6`, so a gate
    # of `M6` would wrongly admit a task waiting on `SF-20`, which lands at `M5`
    # — AFTER the gate. And the other way round, a gate of `M5` admits it.
    def gated(gate: str) -> Backlog:
        waits = (plans.reading_task("C-01", depends_on=("SF-20",)),)
        return Backlog(
            corpus="a corpus",
            milestones=(milestone(gated_by=gate, tasks=waits),),
            terminal=plans.terminal(),
        )

    with pytest.raises(PlanRefused, match="gated by M6, .* waits on SF-20, which lands at M5"):
        gated("M6").checked(plans.index())
    assert gated("M5").checked(plans.index())


def test_a_milestone_that_waits_on_nothing_outside_needs_no_gate():
    # ⭐ The declaration is owed where the reach is, never everywhere.
    plan = Backlog(
        corpus="a corpus",
        milestones=(milestone(gated_by=None),),
        terminal=plans.terminal(),
    ).checked(plans.index())
    assert "⭐ nothing — this corpus alone" in "\n".join(plan.milestones[0].lines())


def test_a_dependency_on_a_task_nobody_carries_is_refused():
    plan = Backlog(
        corpus="a corpus",
        milestones=(milestone(tasks=(plans.reading_task("C-01", depends_on=("C-99",)),)),),
        terminal=plans.terminal(),
    )
    with pytest.raises(PlanRefused, match="neither in this plan nor a capability"):
        plan.checked(plans.index())


def test_a_dependency_on_a_later_milestones_task_is_refused():
    plan = plans.backlog(
        milestones=(
            Milestone("C1", "first", (plans.reading_task("C-01", depends_on=("C-02",)),), "M1"),
            Milestone("C2", "second", (plans.reading_task("C-02"),), "M1"),
        )
    )
    with pytest.raises(PlanRefused, match="waits on a task in a later milestone"):
        plan.checked(plans.index())


# --- the critical path is derived, never asserted --------------------------


def test_the_critical_path_is_the_heaviest_chain_and_not_the_longest():
    plan = plans.backlog(
        milestones=(
            Milestone(
                "C1",
                "first",
                (
                    plans.reading_task("C-01"),
                    plans.reading_task("C-02", effort=9),
                ),
                None,
            ),
            Milestone(
                "C2",
                "second",
                (
                    plans.reading_task("C-03", depends_on=("C-01",)),
                    plans.reading_task("C-04", depends_on=("C-02",)),
                ),
                None,
            ),
        )
    ).checked(plans.index())
    assert plan.critical_path() == ("C-02", "C-04")


def test_a_cycle_through_the_plans_own_tasks_is_refused():
    plan = plans.backlog(
        milestones=(
            Milestone(
                "C1",
                "first",
                (
                    plans.reading_task("C-01", depends_on=("C-02",)),
                    plans.reading_task("C-02", depends_on=("C-01",)),
                ),
                None,
            ),
        )
    )
    with pytest.raises(PlanRefused, match="depends on itself"):
        plan.critical_path()


def test_a_framework_dependency_is_not_walked_into_the_critical_path():
    # ⚠️ The path is a property of THIS plan; a capability's own chain belongs
    # to the framework's plan and would make every corpus's path the same.
    plan = plans.backlog().checked(plans.index())
    assert plan.critical_path() == ("C-01", "C-02")


# --- the shapes a document must not be able to take ------------------------


def test_a_milestone_with_no_tasks_lands_nothing():
    with pytest.raises(PlanRefused, match="lands nothing"):
        milestone(tasks=())


def test_a_backlog_with_no_milestones_delivers_nothing():
    with pytest.raises(PlanRefused, match="delivers nothing"):
        plans.backlog(milestones=())


def test_a_task_id_used_twice_is_refused_across_milestones():
    with pytest.raises(PlanRefused, match="task id is used twice — 1"):
        plans.backlog(
            milestones=(
                Milestone("C1", "first", (plans.reading_task("C-01"),), None),
                Milestone("C2", "second", (plans.reading_task("C-01"),), None),
            )
        )


def test_a_task_id_used_twice_inside_one_milestone_is_refused_by_the_milestone():
    with pytest.raises(PlanRefused, match="two tasks share an id"):
        milestone(tasks=(plans.reading_task("C-01"), plans.reading_task("C-01")))


def test_a_finding_id_used_twice_is_refused():
    twice = Finding("C-01/1", "local", "one thing", (Claim("counted", measured="here"),))
    with pytest.raises(PlanRefused, match="finding id is used twice — 1"):
        plans.backlog(findings=(twice, twice))


def test_the_questions_a_plan_carries_are_numbered_when_it_is_built():
    question = Question(2, "is it?", routed_at="SF-01", blocks=("C-01",), rerun="python3 -m x")
    with pytest.raises(Exception, match=r"\[2\]"):
        plans.backlog(questions=(question,))


def test_open_questions_are_the_ones_still_blocking_somebody():
    one = Question(1, "is it?", routed_at="SF-01", blocks=("C-01",), rerun="python3 -m x")
    two = Question(2, "and this?", routed_at="SF-01", blocks=("C-01",), rerun="python3 -m x")
    plan = plans.backlog(questions=(one, two.settled("yes", at="8146bdb")))
    assert [q.number for q in plan.open_questions] == [1]


# --- the document -----------------------------------------------------------


def test_the_document_carries_every_task_the_terminal_and_the_critical_path():
    plan = plans.backlog().checked(plans.index())
    text = "\n".join(plan.lines())
    assert "**Critical path.** C-01 → C-02" in text
    assert "## This corpus finishes at M2" in text
    for task in plan.tasks:
        assert f"### {task.id} —" in text


def test_the_document_carries_questions_and_findings_when_there_are_any():
    question = Question(1, "is it?", routed_at="SF-01", blocks=("C-01",), rerun="python3 -m x")
    found = Finding("C-01/1", "structural", "a wall", (Claim("hit it", measured="here"),))
    text = "\n".join(plans.backlog(questions=(question,), findings=(found,)).lines())
    assert "## Questions" in text and "## Findings" in text


def test_the_document_omits_the_two_sections_when_there_are_none():
    text = "\n".join(plans.backlog().lines())
    assert "## Questions" not in text and "## Findings" not in text
