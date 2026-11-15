"""Mirror of `studyforge.skills.intake.render`: the brief as Markdown a person reads."""

from __future__ import annotations

import copy

from studyforge.skills.intake.brief import parse
from studyforge.skills.intake.render import render

from tests.studyforge.skills.intake.briefs import PILOT, clean_brief


def _render(track: str = "topic", **edits: object) -> str:
    data = copy.deepcopy(clean_brief(track))
    for key, value in edits.items():
        qid = key.replace("__", ".")
        if value is None:
            del data["answers"][qid]
        elif isinstance(value, dict):
            data["answers"][qid] = value
        else:
            data["answers"][qid]["value"] = value
    return render(parse(data))


def test_render_is_deterministic_and_ends_with_one_newline():
    first = _render()
    assert first == _render()
    assert first.endswith("\n") and not first.endswith("\n\n")
    assert "\r" not in first
    assert first.startswith("# Graph Basics\n\nTrack: topic\n")
    assert "## Goal\n" in first and "## Publish\n" in first
    assert first.index("## Goal") < first.index("## Publish")
    assert "- **" in first and "(private" not in first


def test_values_render_as_text_yes_no_and_multiline_stays_in_the_list():
    text = _render(quiz__mocks=False, privacy__fresh_history=True,
                   goal__end_state="line one\nline two")
    assert "yes" in text and "no" in text
    assert " line one\n  line two\n" in text
    assert "env:COURSE_HOLDER" in text


def test_claude_decisions_get_their_own_section():
    answer = {"status": "answered", "value": "Use BFS first.", "decided_by": "claude"}
    text = _render(goal__end_state=answer)
    assert "## Decided by Claude\n\n- `goal.end_state`: Use BFS first.\n" in text
    assert _render().count("None.") >= 3
    assert "## Decided by Claude\n\nNone.\n" in _render()


def test_deferred_and_open_items_are_listed():
    deferred = {"status": "deferred", "reason": "Waiting for the syllabus."}
    text = _render(goal__end_state=deferred, scope__depth=None)
    assert "## Deferred\n\n- `goal.end_state`: Waiting for the syllabus.\n" in text
    still = text.split("## Still open")[1].split("## Outline")[0]
    assert "- open: scope.depth: missing" in still
    assert "private" not in still
    assert "## Still open\n\nNone.\n" in _render()


def test_the_outline_marks_the_pilot_and_depths():
    text = _render()
    assert f"### Foundations\n\n- {PILOT} (pilot)\n  - Breadth-first search [core]\n" in text
    assert "- Weighted graphs\n  - Dijkstra [deep]\n" in text
