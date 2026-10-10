"""Mirror of `src/studyforge/skills/adapter/editions.py` (R12): one id per practice folder.

⭐ And no language in a title; `skills.adapter.practices` re-exports the helpers.
"""

from __future__ import annotations

import pytest

from studyforge.skills.adapter.practices import EditionRefused, as_edition, edition_id, untitled

FOLDER = "exercises/02-intermediate/27-references/unit-02/practice-1"


def test_every_language_of_one_folder_gets_one_edition_id():
    first = {"title": "Count by a key (Kotlin)", "ordinal": 1}
    second = {"title": "Count by a key (Java)", "ordinal": 2}
    kotlin = as_edition(first, folder=FOLDER, lang="kotlin", labels=["Kotlin"])
    java = as_edition(second, folder=FOLDER, lang="java", labels=["Java"])
    assert kotlin["edition"] == java["edition"] == edition_id(FOLDER)
    assert (kotlin["lang"], java["lang"]) == ("kotlin", "java")
    assert kotlin["title"] == java["title"] == "Count by a key"


def test_two_folders_get_two_ids_and_the_id_is_an_archive_id():
    other = FOLDER.replace("practice-1", "practice-2")
    assert edition_id(FOLDER) != edition_id(other)
    assert edition_id(FOLDER) == "exercises-02-intermediate-27-references-unit-02-practice-1"


def test_a_title_naming_no_declared_language_is_kept():
    assert untitled("Sort (stable)", ["kotlin", "Kotlin"]) == "Sort (stable)"
    assert untitled("(Kotlin)", ["kotlin"]) == "(Kotlin)"
    assert untitled("Sort (KOTLIN)", ["kotlin"]) == "Sort"


def test_the_fields_given_are_not_changed_in_place():
    given = {"title": "A (Java)"}
    as_edition(given, folder=FOLDER, lang="java")
    assert given == {"title": "A (Java)"}


def test_a_folder_with_no_letter_or_digit_is_refused():
    with pytest.raises(EditionRefused):
        edition_id("//")
