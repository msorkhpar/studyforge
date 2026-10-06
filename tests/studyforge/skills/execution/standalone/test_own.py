"""Mirror of `src/studyforge/skills/execution/standalone/own.py`: a course's own README sections."""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.skills.execution.standalone import compose, learner, own

PNG = b"\x89PNG\r\n\x1a\n" + b"0" * 64


def course_dir(root: Path) -> Path:
    where = root / own.DIRNAME
    (where / own.SHOTS).mkdir(parents=True)
    return where


def test_a_course_without_the_directory_has_no_own_sections(tmp_path):
    assert own.read(tmp_path) == own.Own()


def test_the_sections_are_read_and_their_picture_links_point_into_the_tree(tmp_path):
    where = course_dir(tmp_path)
    (where / "top.md").write_text("## Read this first\n\nHonest note.\n", encoding="utf-8")
    (where / "body.md").write_text("## Look\n\n![x](shots/a.png)\n", encoding="utf-8")
    (where / "shots" / "a.png").write_bytes(PNG)
    found = own.read(tmp_path)
    assert found.top[0] == "## Read this first"
    assert f"![x]({compose.IMAGES}/readme/a.png)" in found.body
    assert found.shots == (("a.png", where / "shots" / "a.png"),)


def test_a_link_to_a_picture_that_is_not_there_is_refused(tmp_path):
    where = course_dir(tmp_path)
    (where / "body.md").write_text("![x](shots/missing.png)\n", encoding="utf-8")
    with pytest.raises(ValueError, match="missing.png"):
        own.read(tmp_path)


def test_a_picture_over_the_size_or_of_another_kind_is_refused(tmp_path):
    where = course_dir(tmp_path)
    (where / "shots" / "big.png").write_bytes(PNG + b"0" * own.SHOT_MAX_BYTES)
    with pytest.raises(ValueError, match="big.png"):
        own.read(tmp_path)
    (where / "shots" / "big.png").unlink()
    (where / "shots" / "a.gif").write_bytes(PNG)
    with pytest.raises(ValueError, match="a.gif"):
        own.read(tmp_path)


def test_the_readme_places_the_top_after_the_title_and_the_body_in_place_of_the_features():
    base = learner.Course("A Course", "a-course", 1, 2, "ns", False)
    plain = learner.readme(base)
    mine = learner.readme(
        learner.Course(
            "A Course", "a-course", 1, 2, "ns", False, top=("## Top note", ""), body=("## Body", "")
        )
    )
    assert mine.index("# A Course") < mine.index("## Top note") < mine.index("## The course")
    assert mine.index("## The course") < mine.index("## Body") < mine.index("## What you need")
    assert "## What you get" not in mine and "## Two ways to use it" not in mine
    assert "## What you get" in plain
    assert "docker compose -f compose.pull.yaml up -d" in mine


def test_a_course_without_own_sections_gets_the_readme_it_always_had():
    base = learner.Course("A Course", "a-course", 1, 2, "ns", False)
    assert learner.readme(base) == learner.readme(
        learner.Course("A Course", "a-course", 1, 2, "ns", False, top=(), body=())
    )
