"""Synthetic units: contract-valid archive documents, built the way one is built.

⛔ Built through `archive.document.build`, never typed as literals. A fixture
assembled by hand drifts from the format the moment the format moves, and the
drift shows up as a builder bug.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.archive.document import build as archive_document
from studyforge.archive.document import render as render_archive

#: A practice's three-section layout, which `archive.blocks` requires.
PRACTICE_BLOCKS = [
    {"type": "heading", "level": 2, "text": "Problem statement"},
    {"type": "para", "text": "Make it pass."},
    {"type": "heading", "level": 2, "text": "Lesson: the shape of it"},
    {"type": "para", "text": "Prose about the shape."},
    {"type": "heading", "level": 2, "text": "Starting code"},
    {"type": "code", "lang": "python", "text": "def greet(who):\n    ...\n"},
]

LESSON_BLOCKS = [
    {"type": "heading", "level": 2, "text": "One block is enough"},
    {"type": "para", "text": "Prose."},
]

VIDEO = {
    "src": "video/java.mp4",
    "poster": "video/java.jpg",
    "mime": "video/mp4",
    "remote": "https://example.invalid/java.mp4",
    "poster_remote": "https://example.invalid/java.jpg",
}

EXERCISE = {
    "main_path": "practice/basics-01/greeter.py",
    "test_path": "practice/basics-01/test_greeter.py",
    "run_command": ["python3", "-m", "greeter"],
    "test_command": ["python3", "-m", "pytest", "-q"],
    "provenance": "bundled",
    "trust": "authoritative",
}


#: ⭐ One declared companion file, in the archive's own entry shape
#: (`archive.document.MEDIA_ENTRY_KEYS`). ⚠️ `remote` is provenance and must
#: never reach a page, so it is a value here rather than `None`.
ATTACHMENT = {
    "remote": "https://example.invalid/small-graph.ttl",
    "local": "media/small-graph.ttl",
    "sha256": "0" * 64,
    "bytes": 103,
    "content_type": "text/turtle",
    "kind": "dataset",
}


def lesson(
    ordinal: int = 1,
    *,
    title: str = "A lesson",
    video: dict | None = None,
    attachments: list | None = None,
    lang: str | None = None,
) -> dict:
    """One valid lesson document, tagged with a language when one is passed."""
    return archive_document(
        source="demo",
        address=["solo"],
        variant="prose",
        unit=1,
        kind="lesson",
        ordinal=ordinal,
        ingested="2026-01-05",
        title=title,
        blocks=list(LESSON_BLOCKS),
        video=video,
        attachments=attachments,
        lang=lang,
    )


def practice(
    ordinal: int = 1, *, title: str = "A practice", exercise: object = None, lang: str | None = None
) -> dict:
    """One valid practice document, graded when an exercise is passed."""
    return archive_document(
        source="demo",
        address=["solo"],
        variant="prose",
        unit=1,
        kind="practice",
        ordinal=ordinal,
        ingested="2026-01-05",
        title=title,
        blocks=list(PRACTICE_BLOCKS),
        starting_code="def greet(who):\n    ...\n",
        exercise=exercise,
        lang=lang,
    )


def unit_directory(root: Path, documents: list[dict]) -> Path:
    """Write documents into a unit directory the way ingestion leaves them."""
    root.mkdir(parents=True, exist_ok=True)
    for document in documents:
        name = f"{document['kind']}-{document['ordinal']}.json"
        (root / name).write_text(render_archive(document), encoding="utf-8")
    return root


def overlay_document(sections: list[dict], *, unit: int = 1, title: str = "Authored") -> dict:
    """One `content.json` object, ready for `unit.content.from_document`."""
    return {
        "content_api": 1,
        "address": ["solo"],
        "unit": unit,
        "title": title,
        "sections": sections,
    }


def authored_section(
    kind: str, *, lang: str | None = None, heading: str = "H", blocks: list | None = None
) -> dict:
    """One authored section, in the shape `content.json` writes."""
    section: dict = {
        "kind": kind,
        "heading": heading,
        "blocks": list(blocks if blocks is not None else [{"type": "para", "text": "Authored."}]),
    }
    if lang is not None:
        section["lang"] = lang
    return section


def written(path: Path, document: dict) -> dict:
    """Round-trip a document through JSON, as a consumer reading it would."""
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return json.loads(path.read_text(encoding="utf-8"))
