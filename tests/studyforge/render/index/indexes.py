"""The root index of both FND-04 fixtures, built the way a build would.

⛔ **Imported, never copied.** Six test modules render these pages and a seventh
regenerates the goldens; seven spellings of "turn two contents documents into a
page" is seven places to forget when the renderer's signature changes.

⭐ **The cases are DERIVED from the fixture corpora, not listed.** `depth1`
declares one container at depth 1 and `depth2` declares two at depth 2, and both
facts are read out of the fixtures rather than written here.

⛔ **The last unit in reading order has NO page on this machine**, deliberately
and in both cases. §7 has three states and two of them are visible in a rendered
row — linked, and listed with `data-readable="false"` — so a golden in which
every unit was present would pin only one of them, and the `href=None` branch
would be exercised by nothing that is committed.

⚠️ **Every href here is computed by the renderer**, never spelled: `Entry.page`
comes out of the fixture's own contents document, which was written under that
corpus's placement profile — `depth1` is `tree` and `depth2` is `sibling` — so
the two answer differently and neither is typed in this file.

Rewrite the goldens after a deliberate change to the page with:

    docker/dev/check env PYTHONPATH=src:. \
        python3 -m tests.studyforge.render.index.indexes

⚠️ **`PYTHONPATH` is not optional** — `pyproject.toml` puts `src` and `.` on the
path through `[tool.pytest]`, which `python3 -m` never reads.

⚠️ **This is the third regenerator writing into `tests/fixtures/pages/` and none
of the three cleans it**. Each writes named files and none
enumerates the directory, so today they coexist; the day any of them gains a
`glob`-and-delete it silently deletes the other two's evidence.

⚠️ A golden that changes without a deliberate change to the renderer is the R10
failure the test exists to catch — regenerate only once you know which change
you made.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from html.parser import HTMLParser
from pathlib import Path, PurePosixPath

from studyforge.contents import Contents, LocalStatus, build, order, status
from studyforge.corpus.placement import profile_for
from studyforge.render.index import Document, Placement, from_contents, render
from tests.studyforge.contents.corpora import (
    a_container,
    a_manifest,
    fixture_contents,
    fixture_manifest,
)
from tests.support import repository_root

#: Where the committed goldens live. ⚠️ Under `tests/fixtures/` because the
#: repository's ignore rules exempt exactly that tree from the build-output
#: patterns that would otherwise swallow a generated page.
GOLDEN_DIR = repository_root() / "tests" / "fixtures" / "pages"

#: The two FND-04 fixture corpora, in a stated order. ⛔ A tuple rather than a
#: directory walk, so the suite's own list does not depend on filesystem
#: order (R10).
FIXTURES = ("depth1", "depth2")

#: What a fixture's golden index is called. ⚠️ Not `index.html`: three corpora's
#: indexes share one directory here, and the one `index.html` in a generated
#: site is at that site's own root.
GOLDEN_SUFFIX = ".index.html"

#: A path shaped like the one thing R7 exists for, for the tests that need a
#: refusal to prove it does not echo what it refused. ⛔ Written as FRAGMENTS and
#: joined, because a real home path written whole into a tracked file is a
#: finding against that file — by the very sweep this constant is here to
#: exercise. `docs/conventions/personal-data-shapes.md` uses the same technique
#: for the same reason, and `jane` is nobody.
A_HOME_PATH = "".join(("/", "home/jane/material/one.unit.html"))


@dataclass(frozen=True)
class Case:
    """One fixture corpus's root index, ready to render, and its golden.

    `contents` and `local` are kept beside the document so a test can assert
    against the corpus's own declarations — the reading order, the keys, the
    recorded page paths — rather than against a shape the test spelled itself.
    """

    name: str
    contents: Contents
    status: LocalStatus
    document: Document
    placement: Placement

    @property
    def golden(self) -> Path:
        """The committed page for this case."""
        return GOLDEN_DIR / f"{self.name}{GOLDEN_SUFFIX}"

    @property
    def absent(self) -> str:
        """The one declared unit key this machine has no page for."""
        return order(self.contents)[-1].key

    def targets(self) -> dict[str, PurePosixPath]:
        """Where the contents record each declared unit's page, by key."""
        return {entry.key: entry.page for entry in order(self.contents)}

    def render(self) -> bytes:
        """The page, exactly as a build would write it."""
        return render(self.document, self.placement)


def cases() -> tuple[Case, ...]:
    """The root index of both fixture corpora, in fixture order."""
    return tuple(case(name) for name in FIXTURES)


def case(name: str) -> Case:
    """The root index one fixture corpus's two documents produce."""
    contents = fixture_contents(name)
    here = a_status(contents)
    where = placement_for(name)
    return Case(
        name=name,
        contents=contents,
        status=here,
        document=from_contents(contents, here, where),
        placement=where,
    )


def placement_for(name: str) -> Placement:
    """Where one fixture corpus's root index sits, under that corpus's own profile."""
    return Placement(shared=profile_for(fixture_manifest(name).placement).corpus())


def a_status(contents: Contents, absent: int = 1) -> LocalStatus:
    """This machine's status for `contents`, with the last `absent` units missing.

    ⛔ Built through the real `contents.status`, so the digest that `join`
    refuses a stale pair on is the real one and a test cannot accidentally
    assert against a pair no build could produce.
    """
    walked = order(contents)
    present = [entry.key for entry in walked[: len(walked) - absent]]
    return status(contents, present)


@dataclass(frozen=True)
class Row:
    """One element carrying an `id`, and the disclosures standing between it and the page.

    ⛔ **The ancestors are what a deep link has to get through**, so they are
    read out of the rendered markup by a real parser rather than inferred from
    the string — an assertion built from the same f-strings the renderer uses
    would agree with a renderer that nested nothing at all.
    """

    id: str
    tag: str
    ancestors: tuple[tuple[str, bool], ...] = ()

    @property
    def reachable_without_opening_anything(self) -> bool:
        """Whether every disclosure above this row already renders open."""
        return all(is_open for _, is_open in self.ancestors)


class _Rows(HTMLParser):
    """Collect every `id` in a page, with the `<details>` chain enclosing it."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.found: dict[str, Row] = {}
        self._open: list[tuple[str, bool]] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        seen = dict(attrs)
        where = seen.get("id")
        if where is not None:
            self.found[where] = Row(id=where, tag=tag, ancestors=tuple(self._open))
        if tag == "details":
            self._open.append((where or "", "open" in seen))

    def handle_endtag(self, tag: str) -> None:
        if tag == "details" and self._open:
            self._open.pop()


@dataclass(frozen=True)
class Planted:
    """A corpus built to a stated shape, for the tests that need one bigger than a fixture."""

    contents: Contents
    document: Document
    placement: Placement
    shape: tuple[int, ...] = field(default=())

    def render(self) -> bytes:
        """The page this corpus's two documents produce."""
        return render(self.document, self.placement)


def planted(shape: tuple[int, ...], *, absent: int = 0) -> Planted:
    """Build a corpus of exactly `shape` — containers per level, then units per container.

    ⭐ **The fixtures are small on purpose and a corpus that outgrows the budget
    is what the open/closed policy exists for**, so the shape that exercises it
    is declared here as a number rather than found by hoping a fixture grows.
    ⛔ Built through the real manifest and container readers, so the tree it
    produces is one a corpus could actually declare.
    """
    levels = [f"level-{depth}" for depth in range(1, len(shape))]
    manifest = a_manifest(levels=levels)
    units = [{"n": n, "title": f"Unit {n}", "practices": 0} for n in range(1, shape[-1] + 1)]
    containers = tuple(
        a_container(manifest, address, tuple(f"Title {part}" for part in address), units=units)
        for address in _addresses(shape[:-1])
    )
    contents = build(manifest, containers)
    local = a_status(contents, absent=absent) if absent else status(contents, _every(contents))
    where = Placement(shared=profile_for(manifest.placement).corpus())
    return Planted(
        contents=contents,
        document=from_contents(contents, local, where),
        placement=where,
        shape=shape,
    )


def _addresses(counts: tuple[int, ...]) -> tuple[tuple[str, ...], ...]:
    """Every address a corpus of these per-level counts declares, in declared order."""
    built: tuple[tuple[str, ...], ...] = ((),)
    for depth, how_many in enumerate(counts, start=1):
        built = tuple(
            (*prefix, f"g{depth}-{position:02d}")
            for prefix in built
            for position in range(1, how_many + 1)
        )
    return built


def _every(contents: Contents) -> tuple[str, ...]:
    """Every declared unit key, for a machine that has generated all of them."""
    return tuple(entry.key for entry in order(contents))


def rows(page: str) -> dict[str, Row]:
    """Every element in `page` that carries an `id`, by that id."""
    reader = _Rows()
    reader.feed(page)
    reader.close()
    return reader.found


def regenerate() -> list[Path]:
    """Rewrite every golden from the current renderer, and say which changed."""
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    changed = []
    for built in cases():
        page = built.render()
        if not built.golden.exists() or built.golden.read_bytes() != page:
            built.golden.write_bytes(page)
            changed.append(built.golden)
    return changed


if __name__ == "__main__":  # pragma: no cover - a maintenance entry point
    for path in regenerate() or []:
        print(f"rewrote {path.name}")
