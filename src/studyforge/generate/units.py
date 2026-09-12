r"""One corpus root in, its unit pages on disk — the caller the renderer never had.

**What it does.** Walks a corpus root, builds each declared unit's served
document from the material an adapter wrote, places it under the corpus's own
placement profile, renders its page and writes the bytes.

**How you use it.** `sources(root)` to see which declared units have material
and where it sits; `write_pages(root, into)` to render and write them. ⛔ `into`
is **required and has no default** — where a build's output goes is a decision
this module does not take.

**Depends on.** `corpus.manifest` and `corpus.container` for the declarations,
`skills.adapter` for the archive's layout, `corpus.placement` for the profile,
`unit.builder` for the document and `render.page` for the bytes. ⛔ It names no
source (R1) and it reads nothing outside the archive.

## ⛔ Why this module exists at all

Measured at `2d2af22`, population `src/**/*.py`, instrument `git grep`: **no
module outside `render/` called the page renderer, and no module anywhere wrote
a unit page.** The renderer, the builder, the placement profiles and the
narration join were finished and reachable only from tests — the site harness
under `tests/studyforge/render/page/` says as much in its own docstring and
calls itself the stand-in for a caller that did not exist. This is the first
half of that caller.

## ⛔ Non-destructive by REFUSING, never by remembering (R3)

**No path that already exists is written.** A target already on disk is named
in `Written.refused` and left byte-for-byte alone; nothing is moved, renamed or
overwritten, and the only directories minted are the ones a target needs.

⚠️ **That is R3's floor and it is NOT a rebuild policy.** What a *second* build
should do to a page the first build wrote — overwrite it, skip it, compare a
digest — is a decision left open on purpose. ⛔ Deciding it here by reflex is
exactly how a generator ends up rewriting material somebody else owns, and the
safe direction while it is open is to write nothing over anything.

## ⚠️ Three things this module deliberately does NOT do, each for a reason

⛔ **No narration.** Every page renders with `render.page.SILENT`, so a corpus
that has never been narrated is quiet rather than linking clips that are not
on disk. Who invokes synthesis, and when, is not this module's to say.

⛔ **No prev/next bar and no breadcrumb.** Both need the whole corpus's
contents document, which is a second pass over every container;
`render.page.render` takes them as optional and this module passes neither.

⛔ **No authored overlay.** `unit.content` mints `CONTENT_FILENAME` and
`skills.adapter.Layout` mints every other archive path, but **nothing in `src/`
declares where a unit's overlay sits inside an archive** — so a unit that has
one is built without it. ⭐ The hole is named here rather than guessed at: a
path invented in this module would be a second authority on the archive's
shape, and the adapter that wrote the file would not know about it.

## ⚠️ A defect this module reports is raised, not drained

`studyforge validate` drains every check and reports all of them (R6) because
an integrator fixing one problem per run against a large corpus is the failure
that argument is about. A **build** is downstream of that: it stops on the
first declaration it cannot read, and the report the integrator wants already
exists one command earlier.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path, PurePosixPath

from studyforge.corpus.container import CONTAINER_FILENAME, Container, ContainerError
from studyforge.corpus.container import parse as parse_container
from studyforge.corpus.manifest import MANIFEST_FILENAME, Manifest, ManifestError
from studyforge.corpus.manifest import parse as parse_manifest
from studyforge.corpus.placement import PlacementError, profile_for
from studyforge.render.page import Placement, render
from studyforge.skills.adapter import Layout
from studyforge.unit.builder import build_unit


class BuildError(ValueError):
    """A corpus this module will not build.

    ⛔ The message names the record and the address, **never a path and never
    the offending value** (R7): a corpus root is somebody's home directory with
    a few segments on the end, and a build's messages go into logs.
    """


@dataclass(frozen=True, slots=True)
class UnitSource:
    """One declared unit and the archive directory holding its material.

    ⭐ Every field is a **declaration**, read from the container map — the
    ordinal, the title, the origin and the label are what placement is asked
    with, and none of them is recovered from a filename (§6: recorded, never
    derived).
    """

    container: Container
    ordinal: int
    title: str
    origin: str | None
    label: str | None
    declared_practices: int | None
    directory: Path


@dataclass(frozen=True, slots=True)
class Written:
    """What one run put on disk, and what it refused to touch.

    ⭐ Both are paths **relative to the output root**, exactly as placement
    named them — so a caller can diff them against `studyforge plan` without
    knowing where the run wrote.
    """

    pages: tuple[PurePosixPath, ...]
    refused: tuple[PurePosixPath, ...]


def sources(root: Path | str) -> tuple[UnitSource, ...]:
    """Every declared unit that has material on disk, in declared order.

    ⛔ **A unit declared with no material is skipped in silence, and that is
    deliberate.** `validate`'s `unit-missing` and `empty-unit` already report
    it against the container that declared it; a build that raised a second
    sentence about the same fact would make one defect read as two.
    """
    manifest = read_manifest(root)
    layout = Layout(root)
    found: list[UnitSource] = []
    for _, container in containers(root, manifest):
        for unit in container.units:
            directory = layout.unit_dir(container.address, container.variant, unit.n)
            if not any(directory.glob("*.json")):
                continue
            found.append(
                UnitSource(
                    container=container,
                    ordinal=unit.n,
                    title=unit.title,
                    origin=unit.origin,
                    label=unit.label,
                    declared_practices=declared_practices(manifest, unit.practices),
                    directory=directory,
                )
            )
    return tuple(found)


def write_pages(root: Path | str, into: Path | str) -> Written:
    """Render every unit that has material and write its page under `into`.

    ⛔ `into` is separate from `root` and required. A build that defaulted it to
    the corpus root would have decided, silently, that generated output belongs
    inside the material — which is the one placement question §5 gives to the
    corpus and not to the framework.
    """
    manifest = read_manifest(root)
    profile = profile_for(manifest.placement)
    shared = profile.corpus()
    out = Path(into)
    pages: list[PurePosixPath] = []
    refused: list[PurePosixPath] = []
    for source in sources(root):
        try:
            at = profile.unit(
                source.container.address,
                source.ordinal,
                source.title,
                origin=source.origin,
                label=source.label,
            )
        except PlacementError as error:
            raise BuildError(
                f"the unit {source.ordinal} declared at {source.container.address.key!r} "
                f"cannot be placed: {error}"
            ) from None
        target = out / at.page
        if target.exists():
            # ⛔ R3: named and left alone, never opened for writing.
            refused.append(at.page)
            continue
        document = build_unit(source.directory, declared_practices=source.declared_practices)
        placement = Placement(corpus=manifest.source, unit=at, shared=shared)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(render(document, placement))
        pages.append(at.page)
    return Written(pages=tuple(pages), refused=tuple(refused))


def declared_practices(manifest: Manifest, practices: int) -> int | None:
    """How many practices a unit declares, given its corpus's own declaration.

    ⛔ **`exercises: false` is a declaration of ZERO, not an absence**, and the
    difference is a *"more to come"* panel on every page of a finished prose
    corpus — which contradicts §7's three states and §11.0's reading floor,
    where a graderless corpus is complete rather than short. ⭐ One direction
    only: `exercises: true` says nothing about any unit, so the count then comes
    from the container map that declared the unit.
    """
    return 0 if not manifest.exercises else practices


def read_manifest(root: Path | str) -> Manifest:
    """Read and parse one corpus manifest, or refuse naming the file (R7)."""
    text = _text(Path(root) / MANIFEST_FILENAME, MANIFEST_FILENAME)
    try:
        return parse_manifest(text, MANIFEST_FILENAME)
    except ManifestError as error:
        raise BuildError(str(error)) from None


def _text(path: Path, where: str) -> str:
    """One file's text, or a refusal that names the record and never the path.

    ⛔ `exc.strerror`, never `exc`: `OSError` formats itself with the filename
    it was given, so `{exc}` here would put a corpus root — somebody's home
    directory with a few segments on the end — into a build log (R7).

    ⚠️ **Two `except` clauses rather than one two-type clause, deliberately.**
    Ruling 74 rules the unparenthesised spelling out and `ruff format` rewrites
    the parenthesised one into it whenever there is no `as` binding, so the two
    cannot both be satisfied by a single clause — see `DEV3/8`. One type each
    satisfies both, and it lets each refusal say what actually went wrong.
    """
    try:
        return path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BuildError(f"{where} cannot be read: {exc.strerror}") from None
    except UnicodeDecodeError:
        raise BuildError(f"{where} is not UTF-8 text") from None


def containers(root: Path | str, manifest: Manifest) -> tuple[tuple[str, Container], ...]:
    """Every container map beneath the archive, in sorted path order (R10).

    ⚠️ **The archive's shape is `Layout`'s and not this module's.** A build
    that composed `archive/<address>/raw/<variant>` from string pieces would be
    a second authority on a layout the adapter already writes to one.
    """
    layout = Layout(root)
    held: list[tuple[str, Container]] = []
    for path in sorted(layout.archive.rglob(CONTAINER_FILENAME)):
        where = path.relative_to(Path(root)).as_posix()
        text = _text(path, where)
        try:
            held.append((where, parse_container(text, where, manifest)))
        except ContainerError as error:
            raise BuildError(str(error)) from None
    return tuple(held)
