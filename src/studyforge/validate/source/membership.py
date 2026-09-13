r"""What sits beneath the archive root that the archive does not account for.

**What it does.** Refuses, by name, every file beneath the archive root that is
not an archive member (`W248`, `W241/2`). `classification` never scans beneath
the root, so this check is the other half of that skip: every file there is a
member or a finding, and none is silently lost.

**How you use it.** `check_archive_members(walk)`, yielding `Finding`s like
every other check. `archive_members(walk)` returns the member set on its own.

**Depends on.** `validate.corpus` for what the archive reader read,
`skills.adapter.Layout` for a unit's own files (deferred, `_unit_files` says
why), `corpus.container`, `corpus.placement`, `validate.report`. ⛔ Nothing in
this package's other two modules.

## ⛔ A member is what the readers read, never a list kept here

⭐ **Derived from two sources that already exist.** The walk records every
container map it parsed and every document beneath each map's variant, parsed
or refused. SK-02's `Layout.unit_files` names each declared unit's own
directory, which a build reads for media and the overlay. ⛔ Anything else is
a stray: a note, a map's second variant, a file outside a unit, an undeclared
unit's files.

⚠️ **A member-shaped file at the wrong depth is not always a stray.** A `.json`
beneath a map's variant is read as a document wherever it sits, so
`identity` refuses it and this check does not refuse it twice. A non-`.json`
file at the same place is never read, and so it is a stray.

⛔ **Refused, never resolved.** A stray is not read as material, and the
manifest cannot include it. Beneath a map that did not parse, nothing is
judged here: `run` already reports that no document there was read.
"""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

from studyforge.corpus.container import CONTAINER_FILENAME
from studyforge.corpus.placement import ARCHIVE_DIRNAME
from studyforge.validate.corpus import Walk
from studyforge.validate.report import Finding

#: ⛔ A file beneath the archive root that no reader reads (`W248`).
RULE_ARCHIVE_STRAY = "archive-stray"


def check_archive_members(walk: Walk) -> Iterator[Finding]:
    """Refuse each file beneath the archive root that is not an archive member."""
    if walk.manifest is None:  # pragma: no cover - the walk stops without one
        return
    archive = walk.root / ARCHIVE_DIRNAME
    if not archive.is_dir():
        return
    members = archive_members(walk)
    units = _unit_files(walk)
    unread = {item.path.parent for item in walk.refused if item.container is None}
    for path in sorted(archive.rglob("*")):
        if not path.is_file() or path in members:
            continue
        if any(parent in units or parent in unread for parent in path.parents):
            continue
        yield Finding(
            RULE_ARCHIVE_STRAY,
            walk.relative(path),
            f"sits beneath {ARCHIVE_DIRNAME}/ and is not an archive member, so no check and "
            f"no build reads it. The archive holds container maps, the documents under each "
            f"map's variant, and each declared unit's own files. It is refused, not skipped "
            f"and not read as material: move it out, or write it where the layout places it.",
        )


def archive_members(walk: Walk) -> frozenset[Path]:
    """Every container map and document file the archive reader read, parsed or refused."""
    found = {held.directory / CONTAINER_FILENAME for held in walk.containers}
    found.update(unit.path for unit in walk.units)
    found.update(item.path for item in walk.refused if item.container is not None)
    return frozenset(found)


def _unit_files(walk: Walk) -> frozenset[Path]:
    """Each declared unit's own directory, as SK-02's published layout places it.

    ⚠️ **The import is deferred.** `skills.adapter`'s package imports its
    scaffold and plan, and `validate` must stay importable before either.
    ⭐ Asked of the address, as a build asks it (`generate.media`). A unit's
    files beside a map held at another directory are strays, beside that map's
    `address-directory`, because no build reads them there either.
    """
    from studyforge.skills.adapter import Layout

    layout = Layout(walk.root)
    return frozenset(
        layout.unit_files(held.container.address, unit.n)
        for held in walk.containers
        for unit in held.container.units
    )
