"""Which pages of a built site to look at, and where each picture of one goes.

**What it does.** Reads a built site's pages the way discovery reads them — the
root index, then every container and unit page by its suffix — and chooses the
ones a look covers: a sample of one page of each kind, every page, or the pages a
reader names.

**How you use it.**

    chosen = choose(site, named=(), every=False)   # index, a container, a unit
    for n, page in enumerate(chosen, 1):
        png, dom = outputs(out, n, page)

**Depends on.** `studyforge.corpus.discovery` for the page population and
`studyforge.corpus.placement` for the root index's one name. ⛔ Not on `render`,
`generate` or `serve`: a look reads what a build wrote and nothing else.

## ⛔ A named page must be a page of THIS site

A name is resolved against the site and refused when it leaves it or names no
file. ⛔ The refusal never quotes the name back (R7): a name that leaves the site
is, more often than not, an absolute path on somebody's machine.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from studyforge.corpus.discovery import PAGE_SUFFIXES, pages
from studyforge.corpus.placement import ROOT_INDEX_FILENAME


class LookRefused(Exception):
    """The look cannot start: the site, a named page or the output is not usable."""


def site_pages(site: Path) -> tuple[PurePosixPath, ...]:
    """Every page of the site, relative to it: the root index first, then discovery's order."""
    if not (site / ROOT_INDEX_FILENAME).is_file():
        raise LookRefused(
            f"the site directory holds no {ROOT_INDEX_FILENAME} at its root, so it is not a "
            f"built site; pass the directory `studyforge build --out` wrote"
        )
    found = [PurePosixPath(ROOT_INDEX_FILENAME)]
    found += [PurePosixPath(path.relative_to(site).as_posix()) for path in pages(site)]
    return tuple(found)


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
