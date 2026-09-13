"""Mirror of `src/studyforge/skills/buildserve/states.py` (R12).

⛔ The derivations are asserted over the verbs' own answers: the plan the plan
verb derives for each `FND-04` fixture, and the narrate report's own sentence.
"""

from __future__ import annotations

from dataclasses import dataclass

import pytest

from studyforge.cli.narrate import report
from studyforge.cli.plan import plan_for
from studyforge.skills.buildserve import states
from studyforge.skills.buildserve.states import (
    EXECUTION_NAMESPACE,
    KNOWN,
    NARRATION_INCOMPLETE,
    NO_EXERCISES,
    NO_NARRATION,
    NO_NARRATION_SERVICE,
    NO_TOOLCHAIN,
    PartialState,
    exercise_states,
    narration_states,
    recorded,
)
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES
from tests.fixture_checks.vocabulary import VALID


@dataclass(frozen=True)
class Made:
    path: str
    narration: bool


@dataclass(frozen=True)
class Plan:
    creations: tuple[Made, ...]


def test_every_state_says_what_is_missing_what_works_and_what_to_do():
    assert len({state.name for state in KNOWN}) == len(KNOWN)
    for state in KNOWN:
        assert all((state.name, state.missing, state.works, state.remedy)), state
        lines = state.lines()
        assert [line.split()[0] for line in lines] == ["partial", "works", "remedy"]
        assert all(line.split()[1] == state.name for line in lines)


def test_the_no_service_sentence_is_the_narrate_reports_own():
    # ⛔ Imported, never respelled: a reworded report must not silently stop matching.
    assert states.NO_SERVICE is report.NO_SERVICE


@pytest.mark.parametrize("name", VALID)
def test_no_fixture_has_a_narration_record_by_the_plans_own_mark(name):
    plan = plan_for(FIXTURES / name)
    assert any(made.narration for made in plan.creations), "no audio directory is planned"
    assert not recorded(plan)


def test_a_planned_clip_copy_is_a_record_and_an_audio_directory_is_not():
    directory = Made("unit-01/audio/", narration=True)
    clip = Made("unit-01/audio/clip.mp3", narration=True)
    page = Made("unit-01/index.html", narration=False)
    assert not recorded(Plan((directory, page)))
    assert recorded(Plan((directory, clip)))


@pytest.mark.parametrize(
    ("code", "said", "has_record", "expected"),
    [
        (None, "", False, (NO_NARRATION,)),
        (None, "", True, ()),
        (OK, "", False, (NO_NARRATION,)),
        (OK, "", True, ()),
        (UNUSABLE, f"refuse service  {report.NO_SERVICE}", False, (NO_NARRATION_SERVICE,)),
        (UNUSABLE, f"refuse service  {report.NO_SERVICE}", True, (NO_NARRATION_SERVICE,)),
        (INVALID, "a unit was not produced", True, (NARRATION_INCOMPLETE,)),
        (UNUSABLE, "the record cannot be read", False, (NARRATION_INCOMPLETE,)),
    ],
)
def test_the_narration_state_follows_the_narration_runs_answer(code, said, has_record, expected):
    assert narration_states(code, said, has_record=has_record) == expected


def test_the_exercise_state_follows_the_manifest_and_the_serving_process():
    assert exercise_states(False, ()) == (NO_EXERCISES,)
    assert exercise_states(False, (EXECUTION_NAMESPACE,)) == (NO_EXERCISES,)
    assert exercise_states(True, ("content", "assets")) == (NO_TOOLCHAIN,)
    assert exercise_states(True, ("content", EXECUTION_NAMESPACE)) == ()


def test_a_state_is_data_and_not_an_exception():
    assert not any(isinstance(state, BaseException) for state in KNOWN)
    assert all(isinstance(state, PartialState) for state in KNOWN)
