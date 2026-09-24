"""Mirror of `src/studyforge/narrate/enabled.py` (R12) — the one "narration is on" predicate."""

from __future__ import annotations

import pytest

from studyforge.narrate.enabled import narration_on


def test_a_run_nobody_asked_is_on(tmp_path):
    # ⭐ The behaviour every corpus had before narration was made optional.
    assert narration_on(tmp_path) is True


@pytest.mark.parametrize("asked", [True, False])
def test_the_runs_own_answer_wins_either_way(tmp_path, asked):
    assert narration_on(tmp_path, asked=asked) is asked


def test_the_run_is_keyword_only(tmp_path):
    # ⛔ A positional `False` would read as a root, not as an answer.
    with pytest.raises(TypeError):
        narration_on(tmp_path, False)  # type: ignore[misc]
