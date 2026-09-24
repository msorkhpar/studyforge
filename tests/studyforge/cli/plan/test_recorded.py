"""Mirror of `src/studyforge/cli/plan/recorded.py` (R12) — the record as a plan input.

The record is a plan input: a copy is something the record LOCATES, and a
superseded clip is something the plan names as superseded. The
record-level tests fabricate a record over a fixture copy; the last test
narrates a corpus through the recording fake and builds it, so "a copy the
build makes" is read off the build and never assumed.
"""

from __future__ import annotations

import json
import shutil
from pathlib import Path, PurePosixPath

from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.cli.plan import plan_for
from studyforge.cli.plan.recorded import NOT_ONE_FILE, read_record
from studyforge.corpus.container import CONTAINER_FILENAME
from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.corpus.placement import AUDIO_DIRNAME
from studyforge.generate import read_corpus, unit_location, write_site
from studyforge.narrate.client import NarrateClient
from studyforge.narrate.speakable import unit_token
from studyforge.narrate.synth import Clip, Conditions, Superseded, state_file, write_state
from studyforge.validate.report import INVALID, OK
from tests.fixture_checks import FIXTURES
from tests.studyforge.cli.narrate.service import BASE, FMT, VOICE, FakeService
from tests.studyforge.generate.corpora import a_corpus, an_output

RECORD = ".studyforge/narration.json"
#: Where a dead entry's clip sits: a directory no declared unit's page reads.
ELSEWHERE = ".studyforge/units/a-unit-no-longer-declared/audio"


def a_unit(tmp_path: Path) -> tuple[Path, str, str]:
    """A depth1 copy, its first unit's token and that unit's audio directory."""
    root = tmp_path / "depth1"
    shutil.copytree(FIXTURES / "depth1", root)
    corpus = read_corpus(root)
    audio = unit_location(corpus, corpus.units[0]).media_dir(AUDIO_DIRNAME).as_posix()
    return root, unit_token(corpus.units[0].key), audio


def record(root: Path, clips: dict[str, Clip]) -> None:
    settings = Conditions(voice="voice-a", fmt="mp3", provides=3, chunk_chars=320)
    clips = {
        key: Clip(**{**_fields(clip), "conditions": settings.fingerprint})
        for key, clip in clips.items()
    }
    state_file(root).parent.mkdir(parents=True, exist_ok=True)
    write_state(state_file(root), clips, settings)


def _fields(clip: Clip) -> dict:
    return {name: getattr(clip, name) for name in Clip.__slots__}


def on_disk(root: Path, where: str, name: str) -> str:
    (root / where).mkdir(parents=True, exist_ok=True)
    (root / where / name).write_bytes(b"clip")
    return f"{where}/{name}"


def copies(plan) -> list[str]:
    return sorted(c.path for c in plan.creations if c.narration and not c.path.endswith("/"))


# --------------------------------------------------------------------------
# ⛔ The record is read, and nothing else is opened
# --------------------------------------------------------------------------


def test_with_a_record_it_opens_the_record_and_still_no_source_material(tmp_path, monkeypatch):
    import pathlib

    root, token, audio = a_unit(tmp_path)
    record(root, {f"{token}.intro.b1": Clip(f"{token}.intro.b1-0123abcd.mp3", "", where=audio)})
    opened: list[str] = []
    original = pathlib.Path.read_text

    def spy(self, *args, **kwargs):
        opened.append(self.name)
        return original(self, *args, **kwargs)

    monkeypatch.setattr(pathlib.Path, "read_text", spy)
    plan = plan_for(root)
    assert "narration.json" in opened
    assert set(opened) <= {MANIFEST_FILENAME, CONTAINER_FILENAME, "narration.json"}
    assert plan.read_files[-1] == RECORD and RECORD in plan.lines()[2]


def test_an_absent_record_is_not_read_and_names_nothing(tmp_path):
    root, _, _ = a_unit(tmp_path)
    found = read_record(root)
    assert found.read == () and found.refusals == () and found.superseded == ()
    assert found.copies("any", "any/audio") == ()


def test_an_unreadable_record_or_a_clip_name_with_a_directory_is_a_refusal_not_a_raise(tmp_path):
    root, token, audio = a_unit(tmp_path / "a")
    name = f"../{token}.intro.b1-0123abcd.mp3"
    record(root, {f"{token}.intro.b1": Clip(name, "", where=audio)})
    named = plan_for(root)
    assert named.exit_code == INVALID
    assert [(r.where, r.why) for r in named.refusals] == [(RECORD, NOT_ONE_FILE)]
    assert copies(named) == []

    broken, _, _ = a_unit(tmp_path / "b")
    (broken / ".studyforge").mkdir()
    (broken / RECORD).write_text("not a record", "utf-8")
    plan = plan_for(broken)
    assert plan.exit_code == INVALID
    assert [r.where for r in plan.refusals] == [RECORD]


def test_only_a_units_audio_directory_is_marked_narration_when_no_record_exists():
    for name in ("depth1", "depth2"):
        marked = [c for c in plan_for(FIXTURES / name).creations if c.narration]
        audio = [c for c in plan_for(FIXTURES / name).creations if c.what.endswith("'s audio")]
        assert marked and marked == audio


# --------------------------------------------------------------------------
# ⛔ A copy is named only where the RECORD locates its clip
# --------------------------------------------------------------------------


def test_W288_a_copy_is_named_only_where_the_record_locates_it_in_its_units_audio_directory(
    tmp_path,
):
    root, token, audio = a_unit(tmp_path)
    live, absent = f"{token}.intro.b1-0123abcd.mp3", f"{token}.intro.b4-0123abcd.mp3"
    dead, unlocated = f"{token}.intro.b2-0123abcd.mp3", f"{token}.intro.b3-0123abcd.mp3"
    on_disk(root, audio, live)
    on_disk(root, ELSEWHERE, dead)
    on_disk(root, audio, unlocated)
    record(
        root,
        {
            f"{token}.intro.b1": Clip(live, "", where=audio),
            f"{token}.intro.b4": Clip(absent, "", where=audio),
            f"{token}.intro.b2": Clip(dead, "", where=ELSEWHERE),
            f"{token}.intro.b3": Clip(unlocated, "", where=None),
            f"{token}.intro.b5": Clip(f"{token}.intro.b9-0123abcd.mp3", "", where=audio),
            f"{token}.intro.b6": Clip("", "", where=audio),
            "no--such--unit.intro.b1": Clip(
                "no--such--unit.intro.b1-0123abcd.mp3", "", where=audio
            ),
        },
    )

    plan = plan_for(root)

    assert plan.exit_code == OK
    # ⭐ The direction that must hold: a clip the record locates in its unit's directory.
    assert copies(plan) == [f"{audio}/{live}", f"{audio}/{absent}"]
    verbs = {c.path: c.verb for c in plan.creations}
    assert (verbs[f"{audio}/{live}"], verbs[f"{audio}/{absent}"]) == ("keep", "expect")
    # ⛔ The dead entry is named as nothing.
    text = "\n".join(plan.lines())
    assert dead not in text and unlocated not in text
    assert plan.superseded == ()


# --------------------------------------------------------------------------
# ⛔ A superseded clip is named SUPERSEDED, never as a copy
# --------------------------------------------------------------------------


def test_W288_a_superseded_clip_is_named_superseded_and_never_a_path_a_build_owns(tmp_path):
    root, token, audio = a_unit(tmp_path)
    live, reworded = f"{token}.intro.b1-0123abcd.mp3", f"{token}.intro.b1-feedbeef.mp3"
    on_disk(root, audio, live)
    older = [
        Superseded(reworded, audio),
        Superseded(f"{token}.intro.b1-00000000.mp3", ELSEWHERE),
        Superseded(f"{token}.intro.b1-11111111.mp3", audio),
        Superseded(f"{token}.intro.b1-22222222.mp3", None),
        Superseded("../escapes-0123abcd.mp3", audio),
    ]
    named = [on_disk(root, older[0].where, reworded), on_disk(root, ELSEWHERE, older[1].filename)]
    on_disk(root, audio, older[3].filename)
    record(root, {f"{token}.intro.b1": Clip(live, "", where=audio, superseded=tuple(older))})

    plan = plan_for(root)

    assert plan.exit_code == OK
    assert [clip.path for clip in plan.superseded] == sorted(named)
    assert all(clip.speech_id == f"{token}.intro.b1" for clip in plan.superseded)
    lines = plan.lines()
    printed = [line.split()[1] for line in lines if line.startswith("superseded ")]
    assert sorted(printed) == sorted(named)
    assert not set(named) & set(plan.paths)
    assert copies(plan) == [f"{audio}/{live}"]
    assert "2 superseded clip(s) no build copies" in plan.summary()
    # ⛔ Why it must never be a path: a build's footprint is taken from `Plan.paths`.
    footprint = read_corpus(root).footprint
    assert footprint.owns(PurePosixPath(f"{audio}/{live}"))
    assert not [path for path in named if footprint.owns(PurePosixPath(path))]


# --------------------------------------------------------------------------
# ⛔ Asserted both ways against what a BUILD copies
# --------------------------------------------------------------------------


def test_W288_over_a_dead_and_a_superseded_entry_the_plan_names_exactly_what_the_build_copies(
    tmp_path,
):
    root = a_corpus(tmp_path, "depth1")
    client = NarrateClient(BASE, voice=VOICE, fmt=FMT, transport=FakeService())
    narrate_corpus(root, client, voice=VOICE, fmt=FMT)
    document = json.loads((root / RECORD).read_text("utf-8"))
    ids = sorted(document["clips"])
    assert len(ids) >= 2, "the fake narrated too little to plant a dead and a superseded entry"

    dead, kept = document["clips"][ids[0]], document["clips"][ids[1]]
    moved = root / ELSEWHERE / dead["filename"]
    moved.parent.mkdir(parents=True)
    (root / dead["where"] / dead["filename"]).rename(moved)
    dead["where"] = ELSEWHERE
    stale = f"{kept['filename'].rsplit('-', 1)[0]}-{'0' * 8}.{FMT}"
    shutil.copyfile(root / kept["where"] / kept["filename"], root / kept["where"] / stale)
    kept["superseded"] = [{"filename": stale, "where": kept["where"]}]
    (root / RECORD).write_text(json.dumps(document, indent=2) + "\n", "utf-8")

    plan = plan_for(root)
    written = write_site(root, an_output(tmp_path))
    built = sorted(str(path) for path in written.media if str(path).endswith(f".{FMT}"))
    kept_at = [c.path for c in plan.creations if c.path in copies(plan) and c.verb == "keep"]

    assert plan.exit_code == OK
    # ⭐ Every clip the plan names as on disk is a clip the build copied, and no other.
    assert sorted(kept_at) == built
    dead_at = f"{dead['where']}/{dead['filename']}"
    stale_at = f"{kept['where']}/{stale}"
    # ⛔ The dead entry: not named at its unit, and not copied by the build.
    assert not [path for path in copies(plan) if path.endswith(dead["filename"])]
    assert not [path for path in built if path.endswith(dead["filename"])]
    # ⛔ The superseded clip: named as superseded, never a copy, never copied.
    assert [clip.path for clip in plan.superseded] == [stale_at]
    assert stale_at not in plan.paths and stale_at not in built
    assert dead_at not in plan.paths
