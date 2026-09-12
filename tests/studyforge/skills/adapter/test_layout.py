"""Mirror of `src/studyforge/skills/adapter/layout.py` (R12)."""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.address import Address, unit_name
from studyforge.archive.document import KINDS, build
from studyforge.archive.document import render as render_document
from studyforge.corpus.container import CONTAINER_FILENAME, Container, Unit
from studyforge.corpus.container import render as render_map
from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.skills.adapter import (
    ARCHIVE_DIR,
    RAW_DIR,
    UNITS_DIR,
    Layout,
    LayoutError,
    document_name,
)
from studyforge.validate.corpus import read as walk
from tests.studyforge.skills.adapter import corpora

ADDRESS = Address(["depth-one"])


def test_the_manifest_is_where_validate_reads_it(tmp_path):
    assert Layout(tmp_path).manifest == tmp_path / MANIFEST_FILENAME


def test_a_container_directory_is_its_address(tmp_path):
    # ⛔ §6: the address is the directory, not something derived from it.
    layout = Layout(tmp_path, "archive")
    assert layout.container_dir(Address(["a", "b"])) == tmp_path / "archive/a/b"
    assert layout.container_map(ADDRESS).name == CONTAINER_FILENAME


def test_a_document_path_is_five_joins_and_this_module_owns_all_of_them(tmp_path):
    where = Layout(tmp_path, "archive").document(ADDRESS, "prose", 3, "lesson", 2)
    assert where == tmp_path / "archive/depth-one/raw/prose/unit-03/lesson-2.json"


def test_the_unit_directory_is_named_by_the_package_that_owns_the_padding(tmp_path):
    # ⭐ Ruling 101's other row: `unit_name` IS on `studyforge.address.__all__`,
    # so it is imported rather than re-derived — and this asserts the import
    # rather than the string it happens to produce.
    layout = Layout(tmp_path, "archive")
    assert layout.unit_dir(ADDRESS, "prose", 7).name == unit_name(7)


def test_a_units_own_directory_is_beside_raw_and_not_inside_any_variant(tmp_path):
    """⛔ The distinction is the variant, and it is the whole reason both exist.

    ⭐ `unit_dir` is per *variant* and holds the archive documents; `unit_files`
    is per *unit* and holds what the unit owns — an asset's `local` path
    resolves against it, and `<address>/units/unit-NN/content.json` is the
    authored overlay §5's contract table names.
    """
    layout = Layout(tmp_path, "archive")

    files = layout.unit_files(ADDRESS, 7)

    assert files == layout.container_dir(ADDRESS) / UNITS_DIR / unit_name(7)
    assert RAW_DIR not in files.parts
    assert layout.variant_dir(ADDRESS, "prose") not in files.parents


def test_the_two_shipped_fixtures_keep_their_material_where_unit_files_says():
    """⭐ The behavioural pin, on the corpora rather than on a literal.

    ⚠️ **This method was landed by `SF-37` because the path was declared nowhere
    in `src/`** — both fixtures use the directory and every reader was composing
    it for itself. A literal compared against the same literal would agree with
    itself; these are files somebody else wrote.
    """
    fixtures = Path(__file__).resolve().parents[3] / "fixtures"

    depth1 = Layout(fixtures / "depth1").unit_files(ADDRESS, 2)
    depth2 = Layout(fixtures / "depth2").unit_files(Address(["basics", "01-getting-started"]), 1)

    assert (depth1 / "media" / "diagram.svg").is_file()
    assert (depth2 / "content.json").is_file()


def test_staging_is_beside_the_archive_and_never_inside_it(tmp_path):
    # ⛔ `validate` rglobs the archive, so a half-written tree left inside it is
    # a tree the next run reports on — at the reader, not at the writer.
    layout = Layout(tmp_path, "archive")
    assert layout.archive not in layout.staging.parents
    assert layout.staging != layout.archive


def test_a_document_kind_comes_from_a_closed_set():
    for kind in KINDS:
        assert document_name(kind, 1) == f"{kind}-1.json"
    with pytest.raises(LayoutError) as refused:
        document_name("chapter", 1)
    assert "chapter" not in str(refused.value), "a refusal quoted the value it refused (R7)"


def test_an_ordinal_below_one_is_refused_rather_than_written(tmp_path):
    # ⛔ `unit-00` matches validate's directory pattern and would be read as a
    # unit that no container declares — the one shape a layout can prevent.
    with pytest.raises(ValueError):
        Layout(tmp_path, "archive").unit_dir(ADDRESS, "prose", 0)


def test_an_archive_directory_with_a_separator_is_refused(tmp_path):
    for bad in ("a/b", "", ".hidden"):
        with pytest.raises(LayoutError):
            Layout(tmp_path, bad)


def test_a_report_never_carries_an_absolute_path(tmp_path):
    # ⛔ R7. A report is the most-pasted artifact an adapter produces.
    layout = Layout(tmp_path, "archive")
    named = layout.relative(layout.document(ADDRESS, "prose", 1, "lesson", 1))
    assert not Path(named).is_absolute()
    assert str(tmp_path) not in named


def test_what_this_layout_writes_is_what_validate_reads(tmp_path):
    """⛔ The pin for `ARCHIVE_DIR` and `RAW_DIR`, and it is behavioural.

    ⚠️ Both names are owned by `validate.corpus`, which puts neither on a
    package surface — Ruling 101's second row, so they are re-derived here.
    ⛔ A test comparing this module's literal against the same literal would
    agree with itself. This one lays out a real archive with `Layout` alone and
    asserts that `validate`'s own walk finds the document it wrote.
    """
    corpora.write(tmp_path)
    layout = Layout(tmp_path, ARCHIVE_DIR)
    container = Container(
        address=ADDRESS,
        titles=("A Walkthrough Corpus",),
        variant="prose",
        ingested=corpora.INGESTED,
        origin="README.md",
        units=(Unit(n=1, title="First", practices=0, origin="src/01.md"),),
    )
    _write(layout.container_map(ADDRESS), render_map(container))
    document = build(
        source="walkthrough",
        address=ADDRESS,
        variant="prose",
        unit=1,
        kind="lesson",
        ordinal=1,
        ingested=corpora.INGESTED,
        title="First",
        blocks=[{"type": "heading", "level": 1, "text": "First"}],
    )
    where = layout.document(ADDRESS, "prose", 1, "lesson", 1)
    _write(where, render_document(document))
    assert RAW_DIR in where.parts, "the raw segment left the path this module builds"

    found = walk(tmp_path)
    assert [held.container.address.key for held in found.containers] == [ADDRESS.key]
    assert [unit.path for unit in found.units] == [where], (
        "validate's own walk did not find the document this module laid out"
    )
    assert not found.findings


def _write(path: Path, text: str) -> None:
    """Write one file, making its directory — what the generated `emit` does."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
