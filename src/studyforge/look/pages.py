"""Which pages of a built site to look at, and where each picture of one goes.

**What it does.** Reads a built site's pages the way discovery reads them — the
root index, then every container and unit page by its suffix, of those a link
from the root index reaches or that list only such pages — and chooses the
ones a look covers: a sample of one page of each kind, every page, or the pages a
reader names.

**How you use it.**

    chosen = choose(site, named=(), every=False)   # index, a container, a unit
    for n, page in enumerate(chosen, 1):
        png, dom = outputs(out, n, page)

**Depends on.** `studyforge.corpus.discovery` for the page population and
`studyforge.corpus.placement` for the root index's one name; the standard
library's HTML parser for the links. ⛔ Not on `render`,
`generate` or `serve`: a look reads what a build wrote and nothing else.

## ⛔ Every page means every page the site LINKS

⭐ **The built site is what its root index reaches.** A site is often a corpus
root, and a corpus root also holds git-ignored scratch, a plant or an old build
under another name, each of them a file with a page's suffix (ISO-37/3). So
`--all` follows the links from the root index, page to page, and looks at a
discovered page only when a link reaches it, or when every page it links is
one a link reaches (a flat corpus's container page, which nothing links). A
copy of a page in scratch links pages that are not beside it, so it is never
looked at, whatever its suffix.

## ⛔ A named page must be a page of THIS site

A name is resolved against the site and refused when it leaves it or names no
file. ⛔ The refusal never quotes the name back (R7): a name that leaves the site
is, more often than not, an absolute path on somebody's machine.
"""

from __future__ import annotations

from html.parser import HTMLParser
from pathlib import Path, PurePosixPath
from urllib.parse import unquote, urlsplit

from studyforge.corpus.discovery import PAGE_SUFFIXES, pages
from studyforge.corpus.placement import ROOT_INDEX_FILENAME


class LookRefused(Exception):
    """The look cannot start: the site, a named page or the output is not usable."""


def site_pages(site: Path) -> tuple[PurePosixPath, ...]:
    """Every page of the site, relative to it: the root index first, then discovery's order.

    ⛔ Only a page a link from the root index reaches is one of the site's pages.
    """
    if not (site / ROOT_INDEX_FILENAME).is_file():
        raise LookRefused(
            f"the site directory holds no {ROOT_INDEX_FILENAME} at its root, so it is not a "
            f"built site; pass the directory `studyforge build --out` wrote"
        )
    root = PurePosixPath(ROOT_INDEX_FILENAME)
    inside = site.resolve()
    reached = _reached(inside, root)
    found = [PurePosixPath(path.relative_to(site).as_posix()) for path in pages(site)]
    return (root, *(page for page in found if _of_the_site(inside, page, reached)))


def _of_the_site(inside: Path, page: PurePosixPath, reached: frozenset[PurePosixPath]) -> bool:
    """Whether `page` is one of the site's: reached, or a listing of reached pages only.

    ⭐ A container page no link reaches (a flat corpus's one container) still
    belongs to the site when every page it links is one the index reaches. A
    copy of any page moved into scratch links pages that are not there, so it
    never qualifies.
    """
    if page in reached:
        return True
    targets = [_target(inside, page, href) for href in _hrefs(inside / page)]
    return bool(targets) and all(target in reached for target in targets)


class _Links(HTMLParser):
    """Collects every `<a href>` of one page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.hrefs: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "a":
            self.hrefs += [value for name, value in attrs if name == "href" and value]


def _hrefs(path: Path) -> list[str]:
    """Every relative link to an `.html` file that the page at `path` holds."""
    links = _Links()
    links.feed(path.read_text("utf-8", errors="replace"))
    return [href for href in links.hrefs if _page_link(href)]


def _page_link(href: str) -> bool:
    parts = urlsplit(href)
    return not parts.scheme and not parts.netloc and parts.path.endswith(".html")


def _reached(inside: Path, start: PurePosixPath) -> frozenset[PurePosixPath]:
    """Every page inside the site a chain of links from `start` reaches, `start` included."""
    seen = {start}
    todo = [start]
    while todo:
        page = todo.pop()
        for href in _hrefs(inside / page):
            target = _target(inside, page, href)
            if target is not None and target not in seen:
                seen.add(target)
                todo.append(target)
    return frozenset(seen)


def _target(inside: Path, page: PurePosixPath, href: str) -> PurePosixPath | None:
    """Return the site page a relative page link names, or `None` when it names none."""
    path = (inside / page.parent / unquote(urlsplit(href).path)).resolve()
    if not path.is_relative_to(inside) or not path.is_file():
        return None
    return PurePosixPath(path.relative_to(inside).as_posix())


def choose(site: Path, named: tuple[str, ...], every: bool) -> tuple[PurePosixPath, ...]:
    """Return the pages to look at, in the order they are looked at.

    ⭐ With nothing named and `every` false: the root index, the first container
    page and the first unit page — one of each kind a build writes.
    """
    everything = site_pages(site)
    if named:
        return tuple(_named(site, name) for name in named)
    if every:
        return everything
    sample = [everything[0]]
    for suffix in reversed(PAGE_SUFFIXES):
        first = next((page for page in everything if page.name.endswith(suffix)), None)
        if first is not None:
            sample.append(first)
    return tuple(sample)


def outputs(out: Path, n: int, page: PurePosixPath) -> tuple[Path, Path]:
    """Return where page `n`'s screenshot and DOM go: numbered, so no two pages share one."""
    stem = f"{n:02d}-{page.name.removesuffix('.html')}"
    return out / f"{stem}.png", out / f"{stem}.dom.html"


def _named(site: Path, name: str) -> PurePosixPath:
    """Resolve one named page against the site, refusing one outside it or absent."""
    path = (site / name).resolve()
    if not path.is_relative_to(site.resolve()) or not path.is_file():
        raise LookRefused(
            "a page named with --page is not a file inside the site; name it relative to "
            "the site directory, as the site's own index links it"
        )
    return PurePosixPath(path.relative_to(site.resolve()).as_posix())
