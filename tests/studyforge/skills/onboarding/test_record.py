"""Mirror of `src/studyforge/skills/onboarding/record.py` (R12).

⭐ **Asserted both ways:** the record marks the one module a
person writes and carries no digest for it, so an edit there reads clean after
a regenerate — and every generated file whose bytes differ is still named.
"""

from __future__ import annotations

import hashlib
import importlib
import json
import os
from dataclasses import replace
from pathlib import PurePosixPath

import pytest

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.skills.adapter import PARTS, Written, scaffold
from studyforge.skills.onboarding.onboard import onboard
from studyforge.skills.onboarding.pin import RECORD_FILE
from studyforge.skills.onboarding.record import (
    INSTALLED_API,
    READS,
    OnboardingRefused,
    hand_edited,
    refuse_unrecorded,
)
from studyforge.skills.onboarding.removal import uninstall
from tests.studyforge.skills.onboarding import corpora


def _made():
    return onboard(corpora.draft(), framework_commit=corpora.COMMIT)


def _written(tmp_path):
    root = corpora.material(tmp_path / "corpus")
    made = _made()
    made.write(root)
    return root, made


def _record(root):
    return json.loads((root / RECORD_FILE).read_text(encoding="utf-8"))


def _marked(record):
    return [entry for entry in record["files"] if entry.get("hand_written") is True]


# --------------------------------------------------------------------------
# ⛔ Clause 1: the record marks the person's module; a regenerate neither
# re-records its digest nor writes the file
# --------------------------------------------------------------------------


def test_the_record_marks_the_persons_module_and_carries_no_digest_for_it(tmp_path):
    root, made = _written(tmp_path)

    record = _record(root)

    assert record["installed_api"] == INSTALLED_API
    assert _marked(record) == [{"where": made.hand_written[0], "hand_written": True}]
    others = [entry for entry in record["files"] if entry not in _marked(record)]
    assert len(others) == len(made.files) - len(made.hand_written) - 1, "the population moved"
    assert all(set(entry) == {"where", "sha256"} for entry in others)


def test_a_regenerate_neither_writes_the_persons_module_nor_records_a_digest_for_it(tmp_path):
    root, made = _written(tmp_path)
    mine = root / made.hand_written[0]
    mine.write_text("# mine\n", encoding="utf-8")

    written = made.write(root, regenerate=True)

    assert made.hand_written[0] not in written, "a regenerate wrote somebody's module"
    assert mine.read_text(encoding="utf-8") == "# mine\n"
    assert RECORD_FILE in written, "the record was not regenerated, so this measured nothing"
    assert _marked(_record(root)) == [{"where": made.hand_written[0], "hand_written": True}]


def test_the_mark_follows_the_seam_the_scaffold_declares_and_not_a_name(monkeypatch):
    # ⛔ R1: onboarding learns which module is a person's from the scaffold's
    # own `generated` flag. Move the seam, and the mark must move with it.
    moved = tuple(
        part if part.generated else replace(part, where="{package}/elsewhere.py") for part in PARTS
    )
    module = importlib.import_module("studyforge.skills.onboarding.onboard")
    monkeypatch.setattr(module, "scaffold", lambda plan: scaffold(plan, moved))

    made = _made()
    record = json.loads(next(item.text for item in made.files if item.where == RECORD_FILE))

    assert made.hand_written == ("ingest/elsewhere.py",)
    assert [entry["where"] for entry in _marked(record)] == ["ingest/elsewhere.py"]


# --------------------------------------------------------------------------
# ⛔ Clauses 2 and 3: both ways
# --------------------------------------------------------------------------


def test_an_edited_persons_module_reads_clean_after_a_regenerate(tmp_path):
    root, made = _written(tmp_path)
    (root / made.hand_written[0]).write_text("# mine\n", encoding="utf-8")

    made.write(root, regenerate=True)

    assert hand_edited(root) == []


def test_an_edited_generated_module_beside_the_persons_is_named(tmp_path):
    root, made = _written(tmp_path)
    (root / made.hand_written[0]).write_text("# mine\n", encoding="utf-8")
    made.write(root, regenerate=True)
    package = PurePosixPath(made.hand_written[0]).parent
    beside = next(
        item.where
        for item in made.files
        if item.generated and PurePosixPath(item.where).parent == package
    )
    (root / beside).write_text("# edited by hand\n", encoding="utf-8")

    assert hand_edited(root) == [beside]


def test_every_generated_file_whose_bytes_differ_from_the_record_is_named(tmp_path):
    root, made = _written(tmp_path)
    generated = [item.where for item in made.files if item.generated and item.where != RECORD_FILE]
    assert len(generated) == len(made.files) - len(made.hand_written) - 1, "the population moved"

    for where in generated:
        path = root / where
        before = path.read_text(encoding="utf-8")
        path.write_text(before + "# edited by hand\n", encoding="utf-8")
        assert hand_edited(root) == [where], where
        path.write_text(before, encoding="utf-8")

    assert hand_edited(root) == []


# --------------------------------------------------------------------------
# The record as a document: its gate, its shapes, and what uninstall does
# --------------------------------------------------------------------------


def test_the_record_is_read_through_the_personal_data_gate(tmp_path):
    # ⛔ R7: a record is a list of paths, the shape a home directory
    # arrives in. The planted path is expanded, never typed.
    root, _ = _written(tmp_path)
    record = _record(root)
    record["files"].append(
        {"where": "/" + f"home/{os.environ.get('USER', 'someone')}/x", "sha256": ""}
    )
    (root / RECORD_FILE).write_text(json.dumps(record), encoding="utf-8")

    with pytest.raises(PersonalDataLeak):
        hand_edited(root)


def test_a_record_this_build_does_not_read_is_refused_by_name(tmp_path):
    root, _ = _written(tmp_path)
    (root / RECORD_FILE).write_text(json.dumps({"installed_api": 99}), encoding="utf-8")

    with pytest.raises(OnboardingRefused) as refused:
        hand_edited(root)

    assert str(INSTALLED_API) in str(refused.value)
    assert INSTALLED_API in READS


def test_uninstall_still_reads_a_record_the_previous_shape_wrote(tmp_path):
    root = corpora.material(tmp_path / "corpus")
    before = sorted(path.relative_to(root).as_posix() for path in root.rglob("*"))
    made = _made()
    made.write(root)
    record = _record(root)
    for entry in _marked(record):
        entry.pop("hand_written")
        entry["sha256"] = hashlib.sha256((root / entry["where"]).read_bytes()).hexdigest()
    (root / RECORD_FILE).write_text(json.dumps({**record, "installed_api": 1}), encoding="utf-8")

    uninstall(root)

    assert sorted(path.relative_to(root).as_posix() for path in root.rglob("*")) == before


def test_uninstall_keeps_the_persons_module_when_its_stub_cannot_be_derived(tmp_path):
    # ⛔ The mark carries no digest, so the stub is re-derived from the written
    # manifest. A changed manifest means it cannot be, and the module is kept.
    root, made = _written(tmp_path)
    manifest = root / "corpus.json"
    manifest.write_text(manifest.read_text(encoding="utf-8") + "\n", encoding="utf-8")

    with pytest.raises(OnboardingRefused) as refused:
        uninstall(root)

    assert "corpus.json" in str(refused.value)
    assert made.hand_written[0] in str(refused.value)
    assert (root / made.hand_written[0]).exists()


# --------------------------------------------------------------------------
# ⛔ A regenerate never claims a file a person wrote
# --------------------------------------------------------------------------


def _at(where):
    """A generated file this regenerate would write at `where`."""
    return Written(where=where, step=3, why="a fabricated file", generated=True, text="x\n")


def test_an_ignore_file_the_record_does_not_list_is_refused_by_name(tmp_path):
    root, made = _written(tmp_path)
    (root / "notes").mkdir()
    (root / "notes/.gitignore").write_text("draft-*\n", encoding="utf-8")

    with pytest.raises(OnboardingRefused) as refused:
        refuse_unrecorded(root, [*made.files, _at("notes/.gitignore")])

    assert "['notes/.gitignore']" in str(refused.value)
    assert str(tmp_path) not in str(refused.value)


def test_a_file_of_any_other_name_the_record_does_not_list_is_refused_too(tmp_path):
    # ⛔ Not only ignore files.
    root, made = _written(tmp_path)
    (root / "notes").mkdir()
    (root / "notes/keep.txt").write_text("mine\n", encoding="utf-8")

    with pytest.raises(OnboardingRefused) as refused:
        refuse_unrecorded(root, [*made.files, _at("notes/keep.txt")])

    assert "['notes/keep.txt']" in str(refused.value)


def test_the_files_the_record_lists_and_an_absent_path_are_not_refused(tmp_path):
    # ⭐ The other way: the record's own files, and a path nobody has written.
    root, made = _written(tmp_path)

    assert made.files, "the onboarding wrote nothing, so this reads nothing"
    refuse_unrecorded(root, [*made.files, _at("absent/.gitignore"), _at("absent/keep.txt")])


def test_a_person_s_module_and_the_record_itself_are_never_refused(tmp_path):
    # ⭐ `write_files` keeps an existing hand-written module, and the record
    # never lists itself — neither is overwritten-and-claimed.
    root, made = _written(tmp_path)
    (root / made.hand_written[0]).write_text("# mine\n", encoding="utf-8")
    assert RECORD_FILE not in {entry["where"] for entry in _record(root)["files"]}

    refuse_unrecorded(root, made.files)


def test_a_path_the_record_marks_as_the_person_s_is_not_claimed_as_generated(tmp_path):
    # ⛔ Listed is not enough: the record must list it as GENERATED.
    root, made = _written(tmp_path)
    target = made.hand_written[0]

    with pytest.raises(OnboardingRefused) as refused:
        refuse_unrecorded(root, [_at(target)])

    assert f"['{target}']" in str(refused.value)
