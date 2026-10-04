"""A practice whose reader edits several files is gated, emitted, read back and shown whole.

⭐ Every run is a real `pytest` over real files (`authoring.Running`). What it asserts:
- every gate holds, and each plant fails exactly its own edge, whichever file it changes;
- the bundle files a starter and a reference for each further file and the gate record digests
  each, so changing one starter drifts the record;
- the emission writes every edited file into the reader's workspace and the record names them;
- a replacement naming a file the reader does not edit is refused;
- a practice of one file is the bundle, record and files it always was.
"""

from __future__ import annotations

import json
from dataclasses import replace
from pathlib import Path

import pytest

from studyforge.exercise import ExerciseError
from studyforge.exercise import of as exercise_of
from studyforge.exercise.bundle import Places, PlantSpec, Replacement, bundle_of
from studyforge.exercise.gates import G1, G2, G3, G4, G5
from studyforge.skills.exercises import Brief, EditedFile, gate_code, source_case, take
from tests.studyforge.skills.exercises import multifile_practice as practice
from tests.studyforge.skills.exercises import pytest_practice as single
from tests.studyforge.skills.exercises.authoring import Running, write_corpus

BASKET = 2


def _brief(tmp_path):
    material, graders, pages = write_corpus(tmp_path)
    ledger = take(tmp_path, material, graders, "the ledger")
    page = pages[BASKET]
    places = Places(page.address, page.variant, page.unit, 1)
    return Brief(page, source_case(page, ledger), 1, places, 1, ()), ledger


def _gated(tmp_path, **parts):
    brief, ledger = _brief(tmp_path)
    made = practice.draft(brief, **parts)
    return gate_code(made, brief, ledger, Running(), source="demo", where="w"), brief


def test_every_gate_holds_for_a_practice_of_three_files(tmp_path):
    gated, _ = _gated(tmp_path)
    assert gated.clears, [verdict.says for verdict in gated.refused]
    assert [verdict.id for verdict in gated.record.verdicts] == [G1, G2, G3, G4, G5]


def test_the_record_digests_every_edited_file_and_names_them(tmp_path):
    gated, brief = _gated(tmp_path)
    roles = {entry.role for entry in gated.record.inputs}
    assert {f"starter:{practice.NOTES}", f"reference:{practice.HOOK}"} <= roles
    held = {path for path, _ in gated.files}
    ws = brief.places.workspace
    assert {f"{ws}/{practice.SETTINGS}", f"{ws}/{practice.NOTES}", f"{ws}/{practice.HOOK}"} <= held
    bundle = bundle_of(
        json.loads(dict(gated.files)[brief.places.document].decode("utf-8")), "w"
    )
    assert bundle.files == (practice.NOTES, practice.HOOK)
    assert bundle.edited == (practice.SETTINGS, practice.NOTES, practice.HOOK)


def test_the_reader_workspace_starts_every_file_from_its_starter(tmp_path):
    gated, brief = _gated(tmp_path)
    ws = brief.places.workspace
    written = dict(gated.files)
    assert written[f"{ws}/{practice.NOTES}"].decode() == practice.STARTER_NOTES
    assert written[f"{ws}/{practice.HOOK}"].decode() == practice.STARTER_HOOK


def test_the_exercise_record_lists_the_further_files_and_reads_back(tmp_path):
    from studyforge.exercise import from_document, to_document

    record = from_document(
        {
            "main_path": "practice/p/settings.json",
            "files": ["practice/p/docs/memory.md"],
            "run_command": ["true"],
        },
        "w",
    )
    assert record.files == ("practice/p/docs/memory.md",)
    assert to_document(record)["files"] == ["practice/p/docs/memory.md"]
    assert list(to_document(record)) == ["main_path", "run_command", "files"]
    with pytest.raises(ExerciseError):
        from_document({"main_path": "a.json", "files": [], "run_command": ["true"]}, "w")
    with pytest.raises(ExerciseError):
        from_document({"main_path": "a.json", "files": ["a.json"], "run_command": ["true"]}, "w")


def test_a_replacement_naming_a_file_the_reader_does_not_edit_is_refused(tmp_path):
    brief, ledger = _brief(tmp_path)
    made = practice.draft(brief)
    plants = dict(made.plants)
    plants[practice.GUARD.id] = PlantSpec((Replacement("test_setup.py", "exit 2", "exit 1"),))
    with pytest.raises(ExerciseError):
        gate_code(
            replace(made, plants=plants), brief, ledger, Running(), source="demo", where="w"
        )


def test_a_plant_that_does_not_fail_its_own_edge_is_caught_by_g3(tmp_path):
    brief, _ = _brief(tmp_path)
    plants = dict(practice.draft(brief).plants)
    # The plant changes the hook, but the edge it is filed for is the memory file's.
    plants[practice.MEMORY.id] = PlantSpec((Replacement(practice.HOOK, "exit 2", "exit 1"),))
    gated, _ = _gated(tmp_path, plants=plants)
    assert not gated.clears
    assert [verdict.id for verdict in gated.refused] == [G3]


def test_a_further_file_whose_starter_already_passes_is_caught_by_g2(tmp_path):
    gated, _ = _gated(
        tmp_path,
        files={
            practice.NOTES: EditedFile(practice.REFERENCE_NOTES, practice.REFERENCE_NOTES),
            practice.HOOK: EditedFile(practice.STARTER_HOOK, practice.REFERENCE_HOOK),
        },
    )
    assert [verdict.id for verdict in gated.refused] == [G2]


def test_a_practice_of_one_file_has_no_further_file_anywhere(tmp_path):
    brief, ledger = _brief(tmp_path)
    made = single.draft(brief)
    gated = gate_code(made, brief, ledger, Running(), source="demo", where="w")
    assert gated.clears
    document = json.loads(dict(gated.files)[brief.places.document].decode("utf-8"))
    assert "files" not in document
    roles = [entry.role for entry in gated.record.inputs]
    assert not any(role.startswith(("starter:", "reference:")) for role in roles)


def test_the_bundle_refuses_a_further_file_that_is_the_main_or_the_test_file(tmp_path):
    brief, _ = _brief(tmp_path)
    ws = brief.places
    document = json.loads(_bundle_text(tmp_path))
    for clash in (document["main_file"], document["test_file"]):
        bad = {**document, "files": [clash]}
        with pytest.raises(ExerciseError):
            bundle_of(bad, "w")
    assert isinstance(ws, Places)


def _bundle_text(tmp_path) -> str:
    gated, brief = _gated(tmp_path)
    return dict(gated.files)[brief.places.document].decode("utf-8")


def _committed(tmp_path):
    gated, brief = _gated(tmp_path)
    root = tmp_path / "corpus"
    for path, data in gated.files:
        target = root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(data)
    return root, brief


def test_the_adapter_reads_the_committed_bundle_into_a_document_that_names_every_file(tmp_path):
    from studyforge.skills.adapter.practices import authored

    root, brief = _committed(tmp_path)
    found = authored(root)
    (practice_found,) = next(iter(found.pages.values()))
    ws = brief.places.workspace
    record = practice_found.fields["exercise"]
    assert record["main_path"] == f"{ws}/{practice.SETTINGS}"
    assert record["files"] == [f"{ws}/{practice.NOTES}", f"{ws}/{practice.HOOK}"]
    text = json.dumps(practice_found.fields["blocks"])
    assert "File: docs/memory.md" in text and "File: hooks/guard.sh" in text


def test_a_changed_starter_of_a_further_file_drifts_the_gate_record(tmp_path):
    from studyforge.skills.adapter.practices import PracticeRefused, authored

    root, brief = _committed(tmp_path)
    starter = root / brief.places.in_bundle(f"starter/{practice.NOTES}")
    starter.write_text(starter.read_text(encoding="utf-8") + "changed\n", encoding="utf-8")
    with pytest.raises(PracticeRefused):
        authored(root)


def test_the_edited_files_are_in_the_workspace_the_reader_opens(tmp_path):
    root, brief = _committed(tmp_path)
    workspace = Path(root / brief.places.workspace)
    names = sorted(p.relative_to(workspace).as_posix() for p in workspace.rglob("*") if p.is_file())
    assert {practice.NOTES, practice.HOOK, practice.SETTINGS, "test_setup.py"} <= set(names)
