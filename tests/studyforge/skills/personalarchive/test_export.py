"""Mirror of `src/studyforge/skills/personalarchive/export.py` (R12): who the archive is for.

⛔ **Asserted, not inspected.** A sharing archive is opened and every member is read. The
test fails if a practice key, a progress field or a store path reaches it, or if any
member carries an R7 shape. The owner archive of the same corpus carries every one of
those progress tokens, so each assertion has been shown capable of red.

⛔ **No file reaches a sharing archive unjudged.** The planted `cover.bin` is
refused by name, a corpus narrated by the framework's own stage still exports with every
clip judged and carried, a file under a clip's name is judged like any other, and an owner
archive carries a file that is not text unread, as before.
"""

from __future__ import annotations

import inspect
import io
import json
import os

import pytest

from studyforge.archive.scrub import leaks
from studyforge.skills.personalarchive import OWNER, SHARING, export, record
from studyforge.skills.personalarchive.export import material
from studyforge.skills.personalarchive.layout import (
    MANIFEST_MEMBER,
    MATERIAL_PREFIX,
    PROGRESS_MEMBER,
    read_manifest,
)
from tests.studyforge.cli.narrate import service
from tests.studyforge.cli.narrate.plant import narrated, record_of
from tests.studyforge.generate.corpora import BOTH, a_corpus
from tests.studyforge.skills.personalarchive.archiving import (
    KEY,
    TIMES,
    binary_identity,
    clip_audio,
    machine,
    members,
    planted_identity,
    run,
    store,
)

#: What progress looks like inside an archive. ⛔ None of them may reach a sharing one.
PROGRESS_TOKENS = (KEY, "first_passed_at", "progress_api", TIMES["t2"])


def exported(root, archive, kind):
    out = io.StringIO()
    return export(root, archive, kind=kind, stream=out), out.getvalue()


def with_progress(tmp_path):
    root = machine(tmp_path, "a")
    run(root, passed=False, when=TIMES["t1"])
    run(root, passed=True, when=TIMES["t2"])
    return root


def carried_text(archive) -> str:
    return "\n".join(data.decode("utf-8") for data in members(archive).values())


def test_a_sharing_archive_carries_no_progress_and_no_store_path(tmp_path):
    root = with_progress(tmp_path)
    archive = tmp_path / "shared.zip"
    code, said = exported(root, archive, SHARING)
    assert code == 0, said
    carried = members(archive)
    assert PROGRESS_MEMBER not in carried
    assert read_manifest(carried[MANIFEST_MEMBER].decode("utf-8"))["progress"] is False
    assert not [name for name in carried if record.store_path(root) in name]
    text = carried_text(archive)
    assert [token for token in PROGRESS_TOKENS if token in text] == []
    assert "progress none: a sharing archive carries no progress" in said
    assert "material judged as bytes 0" in said


def test_the_owner_archive_of_the_same_corpus_carries_the_progress_the_store_reads(tmp_path):
    root = with_progress(tmp_path)
    archive = tmp_path / "mine.zip"
    code, said = exported(root, archive, OWNER)
    assert code == 0, said
    carried = members(archive)
    assert json.loads(carried[PROGRESS_MEMBER]) == store(root).read()
    text = carried_text(archive)
    assert [token for token in PROGRESS_TOKENS if token in text] == list(PROGRESS_TOKENS)
    # ⭐ Progress travels as progress, never as the store's files.
    assert not [name for name in carried if record.store_path(root) in name]
    assert "progress 1 practice(s)" in said


def test_every_member_of_a_sharing_archive_is_clean_by_the_r7_gate(tmp_path):
    archive = tmp_path / "shared.zip"
    assert exported(with_progress(tmp_path), archive, SHARING)[0] == 0
    for name, data in members(archive).items():
        assert list(leaks(name, "a member name")) == []
        assert list(leaks(data.decode("utf-8"), name)) == []


@pytest.mark.parametrize("kind", [OWNER, SHARING])
def test_a_planted_identity_in_a_material_file_refuses_the_export_and_leaves_no_file(
    tmp_path, kind
):
    root = with_progress(tmp_path)
    (root / "notes.md").write_text(f"kept at {planted_identity()}\n", encoding="utf-8")
    archive = tmp_path / "out.zip"
    code, said = exported(root, archive, kind)
    assert code == 1 and not archive.exists(), said
    assert "refused" in said and planted_identity() not in said


def test_a_planted_identity_in_a_file_name_refuses_the_export(tmp_path):
    root = machine(tmp_path, "a")
    (root / ("jane.doe" + "@" + "mailhost.org.md")).write_text("notes\n", encoding="utf-8")
    archive = tmp_path / "out.zip"
    assert exported(root, archive, SHARING)[0] == 1 and not archive.exists()


def test_who_the_archive_is_for_has_no_default(tmp_path):
    assert inspect.signature(export).parameters["kind"].default is inspect.Parameter.empty
    archive = tmp_path / "out.zip"
    for kind in ("", None, "everyone"):
        assert exported(machine(tmp_path, f"k{kind}"), archive, kind)[0] == 1
        assert not archive.exists()


def test_an_existing_archive_file_is_never_overwritten(tmp_path):
    archive = tmp_path / "out.zip"
    archive.write_bytes(b"mine")
    assert exported(machine(tmp_path, "a"), archive, SHARING)[0] == 1
    assert archive.read_bytes() == b"mine"


def test_an_archive_inside_the_corpus_root_is_refused(tmp_path):
    root = machine(tmp_path, "a")
    assert exported(root, root / "out.zip", OWNER)[0] == 1
    assert not (root / "out.zip").exists()


@pytest.mark.parametrize("target", ["corpus.json", "archive"])
def test_a_symbolic_link_in_the_corpus_is_refused(tmp_path, target):
    root = machine(tmp_path, "a")
    (root / "link").symlink_to(root / target)
    code, said = exported(root, tmp_path / "out.zip", OWNER)
    assert code == 1 and ("symbolic link" in said or "regular file" in said), said
    assert not (tmp_path / "out.zip").exists()


def test_version_control_bytecode_and_the_store_are_never_material_and_the_rest_is(tmp_path):
    root = with_progress(tmp_path)
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("[core]\n", encoding="utf-8")
    (root / "tools" / "__pycache__").mkdir(parents=True)
    (root / "tools" / "__pycache__" / "m.pyc").write_bytes(b"\x00")
    (root / "tools" / "run.sh").write_text("#!/bin/sh\n", encoding="utf-8")
    everything = {
        os.path.relpath(os.path.join(directory, name), root).replace(os.sep, "/")
        for directory, _, names in os.walk(root)
        for name in names
    }
    store_prefix = record.store_path(root) + "/"
    expected = {
        path
        for path in everything
        if not path.startswith((".git/", store_prefix)) and "__pycache__" not in path
    }
    carried = {carried.path for carried in material(root, record.store_path(root), kind=SHARING)}
    assert carried == expected and "tools/run.sh" in carried
    assert any(path.startswith(store_prefix) for path in everything)


def test_exporting_one_tree_twice_gives_the_same_bytes(tmp_path):
    root = with_progress(tmp_path)
    first, second = tmp_path / "one.zip", tmp_path / "two.zip"
    assert exported(root, first, OWNER)[0] == exported(root, second, OWNER)[0] == 0
    assert first.read_bytes() == second.read_bytes()


def test_the_material_prefix_holds_every_carried_file(tmp_path):
    archive = tmp_path / "out.zip"
    root = machine(tmp_path, "a")
    assert exported(root, archive, SHARING)[0] == 0
    carried = members(archive)
    declared = read_manifest(carried[MANIFEST_MEMBER].decode("utf-8"))["material"]
    assert {MATERIAL_PREFIX + entry["path"] for entry in declared} == set(carried) - {
        MANIFEST_MEMBER
    }


@pytest.mark.parametrize("name", BOTH)
@pytest.mark.parametrize("encoding", ["utf-8", "utf-16-le", "utf-16-be"])
def test_the_registers_cover_bin_is_refused_for_sharing_by_name_with_the_remedy(
    tmp_path, name, encoding
):
    root = a_corpus(tmp_path, name)
    (root / "cover.bin").write_bytes(binary_identity(encoding))
    archive = tmp_path / "shared.zip"
    code, said = exported(root, archive, SHARING)
    assert code == 1 and not archive.exists(), said
    assert "refused 'cover.bin' is not UTF-8 text" in said and "owner archive" in said, said
    assert planted_identity() not in said


def test_an_owner_archive_carries_a_file_that_is_not_text_unread_as_before(tmp_path):
    root = machine(tmp_path, "a")
    (root / "cover.bin").write_bytes(binary_identity())
    archive = tmp_path / "mine.zip"
    code, said = exported(root, archive, OWNER)
    assert code == 0, said
    assert members(archive)[MATERIAL_PREFIX + "cover.bin"] == binary_identity()
    assert "judged as bytes" not in said


@pytest.mark.parametrize("name", BOTH)
def test_a_corpus_narrated_by_the_framework_exports_for_sharing_with_every_clip_judged(
    tmp_path, monkeypatch, name
):
    monkeypatch.setattr(service, "audio_for", clip_audio)
    root = narrated(tmp_path, name)
    clips = sorted(root.rglob(f"*.{service.FMT}"))
    assert clips and len(clips) == len(record_of(root)["clips"])
    assert not [clip for clip in clips if _is_text(clip.read_bytes())]
    archive = tmp_path / "shared.zip"
    code, said = exported(root, archive, SHARING)
    assert code == 0, said
    assert f"material judged as bytes {len(clips)}" in said
    carried = members(archive)
    for clip in clips:
        assert carried[MATERIAL_PREFIX + clip.relative_to(root).as_posix()] == clip.read_bytes()


def test_a_file_under_a_clips_name_is_judged_like_any_other(tmp_path, monkeypatch):
    # ⛔ Provenance faked: nothing on disk proves a clip is one, so none is trusted.
    monkeypatch.setattr(service, "audio_for", clip_audio)
    root = narrated(tmp_path, "depth1")
    clip = sorted(root.rglob(f"*.{service.FMT}"))[0]
    clip.write_bytes(clip_audio("placed")[:4096] + binary_identity())
    archive = tmp_path / "shared.zip"
    code, said = exported(root, archive, SHARING)
    assert code == 1 and not archive.exists(), said
    assert f"refused '{clip.relative_to(root).as_posix()}' is not UTF-8 text" in said


def _is_text(data: bytes) -> bool:
    try:
        data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return True
