"""Mirror of `src/studyforge/skills/buildserve/states.py` (R12).

⛔ The derivations are asserted over the verbs' own answers: the plan the plan
verb derives for each `FND-04` fixture, and the narrate report's own sentence.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

import pytest

from studyforge.cli.narrate import report
from studyforge.cli.plan import plan_for
from studyforge.execute import CONTAINER, HOST
from studyforge.skills.buildserve import narration, states
from studyforge.skills.buildserve.states import (
    EXECUTION_NAMESPACE,
    HOST_EXECUTION,
    KNOWN,
    NARRATION_INCOMPLETE,
    NO_EXERCISES,
    NO_NARRATION_SERVICE,
    NOT_NARRATED,
    NOTHING_TO_NARRATE,
    PartialState,
    exercise_states,
    narration_states,
    probe_for,
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
        (None, "", False, (NOT_NARRATED,)),
        (None, "", True, ()),
        (OK, "", False, (NOTHING_TO_NARRATE,)),
        (OK, "", True, ()),
        (UNUSABLE, f"refuse service  {report.NO_SERVICE}", False, (NO_NARRATION_SERVICE,)),
        (UNUSABLE, f"refuse service  {report.NO_SERVICE}", True, (NO_NARRATION_SERVICE,)),
        (INVALID, "a unit was not produced", True, (NARRATION_INCOMPLETE,)),
        (UNUSABLE, "the record cannot be read", False, (NARRATION_INCOMPLETE,)),
    ],
)
def test_the_narration_state_follows_the_narration_runs_answer(code, said, has_record, expected):
    assert narration_states(code, said, has_record=has_record) == expected


def test_a_corpus_that_has_not_narrated_and_one_that_cannot_are_two_distinguishable_answers():
    # ⛔ The row: today both read as one partial state. Asserted both ways, and on
    # every field a reader sees — the name, the missing clause and the remedy.
    has_not = narration_states(None, "", has_record=False)
    cannot = narration_states(OK, "", has_record=False)
    assert has_not == (NOT_NARRATED,) and cannot == (NOTHING_TO_NARRATE,)
    assert has_not != cannot
    assert NOT_NARRATED.name != NOTHING_TO_NARRATE.name
    assert NOT_NARRATED.missing != NOTHING_TO_NARRATE.missing
    assert NOT_NARRATED.remedy != NOTHING_TO_NARRATE.remedy


def test_the_unfinished_one_names_the_component_and_the_finished_one_asks_for_nothing():
    # ⭐ An operator following the skills is TOLD what provides narration, in the
    # line they actually read, rather than being left to find out it exists.
    assert narration.COMPONENT in NOT_NARRATED.remedy
    assert narration.ADDRESS in NOT_NARRATED.remedy
    assert narration.COMPONENT in NO_NARRATION_SERVICE.remedy
    assert NOTHING_TO_NARRATE.remedy == NO_EXERCISES.remedy == "none needed"


def test_only_the_finished_silent_state_reads_like_the_exercise_state():
    # ⛔ The defect measured: a silent corpus reported beside `exercises`, whose
    # whole point is that it IS finished. Only one of the two may read that way.
    for finished in (NOTHING_TO_NARRATE, NO_EXERCISES):
        assert finished.works.startswith("everything:") and "(C5)" in finished.works
    assert not NOT_NARRATED.works.startswith("everything:")
    assert "not yet known whether this corpus could speak" in NOT_NARRATED.missing


class Asked:
    """A stand-in for `execute`'s probe: answers `mode`, and counts being asked."""

    def __init__(self, mode: str) -> None:
        self.answer, self.asked = mode, 0

    def mode(self) -> str:
        self.asked += 1
        return self.answer


def test_the_exercise_state_follows_the_manifest_the_serving_process_and_the_probe():
    # ⭐ `W381` (a), both ways: offered execution on the HOST is `host`; in the
    # runner container it is no state at all.
    served = ("content", EXECUTION_NAMESPACE)
    assert exercise_states(True, served, Asked(HOST)) == (HOST_EXECUTION,)
    assert exercise_states(True, served, Asked(CONTAINER)) == ()
    assert exercise_states(False, (), Asked(HOST)) == (NO_EXERCISES,)
    assert exercise_states(False, served, Asked(HOST)) == (NO_EXERCISES,)


def test_the_probe_is_asked_only_when_a_run_could_happen():
    # ⛔ No exercises, or no execution offered: nothing runs, so where is moot.
    for declared, offered in ((False, ("content", EXECUTION_NAMESPACE)), (True, ("content",))):
        probe = Asked(HOST)
        assert HOST_EXECUTION not in exercise_states(declared, offered, probe)
        assert probe.asked == 0
    probe = Asked(HOST)
    exercise_states(True, (EXECUTION_NAMESPACE,), probe)
    assert probe.asked == 1


def test_the_host_state_says_what_the_ruling_says():
    # ⭐ Round 125's wording: where it runs, what it lacks, that everything works,
    # and the remedy names the runner container and the component's README.
    assert HOST_EXECUTION.name == "host"
    assert "execute on this host, without the runner's isolation" in HOST_EXECUTION.missing
    assert HOST_EXECUTION.works.startswith("everything:")
    assert "(C5)" not in HOST_EXECUTION.works, "host mode is not a finished state"
    assert HOST_EXECUTION.remedy == (
        "start the runner container as code-server-toolchain's README documents, "
        "then serve again"
    )
    assert HOST_EXECUTION in KNOWN


def test_the_probe_is_executes_own_and_asks_what_a_run_asks(tmp_path):
    # ⛔ ONE definition, imported: the probe class is `execute`'s, and it names the
    # container and root the served instance's runner is built from.
    from studyforge.execute import ModeProbe, container_for
    from studyforge.serve.routes.runs import runner_for

    probe = probe_for(tmp_path, "some-corpus")
    runner = runner_for(SimpleNamespace(root=tmp_path, source="some-corpus"))
    assert type(probe) is ModeProbe and states.ModeProbe is ModeProbe
    assert probe.container == runner.probe.container == container_for("some-corpus")
    assert probe.source_root == runner.probe.source_root
    source = Path(states.__file__).read_text(encoding="utf-8")
    assert "docker" not in source.replace("`docker inspect`", ""), "a copied probe"


def test_no_served_form_lacks_execution_so_the_toolchain_state_is_gone():
    # ⭐ `W381` (b): the condition measured, then its consequence. Both forms of
    # `serve` take their namespaces from `namespaces_of`, and it always offers `run`.
    from studyforge.serve import Discovered, namespaces_of

    assert EXECUTION_NAMESPACE in namespaces_of(Discovered(Path("."), (), ()), {})
    assert "toolchain" not in {state.name for state in KNOWN}
    assert not hasattr(states, "NO_TOOLCHAIN")
    assert all("toolchain container" not in state.remedy for state in KNOWN)


def test_the_execution_namespace_is_the_frameworks_one_spelling_and_the_route_registers_it():
    # ⭐ `SK-03/3`, closed by `SF-22`: the skill holds no spelling of its own — it is the
    # run route's `NAMESPACE`, the very object `serve.instance.instance_of` registers.
    from studyforge.serve import instance
    from studyforge.serve.routes import run

    assert EXECUTION_NAMESPACE is run.NAMESPACE
    assert "run.NAMESPACE" in Path(instance.__file__).read_text(encoding="utf-8")
    source = Path(states.__file__).read_text(encoding="utf-8")
    assert f'EXECUTION_NAMESPACE = "{run.NAMESPACE}"' not in source


def test_a_state_is_data_and_not_an_exception():
    assert not any(isinstance(state, BaseException) for state in KNOWN)
    assert all(isinstance(state, PartialState) for state in KNOWN)
