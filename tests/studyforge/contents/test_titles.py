"""Mirror of `src/studyforge/contents/titles.py` (R12).

`test_tree` reads `slug_titled` through `build`; this pins the three slug forms and the
punctuation rule one title at a time, and the walk on a hand-built tree.
"""

from __future__ import annotations

import pytest

from studyforge.contents.entries import Contents, Group
from studyforge.contents.titles import is_slug_form, normalised, slug_titled

SEGMENT = "93-spring-core-beans-injection-scopes-and-lifecycle"


def test_normalised_lowercases_collapses_and_drops_the_leading_number():
    assert normalised(SEGMENT) == "spring core beans injection scopes and lifecycle"
    assert normalised("  Spring core: beans, injection!  ") == "spring core beans injection"
    assert normalised("2024 roadmap") == "roadmap"
    assert normalised("snake_case_name") == "snake case name"


@pytest.mark.parametrize(
    "title",
    ["intro-to-graphs", "01-basics", "a-b-c"],
)
def test_lowercase_words_joined_by_hyphens_are_slug_form(title):
    assert is_slug_form(title)


def test_a_humanised_slug_is_slug_form_only_against_its_own_segment():
    humanised = "Spring core beans injection scopes and lifecycle"
    assert is_slug_form(humanised, SEGMENT)
    assert not is_slug_form(humanised)
    assert not is_slug_form(humanised, "94-something-else")


@pytest.mark.parametrize(
    "title",
    [
        "Spring core: beans, injection, scopes and lifecycle",
        "Intro to graphs",
        "intro",
        "Intro-To-Graphs",
        "",
    ],
)
def test_a_declared_title_is_not_slug_form(title):
    assert not is_slug_form(title, SEGMENT)


def test_a_group_titled_with_its_own_folder_words_is_a_humanised_slug():
    assert is_slug_form("Basics", "01-basics")
    assert not is_slug_form("The basics", "01-basics")


def test_a_title_that_is_not_text_is_never_slug_form():
    assert not is_slug_form(None, SEGMENT)
    assert not is_slug_form(42)


def _group(segment: str, title: str, *children: Group) -> Group:
    return Group(level="group", segment=segment, key=segment, title=title, groups=children)


def test_the_walk_names_every_slug_titled_group_in_tree_order():
    tree = Contents(
        corpus="demo",
        title="Demo",
        levels=("group",),
        groups=(
            _group("01-basics", "The basics", _group("01-intro-to-graphs", "intro-to-graphs")),
            _group("02-spring-core", "Spring core"),
            _group("03-advanced", "Advanced: the rest"),
        ),
    )
    assert slug_titled(tree) == ("01-intro-to-graphs", "02-spring-core")
