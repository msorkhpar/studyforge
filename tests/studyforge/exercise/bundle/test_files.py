"""Mirror of `exercise/bundle/files.py` (R12): the further files a practice's reader edits."""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.bundle.files import read_files, shown

WHERE = "here"


def test_absent_is_no_further_file_and_a_list_is_read_in_order():
    assert read_files(None, WHERE) == ()
    assert read_files(["settings.json", "NOTES.md"], WHERE) == ("settings.json", "NOTES.md")


def test_an_empty_list_a_repeat_and_a_non_list_are_refused():
    for bad in ([], ["a.md", "a.md"], "a.md", {"a.md": 1}):
        with pytest.raises(ExerciseError):
            read_files(bad, WHERE)


def test_the_main_file_comes_first_and_each_further_file_is_named_and_shown_by_suffix():
    reference, starting = shown(
        "python", "ref = 1", "start = 0",
        (("settings.json", "{}", '{"a": 1}'), ("tool.xyz", "x", "y")),
    )
    assert [block["type"] for block in reference] == ["code", "para", "code", "para", "code"]
    assert reference[0] == {"type": "code", "lang": "python", "text": "ref = 1"}
    assert reference[1]["text"] == "File: settings.json" and reference[2]["lang"] == "json"
    assert reference[4]["lang"] == "python", "a suffix with no word is shown in the practice's own"
    assert starting[2] == {"type": "code", "lang": "json", "text": "{}"}


def test_a_practice_of_one_file_is_shown_as_it_always_was():
    reference, starting = shown("python", "ref", "start", ())
    assert reference == [{"type": "code", "lang": "python", "text": "ref"}]
    assert starting == [{"type": "code", "lang": "python", "text": "start"}]
