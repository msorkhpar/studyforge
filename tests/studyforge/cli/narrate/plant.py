"""The plants the prune tests assert against: a narrated corpus, and a DEAD record entry in it.

⛔ **A dead entry is planted, never inferred.** It is filed under a unit the walk
DOES read, beside that unit's real clips and under the record's own
conditions — so the only thing wrong with it is that the corpus does not
produce its speech id. ⭐ The record is re-rendered in the writer's own key
order, so planting it does not by itself make a later run rewrite the record.

⛔ Every root here is a copy under `tmp_path`; nothing under `tests/fixtures/`
is written.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.archive.document import content_sha256
from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.narrate.client import NarrateClient
from studyforge.narrate.synth import state_file
from tests.studyforge.cli.narrate.service import BASE, FMT, VOICE, FakeService
from tests.studyforge.generate.corpora import a_corpus

#: What a planted clip holds — ⭐ distinct from every fake-service clip.
PLANTED = b"ID3planted"


def narrated(tmp_path: Path, name: str = "depth1") -> Path:
    """A fixture copy narrated end to end against the recording fake service."""
    root = a_corpus(tmp_path, name)
    client = NarrateClient(BASE, voice=VOICE, fmt=FMT, transport=FakeService())
    narrate_corpus(root, client, voice=VOICE, fmt=FMT)
    return root


def released_corpus(tmp_path: Path, name: str = "depth1") -> Path:
    """A narrated fixture copy whose manifest keeps its clips out of git, as a release needs."""
    root = narrated(tmp_path, name)
    manifest = root / "corpus.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document["media"] = {"commit": "never"}
    manifest.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return root


def record_of(root: Path) -> dict:
    """The record as JSON, read straight off the disk."""
    return json.loads(state_file(root).read_text(encoding="utf-8"))


def write_record(root: Path, document: dict) -> None:
    """Write `document` as the record, clips sorted as the writer sorts them."""
    document["clips"] = dict(sorted(document["clips"].items()))
    rendered = json.dumps(document, indent=2, ensure_ascii=False) + "\n"
    state_file(root).write_text(rendered, encoding="utf-8")


def plant_dead_entry(
    root: Path,
    *,
    section: str = "gone",
    filename: str | None = None,
    token: str | None = None,
    clip: bool = True,
) -> tuple[str, Path]:
    """Plant one entry the corpus does not produce; return `(speech id, where its clip is)`.

    `filename` overrides the entry's own clip name (a record naming a file that
    is not its clip); `token` files it under another unit (one no longer
    declared); `clip=False` leaves its file absent.
    """
    document = record_of(root)
    live_id, live = sorted(document["clips"].items())[0]
    beside = next(root.rglob(live["filename"])).parent
    dead_id = f"{token or live_id.partition('.')[0]}.{section}.b1"
    name = filename if filename is not None else f"{dead_id}-deadbeef.{FMT}"
    document["clips"][dead_id] = {**live, "filename": name}
    write_record(root, document)
    where = beside / name
    if clip:
        where.write_bytes(PLANTED)
    return dead_id, where


#: The depth1 lesson and the words `reword` changes in it.
LESSON = "archive/depth-one/raw/prose/unit-01/lesson-1.json"
WORDS = ("one breath", "a single breath")


def reword(root: Path) -> None:
    """Re-word one fixture paragraph in place, the way an author edits a lesson."""
    lesson = root / LESSON
    text = lesson.read_text(encoding="utf-8")
    assert WORDS[0] in text, "the fixture paragraph moved; this re-wording would change nothing"
    lesson.write_text(text.replace(*WORDS), encoding="utf-8")


def edit_one_paragraph(root: Path) -> str:
    """Re-word the lesson's one paragraph AND re-digest it; return the paragraph's speech id.

    ⭐ Unlike `reword`, the archive stays valid, so the only thing wrong
    with the corpus afterwards is that one clip says the old words.
    """
    lesson = root / LESSON
    document = json.loads(lesson.read_text(encoding="utf-8"))
    paragraphs = [block for block in document["blocks"] if block["type"] == "para"]
    assert len(paragraphs) == 1 and WORDS[0] in paragraphs[0]["text"], "the fixture moved"
    paragraphs[0]["text"] = paragraphs[0]["text"].replace(*WORDS)
    document["content_sha256"] = content_sha256(document["blocks"])
    lesson.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    index = document["blocks"].index(paragraphs[0])
    return f"depth-one--unit-01.prose.b{index + 1}"


def unlocate(root: Path) -> None:
    """Rewrite the record as a version-1 writer left it: no directories, nothing superseded."""
    document = record_of(root)
    document["narration_api"] = 1
    for entry in document["clips"].values():
        entry.pop("where", None)
        entry.pop("superseded", None)
    write_record(root, document)
