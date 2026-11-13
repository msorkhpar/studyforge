"""Mirror of `exercise.workfiles` (R12): the record's file keys, a project's read-only ones too."""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError, from_document, to_document
from studyforge.exercise.workfiles import files_in, read_only_in, try_file_in

WS = "practice/p"
PROJECT = {
    "main_path": f"{WS}/pkg/model.py",
    "files": [f"{WS}/main.py"],
    "test_path": f"{WS}/tests/test_expected_output.py",
    "run_command": ["python3", f"{WS}/main.py"],
    "test_command": ["python3", "-m", "pytest", f"{WS}/tests"],
    "provenance": "generated",
    "trust": "advisory",
    "read_only": [f"{WS}/tests/test_model.py", f"{WS}/data/lots.csv"],
}


def test_a_project_record_round_trips_and_its_read_only_key_is_written_last():
    record = from_document(PROJECT, "w")
    assert record.read_only == (f"{WS}/tests/test_model.py", f"{WS}/data/lots.csv")
    assert to_document(record) == PROJECT
    assert list(to_document(record))[-1] == "read_only"


def test_a_record_with_no_read_only_files_is_unchanged():
    plain = {key: value for key, value in PROJECT.items() if key != "read_only"}
    assert from_document(plain, "w").read_only is None
    assert to_document(from_document(plain, "w")) == plain


@pytest.mark.parametrize(
    "listed",
    [
        [],  # empty: a practice that is not a project leaves the key out
        [f"{WS}/a.csv", f"{WS}/a.csv"],  # twice
        [f"{WS}/pkg/model.py"],  # the main file
        [f"{WS}/main.py"],  # a file the reader edits
        [f"{WS}/tests/test_expected_output.py"],  # the test file
        ["../escape.csv"],  # not a safe path
    ],
)
def test_a_bad_read_only_list_is_refused(listed):
    with pytest.raises(ExerciseError):
        read_only_in({**PROJECT, "read_only": listed}, "w")


def test_each_reader_answers_none_for_an_absent_key():
    assert files_in({}, "w") is None
    assert try_file_in({}, "w") is None
    assert read_only_in({}, "w") is None
