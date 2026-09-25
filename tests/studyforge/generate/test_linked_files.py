"""A built page's links lead where the author meant, on every placement profile.

⭐ **Read off the written page, over the filesystem**, the way a reader opens it
from `file://`: every relative `href` and `src` of every unit page is resolved
from the page's own directory, and a fragment against the ids of the page it
lands on. `unit.mentions` and `validate.links` are mirrored beside their modules;
this is the build's end of the same promise.
"""

from __future__ import annotations

import html.parser
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

import pytest

from studyforge.generate import write_site
from tests.studyforge.generate.corpora import an_output
from tests.studyforge.validate.corpora import LINKED, linked

#: The links of unit 1 that lead somewhere, and none of the four that lead nowhere.
GOOD = LINKED.split(" [gone]")[0]


class _Links(html.parser.HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.refs: list[str] = []
        self.ids: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for name, value in attrs:
            if name == "id" and value:
                self.ids.add(value)
            if name in ("href", "src") and value:
                self.refs.append(value)


def _read(page: Path) -> _Links:
    found = _Links()
    found.feed(page.read_text(encoding="utf-8"))
    return found


def unresolved(root: Path) -> list[str]:
    """Every relative reference of every unit page under `root` that leads nowhere."""
    missing: list[str] = []
    for page in sorted(root.rglob("*.unit.html")):
        for ref in _read(page).refs:
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", ref) or ref.startswith("//"):
                continue
            parts = urlsplit(ref)
            target = (page.parent / unquote(parts.path)).resolve() if parts.path else page
            ok = target.is_relative_to(root.resolve()) and target.is_file()
            if ok and parts.fragment and target.suffix == ".html":
                ok = unquote(parts.fragment) in _read(target).ids
            if not ok:
                missing.append(ref)
    return missing


@pytest.mark.parametrize("placement", ["tree", "sibling"])
def test_a_site_built_into_its_corpus_leads_every_link_somewhere(tmp_path, placement):
    root = linked(tmp_path, placement, GOOD)
    write_site(root, root, narration=False)
    pages = sorted(root.rglob("*.unit.html"))
    assert len(pages) == 2
    assert unresolved(root) == []
    first = pages[0].read_text(encoding="utf-8")
    # ⭐ The file stays where the author put it; nothing is copied beside the page.
    assert sorted(path.name for path in root.rglob("Types.java")) == ["Types.java"]
    assert "Types.java" in first
    # ⭐ The number is served as the heading's words, linking its page and heading.
    assert "Section <a href=" in first
    assert ">Two</a> goes on." in first


@pytest.mark.parametrize("placement", ["tree", "sibling"])
def test_the_crawl_finds_every_link_that_leads_nowhere(tmp_path, placement):
    # ⭐ The crawl above is a reading that can fail: the links that lead nowhere
    # are found by it, on the page as it is written. ⚠️ The rooted one is not
    # there to find: the page refuses a rooted href and prints its words (R8).
    root = linked(tmp_path, placement)
    write_site(root, root, narration=False)
    assert unresolved(root) == ["code/Gone.java", "../../outside.txt", "#no-such-heading"]


def test_a_site_written_elsewhere_keeps_the_author_s_href(tmp_path):
    # ⛔ The file is reached only from beside it; anywhere else the href is the author's.
    root = linked(tmp_path, "tree", GOOD)
    out = an_output(tmp_path)
    written = write_site(root, out, narration=False)
    (page, _) = sorted(out.rglob("*.unit.html"))
    assert 'href="code/Types.java"' in page.read_text(encoding="utf-8")
    # ⭐ And the build names the page whose link it could not keep, once per link.
    assert [out / str(path) for path in written.unreached] == [page]
    # ⛔ Nothing was copied beside the page, and nothing links upward out of the site.
    assert not list(out.rglob("Types.java"))
    body = page.read_text(encoding="utf-8")
    assert [ref for ref in _read_text(body) if "Types.java" in ref] == ["code/Types.java"]


@pytest.mark.parametrize("placement", ["tree", "sibling"])
def test_a_site_written_into_its_corpus_reaches_every_file_and_names_none(tmp_path, placement):
    root = linked(tmp_path, placement, GOOD)
    assert write_site(root, root, narration=False).unreached == ()


@pytest.mark.parametrize("placement", ["tree", "sibling"])
def test_a_link_to_another_unit_s_file_lands_on_the_heading_it_names(tmp_path, placement):
    # ⭐ `two.md#12-two` is unit 2's source and its heading `1.2 Two`: the link
    # keeps the heading, and the crawl checks the id is on the page it lands on.
    root = linked(tmp_path, placement, "See [two's heading](two.md#12-two) and [top](two.md#no).")
    write_site(root, root, narration=False)
    assert unresolved(root) == []
    first = sorted(root.rglob("*.unit.html"))[0].read_text(encoding="utf-8")
    # ⭐ The prose's two links come first; the page's own navigation follows.
    heading, top = [ref for ref in _read_text(first) if ".unit.html" in ref][:2]
    assert heading.endswith(".unit.html#prose-b0")
    # ⛔ A fragment that names no heading of the target is dropped: the top of its page.
    assert top.endswith(".unit.html")


def _read_text(body: str) -> list[str]:
    found = _Links()
    found.feed(body)
    return [ref for ref in found.refs if not ref.startswith(("#", "http"))]
