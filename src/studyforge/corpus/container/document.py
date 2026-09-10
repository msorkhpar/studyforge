"""The container-map format: what a `container.json` is, read and rendered.

**What it does.** Owns the key order that reaches disk, the two records a map
decodes to, and the four entry points that read and re-render one.

**How you use it.** `parse(text, where, manifest)`, `load(path, manifest)`,
`render(container)`, `to_document(container)`. ⛔ The manifest is required.

**Depends on.** `studyforge.address`, `studyforge.corpus.manifest`,
`archive.scrub` for R7's gate, `studyforge.version` for R9's, and this
package's `fields` and `errors`. The package contract is in `__init__.py`.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from studyforge.address import Address, AddressError, require_ordinal
from studyforge.archive.scrub import assert_clean
from studyforge.corpus.container import fields
from studyforge.corpus.container.errors import ContainerError
from studyforge.corpus.manifest import Manifest
from studyforge.version import check as check_version

#: The document format version. ⚠️ Bumped when a reader of the old shape would
#: be *wrong* rather than merely incomplete.
CONTAINER_API = 1

#: The versions this build reads. ⛔ The membership test is
#: `studyforge.version`'s (SF-33); what lives here is the set.
KNOWN_CONTAINER_API = frozenset({CONTAINER_API})

CONTAINER_FILENAME = "container.json"

#: The document's key order, which is what reaches disk (R10). ⚠️ `origin` and
#: `note` are omitted when they have nothing to say; the rest keep this order.
CONTAINER_KEYS = (
    "container_api",
    "address",
    "titles",
    "variant",
    "ingested",
    "origin",
    "note",
    "units",
)

#: A unit entry's key order. `origin`, `url_slug`, `label` and `note` are
#: omitted when absent.
#:
#: ⭐ **`origin` and `url_slug` are both provenance and neither is redundant.**
#: `origin` is a path *inside* the source, which is what a repository corpus
#: has; `url_slug` is the source's own addressing for the unit, which is what a
#: web source has instead — it has no file. A corpus normally carries one or
#: the other. ⚠️ `depth2`'s second container carries both because it is the
#: fixture that exercises both.
UNIT_KEYS = ("n", "title", "practices", "origin", "url_slug", "label", "note")

#: ⭐ **The whole content of "hand-authorable"** (Q3). These are the fields a
#: person may amend and a generator must round-trip rather than overwrite;
#: everything else is derived and hand-writing it is a finding.
EDITORIAL_KEYS = ("title", "titles", "note")


@dataclass(frozen=True, slots=True)
class Unit:
    """One unit as its container declares it.

    `practices` is the **declared** count, preserved verbatim: SF-25 checks it
    against what is actually on disk, and a reader that corrected it here
    would delete the disagreement that check exists to find.
    """

    n: int
    title: str
    practices: int
    origin: str | None = None
    url_slug: str | None = None
    label: str | None = None
    note: str | None = None

    @property
    def numbering(self) -> str:
        """Return this unit's numbering **as a reader sees it**: `4.4.1`, or `7`.

        ⚠️ **Not the filename component**, which is SF-03's `label_of` and
        gives `unit-07` where this gives `7`. The two are one rule with two
        fallbacks: when a label is present they are identical and it *is* the
        label; when it is absent, a filename wants a prefixed, zero-padded,
        sortable form and a page heading does not.

        ⛔ Presentation only, either way. Nothing may read one back as an
        ordinal — R4's argument about paths, applied to numbering.
        """
        return self.label if self.label is not None else str(self.n)


@dataclass(frozen=True, slots=True)
class Container:
    """One container's declaration. Immutable once validated."""

    address: Address
    titles: tuple[str, ...]
    variant: str
    ingested: str
    units: tuple[Unit, ...]
    origin: str | None = None
    note: str | None = None
    container_api: int = CONTAINER_API

    @property
    def ordinals(self) -> tuple[int, ...]:
        """The unit ordinals, in declared order."""
        return tuple(unit.n for unit in self.units)

    def unit(self, n: int) -> Unit:
        """Return unit `n`, or raise `ContainerError` naming what is declared."""
        for unit in self.units:
            if unit.n == n:
                return unit
        raise ContainerError(
            f"{self.address.key} declares units {list(self.ordinals)}; there is no unit {n!r}"
        )


def from_document(document: dict, where: str, manifest: Manifest) -> Container:
    """Build a `Container` from a decoded `container.json`, checked against its corpus."""
    check_version(
        "container_api",
        document.get("container_api"),
        KNOWN_CONTAINER_API,
        where=where,
        error=ContainerError,
    )
    assert_clean(document, where)
    unknown = sorted(set(document) - set(CONTAINER_KEYS))
    if unknown:
        raise ContainerError(
            f"{where} carries unknown key(s) {unknown}; a container map is {list(CONTAINER_KEYS)}"
        )

    address = Address(document.get("address", ())).require_depth(manifest.depth)
    titles = _titles(document.get("titles"), manifest.depth, where)
    variant = document.get("variant")
    if variant not in manifest.variants:
        raise ContainerError(
            f"{where} declares variant {variant!r}; {manifest.source} declares "
            f"{list(manifest.variants)}"
        )
    return Container(
        address=address,
        titles=titles,
        variant=variant,
        ingested=fields.required_text(document.get("ingested"), "ingested", where),
        units=_units(document.get("units"), where),
        origin=fields.optional_path(document.get("origin"), "origin", where),
        note=fields.optional_text(document.get("note"), "note", where),
    )


def parse(text: str, where: str, manifest: Manifest) -> Container:
    """Read one container map from its text: valid JSON, a known version, clean."""
    try:
        document = json.loads(text)
    except json.JSONDecodeError as exc:
        # ⛔ Names the fields, never the exception object and never the text.
        raise ContainerError(
            f"{where} is not valid JSON: {exc.msg} at line {exc.lineno} column {exc.colno}"
        ) from None
    if not isinstance(document, dict):
        raise ContainerError(f"{where} must be a JSON object, got a {type(document).__name__}")
    return from_document(document, where, manifest)


def load(path: Path | str, manifest: Manifest) -> Container:
    """Read, version-check and gate one container map from disk.

    ⛔ `where` is the file's **name**, never the path it was read from: an
    absolute path in a refusal is personal data in a log (R7).
    """
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        # ⛔ `exc.strerror`, never `exc`: `OSError` formats itself with the
        # filename it was given.
        raise ContainerError(f"cannot read {path.name}: {exc.strerror}") from None
    return parse(text, path.name, manifest)


def to_document(container: Container) -> dict:
    """Return the container as the decoded document, in `CONTAINER_KEYS` order."""
    document = {
        "container_api": container.container_api,
        "address": list(container.address.segments),
        "titles": list(container.titles),
        "variant": container.variant,
        "ingested": container.ingested,
    }
    if container.origin is not None:
        document["origin"] = container.origin
    if container.note is not None:
        document["note"] = container.note
    document["units"] = [_unit_document(unit) for unit in container.units]
    return document


def render(container: Container) -> str:
    """Serialise a container to the exact bytes that reach disk.

    ⛔ `sort_keys=False`. ⭐ This is the round-trip half of "hand-authorable":
    read a map, amend an editorial field, write it back, and every byte of
    everything untouched is the byte that was there.
    """
    return json.dumps(to_document(container), indent=2, ensure_ascii=False, sort_keys=False) + "\n"


def _unit_document(unit: Unit) -> dict:
    entry: dict[str, object] = {"n": unit.n, "title": unit.title, "practices": unit.practices}
    for key in ("origin", "url_slug", "label", "note"):
        value = getattr(unit, key)
        if value is not None:
            entry[key] = value
    return entry


def _titles(value: object, depth: int, where: str) -> tuple[str, ...]:
    if not isinstance(value, list) or len(value) != depth:
        raise ContainerError(
            f"{where} must carry one title per container level; the corpus declares {depth}"
        )
    return tuple(fields.required_text(title, "title", where) for title in value)


def _units(value: object, where: str) -> tuple[Unit, ...]:
    if not isinstance(value, list) or not value:
        raise ContainerError(f"{where} declares no units; a container map declares at least one")
    units = tuple(_unit(entry, where) for entry in value)
    expected = list(range(1, len(units) + 1))
    if [unit.n for unit in units] != expected:
        raise ContainerError(
            f"{where} declares units {[unit.n for unit in units]}; ordinals must be "
            f"contiguous from 1, so {expected} was expected. A gap is a unit that was "
            f"not ingested, and it is reported rather than closed."
        )
    return units


def _unit(entry: object, where: str) -> Unit:
    if not isinstance(entry, dict):
        raise ContainerError(f"{where} has a unit entry that is not an object")
    unknown = sorted(set(entry) - set(UNIT_KEYS))
    if unknown:
        raise ContainerError(
            f"{where} has a unit carrying unknown key(s) {unknown}; a unit is {list(UNIT_KEYS)}"
        )
    try:
        n = require_ordinal(entry.get("n"), f"{where} unit ordinal")
    except AddressError:
        # ⛔ Converted rather than allowed to escape, and not only for
        # consistency: SF-01's message formats the value with `!r`, and this
        # one is read straight out of a file somebody else wrote (R7).
        raise ContainerError(
            f"{where} has a unit whose ordinal is {fields.said(entry.get('n'))}; "
            f"it must be a whole number of 1 or more"
        ) from None
    practices = entry.get("practices")
    if not isinstance(practices, int) or isinstance(practices, bool) or practices < 0:
        raise ContainerError(
            f"{where} unit {n} declares a practice count that is not a whole number. "
            f"It is preserved verbatim for SF-25 to check against reality, so it is "
            f"never corrected here."
        )
    return Unit(
        n=n,
        title=fields.required_text(entry.get("title"), f"unit {n} title", where),
        practices=practices,
        origin=fields.optional_path(entry.get("origin"), f"unit {n} origin", where),
        url_slug=fields.optional_slug(entry.get("url_slug"), f"unit {n} url_slug", where),
        label=fields.optional_label(entry.get("label"), f"unit {n} label", where),
        note=fields.optional_text(entry.get("note"), f"unit {n} note", where),
    )
