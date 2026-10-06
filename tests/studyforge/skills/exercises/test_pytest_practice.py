"""A Python practice is graded with pytest through the framework's own gates, G1 to G5.

⭐ **Every reading is a real `pytest` process** over real files (the runner is
`authoring.Running`, which stands this interpreter in for `python3`), so what each gate
reads comes out of a JUnit report and not out of a verdict typed here.

**What it asserts.**
- the reference passes and the starter and every plant fail, and the output of EACH failing
  run names an assertion (`AssertionError`), never an import error, a missing implementation
  or a timeout;
- the cases whose ids carry a space, and a pytest node id spelled from the dotted `classname`,
  fold out of the real report;
- a starter that raises instead of returning a wrong value is flagged when the draft asks for
  assertion failures only, and passes as it always did when it does not;
- a report path that is wrong is named by the gate that found no report.
"""

from __future__ import annotations

import re
import time
from dataclasses import replace
from pathlib import Path

import pytest

from studyforge.exercise import (
    EDGE,
    MAIN,
    Case,
    Exercise,
    ExerciseError,
    Report,
    breakdown_of,
)
from studyforge.exercise.bundle import Places
from studyforge.exercise.gates import G1, G2, G3, G4, G5
from studyforge.skills.exercises import Brief, Ran, gate_code, source_case, take
from tests.studyforge.skills.exercises import pytest_practice as practice
from tests.studyforge.skills.exercises.authoring import Running, write_corpus
from tests.support import run

BASKET = 2

#: What a failing run must NOT say: the failure would be about the draft, not the task.
NOT_AN_ASSERTION = re.compile(
    r"ImportError|ModuleNotFoundError|NotImplementedError|SyntaxError|NameError|"
    r"Timeout|timed out|TypeError|AttributeError"
)


class Recording:
    """The real runner, remembering which solution each run had in place and what it printed."""

    def __init__(self, solutions: dict[str, str]) -> None:
        self.running = Running()
        self.solutions = solutions
        self.outputs: dict[str, list[str]] = {}

    def __call__(self, root: Path, command: tuple[str, ...]) -> Ran:
        ran = self.running(root, command)
        placed = next(root.rglob("normalise.py")).read_text(encoding="utf-8")
        role = next(name for name, text in self.solutions.items() if text == placed)
        self.outputs.setdefault(role, []).append(ran.output)
        return ran


def _brief(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    page = pages[BASKET]
    places = Places(page.address, page.variant, page.unit, 1)
    return Brief(page, source_case(page, ledger), 1, places, 1, ()), ledger


def _solutions(draft) -> dict[str, str]:
    return {
        "reference": draft.reference,
        "starter": draft.starter,
        **{f"plant:{case}": text for case, text in draft.plants.items()},
    }


def _gated(tmp_path, **parts):
    brief, ledger = _brief(tmp_path)
    made = practice.draft(brief, **parts)
    recording = Recording(_solutions(made))
    return gate_code(made, brief, ledger, recording, source="demo", where="w"), recording


def _g(gated, gate):
    return next(verdict for verdict in gated.record.verdicts if verdict.id == gate)


def test_every_gate_holds_for_a_pytest_practice_graded_through_its_junit_report(tmp_path):
    gated, recording = _gated(tmp_path)
    assert gated.clears, [verdict.says for verdict in gated.refused]
    assert [verdict.id for verdict in gated.record.verdicts] == [G1, G2, G3, G4, G5]
    assert sorted(recording.outputs) == sorted(
        ["reference", "starter", *[f"plant:{case}" for case in practice.PLANTS]]
    )
    assert len(recording.outputs["reference"]) == 2, "G1 reads the reference twice"


def test_each_failing_run_fails_on_an_assertion_and_its_output_says_so(tmp_path):
    _, recording = _gated(tmp_path)
    for role, outputs in recording.outputs.items():
        text = "\n".join(outputs)
        if role == "reference":
            assert "AssertionError" not in text and " failed" not in text
            continue
        assert "AssertionError" in text, f"{role} did not fail on an assertion"
        assert NOT_AN_ASSERTION.search(text) is None, f"{role} failed for another reason"


def test_a_plant_fails_its_own_edge_and_only_the_cases_it_names(tmp_path):
    _, recording = _gated(tmp_path)
    failed = {
        role: set(re.findall(r"^FAILED \S+::(.+?)(?: - |$)", "\n".join(outputs), re.MULTILINE))
        for role, outputs in recording.outputs.items()
    }
    assert failed["plant:" + practice.BLANK.id] == {practice.BLANK.id}
    assert practice.INNER.id in failed["plant:" + practice.INNER.id]
    assert practice.MAIN_CASE.id not in failed["plant:" + practice.TABS.id]
    assert failed["starter"] == {case.id for case in (practice.MAIN_CASE, *_edges())}


def _edges():
    return (practice.BLANK, practice.INNER, practice.TABS)


def test_the_starter_that_raises_is_flagged_when_the_draft_asks_for_assertions_only(tmp_path):
    gated, _ = _gated(tmp_path, starter=practice.RAISING_STARTER)
    assert not gated.clears
    assert [verdict.id for verdict in gated.refused] == [G2]
    assert "not an assertion" in _g(gated, G2).says


def test_the_same_raising_starter_passes_as_it_always_did_without_that_request(tmp_path):
    gated, _ = _gated(tmp_path, starter=practice.RAISING_STARTER, assertions_only=False)
    assert gated.clears, [verdict.says for verdict in gated.refused]


def test_a_plant_that_errors_instead_of_failing_is_flagged_when_asked(tmp_path):
    brief, _ = _brief(tmp_path)
    broken = dict(practice.draft(brief).plants)
    broken[practice.BLANK.id] = "def normalise(text):\n    raise NotImplementedError\n"
    gated, _ = _gated(tmp_path, plants=broken)
    assert [verdict.id for verdict in gated.refused] == [G3]
    assert "not an assertion" in _g(gated, G3).says


def test_a_wrong_report_path_reads_no_report_and_the_gate_names_the_path(tmp_path):
    gated, _ = _gated(tmp_path, written="target/elsewhere.xml")
    assert not gated.clears
    says = [_g(gated, gate).says for gate in (G1, G4)]
    assert all(f"{practice.REPORT}'" in text and "no report at '" in text for text in says), says


def test_a_starter_that_does_not_import_is_not_a_clean_failure(tmp_path):
    gated, recording = _gated(tmp_path, starter="def normalise(:\n")
    assert not gated.clears
    assert "SyntaxError" in "\n".join(recording.outputs["starter"])
    assert _g(gated, G2).held is False


@pytest.mark.parametrize(
    "flag",
    [
        "--junitxml=/elsewhere/report.xml",
        "--junitxml=../report.xml",
        "--junitxml=other/dir/report.xml",
        "--junitxml=a\\b/report.xml",
    ],
)
def test_an_option_naming_a_path_outside_the_workspace_is_still_refused(tmp_path, flag):
    brief, ledger = _brief(tmp_path)
    ws = brief.places.workspace
    made = practice.draft(brief)
    command = tuple(flag if part.startswith("--junitxml=") else part for part in made.test_command)
    assert any(part == flag for part in command), ws
    with pytest.raises(ExerciseError):
        gate_code(
            replace(made, test_command=command), brief, ledger, Running(), source="demo", where="w"
        )


# --- the report reader, over a real pytest report -------------------------------------------


def _report(tmp_path, source: str) -> Path:
    """Run pytest over `source` as `tests/test_it.py` and return the root the report is in."""
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_it.py").write_text(source, encoding="utf-8")
    done = run(
        [
            "python3",
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--junitxml=report.xml",
            "tests/test_it.py",
        ],
        tmp_path,
    )
    assert done.returncode in (0, 1), done.stdout
    return tmp_path


def _fold(root, ids, started=0.0):
    cases = tuple(Case(i, MAIN if n == 0 else EDGE, "one sentence") for n, i in enumerate(ids))
    exercise = Exercise(
        main_path="m.py",
        test_path="tests/test_it.py",
        run_command=("python3", "m.py"),
        test_command=("python3", "-m", "pytest"),
        provenance="generated",
        trust="advisory",
        cases=cases,
        report=Report(format="junit", path="report.xml"),
    )
    return breakdown_of(exercise, root, "w", started=started)


SOURCE = """import pytest


def test_plain():
    assert True


class TestGroup:
    def test_inside(self):
        assert False


@pytest.mark.parametrize("v", ["a b", "1-2", "-1", "x.y"])
def test_param(v):
    assert v != "x.y"
"""


def test_a_bare_name_and_a_spaced_parametrised_id_fold_out_of_a_real_report(tmp_path):
    root = _report(tmp_path, SOURCE)
    ids = [
        "test_plain",
        "test_inside",
        "test_param[a b]",
        "test_param[1-2]",
        "test_param[-1]",
        "test_param[x.y]",
    ]
    folded = _fold(root, ids)
    assert folded.passed_ids == frozenset(ids) - {"test_inside", "test_param[x.y]"}
    assert folded.unasserted == frozenset()


def test_a_node_id_with_no_file_attribute_is_read_from_the_dotted_classname(tmp_path):
    root = _report(tmp_path, SOURCE)
    ids = [
        "tests/test_it.py::test_plain",
        "tests/test_it.py::TestGroup::test_inside",
        "tests/test_it.py::test_param[a b]",
    ]
    cases = ids + ["test_param[1-2]", "test_param[-1]", "test_param[x.y]"]
    folded = _fold(root, cases)
    assert folded.passed_ids >= {ids[0], ids[2]} and ids[1] not in folded.passed_ids


def test_a_node_id_that_spells_another_module_or_class_is_still_refused(tmp_path):
    root = _report(tmp_path, "def test_plain():\n    assert True\n")
    for wrong in (
        "tests/test_other.py::test_plain",
        "tests/test_it.py::TestX::test_plain",
        "tests/test_it::test_plain",
    ):
        with pytest.raises(ExerciseError, match="names a test"):
            _fold(root, [wrong])


def test_every_id_spelling_accepted_before_is_accepted_now(tmp_path):
    root = _report(tmp_path, "def test_plain():\n    assert True\n")
    assert _fold(root, ["test_plain"]).passed_ids == frozenset({"test_plain"})
    assert _fold(root, ["tests.test_it#test_plain"]).passed_ids == frozenset(
        {"tests.test_it#test_plain"}
    )


def test_what_failed_without_an_assertion_is_told_apart_from_what_failed_on_one(tmp_path):
    source = """import pytest


def test_assert():
    assert 1 == 2


def test_message():
    assert 1 == 2, "words"


def test_raised():
    raise AssertionError("explicit")


def test_did_not_raise():
    with pytest.raises(ValueError):
        pass


def test_nie():
    raise NotImplementedError("x")


def test_type():
    1 + "a"


def test_skipped():
    pytest.skip("s")
"""
    root = _report(tmp_path, source)
    ids = [
        "test_assert",
        "test_message",
        "test_raised",
        "test_did_not_raise",
        "test_nie",
        "test_type",
        "test_skipped",
    ]
    folded = _fold(root, ids)
    assert folded.passed_ids == frozenset()
    assert folded.unasserted == {"test_nie", "test_type", "test_skipped"}


def test_a_report_is_still_refused_when_stale(tmp_path):
    root = _report(tmp_path, "def test_plain():\n    assert True\n")
    with pytest.raises(ExerciseError, match="older than the run"):
        _fold(root, ["test_plain"], started=time.time() + 3600)
