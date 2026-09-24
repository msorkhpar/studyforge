"""Mirror of `src/studyforge/skills/delivery/task.py` (R12)."""

from __future__ import annotations

import pytest

from studyforge.skills.delivery import Acceptance, PlanRefused, Task
from tests.studyforge.skills.delivery import plans


def test_a_task_that_ends_in_a_layer_is_refused():
    # ⛔ "the parser is written" is not a task. The refusal names why, because
    # a planner who is told only "invalid" writes a longer version of the same
    # sentence.
    with pytest.raises(PlanRefused, match="shown"):
        plans.reading_task(demonstrable="done")


def test_a_task_with_no_acceptance_is_refused():
    with pytest.raises(PlanRefused, match="nobody can close it"):
        plans.reading_task(acceptance=())


def test_a_task_may_own_nothing_when_it_states_the_evidence_it_produces():
    # ⭐ SK08-D: the expected shape as the generators improve, not a degenerate
    # one. A template that assumes the integrator WRITES things describes a
    # framework whose skills do not work yet.
    task = plans.reading_task(owns=(), evidence="a re-run that changes no byte")
    assert task.owns_nothing
    assert "⭐ nothing" in "\n".join(task.lines())


def test_a_task_that_owns_nothing_and_states_no_evidence_is_refused():
    with pytest.raises(PlanRefused, match="owns nothing and states no evidence"):
        plans.reading_task(owns=())


def test_effort_below_one_is_not_work_anybody_does():
    with pytest.raises(PlanRefused, match="which is not work anybody does"):
        plans.reading_task(effort=0)


def test_a_task_with_no_id_or_no_title_is_refused():
    with pytest.raises(PlanRefused, match="id and a title"):
        plans.reading_task(title="  ")


# --- acceptance: exactly one instrument, always ----------------------------


def test_a_clause_decided_by_nobody_is_refused():
    # ⛔ "the pages look right" is a task nobody can close and everybody can
    # argue about.
    with pytest.raises(PlanRefused, match="names neither"):
        Acceptance("the pages look right")


def test_a_clause_decided_by_two_instruments_is_refused():
    # ⚠️ Under pressure the answer is always the reviewer, so a clause naming
    # both is a clause that names one and pretends otherwise.
    with pytest.raises(PlanRefused, match="names both"):
        Acceptance("it renders", runs="python3 -m pytest", looked_at_by="the owner", at="unit 1")


def test_a_reviewer_who_looks_at_nothing_named_is_refused():
    with pytest.raises(PlanRefused, match="names a reviewer and no `at`"):
        Acceptance("it renders", looked_at_by="the corpus owner")


def test_a_clause_with_no_text_accepts_everything():
    with pytest.raises(PlanRefused, match="accepts everything"):
        Acceptance("   ", runs="python3 -m pytest")


def test_the_visual_judgement_is_legal_when_it_says_who_and_at_what():
    clause = Acceptance("the theme is legible", looked_at_by="the corpus owner", at="unit 1")
    assert clause.instrument == "the corpus owner looks at unit 1"


def test_a_commanded_clause_renders_its_command():
    clause = Acceptance("the archive validates", runs="python3 -m pytest tests")
    assert clause.instrument == "`python3 -m pytest tests`"


# --- SK08-A's other half: a dependency may reach out of the corpus ---------


def test_a_tasks_dependencies_split_into_framework_and_corpus():
    known = frozenset({"RS-01", "RS-02"})
    task = plans.reading_task(depends_on=("C-01", "RS-02"))
    assert task.framework_dependencies(known) == ("RS-02",)
    assert task.corpus_dependencies(known) == ("C-01",)


def test_the_two_halves_partition_every_dependency():
    known = frozenset({"RS-01"})
    task = plans.reading_task(depends_on=("RS-01", "C-01", "C-02"))
    both = task.framework_dependencies(known) + task.corpus_dependencies(known)
    assert sorted(both) == sorted(task.depends_on)


def test_a_task_renders_every_field_a_reader_of_the_plan_needs():
    lines = "\n".join(Task(**{**_fields(), "evidence": "a diff that is empty"}).lines())
    for expected in (
        "**Owns**",
        "**Depends on**",
        "**Shown at the end of it.**",
        "**Evidence it produces.**",
        "**Acceptance.**",
    ):
        assert expected in lines


def _fields() -> dict:
    task = plans.reading_task()
    return {
        "id": task.id,
        "title": task.title,
        "demonstrable": task.demonstrable,
        "acceptance": task.acceptance,
        "owns": task.owns,
    }
