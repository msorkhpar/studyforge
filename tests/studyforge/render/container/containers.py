"""Every container page of both FND-04 fixtures, built the way a build would.

⛔ **Imported, never copied.** Four test modules render these pages and a fifth
regenerates the goldens; five spellings of "turn a container map into a page" is
five places to forget when the renderer's signature changes.

⭐ **The cases are DERIVED from the fixture corpora, not listed.** `depth1` has
one container and `depth2` has two, and that is a property of the fixtures — a
hand-written list of three would be a second copy of the fixtures' shape, and
the one nobody re-measures when a fixture gains a container.

⚠️ **Every href here is computed by `placement.relative_href`, never spelled.**
`depth1` is `tree` and `depth2` is `sibling`, so a container page addresses its
units with `units/unit-NN/…` in one and with a bare filename in the other —
which is exactly the pair `SF-13/1` and `W57` were about.

Run `python3 -m tests.studyforge.render.container.containers` to rewrite the
goldens after a deliberate change to the page. ⚠️ A golden that changes without
a deliberate change to the renderer is the R10 failure the test exists to catch.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.corpus.container import Container
from studyforge.corpus.manifest import Manifest
from studyforge.corpus.placement import Profile, profile_for, relative_href
from studyforge.render.container import Document, Item, Link, Links, Placement, render
from tests.studyforge.contents.corpora import fixture_containers, fixture_manifest
from tests.support import repository_root

#: Where the committed goldens live. ⚠️ Under `tests/fixtures/` because the
#: repository's ignore rules exempt exactly that tree from `*.section.html`,
#: which is otherwise ignored as build output everywhere.
GOLDEN_DIR = repository_root() / "tests" / "fixtures" / "pages"

#: The two FND-04 fixture corpora, in a stated order. ⛔ A tuple rather than a
#: directory walk, so the suite's own list does not depend on filesystem
#: order (R10).
FIXTURES = ("depth1", "depth2")


@dataclass(frozen=True)
class Case:
    """One fixture container, ready to render, and the golden it is compared against.

    `targets` is where placement said each listed unit's page goes, in item
    order — ⭐ kept beside the document so a test can resolve an href against
    the page that wrote it and compare the answer with the real path, rather
    than against a string the test spelled itself.
    """

    name: str
    document: Document
    placement: Placement
    links: Links
    targets: tuple[PurePosixPath, ...]

    @property
    def golden(self) -> Path:
        """The committed page for this case, named as placement would name it."""
        return GOLDEN_DIR / Path(self.placement.container.page).name

    def render(self) -> bytes:
        """The page, exactly as a build would write it."""
        return render(self.document, self.placement, self.links)


def cases() -> tuple[Case, ...]:
    """Every container of both fixture corpora, in fixture order then map order."""
    built: list[Case] = []
    for name in FIXTURES:
        manifest = fixture_manifest(name)
        profile = profile_for(manifest.placement)
        for container in fixture_containers(name):
            built.append(_case(name, manifest, profile, container))
    return tuple(built)


def fixture_cases(name: str) -> tuple[Case, ...]:
    """Every container of one fixture corpus."""
    return tuple(case for case in cases() if case.name.startswith(f"{name}-"))


def _case(name: str, manifest: Manifest, profile: Profile, container: Container) -> Case:
    """The page a build would write for one container map."""
    where = Placement(
        corpus=manifest.source,
        container=profile.container(container.address, container.titles, origin=container.origin),
        shared=profile.corpus(),
    )
    targets = _unit_pages(profile, container)
    return Case(
        name=f"{name}-{container.address.key.replace('/', '-')}",
        document=Document(
            address=container.address,
            title=container.titles[-1],
            variant=container.variant,
            items=_items(where, container, targets),
            level=manifest.levels[-1],
            note=container.note,
        ),
        placement=where,
        links=Links(
            index=Link(
                href=relative_href(where.container.page, where.shared.root_index),
                label=manifest.title,
            )
        ),
        targets=targets,
    )


def _unit_pages(profile: Profile, container: Container) -> tuple[PurePosixPath, ...]:
    """Where placement puts each declared unit's page, in declared order."""
    return tuple(
        profile.unit(
            container.address, unit.n, unit.title, origin=unit.origin, label=unit.label
        ).page
        for unit in container.units
    )


def _items(
    where: Placement, container: Container, targets: tuple[PurePosixPath, ...]
) -> tuple[Item, ...]:
    """One row per declared unit, each addressing that unit's page from this one.

    ⛔ **Asked, never composed** — `relative_href` answers, so the same helper
    is correct under `tree` and under `sibling` without knowing which it has.
    """
    return tuple(
        Item(
            numbering=unit.numbering,
            title=unit.title,
            href=relative_href(where.container.page, target),
        )
        for unit, target in zip(container.units, targets, strict=True)
    )


def regenerate() -> list[Path]:
    """Rewrite every golden from the current renderer, and say which changed."""
    GOLDEN_DIR.mkdir(parents=True, exist_ok=True)
    changed = []
    for case in cases():
        page = case.render()
        if not case.golden.exists() or case.golden.read_bytes() != page:
            case.golden.write_bytes(page)
            changed.append(case.golden)
    return changed


if __name__ == "__main__":  # pragma: no cover - a maintenance entry point
    for path in regenerate() or []:
        print(f"rewrote {path.name}")
