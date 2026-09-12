"""Mirror of `src/studyforge/cli/narrate/prune.py` (R12) — `W218`'s settlement, over the DISK.

⛔ **Every clause is a reading of the files under the copied corpus**, bytes
and modification times, taken before and after — never `Pruned`'s own
account. ⭐ Each plant is a record entry the corpus does not produce
(`plant.py`), and the population a prune may touch is derived from that plant,
so a prune that deletes one file too many fails the set equality.
"""

from __future__ import annotations

import ast
import io
import shutil

import pytest

from studyforge.cli.narrate import cli
from studyforge.cli.narrate.prune import NOT_ITS_CLIP, UNDECLARED, prune_corpus
from studyforge.cli.site.cli import main as build_main
from studyforge.generate.declarations import read_corpus
from studyforge.narrate.synth import read_state, state_file
from studyforge.validate.report import INVALID, OK
from tests.studyforge.cli.narrate.plant import PLANTED, narrated, plant_dead_entry, record_of
from tests.studyforge.cli.narrate.service import VOICE, FakeService, files, speech_ids
from tests.studyforge.generate.corpora import BOTH, an_output
from tests.support import repository_root


def invoke(*argv):
    out = io.StringIO()
    return cli.main(list(argv), out=out), out.getvalue()


def relative(root, path) -> str:
    return path.relative_to(root).as_posix()


def recorded(root) -> list[str]:
    return sorted(read_state(state_file(root)).clips)


# --------------------------------------------------------------------------
# ⛔ clause 3: it deletes ONLY what the record names, and forgets those entries
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_prune_deletes_exactly_the_planted_clip_and_changes_nothing_else(tmp_path, name):
    root = narrated(tmp_path, name)
    dead, clip = plant_dead_entry(root)
    before = files(root)
    assert relative(root, clip) in before, "the plant is not on disk; the reading is vacuous"

    pruned = prune_corpus(root)
    after = files(root)

    # ⛔ The set of files that went away is EXACTLY the planted clip.
    assert sorted(set(before) - set(after)) == [relative(root, clip)]
    assert set(after) - set(before) == set()
    # ⛔ And the only surviving file whose bytes or mtime moved is the record.
    moved = sorted(path for path in after if after[path] != before[path])
    assert moved == [relative(root, state_file(root))]
    assert recorded(root) == speech_ids(root)
    assert (pruned.deleted, pruned.forgotten, pruned.held) == ((clip,), (dead,), ())


def test_a_foreign_file_beside_the_clips_survives_byte_for_byte(tmp_path):
    # ⭐ Discrimination by PATH: a file the record does not name, even one shaped
    # exactly like a clip and even one sharing the dead clip's stem.
    root = narrated(tmp_path)
    dead, clip = plant_dead_entry(root)
    foreign = [
        clip.parent / "notes.txt",
        clip.parent / f"{dead.rpartition('.')[0]}.b2-0badf00d.mp3",
        clip.with_suffix(".opus"),
    ]
    for index, path in enumerate(foreign):
        path.write_bytes(b"foreign %d" % index)
    before = files(root)

    prune_corpus(root)

    after = files(root)
    assert not clip.exists(), "the control: the plant beside them WAS deleted"
    for path in foreign:
        assert after[relative(root, path)] == before[relative(root, path)]


def test_an_entry_whose_clip_is_already_absent_is_forgotten_and_nothing_is_deleted(tmp_path):
    root = narrated(tmp_path)
    dead, _ = plant_dead_entry(root, clip=False)
    clips_before = {path: value for path, value in files(root).items() if path.endswith(".mp3")}

    pruned = prune_corpus(root)

    assert (pruned.deleted, pruned.forgotten) == ((), (dead,))
    assert {p: v for p, v in files(root).items() if p.endswith(".mp3")} == clips_before
    assert dead not in recorded(root)


@pytest.mark.parametrize("named", ["LIVE", "../../corpus.json", "corpus.json"])
def test_an_entry_naming_a_file_that_is_not_its_own_clip_is_held_and_the_file_survives(
    tmp_path, named
):
    root = narrated(tmp_path)
    live = record_of(root)["clips"]
    filename = sorted(live.values(), key=lambda entry: entry["filename"])[0]["filename"]
    dead, where = plant_dead_entry(
        root, filename=filename if named == "LIVE" else named, clip=False
    )
    before = files(root)

    code, printed = invoke(str(root), "--prune")

    assert files(root) == before
    assert code == INVALID
    assert f"held {dead}  {NOT_ITS_CLIP}" in printed
    assert dead in recorded(root)


def test_an_entry_of_a_unit_no_longer_declared_is_held_with_its_entry(tmp_path):
    # ⚠️ The record carries no directory, so this clip cannot be located by rule.
    root = narrated(tmp_path)
    dead, _ = plant_dead_entry(root, token="depth-one--unit-09", clip=False)
    before = files(root)

    pruned = prune_corpus(root)

    assert pruned.held == ((dead, UNDECLARED),)
    assert files(root) == before


def test_a_second_prune_writes_nothing(tmp_path):
    root = narrated(tmp_path)
    plant_dead_entry(root)
    prune_corpus(root)
    before = files(root)

    again = prune_corpus(root)

    assert files(root) == before
    assert (again.deleted, again.forgotten, again.held) == ((), (), ())


# --------------------------------------------------------------------------
# ⛔ clause 2: a PARTIAL walk refuses by name — read off the DISK
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_prune_over_a_partial_walk_refuses_by_name_and_the_disk_is_unchanged(tmp_path, name):
    root = narrated(tmp_path, name)
    _, clip = plant_dead_entry(root)
    missing = read_corpus(root).units[-1]
    shutil.rmtree(missing.directory)
    before = files(root)
    assert relative(root, clip) in before

    code, printed = invoke(str(root), "--prune")

    # ⛔ THE READING: every file, its bytes and its mtime — the plant included,
    # and every clip of the unit whose material went missing.
    assert files(root) == before
    assert code == INVALID
    assert missing.key in printed
    assert "refuse walk" in printed


# --------------------------------------------------------------------------
# ⛔ clause 2 and the MUST-NOT: the prune is its own request
# --------------------------------------------------------------------------


def test_narrating_without_prune_deletes_no_clip_and_discloses_the_plant(tmp_path, monkeypatch):
    root = narrated(tmp_path)
    dead, clip = plant_dead_entry(root)
    before = files(root)
    monkeypatch.setattr(cli, "over_http", FakeService())

    code, printed = invoke(str(root), "--voice", VOICE)

    assert code == OK
    assert files(root) == before
    assert clip.read_bytes() == PLANTED and dead in recorded(root)
    assert "dead record  1 " in printed


def test_a_build_deletes_no_clip_and_forgets_no_entry(tmp_path):
    root = narrated(tmp_path)
    dead, clip = plant_dead_entry(root)
    before = files(root)
    site = an_output(tmp_path, "site")

    code = build_main([str(root), "--out", str(site)], out=io.StringIO())

    assert code == OK
    assert any(site.rglob("*.html")), "the control: the build wrote a site"
    after = files(root)
    assert before.items() <= after.items(), "a build removed or rewrote a file under the corpus"
    assert clip.read_bytes() == PLANTED and dead in recorded(root)


def test_a_prune_requests_nothing_from_any_service(tmp_path, monkeypatch):
    root = narrated(tmp_path)
    plant_dead_entry(root)
    service = FakeService()
    monkeypatch.setattr(cli, "over_http", service)

    code, _ = invoke(str(root), "--prune")
    assert code == OK
    assert service.sent == []

    # ⭐ The control: the same swapped transport DOES record a narration run.
    invoke(str(root), "--voice", VOICE)
    assert service.sent


def test_prune_and_voice_cannot_be_one_request():
    with pytest.raises(SystemExit):
        cli.build_parser().parse_args(["corpus", "--voice", VOICE, "--prune"])


def test_nothing_in_the_framework_calls_the_prune_or_the_removal_but_their_owners():
    # ⛔ Population: every module under `src/`, printed on failure. A call of
    # `prune_corpus` or `forget` anywhere else is a prune reached by another path.
    owners = {
        "prune_corpus": {"src/studyforge/cli/narrate/cli.py"},
        "forget": {"src/studyforge/cli/narrate/prune.py"},
    }
    scanned = sorted((repository_root() / "src").rglob("*.py"))
    assert len(scanned) > 50, f"only {len(scanned)} modules scanned"
    callers: dict[str, set[str]] = {name: set() for name in owners}
    for path in scanned:
        for node in ast.walk(ast.parse(path.read_text(encoding="utf-8"))):
            if isinstance(node, ast.Call):
                called = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                if called in callers:
                    callers[called].add(path.relative_to(repository_root()).as_posix())
    assert callers == owners, f"{len(scanned)} modules scanned"


def test_an_entry_whose_id_and_filename_climb_out_of_the_audio_directory_is_held(tmp_path):
    # ⛔ The crafted case the separator guard exists for: the id and the filename
    # agree, and the id's unit IS walked, so only the guard keeps the prune inside
    # the unit's audio directory. The intermediate directory exists, so the path
    # would resolve to the file beside that directory.
    root = narrated(tmp_path)
    live_id, live = sorted(record_of(root)["clips"].items())[0]
    audio = next(root.rglob(live["filename"])).parent
    token = live_id.partition(".")[0]
    (audio / f"{token}.x").mkdir()
    outside = audio / "outside-deadbeef.mp3"
    outside.write_bytes(b"not a clip")
    dead, _ = plant_dead_entry(
        root, section="x/../outside", filename=f"{token}.x/../outside-deadbeef.mp3", clip=False
    )
    before = files(root)

    pruned = prune_corpus(root)

    assert pruned.held == ((dead, NOT_ITS_CLIP),)
    assert files(root) == before
