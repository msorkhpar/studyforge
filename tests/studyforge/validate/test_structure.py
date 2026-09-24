"""Checks about the archive alone.

⭐ Every check here has a **negative control**: the same corpus with the defect
removed is clean. A validator that passes everything and a gate nobody calls
are the same failure, and a check nobody has watched fail is a check nobody has
watched work.
"""

import json

import pytest

from studyforge.validate import validate
from tests.studyforge.validate import corpora


def test_two_containers_at_different_addresses_are_fine(tmp_path):
    assert validate(corpora.two_containers(tmp_path / "c")).findings == ()


def test_no_two_containers_may_claim_the_same_address(tmp_path):
    # ⭐ `slugify`'s collision caught from the other end: the framework never
    # sees the two titles, but it sees the one address they both produced.
    # ⛔ A collision only the adapter can see is one a careless adapter author
    # disables.
    root = corpora.two_containers(tmp_path / "c")
    other = root / "archive" / "other" / "container.json"
    document = json.loads(other.read_text(encoding="utf-8"))
    document["address"] = ["demo"]
    other.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    report = validate(root)
    assert "duplicate-address" in report.rules
    assert "demo" in "\n".join(f.message for f in report.findings)


def test_an_address_that_is_not_its_directory_is_refused(tmp_path):
    root = corpora.one_unit(tmp_path / "c")
    (root / "archive" / "demo").rename(root / "archive" / "elsewhere")
    assert validate(root).rules == ("address-directory",)


def test_the_directory_check_is_not_resolved_by_preferring_either_side(tmp_path):
    root = corpora.one_unit(tmp_path / "c")
    (root / "archive" / "demo").rename(root / "archive" / "elsewhere")
    message = validate(root).findings[0].message
    assert "recorded, never derived" in message
    assert "'demo'" in message and "'elsewhere'" in message


# --------------------------------------------------------------------------
# a document against itself and against its container
# --------------------------------------------------------------------------


def edit(root, **changes):
    path = root / "archive/demo/raw/prose/unit-01/lesson-1.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document.update(changes)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return root


@pytest.mark.parametrize(
    ("changes", "rule"),
    [
        ({"content_sha256": "0" * 64}, "digest"),
        ({"counts": {"headings": 9}}, "counts"),
        ({"variant": "java"}, "identity"),
        ({"unit": 7}, "identity"),
        ({"kind": "practice"}, "identity"),
        ({"ordinal": 4}, "identity"),
    ],
)
def test_a_document_that_disagrees_with_itself_is_refused(tmp_path, changes, rule):
    root = edit(corpora.one_unit(tmp_path / "c"), **changes)
    assert rule in validate(root).rules


def test_an_untouched_document_agrees_with_itself(tmp_path):
    assert validate(corpora.one_unit(tmp_path / "c")).findings == ()


def test_a_unit_with_no_blocks_is_reported(tmp_path):
    # ⛔ R6: an empty unit is the shape of a short read that produced a
    # well-formed file, not "a unit that happens to be empty".
    root = corpora.one_unit(tmp_path / "c", blocks=[])
    assert "empty-unit" in validate(root).rules


# --------------------------------------------------------------------------
# the container's declarations against what is on disk
# --------------------------------------------------------------------------


def test_a_declared_unit_with_no_document_is_reported_by_name(tmp_path):
    root = corpora.one_unit(tmp_path / "c")
    (root / "archive/demo/raw/prose/unit-01/lesson-1.json").unlink()
    report = validate(root)
    assert "unit-missing" in report.rules
    assert "unit 1" in report.findings[0].message


def test_a_declared_practice_that_is_absent_is_reported(tmp_path):
    root = corpora.write(
        tmp_path / "c",
        containers={"demo": corpora.container([corpora.unit_entry(1, practices=2)])},
        documents={
            "demo/raw/prose/unit-01/lesson-1.json": {
                "source": "demo",
                "address": ["demo"],
                "variant": "prose",
                "unit": 1,
                "kind": "lesson",
                "ordinal": 1,
                "ingested": "2026-01-05",
                "title": "Unit 1",
                "blocks": corpora.BLOCKS,
            }
        },
    )
    report = validate(root)
    assert "practice-count" in report.rules
    assert "declares 2 practice(s) for unit 1; the archive holds 0" in report.findings[0].message


def test_a_matching_practice_count_is_not_reported(tmp_path):
    parts = {
        "source": "demo",
        "address": ["demo"],
        "variant": "prose",
        "unit": 1,
        "ingested": "2026-01-05",
        "blocks": corpora.BLOCKS,
    }
    root = corpora.write(
        tmp_path / "c",
        containers={"demo": corpora.container([corpora.unit_entry(1, practices=1)])},
        documents={
            "demo/raw/prose/unit-01/lesson-1.json": {
                **parts,
                "kind": "lesson",
                "ordinal": 1,
                "title": "Unit 1",
            },
            "demo/raw/prose/unit-01/practice-1.json": {
                **parts,
                "kind": "practice",
                "ordinal": 1,
                "title": "Practice 1",
            },
        },
    )
    assert validate(root).findings == ()


def test_a_refused_document_is_not_reported_as_a_missing_unit(tmp_path):
    # ⭐ **One defect must not become two findings.** A document the R7 gate
    # refuses is not an absent unit, and reporting it as one sends the reader
    # after the wrong problem.
    root = corpora.one_unit(tmp_path / "c")
    path = root / "archive/demo/raw/prose/unit-01/lesson-1.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document["source"] = "ingested from " + "/" + "home/jane/corpus"
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    report = validate(root)
    assert report.rules == ("personal-data",)
    assert "unit-missing" in {u.rule for u in report.unchecked}
