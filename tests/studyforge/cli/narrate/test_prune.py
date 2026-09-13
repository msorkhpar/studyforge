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
from studyforge.cli.narrate.prune import (
    NOT_A_FILE,
    NOT_ITS_CLIP,
    STILL_NAMES,
    UNDECLARED,
    prune_corpus,
)
from studyforge.cli.site.cli import main as build_main
from studyforge.generate.declarations import read_corpus
from studyforge.narrate.synth import read_state, state_file
from studyforge.validate.report import INVALID, OK
from tests.studyforge.cli.narrate.plant import (
    PLANTED,
    narrated,
    plant_dead_entry,
    record_of,
    reword,
    unlocate,
    write_record,
)
from tests.studyforge.cli.narrate.service import FMT, VOICE, FakeService, files, speech_ids
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


def test_an_entry_of_a_unit_no_longer_declared_is_reached_through_its_recorded_directory(tmp_path):
    # ⛔ W226 clause 3 (W218/1): the record carries the directory, so the held count is 0.
    root = narrated(tmp_path)
    dead, clip = plant_dead_entry(root, token="depth-one--unit-09")
    assert clip.is_file(), "the plant is not on disk; the reading is vacuous"

    pruned = prune_corpus(root)

    assert (pruned.deleted, pruned.forgotten, pruned.held) == ((clip,), (dead,), ())
    assert not clip.exists() and dead not in recorded(root)


def test_a_version_1_entry_of_a_unit_no_longer_declared_is_still_held_and_kept(tmp_path):
    # ⛔ The MUST-NOT: an entry no record can place is kept by name, never dropped.
    root = narrated(tmp_path)
    dead, clip = plant_dead_entry(root, token="depth-one--unit-09")
    unlocate(root)
    before = files(root)

    pruned = prune_corpus(root)

    assert pruned.held == ((dead, UNDECLARED),)
    assert files(root) == before and dead in recorded(root)


def test_a_reworded_passages_old_clip_is_the_one_clip_a_prune_deletes(tmp_path, monkeypatch):
    # ⛔ W226 clauses 1, 3 and 4 through the recording fake: narrate keeps the
    # old clip and names it; `--prune` deletes exactly it, and nothing is held.
    root = narrated(tmp_path)
    reword(root)
    before = files(root)
    monkeypatch.setattr(cli, "over_http", FakeService())

    code, printed = invoke(str(root), "--voice", VOICE)

    assert code == OK
    narrated_after = files(root)
    assert set(before) <= set(narrated_after), "narrate deleted a file"
    assert "superseded clips  1 " in printed
    [(speech_id, old)] = [
        (key, item)
        for key, clip in read_state(state_file(root)).clips.items()
        for item in clip.superseded
    ]
    old_clip = root / old.where / old.filename
    assert relative(root, old_clip) in before, "the superseded clip is not the one narrated first"

    pruned = prune_corpus(root)

    assert (pruned.deleted, pruned.held, pruned.cleared) == ((old_clip,), (), ((speech_id, old),))
    assert sorted(set(narrated_after) - set(files(root))) == [relative(root, old_clip)]
    assert not any(clip.superseded for clip in read_state(state_file(root)).clips.values())


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
        "forget_superseded": {"src/studyforge/cli/narrate/prune.py"},
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
    # ⛔ The crafted case the separator guard exists for: the filename is minted
    # from the entry's OWN id, and that id's unit IS walked — so only the guard
    # keeps the prune inside the unit's audio directory. ⚠️ A first draft paired a
    # filename with a different id; the id check refused it and the guard's plant
    # SURVIVED. The intermediate directory exists, so the path really resolves.
    root = narrated(tmp_path)
    live_id, live = sorted(record_of(root)["clips"].items())[0]
    audio = next(root.rglob(live["filename"])).parent
    (audio / f"{live_id.partition('.')[0]}.x").mkdir()
    dead, _ = plant_dead_entry(root, section="x/../../outside", clip=False)
    outside = audio.parent / f"outside.b1-deadbeef.{FMT}"
    assert (audio / f"{dead}-deadbeef.{FMT}").resolve() == outside.resolve()
    outside.write_bytes(b"not a clip")
    before = files(root)

    pruned = prune_corpus(root)

    assert pruned.held == ((dead, NOT_ITS_CLIP),)
    assert files(root) == before


def test_a_dead_entry_whose_superseded_clip_is_held_is_kept_with_it(tmp_path):
    # ⛔ Files first, then the record: an entry still naming a held clip is not forgotten.
    root = narrated(tmp_path)
    dead, clip = plant_dead_entry(root)
    document = record_of(root)
    kept = f"{dead}-00000000.{FMT}"
    document["clips"][dead]["superseded"] = [
        {"filename": kept, "where": document["clips"][dead]["where"]}
    ]
    write_record(root, document)
    (clip.parent / kept).mkdir()

    pruned = prune_corpus(root)

    assert set(pruned.held) == {(dead, NOT_A_FILE), (dead, STILL_NAMES)}
    assert not clip.exists() and dead in recorded(root)
