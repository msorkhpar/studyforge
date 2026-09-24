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
        "tasks": (plans.reading_task("C-01"),),
    }
    fields.update(overrides)
    return Milestone(**fields)  # type: ignore[arg-type]


#: A finding a plan files when it needs a capability the offer does not list.
MISSING = Finding(
    "C-01/1",
    "structural",
    "the framework cannot read a slide deck",
    (Claim("no offered capability reads one", measured="here"),),
)


def test_a_whole_plan_checks_against_the_offer():
    plan = plans.backlog().checked(plans.offer())
    assert [m.id for m in plan.milestones] == ["C1", "C2"]
    assert plan.effort == 5


# --- a task names what the installed framework offers, or a finding -----------


def test_a_plan_uses_exactly_the_offered_capabilities_its_tasks_name():
    assert plans.backlog().used(plans.offer()) == {plans.READ, plans.RENDER}


def test_a_dependency_nobody_offers_is_refused_and_the_refusal_says_to_file_a_finding():
    # ⛔ A task waiting on a capability the installed framework lacks is a plan
    # that slips for a reason nobody wrote down.
    plan = plans.backlog(
        milestones=(milestone(tasks=(plans.reading_task("C-01", depends_on=("tool slides",)),)),),
    )
    with pytest.raises(PlanRefused, match="A capability the framework lacks is filed as a finding"):
        plan.checked(plans.offer())


def test_a_task_waiting_on_a_filed_finding_is_admitted_and_counted():
    # ⭐ The wait is written down: the finding is filed and the task names it.
    plan = plans.backlog(
        milestones=(
            milestone(tasks=(plans.reading_task("C-01", depends_on=(plans.READ, MISSING.id)),)),
            Milestone("C2", "renders", (plans.reading_task("C-02", depends_on=(plans.RENDER,)),)),
        ),
        findings=(MISSING,),
    ).checked(plans.offer())
    assert [task.id for task in plan.waiting] == ["C-01"]
    assert "1 tasks waiting on a finding against the framework" in "\n".join(plan.lines())


def test_a_milestone_declares_no_framework_gate():
    # ⛔ The installed framework is the whole of what a plan may use, so there
    # is no later framework to wait for and nothing to gate on.
    text = "\n".join(milestone().lines())
    assert "Gated" not in text
    assert not hasattr(milestone(), "gated_by")


def test_the_terminal_is_checked_against_what_the_tasks_use():
    # ⛔ An offered capability no task uses and the terminal does not name is
    # the one the planner forgot; the backlog refuses it.
    plan = plans.backlog(
        milestones=(milestone(tasks=(plans.reading_task("C-01", depends_on=(plans.READ,)),)),),
    )
    with pytest.raises(PlanRefused, match="neither used by a task nor accounted for — tool render"):
        plan.checked(plans.offer())


def test_a_dependency_on_a_task_nobody_carries_is_refused():
    plan = plans.backlog(
        milestones=(
            milestone(tasks=(plans.reading_task("C-01", depends_on=("C-99",)),)),
            Milestone("C2", "renders", (plans.reading_task("C-02", depends_on=(plans.RENDER,)),)),
        ),
    )
    with pytest.raises(PlanRefused, match="neither a task of this plan"):
        plan.checked(plans.offer())


def test_a_dependency_on_a_later_milestones_task_is_refused():
    plan = plans.backlog(
        milestones=(
            Milestone(
                "C1", "first", (plans.reading_task("C-01", depends_on=("C-02", plans.READ)),)
            ),
            Milestone("C2", "second", (plans.reading_task("C-02", depends_on=(plans.RENDER,)),)),
        )
    )
    with pytest.raises(PlanRefused, match="waits on a task in a later milestone"):
        plan.checked(plans.offer())


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
            ),
            Milestone(
                "C2",
                "second",
                (
                    plans.reading_task("C-03", depends_on=("C-01",)),
                    plans.reading_task("C-04", depends_on=("C-02",)),
                ),
            ),
        )
    )
    assert plan.critical_path() == ("C-02", "C-04")


def test_a_cycle_through_the_plans_own_tasks_is_refused():
    # ⛔ BOTH tasks are on this cycle, so both are counted. A guard
    # inside the walk raised on whichever one it entered first.
    plan = plans.backlog(
        milestones=(
            Milestone(
                "C1",
                "first",
                (
                    plans.reading_task("C-01", depends_on=("C-02",)),
                    plans.reading_task("C-02", depends_on=("C-01",)),
                ),
            ),
        )
    )
    with pytest.raises(PlanRefused) as refused:
        plan.critical_path()
    assert str(refused.value) == ("2 tasks depend on themselves, through this plan's own tasks")


def test_one_task_on_a_cycle_reads_exactly_as_it_did():
    # ⭐ The other direction (R12): the singular sentence did not move.
    plan = plans.backlog(
        milestones=(Milestone("C1", "first", (plans.reading_task("C-01", depends_on=("C-01",)),)),)
    )
    with pytest.raises(PlanRefused) as refused:
        plan.critical_path()
    assert str(refused.value) == "a task depends on itself, through this plan's own tasks"


def test_every_cycle_is_counted_and_not_only_the_one_the_walk_entered_first():
    # ⛔ Two DISJOINT cycles: a depth-first guard reports the first it reaches
    # and the reader never learns the second one is there.
    plan = plans.backlog(
        milestones=(
            Milestone(
                "C1",
                "first",
                (
                    plans.reading_task("C-01", depends_on=("C-02",)),
                    plans.reading_task("C-02", depends_on=("C-01",)),
                    plans.reading_task("C-03", depends_on=("C-04",)),
                    plans.reading_task("C-04", depends_on=("C-03",)),
                    plans.reading_task("C-05"),
                ),
            ),
        )
    )
    with pytest.raises(PlanRefused, match="4 tasks depend on themselves"):
        plan.critical_path()


# --- `checked` names every contradiction it found ----------


def test_every_contradiction_in_a_plan_is_named_not_the_first():
    # ⛔ Three things are wrong and one run says so.
    plan = Backlog(
        corpus="a corpus",
        milestones=(
            Milestone(
                "C1",
                "first",
                (
                    plans.reading_task("C-01", depends_on=(plans.READ,)),
                    plans.reading_task("C-02", depends_on=("C-99",)),
                ),
            ),
            Milestone("C2", "second", (plans.reading_task("C-04", depends_on=("C-05",)),)),
            Milestone("C3", "third", (plans.reading_task("C-05"),)),
        ),
        terminal=plans.terminal(),
    )
    with pytest.raises(PlanRefused) as refused:
        plan.checked(plans.offer())
    message = str(refused.value)
    assert "3 refusals" in message
    assert "neither used by a task nor accounted for — tool render" in message
    assert "neither a task of this plan" in message
    assert "waits on a task in a later milestone" in message


def test_one_contradiction_reads_as_one_sentence():
    # ⭐ The other direction (R12): no count and no preamble over one reason.
    plan = plans.backlog(
        milestones=(
            milestone(tasks=(plans.reading_task("C-01", depends_on=("C-99", plans.READ)),)),
            Milestone("C2", "renders", (plans.reading_task("C-02", depends_on=(plans.RENDER,)),)),
        ),
    )
    with pytest.raises(PlanRefused) as refused:
        plan.checked(plans.offer())
    assert str(refused.value) == (
        "a task waits on something that is neither a task of this plan, nor a capability the "
        "installed framework offers, nor a finding this plan files. ⛔ A capability the "
        "framework lacks is filed as a finding, and the task waits on the finding"
    )


def test_a_framework_dependency_is_not_walked_into_the_critical_path():
    # ⚠️ The path is a property of THIS plan; a capability belongs to the
    # framework and would make every corpus's path the same.
    plan = plans.backlog().checked(plans.offer())
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
                Milestone("C1", "first", (plans.reading_task("C-01"),)),
                Milestone("C2", "second", (plans.reading_task("C-01"),)),
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
    question = Question(2, "is it?", routed_at="C-01", blocks=("C-01",), rerun="python3 -m x")
    with pytest.raises(Exception, match=r"\[2\]"):
        plans.backlog(questions=(question,))


def test_open_questions_are_the_ones_still_blocking_somebody():
    one = Question(1, "is it?", routed_at="C-01", blocks=("C-01",), rerun="python3 -m x")
    two = Question(2, "and this?", routed_at="C-01", blocks=("C-01",), rerun="python3 -m x")
    plan = plans.backlog(questions=(one, two.settled("yes", at="8146bdb")))
    assert [q.number for q in plan.open_questions] == [1]


# --- the document -----------------------------------------------------------


def test_the_document_carries_every_task_the_terminal_and_the_critical_path():
    plan = plans.backlog().checked(plans.offer())
    text = "\n".join(plan.lines())
    assert "**Critical path.** C-01 → C-02" in text
    assert "## This corpus finishes at the reading floor" in text
    for task in plan.tasks:
        assert f"### {task.id} —" in text


def test_the_document_carries_questions_and_findings_when_there_are_any():
    question = Question(1, "is it?", routed_at="C-01", blocks=("C-01",), rerun="python3 -m x")
    found = Finding("C-01/1", "structural", "a wall", (Claim("hit it", measured="here"),))
    text = "\n".join(plans.backlog(questions=(question,), findings=(found,)).lines())
    assert "## Questions" in text and "## Findings" in text


def test_the_document_omits_the_two_sections_when_there_are_none():
    text = "\n".join(plans.backlog().lines())
    assert "## Questions" not in text and "## Findings" not in text
