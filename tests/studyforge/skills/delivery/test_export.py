"""Mirror of `src/studyforge/skills/delivery/export.py` (R12)."""

from __future__ import annotations

import csv
import io

import pytest

from studyforge.skills.delivery import FIELDS, GITHUB, JIRA, PROFILES, ExportRefused, Profile
from studyforge.skills.delivery import export as render
from tests.studyforge.skills.delivery import plans


def rows(text: str) -> list[list[str]]:
    return list(csv.reader(io.StringIO(text)))


def test_a_profile_naming_a_field_the_backlog_does_not_carry_is_refused():
    # ⛔ SUBSET. A typo in a column mapping fails where it is written rather
    # than producing a column of empty cells.
    with pytest.raises(ExportRefused, match="no such field — assignee"):
        Profile(name="whatever", columns=(("Assignee", "assignee"),))


def test_every_field_in_the_registry_is_reachable_from_a_shipped_profile():
    # ⛔ COVERAGE. A field nothing exports is a field nobody maintains, and it
    # rots until somebody's first export is missing it.
    reached = {field for profile in PROFILES.values() for field in profile.fields}
    assert reached == set(FIELDS)


def test_the_two_shipped_profiles_are_registered_under_their_own_names():
    assert PROFILES == {"jira": JIRA, "github": GITHUB}


def test_a_profile_with_no_columns_is_a_header_of_nothing():
    with pytest.raises(ExportRefused, match="no columns"):
        Profile(name="empty", columns=())


def test_a_profile_with_no_name_cannot_be_cited_in_a_procedure():
    with pytest.raises(ExportRefused, match="cannot be cited"):
        Profile(name=" ", columns=(("Key", "id"),))


def test_two_columns_sharing_a_header_are_refused():
    with pytest.raises(ExportRefused, match="share a header — Key"):
        Profile(name="x", columns=(("Key", "id"), ("Key", "title")))


def test_the_next_tracker_costs_one_profile_value_and_no_planner_change():
    # ⭐ The seam, asserted rather than described: a profile the shipped code
    # has never seen exports without a line of `export` changing.
    unseen = Profile(name="linear", columns=(("Identifier", "id"), ("Estimate", "effort")))
    exported = rows(render(plans.backlog(), unseen))
    assert exported[0] == ["Identifier", "Estimate"]
    assert exported[1] == ["C-01", "1"]


def test_the_header_is_the_trackers_words_and_never_the_registrys():
    assert rows(render(plans.backlog(), JIRA))[0] == list(JIRA.header)
    assert "Issue key" in JIRA.header and "id" not in JIRA.header


def test_one_row_per_task_in_milestone_order():
    plan = plans.backlog()
    exported = rows(render(plan, JIRA))
    assert len(exported) == len(plan.tasks) + 1
    assert [row[0] for row in exported[1:]] == [task.id for task in plan.tasks]


def test_the_milestone_a_task_sits_in_reaches_the_export():
    exported = rows(render(plans.backlog(), JIRA))
    where = JIRA.header.index("Epic Link")
    assert [row[where] for row in exported[1:]] == ["C1", "C2"]


def test_an_acceptance_clause_exports_with_the_instrument_that_decides_it():
    exported = rows(render(plans.backlog(), JIRA))
    where = JIRA.header.index("Acceptance Criteria")
    assert "[`python3 -m pytest tests`]" in exported[1][where]


def test_a_task_that_owns_nothing_exports_an_empty_owns_and_a_full_evidence():
    exported = rows(render(plans.backlog(), GITHUB))
    owns, evidence = GITHUB.header.index("assignees"), GITHUB.header.index("notes")
    assert exported[2][owns] == ""
    assert exported[2][evidence] == "a re-run of the generator that changes no byte"


def test_no_field_in_the_registry_computes_anything_about_the_plan():
    # ⚠️ A field that computed something would be a second opinion about the
    # plan, disagreeing with the document under exactly the conditions nobody
    # tests. Every one reads a stored attribute.
    plan = plans.backlog()
    milestone = plan.milestones[0]
    task = milestone.tasks[0]
    assert FIELDS["id"](task, milestone) == task.id
    assert FIELDS["milestone"](task, milestone) == milestone.id
    assert FIELDS["gate"](task, milestone) == milestone.gated_by
