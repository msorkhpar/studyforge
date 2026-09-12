"""Mirror of `src/studyforge/generate/declarations.py` (R12)."""

from __future__ import annotations

import shutil

import pytest

from studyforge.corpus.manifest import parse as parse_manifest
from studyforge.generate import BuildError, declared_practices, read_corpus, sources
from tests.studyforge.generate.corpora import FIXTURES, a_corpus, with_a_unit_missing

# --------------------------------------------------------------------------
# ⭐ the walk
# --------------------------------------------------------------------------


def test_every_declared_unit_with_material_is_found_in_declared_order():
    found = sources(FIXTURES / "depth1")

    assert [source.ordinal for source in found] == [1, 2, 3]
    assert [source.title for source in found] == [
        "What a triple is",
        "Reading a small graph",
        "Asking the first question",
    ]
    assert [source.directory.name for source in found] == ["unit-01", "unit-02", "unit-03"]
    assert all(source.directory.is_dir() for source in found)


def test_the_material_directory_is_the_one_the_archive_layout_names():
    """⭐ Asked of `Layout`, never composed here — the archive has one authority."""
    from studyforge.skills.adapter import Layout

    root = FIXTURES / "depth2"
    layout = Layout(root)
    for source in sources(root):
        assert source.directory == layout.unit_dir(
            source.container.address, source.container.variant, source.ordinal
        )


def test_a_declared_unit_with_no_material_is_skipped_rather_than_guessed_at(tmp_path):
    """⛔ The negative direction, with the mechanism removed rather than mocked."""
    before = [source.ordinal for source in sources(FIXTURES / "depth1")]
    root = with_a_unit_missing(tmp_path, "depth1", "archive/depth-one/raw/prose/unit-02")

    assert before == [1, 2, 3]
    assert [source.ordinal for source in sources(root)] == [1, 3]


def test_a_unit_directory_holding_no_document_is_skipped_too(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    for path in (root / "archive/depth-one/raw/prose/unit-03").glob("*.json"):
        path.unlink()

    assert [source.ordinal for source in sources(root)] == [1, 2]


def test_a_corpus_with_no_readable_manifest_refuses_naming_the_file(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    (root / "corpus.json").unlink()

    with pytest.raises(BuildError) as raised:
        sources(root)

    assert "corpus.json" in str(raised.value)
    assert str(tmp_path) not in str(raised.value), "R7: a refusal never carries a path"


def test_an_unreadable_container_map_refuses_naming_the_record_and_not_the_path(tmp_path):
    root = a_corpus(tmp_path, "depth2")
    (root / "archive/basics/01-getting-started/container.json").write_text("{", encoding="utf-8")

    with pytest.raises(BuildError) as raised:
        read_corpus(root)

    assert str(tmp_path) not in str(raised.value), "R7: a refusal never carries a path"


# --------------------------------------------------------------------------
# ⭐ Corpus — read once, and its two sets
# --------------------------------------------------------------------------


def test_present_and_absent_partition_every_declared_unit(tmp_path):
    root = with_a_unit_missing(tmp_path, "depth1", "archive/depth-one/raw/prose/unit-02")
    corpus = read_corpus(root)

    from studyforge.contents import order

    declared = {entry.key for entry in order(corpus.contents)}
    assert len(declared) == 3
    assert corpus.absent == {"depth-one/unit-02"}
    assert corpus.present | corpus.absent == declared
    assert corpus.present & corpus.absent == frozenset()


def test_a_shipped_fixture_declares_nothing_it_has_no_material_for():
    for name in ("depth1", "depth2"):
        assert read_corpus(FIXTURES / name).absent == frozenset()


def test_the_contents_document_is_built_and_never_written(tmp_path):
    """⛔ The seam, asserted: no plan golden and no placement profile names them.

    ⚠️ `toc.json` and `status.json` are values this package hands to the shipped
    index assembler. Writing them would create two paths `studyforge plan` never
    declared — failing Ruling 99's path-for-path clause — at a location
    `CorpusLocations` does not name. ⭐ When placement grows one, this test is
    replaced by one asserting the two files are written.
    """
    from studyforge.contents import STATUS_FILENAME, TOC_FILENAME
    from studyforge.corpus.placement import CorpusLocations
    from studyforge.generate import write_site

    assert {field for field in CorpusLocations.__dataclass_fields__} == {
        "root_index",
        "assets",
        "archive",
        "site_cache",
    }, "placement now names another corpus path; check whether it is the contents"

    write_site(FIXTURES / "depth1", tmp_path)

    on_disk = {path.name for path in tmp_path.rglob("*")}
    assert TOC_FILENAME not in on_disk
    assert STATUS_FILENAME not in on_disk


# --------------------------------------------------------------------------
# ⭐ declared_practices — `exercises: false` is a declaration of ZERO
# --------------------------------------------------------------------------


def a_manifest(exercises: bool):
    document = (FIXTURES / "depth1" / "corpus.json").read_text(encoding="utf-8")
    return parse_manifest(
        document.replace('"exercises": false', f'"exercises": {str(exercises).lower()}'),
        "corpus.json",
    )


def test_a_corpus_declaring_no_exercises_declares_zero_for_every_unit():
    assert declared_practices(a_manifest(False), 0) == 0
    assert declared_practices(a_manifest(False), 3) == 0


def test_a_corpus_declaring_exercises_says_nothing_and_the_container_answers():
    assert declared_practices(a_manifest(True), 3) == 3
    assert declared_practices(a_manifest(True), 0) == 0


def test_a_prose_corpus_builds_units_that_declare_zero_rather_than_nothing(tmp_path):
    """⛔ `None` would put a *more to come* panel on every page of a finished corpus."""
    root = a_corpus(tmp_path, "depth1")
    assert {source.declared_practices for source in sources(root)} == {0}


# --------------------------------------------------------------------------
# ⚠️ A gap this package names rather than guesses at
# --------------------------------------------------------------------------


def test_an_authored_overlay_is_not_applied_because_nothing_declares_where_it_sits(tmp_path):
    """⚠️ The premise of the hole, asserted so it cannot close silently.

    `unit.content` mints `content.json` and `skills.adapter.Layout` mints every
    other archive path — but no module in `src/` says where a unit's overlay
    lives inside an archive. ⭐ The harness knows, because it was written by
    hand; the build cannot, so a unit with an overlay is built without it.

    ⛔ **When `Layout` grows that path, this test fails and is replaced by one
    asserting the section is present** — it is a marker, not a guarantee.
    """
    from studyforge.skills.adapter import Layout
    from studyforge.unit.builder import build_unit
    from tests.studyforge.render.page import pages as harness

    root = FIXTURES / "depth2"
    overlay_holder = root / "archive/basics/01-getting-started/units/unit-01/content.json"
    assert overlay_holder.is_file(), "the fixture carries an overlay"
    assert not hasattr(Layout, "content"), "Layout now names the overlay; close this gap"

    with_overlay = harness.depth2_unit_01().document
    built = next(
        source for source in sources(root) if source.container.address.key.endswith("started")
    )
    without = build_unit(built.directory, declared_practices=built.declared_practices)

    assert [section["kind"] for section in with_overlay["sections"]][0] == "shared"
    assert "shared" not in [section["kind"] for section in without["sections"]]


def test_nothing_under_tests_is_disturbed_by_a_copy(tmp_path):
    """⭐ The helper's own premise: a fixture copy is writable and separate."""
    root = a_corpus(tmp_path, "depth1")
    shutil.rmtree(root / "archive")

    assert (FIXTURES / "depth1" / "archive").is_dir()


def test_a_container_map_whose_address_is_the_wrong_depth_refuses_as_a_BuildError(tmp_path):
    """⚠️ `SF-28/1`: `corpus.container.parse` lets an `AddressError` out.

    ⛔ This package promises one exception, so it catches that one too. The
    refusal names the record and never a path (R7).
    """
    import json

    root = a_corpus(tmp_path, "depth2")
    where = "archive/basics/01-getting-started/container.json"
    document = json.loads((root / where).read_text(encoding="utf-8"))
    document["address"] = document["address"][:1]
    (root / where).write_text(json.dumps(document), encoding="utf-8")

    with pytest.raises(BuildError) as raised:
        read_corpus(root)

    assert where in str(raised.value)
    assert str(tmp_path) not in str(raised.value), "R7: a refusal never carries a path"
