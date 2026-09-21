"""`validate`'s arm over an authored exercise's gate record and bundle (`AX-04`).

⭐ Every check here has a **negative control**: the same corpus with the defect
removed is clean. ⛔ And every plant is a REAL edit to a REAL file whose effect
is asserted and printed before any check is read — a gate record written over a
dictionary would have let each plant be a value somebody typed.
"""

from __future__ import annotations

import json

from studyforge.archive.document import render
from studyforge.exercise.bundle import bundle_of, emit, write
from studyforge.validate import validate
from studyforge.validate.exercises import (
    RULE_BUNDLE_CONTENTS,
    RULE_BUNDLE_DIGEST,
    RULE_GATE_RECORD,
    RULE_GATE_SHORTFALL,
    RULE_PRACTICE_ORDINALS,
)
from tests.studyforge.exercise.bundle import bundles
from tests.studyforge.validate import corpora

#: ⛔ A corpus that commits authored exercises declares their two directories
#: `not_material`: they are neither the material nor a build's output, and an
#: unclassified file is refused rather than guessed at (C2).
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


def a_corpus(root, *, bundles_on_page=1, **overrides):
    """One corpus with `bundles_on_page` authored exercises on unit 1.

    Returns `(root, [Places, ...])`.
    """
    written, documents = [], {}
    for ordinal in range(1, bundles_on_page + 1):
        places = bundles.write_bundle(root, unit=1, ordinal=ordinal, **overrides)
        bundles.write_gate_record(root, places)
        bundle = bundle_of(
            json.loads((root / places.document).read_text(encoding="utf-8")), "bundle.json"
        )
        emission = emit(root, bundle, source="demo", ingested="2026-01-05")
        root.mkdir(parents=True, exist_ok=True)
        write(root, emission, "emission")
        documents[f"demo/raw/prose/unit-01/practice-{ordinal}.json"] = emission.document
        written.append(places)
    corpora.write(
        root,
        manifest=MANIFEST,
        containers={
            "demo": corpora.container([corpora.unit_entry(1, practices=bundles_on_page)])
        },
        sources={"src/one.md": corpora.SOURCE},
    )
    for where, document in documents.items():
        path = root / "archive" / where
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(render(document), encoding="utf-8")
    return root, written


def test_an_authored_corpus_validates(tmp_path):
    root, _ = a_corpus(tmp_path / "c")
    report = validate(root)
    assert report.findings == (), [f.message for f in report.findings]
    assert report.exit_code == 0


def test_a_generated_exercise_with_no_gate_record_is_refused(tmp_path):
    root, places = a_corpus(tmp_path / "c")
    record = root / places[0].gates
    assert record.is_file()
    record.unlink()
    assert not record.exists()  # ⭐ the planted state, asserted before the reading
    report = validate(root)
    assert RULE_GATE_RECORD in report.rules
    assert places[0].gates in "\n".join(f.message for f in report.findings)


def test_a_gate_record_that_will_not_read_is_refused(tmp_path):
    root, places = a_corpus(tmp_path / "c")
    (root / places[0].gates).write_text('{"gates": []}', encoding="utf-8")
    assert json.loads((root / places[0].gates).read_text(encoding="utf-8")) == {"gates": []}
    assert RULE_GATE_RECORD in validate(root).rules


def test_a_gate_record_in_which_a_gate_did_not_hold_is_refused(tmp_path):
    root, places = a_corpus(tmp_path / "c")
    written = bundles.write_gate_record(root, places[0], held=False)
    assert [gate["held"] for gate in written["gates"]].count(False) == 1
    report = validate(root)
    assert RULE_GATE_SHORTFALL in report.rules
    assert RULE_GATE_RECORD not in report.rules


def test_a_bundle_whose_digest_no_longer_matches_is_refused_naming_the_file(tmp_path):
    root, places = a_corpus(tmp_path / "c")
    reference = root / places[0].bundle / "reference" / "bitmap.py"
    before = reference.read_text(encoding="utf-8")
    reference.write_text(before + "# changed after the gates ran\n", encoding="utf-8")
    assert reference.read_text(encoding="utf-8") != before  # ⭐ the plant, observed
    report = validate(root)
    assert RULE_BUNDLE_DIGEST in report.rules
    named = "\n".join(f.message for f in report.findings if f.rule == RULE_BUNDLE_DIGEST)
    assert "reference/bitmap.py" in named


def test_an_input_the_bundle_no_longer_holds_is_refused(tmp_path):
    root, places = a_corpus(tmp_path / "c")
    (root / places[0].bundle / "plants" / "edge-1" / "bitmap.py").unlink()
    report = validate(root)
    assert RULE_BUNDLE_DIGEST in report.rules


def test_a_readers_own_edit_never_moves_a_digest(tmp_path):
    # ⛔ The property the two roots exist for. The reader works in their own
    # file; the gate record was taken over the bundle's, which they never see.
    root, places = a_corpus(tmp_path / "c")
    worked = root / places[0].workspace / "bitmap.py"
    before = worked.read_text(encoding="utf-8")
    worked.write_text("def build(fields):\n    return 7\n", encoding="utf-8")
    assert worked.read_text(encoding="utf-8") != before
    assert validate(root).findings == ()


def test_a_run_report_committed_into_a_bundle_is_refused(tmp_path):
    # ⛔ `AX-03/1`: a JUnit report carries the machine's hostname, and a corpus
    # repository is where this repository's personal-data gate never looks.
    root, places = a_corpus(tmp_path / "c")
    report_file = root / places[0].bundle / "report.xml"
    report_file.write_text('<testsuite name="x" hostname="a-machine"/>\n', encoding="utf-8")
    assert report_file.is_file()
    report = validate(root)
    assert RULE_BUNDLE_CONTENTS in report.rules
    named = "\n".join(f.message for f in report.findings if f.rule == RULE_BUNDLE_CONTENTS)
    assert "report.xml" in named and "hostname" in named


def test_several_exercises_on_one_page_validate(tmp_path):
    root, places = a_corpus(tmp_path / "c", bundles_on_page=2)
    assert len(places) == 2
    assert validate(root).findings == ()


def test_a_page_whose_practices_skip_an_ordinal_is_refused(tmp_path):
    root, _ = a_corpus(tmp_path / "c", bundles_on_page=2)
    second = root / "archive" / "demo" / "raw" / "prose" / "unit-01" / "practice-2.json"
    document = json.loads(second.read_text(encoding="utf-8"))
    document["ordinal"] = 3
    second.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    assert json.loads(second.read_text(encoding="utf-8"))["ordinal"] == 3
    assert RULE_PRACTICE_ORDINALS in validate(root).rules


def test_a_corpus_with_no_authored_exercise_is_untouched(tmp_path):
    # ⚠️ A `bundled` grader's derivation gates are `E08`'s; nothing here widens
    # to it, so a corpus that predates this milestone validates as it did.
    root = corpora.one_unit(tmp_path / "c")
    report = validate(root)
    assert report.findings == ()
    assert RULE_GATE_RECORD not in report.rules
