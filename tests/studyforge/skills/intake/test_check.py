"""Mirror of `studyforge.skills.intake.check`: which costly questions are still open."""

from __future__ import annotations

import copy

import pytest

from studyforge.skills.intake import TRACKS
from studyforge.skills.intake.brief import parse
from studyforge.skills.intake.check import PRIVATE_REF, check, open_questions, outline_faults

from tests.studyforge.skills.intake.briefs import clean_brief


def _brief(track: str = "topic", **edits: object):
    data = copy.deepcopy(clean_brief(track))
    for key, value in edits.items():
        qid = key.replace("__", ".")
        if value is None:
            del data["answers"][qid]
        elif isinstance(value, dict):
            data["answers"][qid] = value
        else:
            data["answers"][qid]["value"] = value
    return parse(data)


@pytest.mark.parametrize("track", TRACKS)
def test_a_clean_brief_has_no_findings(track):
    assert check(parse(clean_brief(track)), True) == []


@pytest.mark.parametrize(
    "edit, expected",
    [
        ({"goal__end_state": None}, "open: goal.end_state: missing"),
        (
            {"goal__end_state": {"status": "proposed", "value": "x"}},
            "open: goal.end_state: proposed, not yet accepted",
        ),
        ({"goal__end_state": ""}, "open: goal.end_state: empty"),
        ({"goal__end_state": "Java where possible"}, "open: goal.end_state: hedged"),
        (
            {"publish__holder": "Jane Doe"},
            "open: publish.holder: not a variable name or a .private/ key",
        ),
        ({"quiz__mocks": "yes"}, "open: quiz.mocks: not a boolean"),
        (
            {"narration__wanted": "sometimes"},
            "open: narration.wanted: not one of yes, no, after-release",
        ),
    ],
)
def test_each_open_condition_is_reported_once(edit, expected):
    assert open_questions(_brief(**edit)) == [expected]


def test_a_deferred_costly_question_with_a_reason_is_not_open():
    deferred = {"status": "deferred", "reason": "waiting on the publisher"}
    assert open_questions(_brief(publish__holder=deferred)) == []


def test_a_personal_value_in_free_text_is_reported_by_id_not_by_text():
    path = "/" + "home" + "/alice/notes"
    lines = open_questions(_brief(sources__list=f"My notes at {path}"))
    assert len(lines) == 1 and lines[0].startswith("open: sources.list: carries ")
    assert "alice" not in "\n".join(lines)


def test_a_boolean_answer_is_not_scrubbed():
    assert open_questions(_brief(quiz__mocks=True)) == []


def test_narration_scope_is_required_only_when_narration_is_wanted():
    assert open_questions(_brief(narration__wanted="no")) == []
    data = clean_brief("topic")
    data["answers"]["narration.wanted"]["value"] = "yes"
    assert open_questions(parse(data)) == ["open: narration.scope: missing"]
    data["answers"]["narration.wanted"] = {"status": "deferred", "reason": "later"}
    assert open_questions(parse(data)) == []


def test_outline_without_pilot_and_pilot_mismatch_are_reported():
    data = clean_brief("topic")
    data["outline"][0]["modules"][0]["pilot"] = False
    faults = outline_faults(parse(data))
    assert "outline: no module is marked pilot" in faults
    data = clean_brief("topic")
    data["answers"]["writing.pilot"]["value"] = "Weighted graphs"
    assert outline_faults(parse(data)) == [
        "outline: writing.pilot names Weighted graphs, which is not a pilot module"
    ]
    data["outline"] = []
    assert outline_faults(parse(data)) == ["outline: empty"]


def test_an_unignored_private_folder_is_reported():
    brief = parse(clean_brief("topic"))
    assert check(brief, False) == [".private/ is not ignored by git"]


def test_a_personal_value_in_an_outline_title_is_reported_by_path():
    data = clean_brief("topic")
    data["outline"][0]["modules"][0]["lessons"][0]["title"] = "See " + "/" + "home" + "/bob/x"
    lines = check(parse(data), True)
    assert len(lines) == 1 and lines[0].startswith("outline: outline.0.modules.0.lessons.0")
    assert "bob" not in lines[0]


@pytest.mark.parametrize(
    "value", ["env:COURSE_HOLDER", "private:release.env#HOLDER", "private:jd.md"]
)
def test_private_ref_forms_accepted(value):
    assert PRIVATE_REF.fullmatch(value)


@pytest.mark.parametrize(
    "value",
    [
        "env:holder", "private:../x", "private:/etc/x", "", "private:a/../x", "env:A#b",
        "private:.", "private:./x", "private:a/./b", "private:a//b", "private:a/", "private:",
        "private:.#KEY",
    ],
)
def test_private_ref_forms_refused(value):
    assert not PRIVATE_REF.fullmatch(value)


@pytest.mark.parametrize(
    "edit, expected",
    [
        ({"goal__end_state": True}, "open: goal.end_state: not text"),
        ({"publish__holder": False}, "open: publish.holder: not text"),
        ({"narration__wanted": True}, "open: narration.wanted: not one of yes, no, after-release"),
        ({"quiz__mocks": "true"}, "open: quiz.mocks: not a boolean"),
    ],
)
def test_an_answer_of_the_wrong_json_type_names_what_its_kind_needs(edit, expected):
    assert open_questions(_brief(**edit)) == [expected]


def test_tracked_files_in_the_private_folder_are_reported():
    brief = parse(clean_brief("topic"))
    assert check(brief, True, private_tracked=True) == [".private/ holds files git tracks"]
