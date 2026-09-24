r"""`curriculum` — where a corpus records its curriculum, and how its names cross-check it (`W340`).

**What it does.** Validates the optional top-level `curriculum` block: the
document that records the corpus's reading order and grouping, the address each
of that document's groups is filed at, and — optionally, per group — the
filename prefix its files carry, declared as a **cross-check**.

**How you use it.** `document.from_document` calls `parse_curriculum`; a caller
reads `Manifest.curriculum`, which is `None` when the corpus declares nothing.

    manifest.curriculum.record                  # 'README.md'
    manifest.curriculum.containers[1].address   # Address(('deeper',))
    manifest.curriculum.containers[1].prefix    # 'deep_'
    prefix_of("lessons/deep_10.md")             # 'deep_' — the name's own claim

**Depends on.** `studyforge.address` for what an address is, and `errors`.
⛔ It reads no file: whether the tree agrees with the declaration is the
adapter skill's `curriculum.filed` to say, because a manifest parses with no
filesystem (`document.parse`).

## ⛔ The record files a unit; a prefix never does

⭐ **§6: an address is recorded, never derived.** The document named by
`record` is the record, and `containers` says which address each of its groups
is filed at — the map a corpus's adapter otherwise carries as a constant a
second corpus would retype (R19, Ruling 107's `Q11` and `Q12`).

⚠️ **A prefix is a derivation, so it may only ever agree.** The reconnaissance
skill's step 2 keeps the filename-prefix rule *"as a cross-check that must
agree — never as the source"* (`W471/1`). So `prefix` decides nothing: it is a
second partition of the same files, and the adapter refuses when the two
partitions differ, in either direction.

## ⭐ What a prefix is, and why it may carry no digit

A file's name carries prefix `p` when its stem is exactly `p` followed by a
number: `s10.md` carries `s`, `10.md` carries the empty prefix, and
`Server.md`, `1a.md` and `s10-notes.md` carry none. ⛔ **A declared prefix may
contain no digit and no `/`**, and that is what makes the partition a
partition: with no digit in `p`, a stem's prefix is the stem with its trailing
number taken off, so no name can carry two declared prefixes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import PurePosixPath

from studyforge.address import Address, AddressError, parse_key
from studyforge.corpus.manifest.errors import ManifestError
from studyforge.corpus.manifest.fields import GLOB_CHARACTERS
from studyforge.describe import describe

#: The keys a `curriculum` block may carry, and the ones each group may carry.
#: ⛔ Closed sets: an unknown key is refused, never ignored (R9).
CURRICULUM_KEYS = ("record", "containers")
CONTAINER_KEYS = ("label", "address", "prefix")

#: A stem that is a prefix and a number, and nothing else.
PREFIXED = re.compile(r"(?P<prefix>\D*)(?P<number>\d+)")


@dataclass(frozen=True, slots=True)
class DeclaredContainer:
    """One group of the record: the label it is written under, its address, its prefix."""

    #: The group's label exactly as the record writes it, emphasis removed.
    label: str
    address: Address
    #: The prefix its files' names carry, or `None` for no cross-check.
    prefix: str | None = None


@dataclass(frozen=True, slots=True)
class Curriculum:
    """Where the curriculum is recorded, and what its groups are filed at."""

    #: The recording document, root-relative.
    record: str
    #: Its groups, in the order the record writes them; empty when undeclared.
    containers: tuple[DeclaredContainer, ...] = ()

    @property
    def prefixes(self) -> dict[str, DeclaredContainer]:
        """Every declared prefix, and the group whose files carry it."""
        return {each.prefix: each for each in self.containers if each.prefix is not None}


def prefix_of(path: str) -> str | None:
    """Return the prefix `path`'s name carries, or `None` when it carries none."""
    match = PREFIXED.fullmatch(PurePosixPath(path).stem)
    return match.group("prefix") if match is not None else None


def parse_curriculum(value: object, where: str, depth: int) -> Curriculum:
    """Return the declaration, refusing anything it does not state exactly.

    ⛔ **Each address is checked against this corpus's depth here**, where the
    levels are known, so no reader of the declaration meets an address the
    manifest could not have filed.
    """
    if not isinstance(value, dict):
        raise ManifestError(
            f"{where} 'curriculum' must be an object with 'record' and optionally "
            f"'containers', got {describe(value)}"
        )
    _closed(value, CURRICULUM_KEYS, "curriculum", where)
    if "record" not in value:
        raise ManifestError(f"{where} 'curriculum' must name its 'record'")
    record = _record_of(value["record"], where)
    containers = _containers_of(value.get("containers", []), where, depth)
    return Curriculum(record=record, containers=containers)


def _record_of(value: object, where: str) -> str:
    """Return the recording document: a Markdown file inside the corpus, spelled one way.

    ⛔ **The value is never quoted** (R7): a path that is not a corpus path is
    usually somebody's home directory.
    """
    rule = (
        f"{where} 'curriculum.record' must be a path inside the corpus ending .md, "
        f"with no '.' or '..' segment and no glob character"
    )
    if not isinstance(value, str) or not value:
        raise ManifestError(f"{rule}, got {describe(value)}")
    path = PurePosixPath(value)
    clean = (
        path.as_posix() == value
        and not path.is_absolute()
        and not any(part in (".", "..") for part in path.parts)
        and not GLOB_CHARACTERS & set(value)
        and path.suffix == ".md"
        and path.stem != ""
    )
    if not clean:
        raise ManifestError(f"{rule}; the value is not reproduced, since it may be a path (R7)")
    return value


def _containers_of(value: object, where: str, depth: int) -> tuple[DeclaredContainer, ...]:
    """Each group's label, address and prefix, refusing a repeat of any of the three."""
    if not isinstance(value, list):
        raise ManifestError(
            f"{where} 'curriculum.containers' must be a list, got {describe(value)}"
        )
    found = tuple(
        _container_of(entry, f"{where} 'curriculum.containers[{index}]'", depth)
        for index, entry in enumerate(value)
    )
    for field in CONTAINER_KEYS:
        seen = [getattr(each, field) for each in found if getattr(each, field) is not None]
        if len(seen) != len(set(seen)):
            # ⛔ A repeated label is two groups the record cannot tell apart, a
            # repeated address is two groups filed in one place, and a repeated
            # prefix is a cross-check that no longer partitions anything.
            raise ManifestError(
                f"{where} 'curriculum.containers' repeats a {field}; each group of the "
                f"record has its own"
            )
    return found


def _container_of(entry: object, where: str, depth: int) -> DeclaredContainer:
    """One group, with its address checked at this corpus's depth."""
    if not isinstance(entry, dict):
        raise ManifestError(f"{where} must be an object, got {describe(entry)}")
    _closed(entry, CONTAINER_KEYS, "container", where)
    label = entry.get("label")
    if not isinstance(label, str) or not label.strip():
        raise ManifestError(f"{where} 'label' must be a non-empty str, got {describe(label)}")
    try:
        address = parse_key(entry.get("address"), depth)
    except AddressError as exc:
        raise ManifestError(f"{where} 'address': {exc}") from None
    return DeclaredContainer(
        label=label, address=address, prefix=_prefix_of(entry.get("prefix"), where)
    )


def _prefix_of(value: object, where: str) -> str | None:
    """Return a declared prefix: no digit, `/` or whitespace. ⭐ Empty is a prefix."""
    if value is None:
        return None
    if not isinstance(value, str) or re.search(r"[\d/\s]", value) or GLOB_CHARACTERS & set(value):
        raise ManifestError(
            f"{where} 'prefix' must be a str with no digit, '/', whitespace or glob "
            f"character — a name carries it as the text before its number — "
            f"got {describe(value)}"
        )
    return value


def _closed(value: dict, keys: tuple[str, ...], what: str, where: str) -> None:
    """Refuse a key this block does not define. ⭐ Names are this module's, never quoted."""
    unknown = set(value) - set(keys)
    if unknown:
        raise ManifestError(
            f"{where} a {what} declaration has {len(unknown)} unknown key(s); "
            f"this build reads {list(keys)}"
        )
