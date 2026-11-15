"""Mirror of `studyforge.skills.intake.brief`: parsing the course brief record."""

from __future__ import annotations

import copy
import json

import pytest

from studyforge.skills.intake.brief import Answer, Brief, BriefError, load, parse

MINIMAL: dict = {
    "brief_api": 1,
    "title": "Graph Basics",
    "track": "topic",
    "answers": {"goal.end_state": {"status": "answered", "value": "x", "decided_by": "author"}},
    "outline": [
        {"title": "S", "modules": [{"title": "M", "lessons": [{"title": "L", "depth": "core"}]}]}
    ],
}


def _with(path: list, value: object) -> dict:
    data = copy.deepcopy(MINIMAL)
    node = data
    for key in path[:-1]:
        node = node[key]
    node[path[-1]] = value
    return data


def test_a_minimal_brief_parses():
    brief = parse(MINIMAL)
    assert isinstance(brief, Brief)
    assert brief.track == "topic"
    assert brief.answers["goal.end_state"] == Answer("answered", "x", "author", None)
    lesson = brief.outline[0].modules[0].lessons[0]
    assert (lesson.title, lesson.depth) == ("L", "core")
    assert brief.outline[0].modules[0].pilot is False
    with pytest.raises(TypeError):
        brief.answers["new"] = Answer("proposed")  # type: ignore[index]


def _missing_outline() -> dict:
    data = copy.deepcopy(MINIMAL)
    del data["outline"]
    return data


@pytest.mark.parametrize(
    ("data", "path"),
    [
        (_with(["answers"], []), "answers"),
        (_missing_outline(), "outline"),
        (_with(["answers", "goal.end_state", "value"], {"a": 1}), "answers.goal.end_state.value"),
        (_with(["brief_api"], 2), "brief_api"),
        (_with(["track"], "tour"), "track"),
        (_with(["outline", 0, "modules", 0, "lessons", 0, "depth"], "medium"),
         "outline.0.modules.0.lessons.0.depth"),
        (_with(["answers", "goal.end_state", "status"], "done"),
         "answers.goal.end_state.status"),
        (_with(["answers", "goal.end_state", "decided_by"], "bot"),
         "answers.goal.end_state.decided_by"),
        (_with(["outline", 0, "modules", 0, "pilot"], "yes"), "outline.0.modules.0.pilot"),
        ([], "brief"),
    ],
)
def test_wrong_shapes_name_their_field(data, path):
    with pytest.raises(BriefError) as err:
        parse(data)
    assert path in str(err.value)
    assert "\n" not in str(err.value)


def test_an_answer_value_is_never_echoed():
    data = _with(["answers", "goal.end_state", "status"], "zq-private-token")
    with pytest.raises(BriefError) as err:
        parse(data)
    assert "zq-private" not in str(err.value)


def test_answered_without_decided_by_and_deferred_without_reason_are_refused():
    with pytest.raises(BriefError, match=r"answers\.a\.decided_by"):
        parse(_with(["answers", "a"], {"status": "answered", "value": "v"}))
    with pytest.raises(BriefError, match=r"answers\.a\.reason"):
        parse(_with(["answers", "a"], {"status": "deferred"}))
    ok = parse(_with(["answers", "a"], {"status": "deferred", "reason": "later"}))
    assert ok.answers["a"].reason == "later"
    assert parse(_with(["answers", "b"], {"status": "proposed", "value": True})).answers["b"].value


def test_load_reports_invalid_json_as_a_brief_error(tmp_path):
    bad = tmp_path / "brief.json"
    bad.write_text("{not json", encoding="utf-8")
    with pytest.raises(BriefError, match="not valid JSON"):
        load(bad)
    with pytest.raises(BriefError, match="cannot read"):
        load(tmp_path / "missing.json")
    good = tmp_path / "ok.json"
    good.write_text(json.dumps(MINIMAL), encoding="utf-8")
    assert load(good).title == "Graph Basics"
