"""An authored practice is not read against the unit's source (`W444`).

⛔ **The corpus here is read against REAL source files**, which is the half the
authored-exercise fixtures in `tests/studyforge/validate/test_exercises.py` never
had: their unit declares no `origin`, so `completeness` counted nothing and the
defect could not show. ⭐ Two units, both with an origin on disk:

- unit 1 — a lesson from `src/one.md`, the source's own `practice-1` from its
  `practice_origin`, and an authored `practice-2` emitted from a bundle;
- unit 2 — a lesson from `src/two.md`, no `practice_origin`, and an authored
  `practice-1` emitted from a bundle.

⛔ Every document here is real: the authored ones are `emit`'s own output over a
bundle on disk with a gate record digested from its files, so the exercise arm
of `validate` reads them as it would a corpus's.
"""

from __future__ import annotations

import json

from studyforge.archive.document import render
from studyforge.exercise.bundle import bundle_of, emit, write
from studyforge.validate import validate
from tests.studyforge.exercise.bundle import bundles
from tests.studyforge.validate import corpora

#: ⭐ The manifest an authored corpus declares: its bundles and workspaces are
#: `not_material` (`AX-04/2`), and the material is `src/*.md`.
MANIFEST = {
    **corpora.MANIFEST,
    "corpus_api": 2,
    "exercises": True,
    "content": {
        "include": ["src/*.md"],
        "not_material": [
            {"glob": "exercises/**", "why": "authored exercise bundles, not the material"},
            {"glob": "practice/**", "why": "the reader's own workspace, not the material"},
        ],
    },
}

#: Unit 2's source file: two headings, as `corpora.SOURCE` has.
SOURCE_TWO = "# Other\n\nProse.\n\n## Deeper\n\nMore prose.\n"

BLOCKS_TWO = [
    {"type": "heading", "level": 1, "text": "Other"},
    {"type": "para", "text": "Prose."},
    {"type": "heading", "level": 2, "text": "Deeper"},
    {"type": "para", "text": "More prose."},
]

#: Where each authored practice lands: `(unit, ordinal)`. ⭐ Ordinal 2 beside the
#: source's own practice-1, and ordinal 1 on a unit with none (`W437`).
AUTHORED = ((1, 2), (2, 1))


def _common(unit: int) -> dict:
    return {
        "source": "demo",
        "address": ["demo"],
        "variant": "prose",
        "unit": unit,
        "ingested": "2026-01-05",
        "title": f"Unit {unit}",
    }


def authored_corpus(root, *, blocks=None, blocks_two=None, practice_blocks=None):
    """Write the two-unit corpus and return `(root, {(unit, ordinal): archive path})`."""
    emitted = {}
    for unit, ordinal in AUTHORED:
        places = bundles.write_bundle(root, unit=unit, ordinal=ordinal)
        bundles.write_gate_record(root, places)
        bundle = bundle_of(
            json.loads((root / places.document).read_text(encoding="utf-8")), "bundle.json"
        )
        emission = emit(root, bundle, source="demo", ingested="2026-01-05")
        write(root, emission, "emission")
        emitted[(unit, ordinal)] = (
            f"demo/raw/prose/unit-{unit:02d}/practice-{ordinal}.json",
            emission.document,
        )
    documents = {
        "demo/raw/prose/unit-01/lesson-1.json": {
            **_common(1),
            "kind": "lesson",
            "ordinal": 1,
            "blocks": corpora.BLOCKS if blocks is None else blocks,
        },
        "demo/raw/prose/unit-01/practice-1.json": {
            **_common(1),
            "kind": "practice",
            "ordinal": 1,
            "blocks": corpora.PRACTICE_BLOCKS if practice_blocks is None else practice_blocks,
        },
        "demo/raw/prose/unit-02/lesson-1.json": {
            **_common(2),
            "kind": "lesson",
            "ordinal": 1,
            "blocks": BLOCKS_TWO if blocks_two is None else blocks_two,
        },
    }
    units = [
        corpora.unit_entry(
            1, practices=2, origin="src/one.md", practice_origin="src/one-practice.md"
        ),
        corpora.unit_entry(2, practices=1, origin="src/two.md"),
    ]
    corpora.write(
        root,
        manifest=MANIFEST,
        containers={"demo": corpora.container(units, container_api=3)},
        documents=documents,
        sources={
            "src/one.md": corpora.SOURCE,
            "src/one-practice.md": corpora.PRACTICE_SOURCE,
            "src/two.md": SOURCE_TWO,
        },
    )
    paths = {}
    for key, (where, document) in emitted.items():
        path = root / "archive" / where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(document), encoding="utf-8")
        paths[key] = path
    return root, paths


def short_reads(report) -> list:
    return sorted((f.where, f.message) for f in report.findings if f.rule == "short-read")


def test_an_archive_with_authored_practices_beside_the_sources_own_validates_clean(tmp_path):
    # ⭐ WHAT SETTLES IT 1. Before `W444` this archive read two short-reads, one
    # per unit that received an authored practice, each over by the layout's
    # three headings — as read on the first corpus.
    root, _ = authored_corpus(tmp_path / "c")
    report = validate(root)
    assert report.findings == (), report.lines()
    assert "short-read" not in {u.rule for u in report.unchecked}
    assert report.exit_code == 0


def test_the_authored_documents_carry_headings_the_check_would_otherwise_count(tmp_path):
    # ⛔ The fixture's own inhabitation: an authored practice that carried no
    # heading would make the clean reading above vacuous.
    _, paths = authored_corpus(tmp_path / "c")
    for path in paths.values():
        document = json.loads(path.read_text(encoding="utf-8"))
        assert document["counts"]["headings"] > 0
        assert document["exercise"]["provenance"] == "generated"


def test_a_lesson_that_lost_a_heading_beside_an_authored_practice_is_still_refused(tmp_path):
    # ⭐ WHAT SETTLES IT 2, on the unit with NO practice origin — the unit whose
    # lesson bucket the authored practice used to land in, where a lost
    # heading could have been papered over by the practice's three.
    root, _ = authored_corpus(tmp_path / "c", blocks_two=BLOCKS_TWO[:2])
    found = short_reads(validate(root))
    assert [where for where, _ in found] == ["demo/unit-02"]
    assert "its source carries 2 heading line(s)" in found[0][1]
    assert "records 1 heading block(s)" in found[0][1]


def test_a_source_practice_that_lost_a_heading_beside_an_authored_one_is_still_refused(tmp_path):
    # ⭐ WHAT SETTLES IT 2, on the practice side: the source's own practice is
    # read against its `practice_origin`, and the authored practice-2 on the
    # same unit neither hides the loss nor inflates the count.
    root, _ = authored_corpus(tmp_path / "c", practice_blocks=corpora.PRACTICE_BLOCKS[:2])
    found = short_reads(validate(root))
    assert [where for where, _ in found] == ["demo/unit-01"]
    assert "its practice source carries 2 heading line(s)" in found[0][1]
    assert "records 1 heading block(s)" in found[0][1]


def test_the_lesson_on_the_unit_with_a_source_practice_is_still_read(tmp_path):
    root, _ = authored_corpus(tmp_path / "c", blocks=corpora.BLOCKS[:2])
    found = short_reads(validate(root))
    assert [where for where, _ in found] == ["demo/unit-01"]
    assert "its source carries 2 heading line(s)" in found[0][1]


def test_a_practice_whose_grader_is_not_generated_is_counted_whatever_its_place(tmp_path):
    # ⛔ **Decided by what the document IS, never by where it sits.** The same
    # document at the same path, its exercise now `bundled` — the source's own
    # grader — is read against the unit's source like any source-derived
    # practice, and its three layout headings are a short read on that unit.
    root, paths = authored_corpus(tmp_path / "c")
    path = paths[(2, 1)]
    document = json.loads(path.read_text(encoding="utf-8"))
    document["exercise"]["provenance"] = "bundled"
    document["exercise"]["trust"] = "authoritative"
    path.write_text(render(document), encoding="utf-8")
    found = short_reads(validate(root))
    assert [where for where, _ in found] == ["demo/unit-02"]
    assert "records 5 heading block(s)" in found[0][1]
