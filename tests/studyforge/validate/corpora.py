"""Building a corpus on disk, so a check can be shown to bite.

⭐ **the fixture corpora's fixtures are archive-only**, and the two checks that read the
material need material. Rather than teach `tests/fixture_checks/` about source
files — its "exactly one rule" invariant is defined over the checks *that*
package knows, so a corpus violating a rule only `validate` can see cannot live
in `tests/fixtures/invalid/` — these corpora are built in a temporary tree by
the tests that need them.

⛔ Nothing here is a fixture in the fixture corpora sense: they are inputs to negative
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


def container(
    units, *, address=("demo",), variant="prose", origin=None, titles=None, container_api=1
):
    """One container map. ⚠️ `container_api` defaults to 1, which is what every
    corpus here declares; a unit whose `origin` names a region needs 2 (R9).
    """
    document = {
        "container_api": container_api,
        "address": list(address),
        "titles": ["Demo"] if titles is None else list(titles),
        "variant": variant,
        "ingested": "2026-01-05",
    }
    if origin is not None:
        document["origin"] = origin
    document["units"] = units
    return document


def unit_entry(n, *, practices=0, origin=None, title="Unit", practice_origin=None):
    entry = {"n": n, "title": f"{title} {n}", "practices": practices}
    if origin is not None:
        entry["origin"] = origin
    if practice_origin is not None:
        # ⚠️ A unit whose practice comes from a file of its own needs
        # `container_api` 3, exactly as a region needs 2.
        entry["practice_origin"] = practice_origin
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


#: The additive file a practice arrives in, and the blocks an adapter reads out
#: of it. ⭐ Two headings on each side, so a plant on either side is one line.
PRACTICE_SOURCE = "## Problem statement\n\nDo the work.\n\n## Starting code\n"

PRACTICE_BLOCKS = [
    {"type": "heading", "level": 2, "text": "Problem statement"},
    {"type": "para", "text": "Do the work."},
    {"type": "heading", "level": 2, "text": "Starting code"},
]


def practised(
    root: Path,
    *,
    source=SOURCE,
    practice_source=PRACTICE_SOURCE,
    practice_blocks=None,
    origin="src/one.md",
    practice_origin="src/one-practice.md",
    declare_practice_origin=True,
    write_practice_document=True,
) -> Path:
    """One unit whose lesson and practice come from two files.

    ⛔ The four switches are what the negative controls need: a practice whose
    origin is **not** declared, a practice document that is **not** written,
    and a plant on either side of either comparison.
    """
    common = {
        "source": "demo",
        "address": ["demo"],
        "variant": "prose",
        "unit": 1,
        "ingested": "2026-01-05",
        "title": "Unit 1",
    }
    documents = {
        "demo/raw/prose/unit-01/lesson-1.json": {
            **common,
            "kind": "lesson",
            "ordinal": 1,
            "blocks": BLOCKS,
        }
    }
    if write_practice_document:
        documents["demo/raw/prose/unit-01/practice-1.json"] = {
            **common,
            "kind": "practice",
            "ordinal": 1,
            "blocks": PRACTICE_BLOCKS if practice_blocks is None else practice_blocks,
        }
    entry = unit_entry(
        1,
        practices=1,
        origin=origin,
        practice_origin=practice_origin if declare_practice_origin else None,
    )
    return write(
        root,
        containers={"demo": container([entry], container_api=3)},
        documents=documents,
        sources={origin: source, practice_origin: practice_source},
    )


def two_containers(
    root: Path,
    *,
    second_address=("other",),
    placement=None,
    origin=None,
    second_origin=None,
    titles=None,
    second_titles=None,
    unit_origin=None,
    second_unit_origin=None,
    unit_title="Unit",
    second_unit_title="Unit",
) -> Path:
    """Two containers, one unit each — the smallest corpus a collision needs.

    ⭐ A collision between two containers cannot be built from one, and every
    check that places the whole corpus needs at least two things placed.
    """
    parts = {
        "source": "demo",
        "variant": "prose",
        "unit": 1,
        "kind": "lesson",
        "ordinal": 1,
        "ingested": "2026-01-05",
        "title": "Unit 1",
        "blocks": BLOCKS,
    }
    manifest = MANIFEST if placement is None else {**MANIFEST, "placement": placement}
    second = "/".join(second_address)
    return write(
        root,
        manifest=manifest,
        containers={
            "demo": container(
                [unit_entry(1, origin=unit_origin, title=unit_title)],
                origin=origin,
                titles=titles,
            ),
            second: container(
                [unit_entry(1, origin=second_unit_origin, title=second_unit_title)],
                address=second_address,
                origin=second_origin,
                titles=second_titles,
            ),
        },
        documents={
            "demo/raw/prose/unit-01/lesson-1.json": {**parts, "address": ["demo"]},
            f"{second}/raw/prose/unit-01/lesson-1.json": {
                **parts,
                "address": list(second_address),
            },
        },
    )


def _lesson(address, n, title):
    return {
        "source": "demo",
        "address": list(address),
        "variant": "prose",
        "unit": n,
        "kind": "lesson",
        "ordinal": 1,
        "ingested": "2026-01-05",
        "title": title,
        "blocks": BLOCKS,
    }


def mirrored(root: Path) -> Path:
    """Two containers whose units share ordinals and titles, every origin in `src/`."""
    manifest = {**MANIFEST, "placement": "sibling"}
    containers, documents = {}, {}
    for letter, segment in (("a", "first"), ("b", "second")):
        units = [unit_entry(n, origin=f"src/{letter}{n}.md", title="Shared") for n in (1, 2)]
        containers[segment] = container(
            units,
            address=(segment,),
            origin=f"src/{letter.upper()}.md",
            titles=[f"Series {letter}"],
        )
        for n in (1, 2):
            documents[f"{segment}/raw/prose/unit-0{n}/lesson-1.json"] = _lesson(
                (segment,), n, f"Shared {n}"
            )
    return write(root, manifest=manifest, containers=containers, documents=documents)


def repeated_label(root: Path) -> Path:
    """One container whose two units record one label and one title, in one directory.

    ⛔ The one collision a unit's container cannot separate under `sibling`:
    both units are named `first.1-shared`, so `validate`, `plan` and a build refuse it.
    """
    manifest = {**MANIFEST, "placement": "sibling"}
    units = [
        {"n": n, "title": "Shared", "practices": 0, "origin": f"src/a{n}.md", "label": "1"}
        for n in (1, 2)
    ]
    return write(
        root,
        manifest=manifest,
        containers={"first": container(units, address=("first",), origin="src/A.md")},
        documents={
            f"first/raw/prose/unit-0{n}/lesson-1.json": _lesson(("first",), n, "Shared")
            for n in (1, 2)
        },
    )


#: What unit 1 says: every kind of link, each leading somewhere or nowhere.
LINKED = (
    "Read [the types](code/Types.java), [the next unit](two.md) and "
    "[the introduction](#11-one); Section 1.2 goes on. "
    "[gone](code/Gone.java), [out](../../outside.txt), [rooted](/etc/hosts), "
    "[nowhere](#no-such-heading) and [a site](https://example.invalid/x)."
)


def linked(tmp_path: Path, placement: str = "tree", text: str = LINKED) -> Path:
    """Two units of one container, their sources, and one file the first links.

    ⭐ Written under `tmp_path / placement`, so both profiles fit in one test.
    """
    common = {
        "source": "demo",
        "address": ["demo"],
        "variant": "prose",
        "kind": "lesson",
        "ordinal": 1,
        "ingested": "2026-01-05",
    }
    return write(
        tmp_path / placement,
        manifest={**MANIFEST, "placement": placement},
        containers={
            "demo": container(
                [unit_entry(1, origin="src/one.md"), unit_entry(2, origin="src/two.md")],
                origin="src/README.md",
            )
        },
        documents={
            "demo/raw/prose/unit-01/lesson-1.json": {
                **common,
                "unit": 1,
                "title": "Unit 1",
                "blocks": [
                    {"type": "heading", "level": 1, "text": "1.1 One"},
                    {"type": "para", "text": text},
                ],
            },
            "demo/raw/prose/unit-02/lesson-1.json": {
                **common,
                "unit": 2,
                "title": "Unit 2",
                "blocks": [{"type": "heading", "level": 1, "text": "1.2 Two"}],
            },
        },
        sources={
            "src/README.md": "# Demo\n",
            "src/one.md": "# 1.1 One\n",
            "src/two.md": "# 1.2 Two\n",
            "src/code/Types.java": "class Types {}\n",
        },
    )
