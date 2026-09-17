"""Mirror of `src/studyforge/generate/site.py` (R12).

⭐ **Ruling 99's clause, run rather than asserted, for the HTML it covers.**
`studyforge plan`'s committed goldens say every path a build creates; this module
diffs the `.html` half of them against what `write_site` actually wrote, on both
`FND-04` fixtures. ⛔ The expected list is READ from the golden, never retyped.
"""

from __future__ import annotations

import re

import pytest

from studyforge.corpus.placement import UNIT_MEDIA_DIRNAMES
from studyforge.generate import assets, read_corpus, root_index, write_site
from tests.studyforge.generate.corpora import (
    BOTH,
    FIXTURES,
    a_corpus,
    an_output,
    planned,
    with_a_unit_missing,
)

#: Every local reference a page makes, absolute URLs and mail links excluded.
#: ⚠️ **`poster` is in here and it was not before `SF-37`.** A `<video poster="…">`
#: addresses a file exactly as a `src` does; the Acceptance's wording — *"every
#: `src` and `href`"* — was written before anything emitted one, and measured at
#: this ref `depth2` emits a poster. Left out, one media reference per deck is
#: invisible to every check in this module.
REFERENCE = re.compile(r'(?:src|href|poster)="([^"]*)"')


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
    for path in written.assets + written.media:
        assert f"{path.parent.as_posix()}/" in declared, f"{path} sits outside the plan"


@pytest.mark.parametrize("name", BOTH)
def test_every_directory_the_build_makes_is_one_the_plan_declared_and_holds_a_file(tmp_path, name):
    """⛔ Ruling 99 over the plan's `create <dir>/` lines, which are the media ones.

    ⭐ **W268 narrowed the other half**: a declared media directory is minted
    only when a copy fills it. So every one on disk is declared, and none is
    empty. ⚠️ `plan` still lists one per kind per unit; W267 makes it agree.
    """
    written = write_site(FIXTURES / name, tmp_path)
    corpus = read_corpus(FIXTURES / name)
    archive = f"{corpus.shared.archive.as_posix()}/"

    directories = [path for path in planned(name, "/") if path != archive]
    assert directories, "the goldens declare directories; this is measuring nothing otherwise"
    filled = {
        directory
        for directory in directories
        if any(path.is_relative_to(directory.rstrip("/")) for path in written.paths)
    }
    assert {f"{path.parent.as_posix()}/" for path in written.media} <= filled
    for path in directories:
        assert (tmp_path / path).is_dir() == (path in filled), path


@pytest.mark.parametrize("name", BOTH)
def test_a_built_site_holds_no_empty_directory(tmp_path, name):
    # ⛔ W268 clause 1, over the whole site: git cannot track an empty directory.
    write_site(FIXTURES / name, tmp_path)

    empty = [path for path in tmp_path.rglob("*") if path.is_dir() and not any(path.iterdir())]

    assert empty == []


@pytest.mark.parametrize("name", BOTH)
def test_no_page_reaches_into_a_media_directory_the_build_did_not_make(tmp_path, name):
    """⛔ W268: a unit with no media still loads offline, because nothing addresses one.

    ⭐ Every `src`, `href` and `poster` a page emits into a media directory lands
    in a directory that exists. ⚠️ Except a file the build NAMED missing, which
    dangles with or without its directory and is `SF-37`'s, below.
    """
    written = write_site(FIXTURES / name, tmp_path)
    missing = {(tmp_path / path).resolve() for path in written.missing}

    reached = [
        landing(page, reference)
        for page in sorted(tmp_path.rglob("*.html"))
        for reference in references_in(page.read_text(encoding="utf-8"))
        if any(f"{kind}/" in reference for kind in UNIT_MEDIA_DIRNAMES)
    ]
    assert reached, "no page reaches into a media directory; this measures nothing"
    unmade = [path for path in reached if path not in missing and not path.parent.is_dir()]
    assert unmade == []


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

    ⚠️ **Media is excluded HERE and nowhere else now.** This clause is about the
    site holding together — a reader can get from any page to any other and to
    the bundle — and it was true before the media copy existed and stays true
    independently of it. ⭐ Media's own clause is `SF-37`'s, below, and it is
    asserted over the whole population rather than as an exception carved here.
    """
    write_site(FIXTURES / name, tmp_path)

    dangling = []
    for page in sorted(tmp_path.rglob("*.html")):
        for reference in references_in(page.read_text(encoding="utf-8")):
            if any(f"{kind}/" in reference for kind in UNIT_MEDIA_DIRNAMES):
                continue
            if not landing(page, reference).exists():
                dangling.append((page.relative_to(tmp_path).as_posix(), reference))
    assert dangling == []


def dangling_in(out) -> set:
    """Every reference a built site emits that lands on nothing, as output-root paths.

    ⭐ Resolved to a path relative to the output root rather than kept as the
    page-relative href, so the answer can be compared with what the build
    *said* it could not write.
    """
    return {
        landing(page, reference).relative_to(out.resolve())
        for page in sorted(out.rglob("*.html"))
        for reference in references_in(page.read_text(encoding="utf-8"))
        if not landing(page, reference).exists()
    }


def test_the_media_bearing_fixture_emits_no_reference_that_dangles(tmp_path):
    """⛔ `SF-37`'s Acceptance, verbatim, on the fixture it names.

    ⭐ *"Every `src` and `href` a built page emits resolves to a file the build
    wrote"* — and after the copy the population it is asserted over is **empty**,
    which is the strongest form the clause has. ⚠️ The `SF-28` test this replaces
    asserted the opposite and said it would go red the day this landed.
    """
    written = write_site(FIXTURES / "depth1", tmp_path)

    assert dangling_in(tmp_path) == set()
    assert written.missing == ()
    assert written.media, "the depth-1 fixture is the media-bearing one"


@pytest.mark.parametrize("name", BOTH)
def test_every_reference_that_DOES_dangle_is_one_the_build_NAMED_missing(tmp_path, name):
    """⛔ The clause in both directions, and the remainder has an owner.

    ⭐ `depth2`'s third unit carries `media_skipped: true` — *"an ingest that
    named media and deliberately did not fetch it"* — so its page reaches for
    three files that are on no disk anywhere, and no copy can produce one. ⛔ The
    build **names** each of them, and this asserts the two sets are the same set:
    nothing dangles that was not named, and nothing is named that resolves.
    """
    written = write_site(FIXTURES / name, tmp_path)

    assert dangling_in(tmp_path) == set(written.missing)


@pytest.mark.parametrize("name", BOTH)
def test_every_media_file_the_build_wrote_sits_where_the_page_addresses_it(tmp_path, name):
    """⭐ The other half: no file is copied that no page reaches for."""
    written = write_site(FIXTURES / name, tmp_path)

    addressed = {
        landing(page, reference).relative_to(tmp_path.resolve())
        for page in sorted(tmp_path.rglob("*.html"))
        for reference in references_in(page.read_text(encoding="utf-8"))
    }
    assert set(written.media) <= addressed


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
def test_a_second_build_replaces_its_own_output_and_refuses_nothing(tmp_path, name):
    """⛔ The row's whole point. ⭐ This asserted the OPPOSITE before the
    footprint: a second run refused every path and produced no site."""
    first = write_site(FIXTURES / name, tmp_path)

    second = write_site(FIXTURES / name, tmp_path)

    assert second.refused == ()
    assert sorted(second.paths) == sorted(first.paths)
    assert sorted(second.replaced) == sorted(first.paths)


def test_a_rebuild_after_the_material_changed_carries_the_change_onto_the_page(tmp_path):
    """⛔ The acceptance the decision is FOR, measured through the BYTES.

    ⚠️ A run that recorded `replaced` for every path while leaving the disk
    alone would pass every clause above this one.
    """
    root = a_corpus(tmp_path, "depth1")
    out = an_output(tmp_path)
    lesson = root / "archive/depth-one/raw/prose/unit-01/lesson-1.json"
    write_site(root, out)
    page = next(path for path in planned("depth1") if "unit-01" in path)
    assert "one breath" in (out / page).read_text(encoding="utf-8")

    lesson.write_text(
        lesson.read_text(encoding="utf-8").replace("one breath", "a single breath"),
        encoding="utf-8",
    )
    write_site(root, out)

    after = (out / page).read_text(encoding="utf-8")
    assert "a single breath" in after
    assert "one breath" not in after


def test_a_readers_own_file_OUTSIDE_the_footprint_survives_byte_for_byte(tmp_path):
    """⛔ The other half of the decision, over the whole site: R3 still protects
    everything the plan did not declare, absolutely."""
    out = an_output(tmp_path)
    mine = b"a reader's own file"
    (out / ".studyforge").mkdir(parents=True)
    for at in ("notes.txt", "README.md", ".studyforge/NOTES.md"):
        (out / at).write_bytes(mine)

    write_site(FIXTURES / "depth1", out)
    write_site(FIXTURES / "depth1", out)

    for at in ("notes.txt", "README.md", ".studyforge/NOTES.md"):
        assert (out / at).read_bytes() == mine, at


def test_a_directory_standing_where_a_declared_page_belongs_is_refused_by_name(tmp_path):
    """⛔ Replacing this build's own file is a write; removing a tree is a
    deletion. ⭐ The only whole-site refusal the footprint leaves standing on a
    path the plan DOES declare, and it is still named."""
    corpus = read_corpus(FIXTURES / "depth1")
    out = an_output(tmp_path)
    (out / corpus.shared.root_index).mkdir(parents=True)

    written = write_site(FIXTURES / "depth1", out)

    assert corpus.shared.root_index in written.refused
    assert (out / corpus.shared.root_index).is_dir()


def test_root_index_alone_rebuilds_the_same_way(tmp_path):
    corpus = read_corpus(FIXTURES / "depth1")
    first = root_index(corpus, tmp_path)

    second = root_index(corpus, tmp_path)

    assert first.pages == (corpus.shared.root_index,)
    assert second.pages == first.pages
    assert second.replaced == first.pages
    assert second.refused == ()


def test_a_pass_handed_a_corpus_with_no_footprint_still_refuses(tmp_path):
    """⛔ `Corpus.footprint` defaults to owning nothing, so a corpus assembled
    by hand — or one whose plan refused — gets R3's floor, never a licence."""
    import dataclasses

    from studyforge.generate import Footprint

    corpus = read_corpus(FIXTURES / "depth1")
    floored = dataclasses.replace(corpus, footprint=Footprint())
    root_index(floored, tmp_path)

    second = root_index(floored, tmp_path)

    assert second.pages == ()
    assert second.refused == (corpus.shared.root_index,)
