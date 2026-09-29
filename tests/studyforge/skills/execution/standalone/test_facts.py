"""Mirror of `src/studyforge/skills/execution/standalone/facts.py` (R12).

⭐ The counts are read from a tree written here, record by record, so a count that
came from anywhere else (a constant, a page, the wrong file name) turns a number red.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.skills.execution.standalone import facts

EXAMPLE_PAGE = "<details data-code-example data-code-open='x'><summary>A.java</summary></details>"


def record(path: Path, document: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(document), encoding="utf-8")


def archive(
    root: Path, *, areas: dict[str, list[str]], units: int, code: int, quizzes: int
) -> None:
    """A course of `areas` (name -> module names), each module holding the given units."""
    for area, modules in areas.items():
        for module in modules:
            base = root / "archive" / area / module
            record(base / "container.json", {"titles": [area.title(), module.title()]})
            for unit in range(1, units + 1):
                folder = base / "raw" / "prose" / f"unit-{unit:02d}"
                record(folder / "lesson-1.json", {"kind": "lesson"})
                for n in range(1, code + 1):
                    record(folder / f"practice-{n}.json", {"starting_code": "class A {}"})
                for n in range(code + 1, code + quizzes + 1):
                    record(folder / f"practice-{n}.json", {"starting_code": None})


def test_the_counts_are_the_records_of_the_tree(tmp_path):
    archive(
        tmp_path, areas={"basics": ["one", "two"], "more": ["three"]}, units=2, code=2, quizzes=1
    )
    read = facts.read(tmp_path)
    assert (read.modules, read.units, read.practices, read.quizzes) == (3, 6, 18, 6)
    assert read.coded == 12
    assert read.areas == ("Basics", "More")


def test_two_courses_state_two_different_counts(tmp_path):
    archive(tmp_path / "a", areas={"x": ["m"]}, units=3, code=1, quizzes=0)
    archive(tmp_path / "b", areas={"x": ["m"]}, units=5, code=2, quizzes=1)
    a, b = facts.read(tmp_path / "a"), facts.read(tmp_path / "b")
    assert (a.units, a.practices) != (b.units, b.practices)


def test_a_course_with_one_level_of_containers_has_no_topic_areas(tmp_path):
    record(tmp_path / "archive" / "solo" / "container.json", {"titles": ["Only"]})
    record(tmp_path / "archive" / "solo" / "raw" / "u" / "lesson-1.json", {})
    read = facts.read(tmp_path)
    assert read.modules == 1 and read.areas == ()


def test_a_number_that_cannot_be_read_is_none_and_never_zero(tmp_path):
    assert facts.read(tmp_path) == facts.Facts()
    archive(tmp_path, areas={"a": ["m"]}, units=1, code=1, quizzes=0)
    read = facts.read(tmp_path)
    assert read.quizzes is None and read.examples is None
    assert read.coded == 1


def test_a_record_that_is_not_json_is_skipped_not_fatal(tmp_path):
    archive(tmp_path, areas={"a": ["m"]}, units=1, code=1, quizzes=1)
    (tmp_path / "archive" / "a" / "m" / "raw" / "prose" / "unit-01" / "practice-1.json").write_text(
        "{"
    )
    assert facts.read(tmp_path).practices == 2


def test_code_examples_are_counted_in_the_pages_and_not_in_the_build_files(tmp_path):
    archive(tmp_path, areas={"a": ["m"]}, units=1, code=1, quizzes=0)
    (tmp_path / "page.html").write_text(EXAMPLE_PAGE * 3, encoding="utf-8")
    hidden = tmp_path / ".studyforge" / "images" / "site"
    hidden.mkdir(parents=True)
    (hidden / "kept.html").write_text(EXAMPLE_PAGE, encoding="utf-8")
    assert facts.read(tmp_path).examples == 3
