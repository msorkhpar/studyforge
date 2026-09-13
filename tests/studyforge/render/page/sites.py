"""The site a build would write, for both `FND-04` fixtures and one planted shape.

⛔ **Imported, never copied.** `SF-15`'s acceptance is about a SITE — *"prev/next
traverses every unit"* and *"no dangling links anywhere in the generated
output"* are false of a function and true only of a directory of pages — so this
module writes one, and `test_acceptance.py` reads it back.

Run nothing here: it writes under a `tmp_path` a test hands it, never into the
repository.

## ⛔ The caller this stands in for is `SF-28`'s, and saying so is the point

⚠️ **Nothing in `src/` turns two contents documents into a `Links` and a trail
yet.** `bar_for` and `trail_for` are that caller, written here so the clause can
be run today rather than asserted about. ⭐ `W57`'s lesson is why it has to
exist at all: a slot computed in `contents` and dropped in `render` satisfied
both halves of two separate tests, because nothing joined them.

## ⛔ The last declared unit of every corpus here has NO page

⭐ `indexes.a_status`'s deliberate shape, carried so the fixture path and the
planted path have one. ⚠️ It is what makes `Link(href=None)` a **measured** path:
the second-to-last unit's `next` has nowhere to point, and the generated site is
where a guessed href would dangle.

## ⭐ `depth2` crosses a module inside one section, and `crossings` says so apart

⛔ **`W108`**: the fixtures used to cross ONE boundary between them, and it
changed the section and the module at once — so a count of crossings read `1`
and hid that the module-only case was absent. ⭐ `depth2` now carries
`advanced/03-putting-it-together`, and `crossings` classes every boundary by the
levels it changes, so each kind is counted under its own name and never summed.
⚠️ `PLANTED_SHAPE` stays as the one module-only crossing under `tree` placement
(`depth2` is `sibling`), which is a different href shape rather than a duplicate.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

from studyforge.contents import Contents, Entry, Group, build, links, order, status
from studyforge.corpus.placement import ROOT_INDEX_FILENAME, profile_for
from studyforge.render import templates
from studyforge.render.index import Placement as IndexPlacement
from studyforge.render.index import from_contents
from studyforge.render.index import render as render_index
from studyforge.render.page import Crumb, Link, Links, Placement, render
from studyforge.render.pageassets import written_files
from tests.studyforge.contents.corpora import (
    a_container,
    depth2_manifest,
    fixture_containers,
    fixture_contents,
    fixture_manifest,
)
from tests.studyforge.render.page.pages import depth1_unit_02, depth2_unit_01

#: Both `FND-04` fixtures, and the served document each one's pages are rendered
#: from. ⚠️ The body is irrelevant to every clause here — what is under test is
#: where a page POINTS — so one real document per corpus is rendered at every
#: unit's own placement rather than fifteen documents being invented.
FIXTURES = {"depth1": depth1_unit_02, "depth2": depth2_unit_01}

#: How a reference with a fragment splits. ⛔ Named so the link check has one
#: spelling of *"the part a file is found by"*.
FRAGMENT = "#"


@dataclass(frozen=True)
class Site:
    """One fixture corpus, generated to disk, with the facts the checks need.

    `absent` is the set of declared unit keys this machine has no page for,
    `pages` maps every other key to the file that was written, and `where` is the
    placement decision each unit was rendered under. ⛔ `where` is CARRIED rather
    than re-derived from `name`: a check that looked a corpus up by name could
    only ever run against the two fixtures, and half of this module's subject is
    a corpus shape neither fixture has.
    """

    name: str
    root: Path
    contents: Contents
    absent: frozenset[str]
    pages: dict[str, Path]
    where: dict[str, Placement]

    def walked(self) -> tuple[Entry, ...]:
        """Every declared unit, in curriculum order."""
        return order(self.contents)

    def text(self, path: Path) -> str:
        """One generated page, read back as the browser would get it."""
        return path.read_bytes().decode("utf-8")


def origins(name: str) -> dict[str, str | None]:
    """`unit key -> the source file it was ingested from`, from the container maps.

    ⚠️ Read rather than guessed: the `sibling` profile places a page beside its
    origin and refuses a unit that records none, so a placement rebuilt without
    this would not be the placement the contents document was written under.
    """
    return {
        container.address.unit_key(unit.n): unit.origin
        for container in fixture_containers(name)
        for unit in container.units
    }


def placements(name: str, contents: Contents) -> dict[str, Placement]:
    """The placement decision a build would make for every declared unit."""
    profile = profile_for(fixture_manifest(name).placement)
    where = origins(name)
    shared = profile.corpus()
    return {
        entry.key: Placement(
            corpus=contents.corpus,
            unit=profile.unit(entry.address, entry.ordinal, entry.title, origin=where[entry.key]),
            shared=shared,
        )
        for entry in order(contents)
    }


def trail_for(contents: Contents, entry: Entry, index_href: str) -> tuple[Crumb, ...]:
    """The crumbs for one unit: the corpus, every container above it, then itself.

    ⛔ **Every label comes out of the contents document** — `Contents.title`,
    `Group.level` (which is `manifest.levels[d]`) and `Group.title` — and not one
    of them is spelled here, which is the clause *"read from data"*.

    ⚠️ **Every container crumb is `href=None`, and that is `SF-14/3` showing up
    from the page's side**: `contents.Group` carries no container page name, so
    nothing that reads only the two contents documents can address a container
    page. ⭐ The trail lists those steps rather than dropping them, which is why
    the hole is visible on the page instead of being invisible.
    """
    return (
        Crumb("", contents.title, index_href),
        *(Crumb(group.level, group.title) for group in ancestors(contents, entry.key)),
        Crumb("", entry.title),
    )


def ancestors(contents: Contents, key: str) -> tuple[Group, ...]:
    """The groups enclosing the unit `key` names, outermost first."""
    for group in contents.groups:
        found = _descend(group, key)
        if found is not None:
            return found
    return ()


def _descend(group: Group, key: str) -> tuple[Group, ...] | None:
    """`group` and what is under it, when the unit is in there."""
    if any(entry.key == key for entry in group.entries):
        return (group,)
    for child in group.groups:
        deeper = _descend(child, key)
        if deeper is not None:
            return (group, *deeper)
    return None


def bar_for(site: Site, entry: Entry) -> Links:
    """The bar for one unit, with a declared absence wherever a page is missing.

    ⛔ This is the one decision standing in for `SF-28`: a neighbour the corpus
    declares but this machine has no page for is handed as `Link(href=None,
    key=…)`, never as the href the contents computed for it. ⚠️ Passing that href
    would be the *guessed href for a page that does not exist* — the one failure
    neither of Ruling 164's policies catches, and the one this clause is about.
    """
    computed = links(site.contents, entry.key)
    slots: dict[str, Link] = {}
    for field in ("previous", "next"):
        if field not in computed:
            continue
        target = _key_at(site, field, entry.key)
        if target in site.absent:
            slots[field] = Link(None, computed[field]["label"], target)
        else:
            slots[field] = Link(computed[field]["href"], computed[field]["label"], target)
    slots["index"] = Link(computed["index"]["href"], computed["index"]["label"])
    return Links(**slots)


def _key_at(site: Site, field: str, key: str) -> str:
    """The key of `key`'s previous or next unit in curriculum order."""
    walked = [entry.key for entry in site.walked()]
    at = walked.index(key)
    return walked[at - 1] if field == "previous" else walked[at + 1]


def assemble(
    name: str,
    contents: Contents,
    where: dict[str, Placement],
    document: dict,
    root: Path,
) -> Site:
    """Write one corpus's whole site under `root`, and say what is in it.

    ⛔ The root index comes from the shipped assembler and the shipped renderer
    (`render.index.from_contents`, `render.index.render`), so the anchors a
    fallback lands on are the real page's anchors and not a shape this module
    agreed with itself about.

    ⚠️ **The last declared unit has no page**, which is `indexes.a_status`'s own
    rule carried here so the fixture path and the planted path have one shape.
    """
    walked = order(contents)
    absent = frozenset({walked[-1].key})
    local = status(contents, [entry.key for entry in walked if entry.key not in absent])
    index_at = IndexPlacement(shared=next(iter(where.values())).shared)

    root.mkdir(parents=True, exist_ok=True)
    (root / ROOT_INDEX_FILENAME).write_bytes(
        render_index(from_contents(contents, local, index_at), index_at)
    )
    assets = root / str(index_at.shared.assets)
    assets.mkdir(parents=True, exist_ok=True)
    for filename, body in written_files().items():
        (assets / filename).write_text(body, encoding="utf-8")

    site = Site(name=name, root=root, contents=contents, absent=absent, pages={}, where=where)
    for entry in walked:
        if entry.key in absent:
            continue
        placement = where[entry.key]
        target = root / str(placement.unit.page)
        target.parent.mkdir(parents=True, exist_ok=True)
        index_href = links(contents, entry.key)["index"]["href"]
        target.write_bytes(
            render(
                document,
                placement,
                bar_for(site, entry),
                trail_for(contents, entry, index_href),
            )
        )
        site.pages[entry.key] = target
    return site


def a_site(name: str, root: Path) -> Site:
    """One `FND-04` fixture corpus, generated as a site."""
    contents = fixture_contents(name)
    return assemble(name, contents, placements(name, contents), FIXTURES[name]().document, root)


#: ⭐ **Two modules inside one section, under `tree` placement.** `SF-15`'s local
#: discharge of `SF-15/6`, written when no fixture had the shape. ⚠️ Kept after
#: `W108` because `depth2`, which now has it, is `sibling`: the two profiles
#: address a neighbouring module with different hrefs.
PLANTED_SHAPE = (("one", "01-first"), ("one", "02-second"), ("two", "03-third"))


def a_planted_site(root: Path) -> Site:
    """A two-level corpus with two modules in one section, generated as a site.

    ⚠️ Built through the real readers (`corpus.manifest.parse`,
    `corpus.container.parse`) and the real builder, so it is a corpus rather than
    a shape this module agreed with itself about — `tests.…contents.corpora`
    exists for exactly this and is imported rather than re-spelled.
    """
    manifest = depth2_manifest(placement="tree")
    containers = tuple(
        a_container(manifest, (section, module), [section.title(), module], units=None)
        for section, module in PLANTED_SHAPE
    )
    contents = build(manifest, containers)
    profile = profile_for(manifest.placement)
    shared = profile.corpus()
    where = {
        entry.key: Placement(
            corpus=contents.corpus,
            unit=profile.unit(entry.address, entry.ordinal, entry.title),
            shared=shared,
        )
        for entry in order(contents)
    }
    return assemble("planted", contents, where, FIXTURES["depth1"]().document, root)


def followed(page: PurePosixPath, reference: str) -> str:
    """Where a browser lands, following `reference` from the page that carries it.

    ⛔ No filesystem: this is URL arithmetic, and resolving against the process's
    working directory would make the answer a property of where the tests ran.
    """
    parts = list(page.parent.parts)
    for part in reference.split("/"):
        if part == "..":
            parts.pop()
        elif part not in ("", "."):
            parts.append(part)
    return "/".join(parts)


def slot(body: str, relation: str) -> str:
    """The href of one slot of the rendered bar. ⛔ Raises when it is not there."""
    found = re.search(rf'<a rel="{relation}" href="([^"]*)"', body)
    assert found is not None, f"the bar carries no {relation!r} slot"
    return found.group(1)


def has_slot(body: str, relation: str) -> bool:
    """Whether the rendered bar carries this slot at all."""
    return f'rel="{relation}"' in body


def boundaries(site: Site) -> list[tuple[str, str]]:
    """Every consecutive pair of units whose enclosing container differs."""
    walked = site.walked()
    return [
        (before.key, after.key)
        for before, after in zip(walked, walked[1:], strict=False)
        if ancestors(site.contents, before.key) != ancestors(site.contents, after.key)
    ]


#: How a crossing's changed levels are joined into its kind, outermost first.
LEVEL_JOIN = "+"


def crossings(site: Site) -> dict[str, int]:
    """Every boundary, counted under the container levels it changes.

    ⛔ **Counted apart, never summed** (`W108`). A crossing that changes the
    section and the module is kind `section+module`; one that changes the module
    inside one section is kind `module`. ⚠️ A single total read `1` for a set
    whose only crossing was the compound one, and that is what hid the gap. The
    level words are the corpus's own (`Group.level`), not this module's.
    """
    found: dict[str, int] = {}
    for before, after in boundaries(site):
        was, now = ancestors(site.contents, before), ancestors(site.contents, after)
        changed = [old.level for old, new in zip(was, now, strict=True) if old.key != new.key]
        kind = LEVEL_JOIN.join(changed)
        found[kind] = found.get(kind, 0) + 1
    return found


def depth_of(site: Site, key: str) -> tuple[str, ...]:
    """The keys of the containers above one unit, outermost first."""
    return tuple(group.key for group in ancestors(site.contents, key))


def crumbs_on(body: str) -> list[str]:
    """The text of each crumb of the rendered trail, in order.

    ⛔ The separator is removed by asking the template for it, never by naming the
    glyph here: a test that spelled `›` itself would be the second place the
    framework's punctuation is decided, which is the R13 defect one layer out.
    """
    region = re.search(r'<nav aria-label="Breadcrumb">(.*?)</nav>', body, re.DOTALL)
    if region is None:
        return []
    separator = templates.fill("crumb-separator.html")
    return [
        re.sub(r"\s+", " ", re.sub(r"<[^>]*>", " ", row.replace(separator, ""))).strip()
        for row in re.findall(r"<li[^>]*>(.*?)</li>", region.group(1), re.DOTALL)
    ]


class _Ids(HTMLParser):
    """Every `id` one generated page carries."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: set[str] = set()

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        where = dict(attrs).get("id")
        if where is not None:
            self.found.add(where)


def ids_in(body: str) -> set[str]:
    """The anchors a page offers, read by a real parser rather than by a regex."""
    parser = _Ids()
    parser.feed(body)
    return parser.found


def generated(site: Site) -> dict[str, Path]:
    """Every page the site holds, by its path relative to the site root."""
    found = {
        entry.page.as_posix(): site.pages[entry.key]
        for entry in site.walked()
        if entry.key in site.pages
    }
    index = site.root / ROOT_INDEX_FILENAME
    if index.exists():
        found[ROOT_INDEX_FILENAME] = index
    return found


def references_in(body: str) -> list[str]:
    """Every local `href` and `src` the page carries, absolute URLs excluded."""
    return [
        reference
        for reference in re.findall(r'(?:src|href)="([^"]*)"', body)
        if "://" not in reference and not reference.startswith("mailto:")
    ]


def dangling_in(site: Site) -> list[str]:
    """Every local reference in the site that goes nowhere, named.

    ⛔ **Two ways to dangle and both are checked**: a path that lands on no file,
    and a fragment the target page does not offer. ⚠️ The second is the one a
    path check alone reads as green, and it is exactly what a fallback pointing
    at a key the index never listed would be.
    """
    found = []
    for where, path in sorted(generated(site).items()):
        for reference in references_in(site.text(path)):
            head, _, fragment = reference.partition(FRAGMENT)
            landed = followed(PurePosixPath(where), head) if head else where
            target = site.root / landed
            if not target.exists():
                if not _inside_the_units_own_media(site, landed):
                    found.append(f"{where} -> {reference} (no such file)")
            elif fragment and fragment not in ids_in(site.text(target)):
                found.append(f"{where} -> {reference} (no such anchor)")
    return found


def _inside_the_units_own_media(site: Site, landed: str) -> bool:
    """Whether a missing target is one of a unit's own media files.

    ⚠️ Media are written by the media step, never by the renderer. What matters
    is that such an href lands inside a unit's own media directories rather than
    anywhere else — the same allowance `test_init`'s `file://` check makes.
    """
    return any(
        PurePosixPath(landed).is_relative_to(PurePosixPath(str(directory)))
        for placement in site.where.values()
        for directory in placement.unit.directories
    )
