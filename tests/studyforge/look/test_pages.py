"""Mirror of `src/studyforge/look/pages.py` (R12): which pages a look covers."""

from __future__ import annotations

from pathlib import PurePosixPath

import pytest

from studyforge.corpus.discovery import pages
from studyforge.look.pages import LookRefused, choose, outputs, site_pages
from tests.studyforge.look.sites import built


def test_the_default_is_one_page_of_each_kind_a_build_writes(tmp_path):
    site = built(tmp_path)
    chosen = choose(site, (), every=False)
    assert [page.name.split(".", 1)[-1] for page in chosen] == [
        "html",
        "section.html",
        "unit.html",
    ]
    assert chosen[0] == PurePosixPath("index.html")


def test_every_page_is_the_root_index_then_discoverys_own_population(tmp_path):
    site = built(tmp_path)
    everything = choose(site, (), every=True)
    found = [PurePosixPath(path.relative_to(site).as_posix()) for path in pages(site)]
    assert list(everything) == [PurePosixPath("index.html"), *found]
    assert len(found) == 4, "the flat fixture builds one container page and three unit pages"


def test_a_named_page_is_looked_at_and_nothing_else(tmp_path):
    site = built(tmp_path)
    unit = site_pages(site)[-1]
    assert choose(site, (unit.as_posix(),), every=True) == (unit,)


@pytest.mark.parametrize("name", ["../outside.html", "missing.unit.html", "/etc/hostname"])
def test_a_named_page_outside_the_site_or_absent_is_refused_unquoted(tmp_path, name):
    site = built(tmp_path)
    (tmp_path / "outside.html").write_text("<html></html>", encoding="utf-8")
    with pytest.raises(LookRefused) as refused:
        choose(site, (name,), every=False)
    assert name not in str(refused.value)


def test_a_directory_with_no_root_index_is_not_a_built_site(tmp_path):
    with pytest.raises(LookRefused, match="not a built site"):
        site_pages(tmp_path)


def test_each_page_gets_its_own_numbered_pair_of_outputs(tmp_path):
    site = built(tmp_path)
    chosen = choose(site, (), every=True)
    names = [path.name for n, page in enumerate(chosen, 1) for path in outputs(tmp_path, n, page)]
    assert len(names) == len(set(names)) == 2 * len(chosen)
    assert names[:2] == ["01-index.png", "01-index.dom.html"]
