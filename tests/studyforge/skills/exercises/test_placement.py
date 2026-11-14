"""Mirror of `skills/exercises/placement.py` (R12): where a practice stands on its page."""

from __future__ import annotations

import json

from studyforge.skills.exercises import placement

PAGE = """# Unit

## Parsing

Text about parsing.

### A detail of parsing

More text.

<!-- practice 1 -->

## Routing

```text
# not a heading, inside a fence
<!-- practice 9 -->
```

Text about routing.

<!-- practice 2 -->

## Summary
"""


def _plan(*slots: list[str]) -> dict:
    aspects, exercises = [], []
    for slot, sections in enumerate(slots, start=1):
        ids = []
        for n, name in enumerate(sections):
            aspect = f"a{slot}-{n}"
            aspects.append({"id": aspect, "basis": [f"section:{name}", "example:p.md:1"]})
            ids.append(aspect)
        exercises.append({"slot": slot, "name": f"p{slot}", "aspects": ids})
    return {"aspects": aspects, "exercises": exercises}


def test_a_practice_under_its_section_or_a_heading_nested_in_it_stands_well():
    assert placement.misplaced(PAGE, _plan(["Parsing"], ["Routing"])) == []


def test_a_one_section_practice_in_another_section_is_reported_with_the_fix():
    found = placement.misplaced(PAGE, _plan(["Routing"], ["Parsing"]))
    assert [p.slot for p in found] == [1, 2]
    assert "'Routing'" in found[0].message and "<!-- practice 1 -->" in found[0].message


def test_a_one_section_practice_with_no_marker_is_drawn_after_the_lesson_and_reported():
    found = placement.misplaced(PAGE, _plan(["Parsing"], ["Routing"], ["Parsing"]))
    assert [p.slot for p in found] == [3]
    assert "no marker" in found[0].message


def test_a_combining_practice_stands_after_every_section_it_combines():
    assert placement.misplaced(PAGE, _plan(["Parsing"], ["Parsing", "Routing"])) == []
    early = placement.misplaced(PAGE, _plan(["Parsing", "Routing"]))
    assert [p.slot for p in early] == [1] and "combines 2 sections" in early[0].message
    assert placement.misplaced(PAGE, _plan(["Parsing"], ["Routing"], ["Parsing", "Routing"])) == []


def test_a_section_the_page_does_not_have_is_left_to_the_checks_that_own_it():
    assert placement.misplaced(PAGE, _plan(["Nowhere"])) == []


def test_the_command_walks_every_plan_and_exits_by_what_it_found(tmp_path, capsys):
    (tmp_path / "unit.md").write_text(PAGE, encoding="utf-8")
    where = tmp_path / "exercises" / "u" / "coverage.json"
    where.parent.mkdir(parents=True)
    where.write_text(json.dumps({"page": "unit.md", "plan": _plan(["Routing"])}), encoding="utf-8")
    assert placement.main([str(tmp_path)]) == 1
    assert "1 practice(s) misplaced" in capsys.readouterr().out
    where.write_text(json.dumps({"page": "unit.md", "plan": _plan(["Parsing"])}), encoding="utf-8")
    assert placement.main([str(tmp_path)]) == 0
    assert placement.main([]) == 2
