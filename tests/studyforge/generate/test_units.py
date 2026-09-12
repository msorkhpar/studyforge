"""Mirror of `src/studyforge/generate/units.py` (R12).

⭐ **Both `FND-04` fixtures, and the golden plan they already have.** The
`create …unit.html` lines in `tests/fixtures/golden/*.plan.txt` are what
`studyforge plan` says a build will write; this module asserts the unit-page
pass writes exactly those and no others, which is the unit half of Ruling 99's
path-for-path clause.
"""

from __future__ import annotations

import pytest

from studyforge.generate import Written, write_pages
from studyforge.render.page import AUDIO_ATTRIBUTE
from tests.studyforge.generate.corpora import BOTH, FIXTURES, a_corpus, an_output, planned


def planned_unit_pages(name: str) -> list[str]:
    return planned(name, ".unit.html")


# --------------------------------------------------------------------------
# ⭐ write_pages — the first non-test caller the renderer has ever had
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_build_writes_exactly_the_unit_pages_the_plan_declared(tmp_path, name):
    written = write_pages(FIXTURES / name, tmp_path)

    assert sorted(page.as_posix() for page in written.pages) == planned_unit_pages(name)
    assert written.refused == ()
    assert written.assets == (), "the bundle is the site pass's, not this one's"


@pytest.mark.parametrize("name", BOTH)
def test_every_page_the_build_names_is_a_file_it_actually_wrote(tmp_path, name):
    written = write_pages(FIXTURES / name, tmp_path)

    for page in written.pages:
        assert (tmp_path / page).is_file()
    on_disk = sorted(path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*.html"))
    assert on_disk == sorted(page.as_posix() for page in written.pages)


def test_the_body_is_the_renderers_own_and_not_a_second_spelling(tmp_path):
    """⭐ The real caller and the harness that stood in for it render one body.

    ⚠️ The chrome is the difference and it is the point of this row: the harness
    renders with no bar and no trail, so what must agree byte for byte is
    everything between them. ⭐ Compared by removing the two chrome regions from
    both sides rather than by re-rendering, so this cannot pass by the two sides
    computing the same thing twice.
    """
    import re

    from studyforge.render.page import render
    from tests.studyforge.render.page import pages as harness

    def without_chrome(body: str) -> str:
        """The page minus every `<nav>` region, and minus the gap each one leaves."""
        body = re.sub(r"<nav[^>]*>.*?</nav>", "", body, flags=re.DOTALL)
        return re.sub(r"\n{2,}", "\n", body)

    case = harness.depth1_unit_02()
    write_pages(FIXTURES / "depth1", tmp_path)

    built = (tmp_path / case.placement.unit.page).read_text(encoding="utf-8")
    bare = render(case.document, case.placement).decode("utf-8")
    assert without_chrome(built) == without_chrome(bare)
    assert built != bare, "the build renders chrome the bare render has none of"


def test_an_unnarrated_corpus_stays_quiet(tmp_path):
    """⛔ No clip is linked when nothing has been synthesised."""
    written = write_pages(FIXTURES / "depth1", tmp_path)

    assert written.pages
    for page in written.pages:
        body = (tmp_path / page).read_text(encoding="utf-8")
        assert AUDIO_ATTRIBUTE not in body


@pytest.mark.parametrize("name", BOTH)
def test_every_page_carries_the_bar_and_the_trail_the_contents_computed(tmp_path, name):
    """⛔ The join, asserted on the artifact rather than on the function."""
    written = write_pages(FIXTURES / name, tmp_path)

    for page in written.pages:
        body = (tmp_path / page).read_text(encoding="utf-8")
        assert 'aria-label="Breadcrumb"' in body
        assert 'rel="up"' in body, "every unit page addresses the root index"


# --------------------------------------------------------------------------
# ⛔ R3 — generation is non-destructive, asserted in both directions
# --------------------------------------------------------------------------


def test_a_hand_edited_page_at_a_declared_path_is_REPLACED_and_that_is_the_gap(tmp_path):
    """⛔ **This clause pins the known cost of the rebuild policy, not a win.**

    ⭐ A footprint answers a question about the PLAN, so it cannot tell this
    build's own prior output from a copy of it somebody edited. R19 rules a
    hand-edit to a generated artifact a *finding, not a fix*, and every
    placement profile already ignores these pages — so the edit is taken.
    ⛔ **Anyone who closes that gap should break this test**, and should read
    `generate/writing.py`'s table before deciding it was passing by accident.
    """
    first = write_pages(FIXTURES / "depth1", tmp_path)
    target = tmp_path / first.pages[0]
    target.write_bytes(b"a page somebody edited by hand")

    second = write_pages(FIXTURES / "depth1", tmp_path)

    assert second.refused == ()
    assert first.pages[0] in second.replaced
    assert target.read_bytes() != b"a page somebody edited by hand"


def test_a_second_build_over_its_own_output_rewrites_every_page_it_declared(tmp_path):
    first = write_pages(FIXTURES / "depth1", tmp_path)
    stamps = {page: (tmp_path / page).read_bytes() for page in first.pages}

    second = write_pages(FIXTURES / "depth1", tmp_path)

    assert sorted(second.pages) == sorted(first.pages)
    assert second.refused == ()
    assert sorted(second.replaced) == sorted(first.pages)
    # ⭐ Same declarations in, same bytes out (R10) — a rebuild is not a churn.
    assert {page: (tmp_path / page).read_bytes() for page in first.pages} == stamps


def test_nothing_is_written_into_the_corpus_root(tmp_path):
    """⛔ R3's whole point: the material repository is read and never touched."""
    root = a_corpus(tmp_path / "in", "depth2")
    before = {
        path.relative_to(root).as_posix(): path.read_bytes()
        for path in sorted(root.rglob("*"))
        if path.is_file()
    }

    write_pages(root, an_output(tmp_path))

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
    assert written.paths == written.pages + written.assets
