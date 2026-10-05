"""The try-it file of a practice (R12): record, bundle, emit and the validate rule."""

from __future__ import annotations

from types import SimpleNamespace

import pytest

from studyforge.exercise import ExerciseError, from_document, of, to_document
from studyforge.exercise.bundle import bundle_of, bundle_document, emit
from studyforge.validate.exercises import RULE_RUN_IS_SUBMIT, check_run_is_not_submit
from tests.studyforge.exercise.bundle import bundles

WS = "practice/p"
BASE = {
    "main_path": f"{WS}/solution.py",
    "test_path": f"{WS}/test_solution.py",
    "run_command": ["python3", f"{WS}/try_it.py"],
    "test_command": ["python3", "-m", "pytest", f"{WS}/test_solution.py"],
    "provenance": "bundled",
    "trust": "authoritative",
}
WITH = {**BASE, "files": [f"{WS}/try_it.py"], "try_file": f"{WS}/try_it.py"}


def test_a_record_with_a_try_file_round_trips_and_one_without_is_unchanged():
    record = from_document(WITH, "w")
    assert record.try_file == f"{WS}/try_it.py"
    assert to_document(record) == WITH
    assert list(to_document(record))[-1] == "try_file"
    plain = from_document(BASE, "w")
    assert plain.try_file is None
    assert "try_file" not in to_document(plain) and to_document(plain) == BASE


def test_an_ungraded_record_may_carry_one():
    ungraded = {key: WITH[key] for key in ("main_path", "run_command", "files", "try_file")}
    assert to_document(from_document(ungraded, "w")) == ungraded


@pytest.mark.parametrize(
    "change",
    [
        {"try_file": f"{WS}/other.py"},  # not one of files
        {"try_file": "../escape.py"},  # not a safe path
        {"run_command": BASE["test_command"]},  # Run would grade like Submit
    ],
)
def test_a_bad_try_file_is_refused(change):
    with pytest.raises(ExerciseError):
        from_document({**WITH, **change}, "w")


def test_a_try_file_on_a_quiz_is_refused():
    with pytest.raises(ExerciseError):
        from_document({"kind": "quiz", "try_file": "a.py", "questions": []}, "w")


TRY_RUN = ["python3", "practice/demo/prose/unit-02/practice-1/try_it.py"]


def _bundle(root, **more):
    more = {"run_command": TRY_RUN, **more}
    declared = bundles.document(files=["try_it.py"], try_file="try_it.py", **more)
    spot = bundles.write_bundle(root, **{"files": ["try_it.py"], "try_file": "try_it.py", **more})
    where = root / spot.bundle
    for role in ("starter", "reference"):
        (where / role / "try_it.py").write_text("print('hi')\n", encoding="utf-8")
    return bundle_of(declared, "bundle.json")


def test_a_bundle_carries_it_to_the_record_and_the_workspace(tmp_path):
    bundle = _bundle(tmp_path)
    assert bundle_document(bundle)["try_file"] == "try_it.py"
    emission = emit(tmp_path, bundle, source="demo", ingested="2026-01-05")
    record = emission.document["exercise"]
    assert record["try_file"] == bundle.places.in_workspace("try_it.py")
    assert record["try_file"] in record["files"]
    assert record["try_file"] in emission.paths


def test_a_bundle_without_one_is_as_before():
    bundle = bundle_of(bundles.document(), "bundle.json")
    assert bundle.try_file is None and "try_file" not in bundle_document(bundle)


def test_a_bundle_whose_try_file_is_not_edited_or_whose_run_grades_is_refused():
    with pytest.raises(ExerciseError):
        bundle_of(bundles.document(try_file="try_it.py"), "bundle.json")
    plain = bundles.document()
    tried = {**plain, "files": ["try_it.py"], "try_file": "try_it.py"}
    bundle_of({**tried, "run_command": TRY_RUN}, "bundle.json")
    with pytest.raises(ExerciseError):
        bundle_of({**tried, "run_command": plain["test_command"]}, "bundle.json")


def _walk(*records):
    units = [SimpleNamespace(where=f"u{n}", document={"kind": "practice", "exercise": r})
             for n, r in enumerate(records)]
    return SimpleNamespace(units=units)


def test_the_rule_fires_on_run_equal_to_test_once_a_course_has_a_try_file():
    same = {**BASE, "run_command": BASE["test_command"]}
    found = list(check_run_is_not_submit(_walk(WITH, same)))
    assert [(f.rule, f.where) for f in found] == [(RULE_RUN_IS_SUBMIT, "u1")]
    assert "Run would grade like Submit" in found[0].message


def test_the_rule_is_quiet_for_a_course_that_has_no_try_file_and_for_no_code_practice():
    same = {**BASE, "run_command": BASE["test_command"]}
    assert list(check_run_is_not_submit(_walk(same, BASE))) == []
    quiz = {"kind": "quiz", "questions": []}
    assert list(check_run_is_not_submit(SimpleNamespace(units=[]))) == []
    assert list(check_run_is_not_submit(_walk(quiz))) == []
