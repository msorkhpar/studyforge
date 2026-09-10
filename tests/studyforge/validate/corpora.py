"""Building a corpus on disk, so a check can be shown to bite (SF-25).

⭐ **FND-04's fixtures are archive-only**, and the two checks that read the
material need material. Rather than teach `tests/fixture_checks/` about source
files — its "exactly one rule" invariant is defined over the checks *that*
package knows, so a corpus violating a rule only `validate` can see cannot live
in `tests/fixtures/invalid/` — these corpora are built in a temporary tree by
the tests that need them.

⛔ Nothing here is a fixture in the FND-04 sense: they are inputs to negative
controls, and each one exists to make a named check fail.
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.archive.document import build, render
from studyforge.corpus.container import render as render_container
from studyforge.corpus.manifest import from_document as manifest_from_document

MANIFEST = {
    "corpus_api": 1,
    "source": "demo",
    "title": "Demo",
    "levels": ["course"],
    "variants": ["prose"],
    "exercises": False,
    "placement": "tree",
    "content": {"include": ["src/*.md"]},
}

SOURCE = "# One\n\nProse.\n\n## Two\n\nMore prose.\n"

BLOCKS = [
    {"type": "heading", "level": 1, "text": "One"},
    {"type": "para", "text": "Prose."},
    {"type": "heading", "level": 2, "text": "Two"},
    {"type": "para", "text": "More prose."},
]


def container(units, *, address=("demo",), variant="prose", origin=None):
    document = {
        "container_api": 1,
        "address": list(address),
        "titles": ["Demo"],
        "variant": variant,
        "ingested": "2026-01-05",
    }
    if origin is not None:
        document["origin"] = origin
    document["units"] = units
    return document


def unit_entry(n, *, practices=0, origin=None, title="Unit"):
    entry = {"n": n, "title": f"{title} {n}", "practices": practices}
    if origin is not None:
        entry["origin"] = origin
    return entry


def write(
    root: Path,
    *,
    manifest=None,
    containers=None,
    documents=None,
    sources=None,
) -> Path:
    """Write one corpus and return its root.

    `containers` is `{address key: container document}`; `documents` is
    `{relative archive path: build kwargs}`; `sources` is `{path: text}`.
    """
    root.mkdir(parents=True, exist_ok=True)
    declared = MANIFEST if manifest is None else manifest
    (root / "corpus.json").write_text(json.dumps(declared, indent=2) + "\n", encoding="utf-8")
    made = manifest_from_document(declared, "corpus.json")
    for key, document in (containers or {}).items():
        directory = root / "archive" / key
        directory.mkdir(parents=True, exist_ok=True)
        from studyforge.corpus.container import from_document

        built = from_document(document, "container.json", made)
        (directory / "container.json").write_text(render_container(built), encoding="utf-8")
    for where, parts in (documents or {}).items():
        path = root / "archive" / where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(build(**parts)), encoding="utf-8")
    for where, text in (sources or {}).items():
        path = root / where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return root


def one_unit(root: Path, *, blocks=None, source=None, origin="src/one.md", **overrides) -> Path:
    """The smallest complete corpus: one container, one unit, one document."""
    parts = {
        "source": "demo",
        "address": ["demo"],
        "variant": "prose",
        "unit": 1,
        "kind": "lesson",
        "ordinal": 1,
        "ingested": "2026-01-05",
        "title": "Unit 1",
        "blocks": BLOCKS if blocks is None else blocks,
    }
    parts.update(overrides)
    sources = {} if source is None else {origin: source}
    return write(
        root,
        containers={"demo": container([unit_entry(1, origin=origin)])},
        documents={"demo/raw/prose/unit-01/lesson-1.json": parts},
        sources=sources,
    )
