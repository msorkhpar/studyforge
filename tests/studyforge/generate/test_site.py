"""Mirror of `src/studyforge/generate/site.py` (R12).

⭐ **Ruling 99's clause, run rather than asserted, for the HTML it covers.**
`studyforge plan`'s committed goldens say every path a build creates; this module
diffs the `.html` half of them against what `write_site` actually wrote, on both
`FND-04` fixtures. ⛔ The expected list is READ from the golden, never retyped.
"""

from __future__ import annotations

import re

import pytest

from studyforge.generate import assets, read_corpus, root_index, write_site
from tests.studyforge.generate.corpora import (
    BOTH,
    FIXTURES,
    an_output,
    planned,
    with_a_unit_missing,
)

#: Every local reference a page makes, absolute URLs and mail links excluded.
REFERENCE = re.compile(r'(?:src|href)="([^"]*)"')

#: The media directories `corpus.placement` mints per unit. ⛔ Named so the one
#: seam this row stops at is spelled once.
MEDIA = ("audio", "images", "video", "practice")


def references_in(body: str) -> list[str]:
    return [
        reference
        for reference in REFERENCE.findall(body)
        if "://" not in reference and not reference.startswith(("mailto:", "#"))
    ]


def landing(page, reference: str):
    return (page.parent / reference.split("#")[0]).resolve()


# --------------------------------------------------------------------------
# ⛔ Ruling 99 — the plan and the build agree, path for path
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_the_build_writes_exactly_the_html_the_plan_declared(tmp_path, name):
    written = write_site(FIXTURES / name, tmp_path)

    assert sorted(page.as_posix() for page in written.pages) == planned(name, ".html")
    assert written.refused == ()


@pytest.mark.parametrize("name", BOTH)
def test_nothing_on_disk_afterwards_is_a_path_the_plan_did_not_declare(tmp_path, name):
    """⛔ The other direction: no stray file, and every asset inside a planned directory."""
    written = write_site(FIXTURES / name, tmp_path)
    declared = set(planned(name, ""))

    on_disk = {
        path.relative_to(tmp_path).as_posix() for path in tmp_path.rglob("*") if path.is_file()
    }
    assert on_disk == {path.as_posix() for path in written.paths}
    for path in written.assets:
        assert f"{path.parent.as_posix()}/" in declared, f"{path} sits outside the plan"


@pytest.mark.parametrize("name", BOTH)
def test_the_committed_golden_still_matches_what_plan_says_at_this_ref(name):
    """⛔ Ruling 99's second half: a plan and a build that drifted together would pass one diff.

    ⭐ So the half of the golden this module reads — its `create` lines — is
    re-derived from `cli.plan`'s public surface here, rather than trusted. If the
    plan changed and the golden did not, this is red before the clause above can
    agree with a stale list.
    """
    from studyforge.cli.plan import plan_for

    fresh = sorted(creation.path for creation in plan_for(FIXTURES / name).creations)
    assert fresh == planned(name, "")


# --------------------------------------------------------------------------
# ⭐ the site holds together
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_no_reference_between_pages_or_to_the_bundle_dangles(tmp_path, name):
    """⛔ `SF-15`'s acceptance, and it is false of a function and true only of a directory.

    ⚠️ **Media is deliberately excluded and that is this row's seam.** The
    renderer emits `<img src="images/…">` and copies nothing — `SF-28`'s
    Acceptance carries the clause and no pass owns it yet — so a media reference
    dangling here is the *next* row's finding, asserted separately below rather
    than silently tolerated.
    """
    write_site(FIXTURES / name, tmp_path)

    dangling = []
    for page in sorted(tmp_path.rglob("*.html")):
        for reference in references_in(page.read_text(encoding="utf-8")):
            if any(f"{kind}/" in reference for kind in MEDIA):
                continue
            if not landing(page, reference).exists():
                dangling.append((page.relative_to(tmp_path).as_posix(), reference))
    assert dangling == []


@pytest.mark.parametrize("name", BOTH)
def test_every_reference_that_DOES_dangle_is_media_and_nothing_else(tmp_path, name):
    """⛔ The seam, measured rather than described — and it closes when the copy lands.

    ⭐ Ruling 99's media clause: *"every `src` and `href` a built page emits
    resolves to a file the build wrote"*. It does not hold yet, so this test
    states exactly what is missing. ⛔ When the media pass exists this test fails
    and is replaced by the clause itself.
    """
    write_site(FIXTURES / name, tmp_path)

    dangling = [
        reference
        for page in sorted(tmp_path.rglob("*.html"))
        for reference in references_in(page.read_text(encoding="utf-8"))
        if not landing(page, reference).exists()
    ]
    assert dangling, "the fixtures carry media; if this is empty the copy has landed"
    assert all(any(f"{kind}/" in reference for kind in MEDIA) for reference in dangling)


@pytest.mark.parametrize("name", BOTH)
def test_the_root_index_lists_every_declared_unit_and_links_the_readable_ones(tmp_path, name):
    corpus = read_corpus(FIXTURES / name)
    write_site(FIXTURES / name, tmp_path)

    body = (tmp_path / corpus.shared.root_index).read_text(encoding="utf-8")
    from studyforge.contents import order

    for entry in order(corpus.contents):
        assert f'id="{entry.key}"' in body
        assert entry.title in body


def test_a_declared_unit_with_no_page_is_listed_unreadable_rather_than_dropped(tmp_path):
    """⛔ §7's three states on the page a reader opens first."""
    root = with_a_unit_missing(tmp_path / "in", "depth1", "archive/depth-one/raw/prose/unit-02")
    out = an_output(tmp_path)
    corpus = read_corpus(root)

    write_site(root, out)
    body = (out / corpus.shared.root_index).read_text(encoding="utf-8")

    row = re.search(r'<li id="depth-one/unit-02"[^>]*>(.*?)</li>', body, re.DOTALL)
    assert row is not None, "the absent unit is listed"
    assert 'data-readable="false"' in row.group(0)
    assert "<a " not in row.group(1), "an anchor here would point at a page nobody wrote"
    assert "Reading a small graph" in row.group(1)


def test_the_index_is_built_from_what_this_build_wrote_and_not_from_a_disk_scan(tmp_path):
    """⚠️ A scan would read the READER's disk, and say something else the day one is deleted."""
    out = an_output(tmp_path)
    write_site(FIXTURES / "depth1", out)
    corpus = read_corpus(FIXTURES / "depth1")
    first = (out / corpus.shared.root_index).read_text(encoding="utf-8")

    for page in out.rglob("*.unit.html"):
        page.unlink()
    (out / corpus.shared.root_index).unlink()
    write_site(FIXTURES / "depth1", out)

    assert (out / corpus.shared.root_index).read_text(encoding="utf-8") == first


# --------------------------------------------------------------------------
# ⭐ the shared bundle
# --------------------------------------------------------------------------


def test_the_bundle_is_asked_of_pageassets_as_one_call(tmp_path):
    from studyforge.render.pageassets import written_files

    corpus = read_corpus(FIXTURES / "depth1")
    written = assets(corpus, tmp_path)

    expected = written_files()
    assert sorted(path.name for path in written.assets) == sorted(expected)
    for path in written.assets:
        assert (tmp_path / path).read_text(encoding="utf-8") == expected[path.name]
        assert path.parent == corpus.shared.assets


# --------------------------------------------------------------------------
# ⛔ R3, over the whole site
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_a_second_build_over_its_own_output_writes_nothing_and_names_everything(tmp_path, name):
    first = write_site(FIXTURES / name, tmp_path)
    stamps = {path: (tmp_path / path).read_bytes() for path in first.paths}

    second = write_site(FIXTURES / name, tmp_path)

    assert second.paths == ()
    assert sorted(second.refused) == sorted(first.paths)
    assert {path: (tmp_path / path).read_bytes() for path in first.paths} == stamps


def test_a_readers_own_file_at_any_target_survives_byte_for_byte(tmp_path):
    corpus = read_corpus(FIXTURES / "depth1")
    mine = b"a reader's own file"
    (tmp_path / corpus.shared.root_index).parent.mkdir(parents=True, exist_ok=True)
    (tmp_path / corpus.shared.root_index).write_bytes(mine)

    written = write_site(FIXTURES / "depth1", tmp_path)

    assert corpus.shared.root_index in written.refused
    assert (tmp_path / corpus.shared.root_index).read_bytes() == mine


def test_root_index_alone_refuses_the_same_way(tmp_path):
    corpus = read_corpus(FIXTURES / "depth1")
    first = root_index(corpus, tmp_path)

    second = root_index(corpus, tmp_path)

    assert first.pages == (corpus.shared.root_index,)
    assert second.pages == ()
    assert second.refused == first.pages
