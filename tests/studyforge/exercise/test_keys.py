"""Mirror of `src/studyforge/exercise/keys.py` (R12).

⭐ The record's key order IS its format (R10), and a key added later is
APPENDED, never inserted — so every record written before it keeps its bytes.
The refusals themselves are read at the record's own reader in
`test_record.py`; what is asserted here is the part only this module holds.
"""

from __future__ import annotations

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise.keys import (
    AUTHORED_KEYS,
    EXERCISE_KEYS,
    GRADER_KEYS,
    REQUIRED_KEYS,
    require_known_keys,
    require_present,
)

#: The six keys the record was first written with, in their first order.
ORIGINAL = ("main_path", "test_path", "run_command", "test_command", "provenance", "trust")


def test_the_original_six_keep_their_order_and_every_later_key_is_appended():
    assert EXERCISE_KEYS[: len(ORIGINAL)] == ORIGINAL
    assert EXERCISE_KEYS[len(ORIGINAL) :] == AUTHORED_KEYS
    assert AUTHORED_KEYS[-6:] == ("concepts", "files", "review", "cards", "layout", "try_file")


def test_every_key_group_is_drawn_from_the_record_s_own_keys():
    for group in (REQUIRED_KEYS, GRADER_KEYS, AUTHORED_KEYS):
        assert set(group) <= set(EXERCISE_KEYS), group


def test_a_key_the_record_does_not_define_is_refused_by_name_without_its_value():
    with pytest.raises(ExerciseError, match="'concept'") as refused:
        require_known_keys({"main_path": "a.py", "concept": "secret words"}, "here")
    assert "secret words" not in str(refused.value)


def test_a_grader_written_in_part_is_refused_naming_what_is_missing():
    with pytest.raises(ExerciseError, match="test_command"):
        require_present({"main_path": "a.py", "run_command": ["x"], "test_path": "t.py"}, "here")
