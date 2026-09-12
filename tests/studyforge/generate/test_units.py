"""Mirror of `src/studyforge/generate/units.py` (R12).

⭐ **Both `FND-04` fixtures, and the golden plan they already have.** The
`create …unit.html` lines in `tests/fixtures/golden/*.plan.txt` are what
`studyforge plan` says a build will write; this module asserts a build writes
exactly those and no others, which is the unit-page half of Ruling 99's
path-for-path clause arriving at a ref where a build exists to run.
"""

from __future__ import annotations

import shutil

import pytest

from studyforge.corpus.manifest import parse as parse_manifest
from studyforge.generate import BuildError, Written, declared_practices, sources, write_pages
from studyforge.render.page import AUDIO_ATTRIBUTE
from tests.studyforge.render.page import pages as harness
from tests.support import repository_root

FIXTURES = repository_root() / "tests" / "fixtures"
GOLDEN = FIXTURES / "golden"


def planned_unit_pages(name: str) -> list[str]:
    """The unit pages `studyforge plan`'s committed golden says a build creates.

    ⛔ Read from the golden rather than recomposed here. A list retyped in this
    module would agree with the build for the same reason the build agrees with
    itself, and Ruling 99 exists because a plan and a build that drifted
    together would pass a diff between them.
    """
    lines = (GOLDEN / f"{name}.plan.txt").read_text(encoding="utf-8").splitlines()
    created = [line.split()[1] for line in lines if line.startswith("create ")]
    return sorted(path for path in created if path.endswith(".unit.html"))


def a_corpus(tmp_path, name: str):
    """A writable copy of one fixture corpus, so nothing under `tests/` is touched."""
    root = tmp_path / name
    shutil.copytree(FIXTURES / name, root)
    return root


# --------------------------------------------------------------------------
# ⭐ sources — the walk
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
    root = a_corpus(tmp_path, "depth1")
    before = [source.ordinal for source in sources(root)]

    shutil.rmtree(root / "archive/depth-one/raw/prose/unit-02")

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
# ⭐ write_pages — the first non-test caller the renderer has ever had
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", ["depth1", "depth2"])
def test_a_build_writes_exactly_the_unit_pages_the_plan_declared(tmp_path, name):
    written = write_pages(FIXTURES / name, tmp_path)

    assert sorted(page.as_posix() for page in written.pages) == planned_unit_pages(name)
    assert written.refused == ()


@pytest.mark.parametrize("name", ["depth1", "depth2"])
def test_every_page_the_build_names_is_a_file_it_actually_wrote(tmp_path, name):
    written = write_pages(FIXTURES / name, tmp_path)

    for page in written.pages:
        assert (tmp_path / page).is_file()
    on_disk = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*.html"))
    assert on_disk == sorted(page.as_posix() for page in written.pages)


def test_the_bytes_are_the_renderers_own_and_not_a_second_spelling(tmp_path):
    """⭐ The real caller and the harness that stood in for it agree.

    The harness renders `depth1` unit 2 *"the way a build would"* and its
    golden page is committed. A build with narration silenced must produce the
    same document — so this compares against the harness's own render with the
    same silence, and a divergence means one of the two invented something.
    """
    from studyforge.render.page import render

    case = harness.depth1_unit_02()
    write_pages(FIXTURES / "depth1", tmp_path)

    built = (tmp_path / case.placement.unit.page).read_bytes()
    assert built == render(case.document, case.placement)


def test_an_unnarrated_corpus_stays_quiet(tmp_path):
    """⛔ No clip is linked when nothing has been synthesised."""
    written = write_pages(FIXTURES / "depth1", tmp_path)

    assert written.pages
    for page in written.pages:
        body = (tmp_path / page).read_text(encoding="utf-8")
        assert AUDIO_ATTRIBUTE not in body


# --------------------------------------------------------------------------
# ⛔ R3 — generation is non-destructive, asserted in both directions
# --------------------------------------------------------------------------


def test_a_file_already_at_a_target_path_is_named_and_left_byte_for_byte_alone(tmp_path):
    first = write_pages(FIXTURES / "depth1", tmp_path)
    target = tmp_path / first.pages[0]
    target.write_bytes(b"a reader's own file")

    second = write_pages(FIXTURES / "depth1", tmp_path)

    assert first.pages[0] in second.refused
    assert first.pages[0] not in second.pages
    assert target.read_bytes() == b"a reader's own file"


def test_a_second_build_over_its_own_output_rewrites_nothing(tmp_path):
    first = write_pages(FIXTURES / "depth1", tmp_path)
    stamps = {page: (tmp_path / page).read_bytes() for page in first.pages}

    second = write_pages(FIXTURES / "depth1", tmp_path)

    assert second.pages == ()
    assert sorted(second.refused) == sorted(first.pages)
    assert {page: (tmp_path / page).read_bytes() for page in first.pages} == stamps


def test_nothing_is_written_into_the_corpus_root(tmp_path):
    """⛔ R3's whole point: the material repository is read and never touched."""
    root = a_corpus(tmp_path / "in", "depth2")
    before = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }

    write_pages(root, tmp_path / "out")

    after = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }
    assert after == before


def test_the_result_is_a_written_record_with_relative_paths(tmp_path):
    written = write_pages(FIXTURES / "depth1", tmp_path)

    assert isinstance(written, Written)
    assert all(not page.is_absolute() for page in written.pages)


# --------------------------------------------------------------------------
# ⚠️ A gap this module names rather than guesses at
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
    root = FIXTURES / "depth2"
    overlay_holder = root / "archive/basics/01-getting-started/units/unit-01/content.json"
    assert overlay_holder.is_file(), "the fixture carries an overlay"

    from studyforge.skills.adapter import Layout

    assert not hasattr(Layout, "content"), "Layout now names the overlay; close this gap"

    with_overlay = harness.depth2_unit_01().document
    built = next(
        source for source in sources(root) if source.container.address.key.endswith("started")
    )
    from studyforge.unit.builder import build_unit

    without = build_unit(built.directory, declared_practices=built.declared_practices)

    assert [section["kind"] for section in with_overlay["sections"]][0] == "shared"
    assert "shared" not in [section["kind"] for section in without["sections"]]
