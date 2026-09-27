"""Mirror of `src/studyforge/archive/layout.py` (R12)."""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.address import Address, unit_name
from studyforge.archive.document import KINDS, build
from studyforge.archive.document import render as render_document
from studyforge.corpus.container import CONTAINER_FILENAME, Container, Unit
from studyforge.corpus.container import render as render_map
from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.corpus.placement import (
    ARCHIVE_DIRNAME,
    RAW_DIRNAME,
    UNITS_DIRNAME,
    profile_for,
)
from studyforge.archive.layout import (
    ARCHIVE_DIR,
    RAW_DIR,
    TREE_ROOT,
    UNITS_DIR,
    Layout,
    LayoutError,
    archive_tree,
    document_name,
)
from studyforge.unit.content import CONTENT_FILENAME
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
    # ⭐ One exported home (R21): `unit_name` IS on `studyforge.address.__all__`,
    # so it is imported rather than re-derived — and this asserts the import
    # rather than the string it happens to produce.
    layout = Layout(tmp_path, "archive")
    assert layout.unit_dir(ADDRESS, "prose", 7).name == unit_name(7)


def test_a_units_own_directory_is_beside_raw_and_not_inside_any_variant(tmp_path):
    """⛔ The distinction is the variant, and it is the whole reason both exist.

    ⭐ `unit_dir` is per *variant* and holds the archive documents; `unit_files`
    is per *unit* and holds what the unit owns — an asset's `local` path
    resolves against it, and the authored overlay `content` addresses sits in
    it. ⛔ The overlay's own file is spelled by `content` and by nothing else,
    here included.
    """
    layout = Layout(tmp_path, "archive")

    files = layout.unit_files(ADDRESS, 7)

    assert files == layout.container_dir(ADDRESS) / UNITS_DIR / unit_name(7)
    assert RAW_DIR not in files.parts
    assert layout.variant_dir(ADDRESS, "prose") not in files.parents


def test_the_two_shipped_fixtures_keep_their_material_where_unit_files_says():
    """⭐ The behavioural pin, on the corpora rather than on a literal.

    ⚠️ **This method is the one place `src/` declares the path** — both
    fixtures use the directory, and no reader composes it for itself. A literal
    compared against the same literal would agree with itself; these are files
    somebody else wrote.

    ⭐ `depth2`'s is asked through `content`, which is this method plus the
    contract's filename, so the one fixture pins both halves. ⛔ The
    filename is not spelled here either.
    """
    fixtures = Path(__file__).resolve().parents[2] / "fixtures"

    depth1 = Layout(fixtures / "depth1").unit_files(ADDRESS, 2)
    depth2 = Layout(fixtures / "depth2")

    assert (depth1 / "media" / "diagram.svg").is_file()
    assert depth2.content(Address(["basics", "01-getting-started"]), 1).is_file()


def test_the_overlays_address_is_this_layouts_to_answer_and_nobody_elses(tmp_path):
    """⛔ This is the one place `src/` says where a unit's authored overlay sits.

    ⭐ Without it a build would have to invent the file — and two builds would
    invent two. This is the join, and
    the point of it is that it is the ONLY join: the directory is `unit_files`'
    answer, the filename is the contract's, and neither is respelled here.
    """
    layout = Layout(tmp_path, "archive")

    overlay = layout.content(ADDRESS, 7)

    assert overlay == layout.unit_files(ADDRESS, 7) / CONTENT_FILENAME
    assert overlay.parent == layout.unit_files(ADDRESS, 7)
    assert RAW_DIR not in overlay.parts, "an overlay belongs to the unit, not to a variant"


def test_the_overlays_filename_is_the_contracts_and_is_not_a_second_literal_here():
    """⭐ The counterpart of the segment test below, one level down.

    ⛔ `ARCHIVE_DIR`, `RAW_DIR` and `UNITS_DIR` survive on this surface because
    an adapter's vocabulary arrives through this package (R19). ⚠️ The overlay's
    filename does NOT, and the reason is R21's producer column: **a person**
    writes `content.json`, never an adapter, so this package has no author to
    hand it to — what it has is one caller, `content`, and a name imported from
    the module that mints it beside `content_api`.
    """
    from studyforge.archive import layout as module

    body = Path(module.__file__).read_text(encoding="utf-8")

    assert "from studyforge.unit.content import CONTENT_FILENAME" in body
    assert CONTENT_FILENAME not in body, (
        "the overlay's filename is spelled as a literal on this surface"
    )


def test_this_layout_locates_an_overlay_and_claims_nothing_about_applying_one():
    """⚠️ Asserted against the prose rather than left to a reader.

    ⛔ An address is not a feature. A maintainer who meets `content` must not
    read it as *overlays work now*, so the docstring says the verb is unowned
    and this fails if that sentence is edited away.
    """
    prose = Layout.content.__doc__ or ""

    assert "unowned" in prose
    assert "applies none" in prose


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


def test_the_segment_names_on_this_surface_are_placements_and_not_a_second_value():
    # ⛔ `archive`, `raw` and `units` each have one value, placement's: the
    # archive's reader and its writer must agree about each directory, so
    # neither may keep a private copy. ⭐ All three names are bound here,
    # because an adapter's whole vocabulary arrives through this package
    # (R19); what they may never be is a second VALUE.
    # ⚠️ That there is no second LITERAL is a claim about `src/`, and it is
    # asserted where the one home is, in `tests/studyforge/corpus/placement/
    # test_names.py`. This asserts what this surface hands an adapter author.
    assert ARCHIVE_DIR == ARCHIVE_DIRNAME
    assert RAW_DIR == RAW_DIRNAME
    assert UNITS_DIR == UNITS_DIRNAME


def test_the_archive_and_the_site_agree_on_where_a_units_own_files_sit(tmp_path):
    """⭐ The cross-TREE pin, and it is the reason the two names bind.

    ⛔ `UNITS_DIR` names a segment in the **archive**, which an adapter writes
    and `validate.source.membership` reads; `UNITS_DIRNAME` names one in the
    **generated site**, which `tree` places. They are two different trees, so
    binding them is a claim — and this is the claim, stated by `tree`'s own
    contract: the shape below a container is identical segment for segment,
    *so every href a page holds to its own media is unchanged*.

    ⚠️ A build depends on it in both directions at once: `generate.media` asks
    `Layout.unit_files` where a unit's media IS and placement where it GOES.
    ⛔ Asserted on the paths the two producers build, never on the constant —
    a constant compared against itself agrees whatever it says.
    """
    archive = Layout(tmp_path, ARCHIVE_DIR).unit_files(ADDRESS, 7)
    site = profile_for("tree").unit_dir(ADDRESS, 7)

    assert archive.parent.name == site.parent.name, (
        "the archive and the site disagree on the segment a unit's own files sit under"
    )
    assert archive.name == site.name == unit_name(7)


def test_what_this_layout_writes_is_what_validate_reads(tmp_path):
    """⛔ The pin for `ARCHIVE_DIR` and `RAW_DIR`, and it is behavioural.

    ⭐ Both names are `corpus.placement`'s, on its surface and imported here,
    so neither has a second home. ⛔ A test
    comparing this module's constant against the same constant would agree with
    itself either way. This one lays out a real archive with `Layout` alone and
    asserts that `validate`'s own walk finds the document it wrote — which is
    the only instrument that would catch the two modules drifting apart.
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


# --------------------------------------------------------------------------
# ⛔ The drawn tree IS the layout, at values it was not drawn at
# --------------------------------------------------------------------------

#: A second set of values, chosen to share nothing with the ones the tree is
#: drawn at: a two-level address, another variant, a two-digit unit, a practice.
#: ⛔ Substituted back in here so the comparison is against `Layout` computing
#: something it has not computed before — a tree re-rendered at its own drawing
#: values would agree with itself.
OTHER = Address(["basics", "01-getting-started"])
OTHER_VARIANT = "java"
OTHER_UNIT = 12
OTHER_ORDINAL = 3


def filled(line: str, root) -> str:
    """Return one drawn line with every placeholder replaced by a real value."""
    for token, value in (
        ("<corpus-root>", str(root)),
        ("<address>", OTHER.key),
        ("<variant>", OTHER_VARIANT),
        ("unit-NN", unit_name(OTHER_UNIT)),
        ("<kind>-N.json", document_name("practice", OTHER_ORDINAL)),
    ):
        line = line.replace(token, value)
    return line.rstrip("/")


def test_the_drawn_tree_is_the_four_places_layout_computes(tmp_path):
    """⛔ R19's whole point: a page shows this, so the page cannot retype it.

    ⭐ Non-circular by construction — the tree is drawn at one address, one
    variant and unit 1, and this fills it at two levels, another variant, unit
    12 and a practice, then asks `Layout` for the same four paths.
    """
    layout = Layout(tmp_path)
    assert [filled(line, tmp_path) for line in archive_tree().splitlines()] == [
        str(layout.manifest),
        str(layout.container_map(OTHER)),
        str(layout.document(OTHER, OTHER_VARIANT, OTHER_UNIT, "practice", OTHER_ORDINAL)),
        str(layout.unit_files(OTHER, OTHER_UNIT)),
    ]


def test_the_tree_draws_a_units_own_directory_and_it_is_not_inside_any_variant():
    # ⛔ The line every page that draws this tree must carry.
    home = archive_tree().splitlines()[-1]
    assert home.endswith(f"{UNITS_DIR}/unit-NN/"), home
    assert f"/{RAW_DIR}/" not in home, "a unit's own files were drawn inside a variant"


def test_the_drawing_replaces_a_whole_segment_and_never_part_of_one():
    # ⚠️ The three segments `corpus.placement` owns must survive the
    # substitution untouched, whatever the tree was drawn at.
    drawn = archive_tree()
    for segment in (ARCHIVE_DIRNAME, RAW_DIRNAME, UNITS_DIRNAME):
        assert f"/{segment}/" in drawn, f"the drawn tree lost {segment!r}"
    assert drawn.count(TREE_ROOT) == len(drawn.splitlines())


def test_the_tree_is_rooted_at_the_placeholder_it_publishes():
    # ⛔ A reader substitutes their own root for this token, so it is a name
    # rather than a string each caller re-types.
    assert all(line.startswith(f"{TREE_ROOT}/") for line in archive_tree().splitlines())
