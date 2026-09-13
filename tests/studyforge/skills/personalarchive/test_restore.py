"""Mirror of `src/studyforge/skills/personalarchive/restore.py` (R12): intact, merged, refused.

⛔ **"Intact" is read back through the framework's own readers.** Those are `studyforge
validate`, `generate.read_corpus`, the progress store and `studyforge build`, run on the
second machine. The test never compares bytes it wrote itself.
"""

from __future__ import annotations

import hashlib
import io
import json
import shutil

import pytest

from studyforge.cli import VERBS
from studyforge.generate import read_corpus
from studyforge.skills.personalarchive import OWNER, SHARING, export, import_archive, record
from studyforge.skills.personalarchive.layout import (
    MANIFEST_MEMBER,
    MATERIAL_PREFIX,
    PROGRESS_MEMBER,
)
from studyforge.validate.report import OK
from tests.fixture_checks import FIXTURES
from tests.studyforge.skills.personalarchive.archiving import (
    KEY,
    OTHER_KEY,
    TIMES,
    binary_identity,
    digest_of,
    entry,
    entry_of,
    machine,
    planted_identity,
    record_file,
    rewritten,
    run,
    store,
)

#: A practice only the importing machine has.
LOCAL_ONLY = "advanced/02-going-further/unit-01/practice-1"

#: A material file an existing machine has changed.
CHANGED = "archive/basics/01-getting-started/raw/java/unit-01/lesson-1.json"


def imported(archive, root):
    out = io.StringIO()
    return import_archive(archive, root, stream=out), out.getvalue()


def owner_archive(tmp_path, kind=OWNER):
    root = machine(tmp_path, "a")
    run(root, passed=False, when=TIMES["t1"])
    run(root, passed=True, when=TIMES["t2"])
    run(root, OTHER_KEY, passed=False, when=TIMES["t1"])
    archive = tmp_path / f"{kind}.zip"
    assert export(root, archive, kind=kind, stream=io.StringIO()) == 0
    return root, archive


def validated(root):
    out = io.StringIO()
    return VERBS["validate"].run([str(root)], out=out), out.getvalue()


def tree(root):
    return {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in root.rglob("*")
        if path.is_file()
    }


def test_another_machine_gets_the_material_and_the_progress_intact(tmp_path):
    first, archive = owner_archive(tmp_path)
    second = machine(tmp_path, "b", corpus=False)
    code, said = imported(archive, second)
    assert code == 0, said
    assert validated(second) == validated(first) and validated(second)[0] == OK
    theirs, ours = read_corpus(first), read_corpus(second)
    assert (ours.manifest, ours.contents, ours.maps) == (
        theirs.manifest,
        theirs.contents,
        theirs.maps,
    )
    assert store(second).read() == store(first).read()
    assert set(store(second).read()["practices"]) == {KEY, OTHER_KEY}
    site = tmp_path / "site"
    site.mkdir()
    assert VERBS["build"].run([str(second), "--out", str(site)], out=io.StringIO()) == OK
    assert f"progress restored {KEY} runs 2 first {TIMES['t2']}" in said


def test_a_sharing_archive_restores_the_material_and_no_progress(tmp_path):
    _, archive = owner_archive(tmp_path, SHARING)
    second = machine(tmp_path, "b", corpus=False)
    code, said = imported(archive, second)
    assert code == 0 and validated(second)[0] == OK, said
    assert not record_file(second).exists() and "progress" not in said.replace("import", "")


def test_importing_the_same_archive_again_changes_nothing_and_says_so(tmp_path):
    _, archive = owner_archive(tmp_path)
    second = machine(tmp_path, "b", corpus=False)
    assert imported(archive, second)[0] == 0
    before = tree(second)
    code, said = imported(archive, second)
    assert code == 0 and tree(second) == before, said
    assert "material added 0" in said and f"progress unchanged {KEY}" in said


def test_an_existing_corpus_merges_rather_than_clobbering_and_says_what_it_merged(tmp_path):
    _, archive = owner_archive(tmp_path)
    here = machine(tmp_path, "c")
    for _ in range(4):
        run(here, passed=False, when=TIMES["t4"])
    only_here = run(here, LOCAL_ONLY, passed=True, when=TIMES["t3"])
    changed = here / CHANGED
    changed.write_bytes(changed.read_bytes() + b"\n")
    mine = changed.read_bytes()
    code, said = imported(archive, here)
    assert code == 0, said
    assert changed.read_bytes() == mine and f"material kept {CHANGED}" in said
    assert entry(here, LOCAL_ONLY) == only_here
    assert entry(here) == {
        **entry_of("runs 6 · first t2 · last t4 fail"),
    }
    assert f"progress merged {KEY} runs 4->6 first archive last kept" in said
    assert f"progress restored {OTHER_KEY} runs 1 first none" in said


def test_an_executable_file_stays_executable_on_the_other_machine(tmp_path):
    root = machine(tmp_path, "a")
    script = root / "run.sh"
    script.write_text("#!/bin/sh\n", encoding="utf-8")
    script.chmod(0o755)
    archive = tmp_path / "out.zip"
    assert export(root, archive, kind=SHARING, stream=io.StringIO()) == 0
    second = machine(tmp_path, "b", corpus=False)
    assert imported(archive, second)[0] == 0
    assert (second / "run.sh").stat().st_mode & 0o111


def declared(path: str, data: bytes):
    """Return a change adding one file to the material, declared with its true digest."""

    def change(carried):
        manifest = json.loads(carried[MANIFEST_MEMBER])
        manifest["material"].append(
            {
                "path": path,
                "sha256": hashlib.sha256(data).hexdigest(),
                "bytes": len(data),
                "executable": False,
            }
        )
        return {
            **carried,
            MANIFEST_MEMBER: json.dumps(manifest).encode(),
            MATERIAL_PREFIX + path: data,
        }

    return change


def manifest_set(**fields):
    def change(carried):
        manifest = {**json.loads(carried[MANIFEST_MEMBER]), **fields}
        return {**carried, MANIFEST_MEMBER: json.dumps(manifest).encode()}

    return change


def flipped(carried):
    # ⚠️ A byte inside a string no reader parses, so ONLY the digest can refuse it: the
    # first version flipped a brace in `corpus.json`, and the manifest parser refused it
    # with the digest check removed (plant P12 survived).
    name = MATERIAL_PREFIX + CHANGED
    data = carried[name]
    at = data.index(b'"', data.index(b":")) + 1
    return {**carried, name: data[:at] + bytes([data[at] ^ 1]) + data[at + 1 :]}


def undeclared(carried):
    return {**carried, MATERIAL_PREFIX + "extra.txt": b"extra\n"}


def progress_dropped_kind_sharing(carried):
    return manifest_set(kind=SHARING, progress=False)(carried)


CRAFTED = {
    "sharing-declaring-progress": manifest_set(kind=SHARING),
    "sharing-carrying-progress": progress_dropped_kind_sharing,
    "into-the-store": declared(".studyforge/progress/progress.json", b"{}\n"),
    "into-version-control": declared(".git/config", b"[core]\n"),
    "climbing-out": declared("../outside.txt", b"out\n"),
    "unknown-version": manifest_set(personal_archive_api=2),
    "digest-mismatch": flipped,
    "undeclared-member": undeclared,
    "identity-in-a-file": declared("notes.md", f"at {planted_identity()}\n".encode()),
    "identity-in-a-name": declared("jane.doe" + "@" + "mailhost.org.md", b"x\n"),
    "no-manifest": lambda carried: {k: v for k, v in carried.items() if k != MANIFEST_MEMBER},
    "progress-absent": lambda carried: {k: v for k, v in carried.items() if k != PROGRESS_MEMBER},
}


@pytest.mark.parametrize("name", sorted(CRAFTED))
def test_a_crafted_archive_is_refused_before_anything_is_written(name, tmp_path):
    _, archive = owner_archive(tmp_path)
    crafted = rewritten(archive, tmp_path / f"{name}.zip", CRAFTED[name])
    here = machine(tmp_path, "c")
    run(here, passed=False, when=TIMES["t4"])
    before, record_before = tree(here), digest_of(record_file(here))
    code, said = imported(crafted, here)
    assert code == 1 and said.startswith("refused "), said
    assert tree(here) == before and digest_of(record_file(here)) == record_before
    assert not (tmp_path / "machine-c" / "outside.txt").exists()
    assert planted_identity() not in said


def test_an_archive_of_another_corpus_is_refused(tmp_path):
    _, archive = owner_archive(tmp_path)
    other = tmp_path / "other"
    shutil.copytree(FIXTURES / "depth1", other)
    before = tree(other)
    code, said = imported(archive, other)
    assert code == 1 and "different corpus" in said
    assert tree(other) == before


def test_a_file_that_is_not_an_archive_and_a_root_that_is_not_a_directory_are_refused(tmp_path):
    bogus = tmp_path / "bogus.zip"
    bogus.write_bytes(b"not a zip")
    assert imported(bogus, machine(tmp_path, "b", corpus=False))[0] == 1
    _, archive = owner_archive(tmp_path)
    assert imported(archive, tmp_path / "absent")[0] == 1
    assert imported(tmp_path / "absent.zip", machine(tmp_path, "d", corpus=False))[0] == 1


def test_a_refused_practice_is_reported_and_the_rest_is_imported(tmp_path):
    _, archive = owner_archive(tmp_path)

    def hand_written(carried):
        progress = json.loads(carried[PROGRESS_MEMBER])
        progress["practices"][KEY]["runs"] = 1
        progress["practices"][KEY]["first_passed_at"] = TIMES["t1"]
        return {**carried, PROGRESS_MEMBER: json.dumps(progress).encode()}

    crafted = rewritten(archive, tmp_path / "hand.zip", hand_written)
    second = machine(tmp_path, "b", corpus=False)
    code, said = imported(crafted, second)
    assert code == 1, said
    assert f"progress refused {KEY} " in said and entry(second) is None
    assert entry(second, OTHER_KEY) is not None and validated(second)[0] == OK
    assert record.store_path(second) not in said


def test_a_sharing_archive_is_judged_on_import_as_on_export_and_an_owner_one_is_not(tmp_path):
    root = machine(tmp_path, "a")
    (root / "cover.bin").write_bytes(binary_identity())
    owner = tmp_path / "owner.zip"
    assert export(root, owner, kind=OWNER, stream=io.StringIO()) == 0

    def as_sharing(carried):
        changed = manifest_set(kind=SHARING, progress=False)(carried)
        return {name: data for name, data in changed.items() if name != PROGRESS_MEMBER}

    crafted = rewritten(owner, tmp_path / "crafted.zip", as_sharing)
    here = machine(tmp_path, "b", corpus=False)
    code, said = imported(crafted, here)
    assert code == 1 and "'cover.bin' is not UTF-8 text" in said, said
    assert tree(here) == {} and planted_identity() not in said
    there = machine(tmp_path, "c", corpus=False)
    assert imported(owner, there)[0] == 0
    assert (there / "cover.bin").read_bytes() == binary_identity()
