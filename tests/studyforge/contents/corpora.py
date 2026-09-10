"""Corpora for the contents tests: both FND-04 fixtures, and small synthetic ones.

⛔ **Imported, never copied.** Five test modules build the same two fixture
corpora, and five spellings of "read every container map under this root" is
five places to forget when a signature changes.

⚠️ **The walk over container maps lives here, in a test helper, and that is a
finding rather than a design** — `SF-13/2`. `contents` deliberately reads no
files, because where a corpus's archive root sits is still open (spec §6).
"""

from __future__ import annotations

import json
from pathlib import Path

from studyforge.contents import Contents, build
from studyforge.corpus.container import CONTAINER_FILENAME, Container
from studyforge.corpus.container import parse as parse_container
from studyforge.corpus.manifest import MANIFEST_FILENAME, Manifest
from studyforge.corpus.manifest import parse as parse_manifest
from tests.support import repository_root

#: Where the two FND-04 fixture corpora sit.
FIXTURES = repository_root() / "tests" / "fixtures"

#: The archive's spelling in the fixtures — `validate.corpus.ARCHIVE_DIR`'s
#: stand-in for `<archive-root>`. ⚠️ Named here rather than imported, because
#: that constant is on no package's public surface (`SF-31/3`).
ARCHIVE_DIR = "archive"


def fixture_manifest(name: str) -> Manifest:
    """The manifest of one FND-04 fixture corpus — `depth1` or `depth2`."""
    root = FIXTURES / name
    return parse_manifest((root / MANIFEST_FILENAME).read_text(encoding="utf-8"))


def fixture_containers(name: str) -> tuple[Container, ...]:
    """Every container map of one fixture corpus, in sorted path order.

    ⚠️ The order is the *caller's*, and `build` is required not to use it —
    `test_tree` shuffles this and asserts the bytes do not move (R10).
    """
    root = FIXTURES / name
    manifest = fixture_manifest(name)
    return tuple(
        parse_container(
            path.read_text(encoding="utf-8"), path.relative_to(root).as_posix(), manifest
        )
        for path in sorted((root / ARCHIVE_DIR).rglob(CONTAINER_FILENAME))
    )


def fixture_contents(name: str) -> Contents:
    """The stable contents of one FND-04 fixture corpus."""
    return build(fixture_manifest(name), fixture_containers(name))


def a_manifest(**overrides) -> Manifest:
    """A synthetic manifest, read through the real reader so its shape is real."""
    document = {
        "corpus_api": 1,
        "source": "demo",
        "title": "A Demo Corpus",
        "levels": ["course"],
        "variants": ["prose"],
        "exercises": False,
        "placement": "tree",
        "content": {"include": ["*.md"], "exclude": []},
        **overrides,
    }
    return parse_manifest(json.dumps(document))


def a_container(manifest: Manifest, address, titles, units=None, **overrides) -> Container:
    """A synthetic container map, read through the real reader."""
    document = {
        "container_api": 1,
        "address": list(address),
        "titles": list(titles),
        "variant": manifest.variants[0],
        "ingested": "2026-01-05",
        "units": units
        if units is not None
        else [{"n": 1, "title": "One"}, {"n": 2, "title": "Two"}],
        **overrides,
    }
    for unit in document["units"]:
        unit.setdefault("practices", 0)
    where = "/".join([ARCHIVE_DIR, *address, CONTAINER_FILENAME])
    return parse_container(json.dumps(document), where, manifest)


def depth2_manifest(**overrides) -> Manifest:
    """A synthetic two-level manifest, for the tests that need real nesting."""
    return a_manifest(levels=["section", "module"], **overrides)


def written(path: Path) -> str:
    """One document's text, for the tests that assert what reached the disk."""
    return path.read_text(encoding="utf-8")
