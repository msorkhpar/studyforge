"""Mirror of `src/studyforge/generate/containers.py` (R12).

⭐ The `create ….section.html` lines in `tests/fixtures/golden/*.plan.txt` are
what `studyforge plan` says a build will write; this module asserts the container
pass writes exactly those.
"""

from __future__ import annotations

import re

import pytest

from studyforge.generate import container_pages, page_paths, read_corpus
from tests.studyforge.generate.corpora import (
    BOTH,
    FIXTURES,
    an_output,
    planned,
    with_a_unit_missing,
)


def a_page(tmp_path, name: str, which: int = 0) -> tuple[str, str]:
    corpus = read_corpus(FIXTURES / name)
    written = container_pages(corpus, tmp_path)
    at = sorted(written.pages)[which]
    return at.as_posix(), (tmp_path / at).read_text(encoding="utf-8")


def hrefs_in(body: str) -> list[str]:
    # ⚠️ An in-page fragment is not a page the build writes: since `W362` every
    # page opens with a skip link to its own `#content`.
    return [href for href in re.findall(r'href="([^"]*)"', body) if not href.startswith("#")]


# --------------------------------------------------------------------------
# ⭐ the paths
# --------------------------------------------------------------------------


@pytest.mark.parametrize("name", BOTH)
def test_exactly_the_container_pages_the_plan_declared_are_written(tmp_path, name):
    written = container_pages(read_corpus(FIXTURES / name), tmp_path)

    assert sorted(page.as_posix() for page in written.pages) == planned(name, ".section.html")
    assert written.refused == ()


@pytest.mark.parametrize("name", BOTH)
def test_page_paths_names_one_page_per_container_map_and_none_above_it(tmp_path, name):
    corpus = read_corpus(FIXTURES / name)

    paths = page_paths(corpus)

    assert set(paths) == {container.address.key for _, container in corpus.maps}
    assert sorted(path.as_posix() for path in paths.values()) == planned(name, ".section.html")


# --------------------------------------------------------------------------
# ⭐ what the page says
# --------------------------------------------------------------------------


def test_a_container_is_called_by_the_corpus_own_deepest_word(tmp_path):
    """⛔ R1: the word for the depth is the corpus's own, never this framework's.

    ⭐ `depth2` declares `["section", "module"]`, so its container pages say
    *module* and never *section*.
    """
    corpus = read_corpus(FIXTURES / "depth2")
    assert corpus.manifest.levels == ("section", "module")

    _, body = a_page(tmp_path, "depth2")

    identity = re.search(r"<h1>[^<]*</h1>\s*<p>([^<]*)</p>", body)
    assert identity is not None, "the page carries R4's identity line"
    # ⚠️ `W362`: the line is a sentence now (`2 units in this module`), so the
    # corpus's word is found in it rather than read off its front.
    assert re.search(r"\bmodule\b", identity.group(1))
    assert "section" not in identity.group(1)


def test_a_container_map_shallower_than_the_corpus_is_refused_before_it_gets_here():
    """⭐ The premise that makes `levels[-1]` the only reachable word.

    ⛔ Measured rather than assumed: a plant swapping `levels[-1]` for
    `levels[depth - 1]` was GREEN on both fixtures, because a container address
    is always exactly `manifest.depth` deep. ⚠️ This is what makes that true, and
    it is a behaviour rather than a convention — if it stops holding, the two
    spellings diverge and this test is where that is noticed.
    """
    import json

    from studyforge.address import AddressError
    from studyforge.corpus.container import parse as parse_container

    corpus = read_corpus(FIXTURES / "depth2")
    where, container = corpus.maps[0]
    assert container.address.depth == len(corpus.manifest.levels) == 2

    document = json.loads((FIXTURES / "depth2" / where).read_text(encoding="utf-8"))
    document["address"] = document["address"][:1]

    # ⚠️ `AddressError` and not `ContainerError`, which the container package's
    # contract does not name as something `parse` raises — `SF-28/1`.
    with pytest.raises(AddressError):
        parse_container(json.dumps(document), where, corpus.manifest)


@pytest.mark.parametrize("name", BOTH)
def test_every_unit_the_container_declares_is_listed_in_declared_order(tmp_path, name):
    corpus = read_corpus(FIXTURES / name)
    written = container_pages(corpus, tmp_path)

    for at, (_, container) in zip(
        sorted(written.pages),
        sorted(corpus.maps, key=lambda pair: pair[1].address.key),
        strict=True,
    ):
        body = (tmp_path / at).read_text(encoding="utf-8")
        for unit in container.units:
            assert unit.title in body


@pytest.mark.parametrize("name", BOTH)
def test_every_link_on_a_container_page_lands_on_a_page_the_build_writes(tmp_path, name):
    from studyforge.generate import write_site

    write_site(FIXTURES / name, tmp_path)
    for at in planned(name, ".section.html"):
        body = (tmp_path / at).read_text(encoding="utf-8")
        page = tmp_path / at
        assert hrefs_in(body), "a container page is its list of units"
        for href in hrefs_in(body):
            assert (page.parent / href).resolve().is_file(), f"{at} -> {href}"


def test_a_unit_with_no_material_is_listed_without_a_link(tmp_path):
    """⛔ §7's third state, and `render.container` refuses to treat it as a fault."""
    root = with_a_unit_missing(tmp_path / "in", "depth1", "archive/depth-one/raw/prose/unit-02")
    corpus = read_corpus(root)
    out = an_output(tmp_path)

    written = container_pages(corpus, out)
    body = (out / written.pages[0]).read_text(encoding="utf-8")

    assert corpus.absent == {"depth-one/unit-02"}
    assert "Reading a small graph" in body, "the unit is still listed"
    assert not [href for href in hrefs_in(body) if "reading-a-small-graph" in href]
    assert [href for href in hrefs_in(body) if "what-a-triple-is" in href]


# --------------------------------------------------------------------------
# ⛔ R3
# --------------------------------------------------------------------------


def test_a_container_page_the_plan_declared_is_replaced_on_a_rebuild(tmp_path):
    corpus = read_corpus(FIXTURES / "depth1")
    first = container_pages(corpus, tmp_path)
    target = tmp_path / first.pages[0]
    target.write_bytes(b"the previous run's answer")

    second = container_pages(corpus, tmp_path)

    assert second.pages == first.pages
    assert second.replaced == first.pages
    assert second.refused == ()
    assert target.read_bytes() != b"the previous run's answer"


def test_a_directory_where_a_container_page_belongs_is_still_named_and_left_alone(tmp_path):
    """⛔ The refusal the footprint does NOT dissolve: nothing here deletes."""
    corpus = read_corpus(FIXTURES / "depth1")
    first = container_pages(corpus, an_output(tmp_path, "second"))
    out = an_output(tmp_path)
    (out / first.pages[0]).mkdir(parents=True)

    written = container_pages(corpus, out)

    assert written.refused == first.pages
    assert written.pages == ()
    assert (out / first.pages[0]).is_dir()
