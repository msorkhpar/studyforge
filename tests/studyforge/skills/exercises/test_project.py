"""Mirror of `skills.exercises.project` (R12): a project practice from a before/after pair.

⭐ **Every gate reading is a real `pytest` process** over the sample project's real snapshots
(`tests/fixtures/project/`): the reference passes, the starter fails on assertions while every
kept requirement still passes on it, and each planted defect is caught by its own test.
"""

from __future__ import annotations

import json

import pytest

from studyforge.exercise import EDGE, KEPT, MAIN, from_document
from studyforge.exercise.bundle import bundle_of, emit
from studyforge.exercise.gates import G1, G2, G3, G4, G5
from studyforge.skills.exercises import AuthoringError
from studyforge.skills.exercises.project import project_draft, read_manifest
from tests.studyforge.skills.exercises.project_sample import MANIFEST, copy_sample, gated

WS = "practice/seeds/prose/unit-01/practice-1"


def test_the_sample_project_clears_every_gate(tmp_path):
    result, _ = gated(tmp_path)
    assert result.clears, [verdict.says for verdict in result.refused]
    assert [verdict.id for verdict in result.record.verdicts] == [G1, G2, G3, G4, G5]
    g2 = next(verdict for verdict in result.record.verdicts if verdict.id == G2)
    assert "all 4 kept cases passed on it" in g2.says


def test_the_draft_takes_its_starter_from_before_and_its_reference_and_grade_from_after():
    draft = project_draft(MANIFEST, WS)
    assert draft.main_file == "seedcrate/model.py"
    assert "def must_ship(lots: list[Lot]) -> tuple[str, ...]:" in draft.starter
    assert "    return ()" in draft.starter, "the new method was not stubbed"
    assert "if room < 0" in draft.reference and "if room < 0" not in draft.starter
    assert set(draft.files) == {
        "main.py", "seedcrate/__init__.py", "seedcrate/data.py", "seedcrate/report.py",
        "seedcrate/solve.py"}
    assert "tests/fixtures/heavy.csv" in draft.read_only and "data/lots.csv" in draft.read_only
    assert draft.test_file == "tests/test_expected_output.py"
    assert draft.build == {"pytest.ini": "[pytest]\npythonpath = .\ntestpaths = tests\n"}
    assert draft.run_command == ("python3", f"{WS}/main.py")
    assert draft.test_command[-1] == f"{WS}/tests"
    assert "### Blueprint" in draft.statement and "[Fixing a variable]" in draft.statement


def test_every_test_is_a_case_and_the_unchanged_ones_are_kept():
    cases = project_draft(MANIFEST, WS).cases
    kinds = {kind: [case.id for case in cases if case.kind == kind] for kind in (MAIN, EDGE, KEPT)}
    assert len(kinds[MAIN]) == 4 and len(kinds[EDGE]) == 3
    assert "tests/test_model.py::test_picks_the_most_valuable_fit" in kinds[KEPT]
    check = "tests/test_expected_output.py::test_the_report_matches_the_expected_output"
    assert cases[-1].id == check
    kept = next(case for case in cases if case.id.endswith("test_nothing_fits_in_an_empty_crate"))
    assert kept.says == "A crate with no room carries nothing", "not worded by its docstring"


def test_a_new_test_the_manifest_does_not_declare_is_refused(tmp_path):
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest = copy_sample(tmp_path, {"cases": document["cases"][1:], "plants": {}})
    with pytest.raises(AuthoringError, match="new or changed in this step"):
        project_draft(manifest, WS)


def test_a_blueprint_method_the_reference_lacks_is_refused(tmp_path):
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    blueprint = [{**document["blueprint"][0], "signature": "def no_such(lots)"}]
    with pytest.raises(AuthoringError, match="does not define 'no_such'"):
        project_draft(copy_sample(tmp_path, {"blueprint": blueprint}), WS)


@pytest.mark.parametrize(
    "change",
    [{"surprise": 1}, {"project_api": 2}, {"title": ""}, {"cases": [["a", "huge", "b"]]}],
)
def test_a_bad_manifest_is_refused_by_key(tmp_path, change):
    with pytest.raises(AuthoringError):
        read_manifest(copy_sample(tmp_path, change))


def test_a_kept_case_that_fails_on_the_starter_is_refused_by_g2(tmp_path):
    # ⛔ Declared kept, the new must-ship test is work this step asks for, and G2 says so.
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    cases = [
        [one[0], KEPT, one[2]] if one[0].endswith("test_a_must_ship_lot_is_always_chosen") else one
        for one in document["cases"]
    ]
    result, _ = gated(tmp_path, copy_sample(tmp_path, {"cases": cases}))
    g2 = next(verdict for verdict in result.record.verdicts if verdict.id == G2)
    assert not g2.held and "kept cases did not pass on the starter" in g2.says


def test_the_bundle_ships_the_read_only_files_and_the_record_names_them(tmp_path):
    result, draft = gated(tmp_path)
    shipped = dict(result.files)
    bundle = result.places.bundle
    assert f"{bundle}/tests/tests/fixtures/must.csv" in shipped
    assert f"{WS}/tests/fixtures/must.csv" in shipped, "the workspace lacks a fixture"
    assert f"{WS}/pytest.ini" in shipped
    roles = {one.role for one in result.record.inputs}
    assert "tests:tests/test_model.py" in roles and "tests:data/lots.csv" in roles
    document = json.loads(shipped[f"{bundle}/bundle.json"])
    assert document["read_only"] == list(draft.read_only)
    out = tmp_path / "out"
    for path, data in result.files:
        (out / path).parent.mkdir(parents=True, exist_ok=True)
        (out / path).write_bytes(data)
    emitted = emit(out, bundle_of(document, "bundle.json"), source="demo", ingested="2026-01-05")
    record = from_document(emitted.document["exercise"], "w")
    assert record.read_only == tuple(f"{WS}/{path}" for path in draft.read_only)


#: A module new in step 01 with a blueprint method: its import, constant and helper must survive.
RULES = (
    '"""Shipping rules."""\n\nfrom seedcrate.data import Lot\n\n'
    "#: The heaviest lot a crate takes.\nHEAVIEST = 5\n\n\n"
    "def too_heavy(lots: list[Lot]) -> tuple[str, ...]:\n"
    '    """The reference body."""\n'
    "    return tuple(lot.name for lot in lots if lot.weight > HEAVIEST)\n\n\n"
    "def names(lots: list[Lot]) -> list[str]:\n    return [lot.name for lot in lots]\n"
)

#: A module new in step 01 with no blueprint method: it ships as the reference has it.
UNITS = '"""Units."""\n\nKG = "kg"\n'


def test_a_file_new_in_the_step_starts_as_the_reference_with_only_blueprint_bodies_stubbed(
    tmp_path,
):
    document = json.loads(MANIFEST.read_text(encoding="utf-8"))
    rule = {
        **document["blueprint"][0],
        "file": "seedcrate/rules.py",
        "signature": "def too_heavy(lots: list[Lot]) -> tuple[str, ...]",
        "contract": "The names of the lots heavier than HEAVIEST.",
    }
    manifest = copy_sample(tmp_path, {"blueprint": [*document["blueprint"], rule]})
    after = manifest.parent / document["after"]
    (after / "seedcrate" / "rules.py").write_text(RULES, encoding="utf-8")
    (after / "seedcrate" / "units.py").write_text(UNITS, encoding="utf-8")
    draft = project_draft(manifest, WS)
    assert draft.files["seedcrate/units.py"].starter == UNITS, "a new file without methods"
    rules = draft.files["seedcrate/rules.py"]
    assert rules.reference == RULES
    assert rules.starter == RULES.replace(
        '    """The reference body."""\n'
        "    return tuple(lot.name for lot in lots if lot.weight > HEAVIEST)\n",
        '    """The names of the lots heavier than HEAVIEST."""\n    return ()\n',
    )
    assert "    return ()" in draft.starter, "a file of the before step lost its stub"
    result, _ = gated(tmp_path / "gate", manifest)
    assert result.clears, [verdict.says for verdict in result.refused]
