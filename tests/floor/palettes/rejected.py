"""The rejected identities, READ OUT of the spec's own table (§8.4).

**What it does.** Reads the two tables the spec's §8.4 writes —
the roles and the tokens that carry them, and the rejected identities as
conjunctions of bands over hue, chroma and light — and returns them as data.
⛔ **The document is the authority and this module is only its reader:** a sixth
rejected identity is a row somebody adds there, with no change here.

**How you use it.** `convention(root)` for both tables off a tree,
`signatures(text)` and `roles(text)` for one document's text, and `band`, `part`
and `table` for the grammar underneath them.

**Depends on.** `tests.floor.config` for reading a file,
`tests.floor.palettes.colours` for what a band is a bound on, and `re`,
`dataclasses` and `pathlib`.

## ⛔ A ROW IS A CONJUNCTION

⭐ **Cool slate is the ACCEPTED identity; slate WITH teal-green AND amber is a
rejected one.** ⛔ So a row is every part at once, and a reader that
returned its parts separately would be describing a different rule from the one
the document states.

## ⚠️ A ROW THAT DOES NOT PARSE IS DROPPED, NEVER GUESSED AT

⛔ A malformed band is not silently widened and a half-read row is not kept:
the row leaves the population. ⭐ **And that is safe only because the mirror
asserts THIS repository's rows all parse** — a table somebody breaks turns the
suite red rather than turning the check into a green that reads nothing.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tests.floor import config
from tests.floor.palettes.colours import Colour

#: The document that carries the table. ⛔ One named document, not a walk: the
#: document is the authority, and a second copy of it could disagree with it.
#: ⭐ The tables live in the spec's §8.4, the product's home for what a rendered
#: page is held to.
UI_CONVENTION = "docs/specs/2026-09-08-studyforge-v1-design.md"

#: The one role that is NOT carried by a token, named here because a document
#: cannot spell a pool. ⭐ Its parts must meet inside ONE gradient.
GRADIENT_ROLE = "gradient stop"

#: The two tables, located by the header cells they carry rather than by a
#: heading or a line number, so a table survives a heading's rewording.
ROLE_HEADER = ("Role", "Read from")
SIGNATURE_HEADER = ("Rejected identity", "Every part must be present", "Why")

#: The top of each measure's range, so `>= 45` is a band and not a special case.
CEILING = {"hue": 360.0, "chroma": 100.0, "light": 100.0}

_SPAN = re.compile(r"`([^`]+)`")
_TOKEN = re.compile(r"^--[a-z0-9-]+$", re.IGNORECASE)
_BAND = re.compile(
    r"^(?P<measure>hue|chroma|light)\s+"
    r"(?:(?P<low>\d+)\s*-\s*(?P<high>\d+)|(?P<op><=|>=)\s*(?P<value>\d+))$"
)


@dataclass(frozen=True)
class Band:
    """One bound on one measure, as the document writes it."""

    measure: str
    low: float
    high: float
    text: str

    def holds(self, read: Colour) -> bool:
        """Whether `read`'s measure is inside this band, endpoints included."""
        return self.low <= getattr(read, self.measure) <= self.high


@dataclass(frozen=True)
class Part:
    """One `role: band, band` of a rejected identity, as the document writes it."""

    role: str
    bands: tuple[Band, ...]
    text: str

    def holds(self, read: Colour) -> bool:
        """Whether one colour satisfies every band of this part."""
        return all(band.holds(read) for band in self.bands)


@dataclass(frozen=True)
class Signature:
    """One rejected identity: its name, its parts, and the ground the document gives."""

    name: str
    parts: tuple[Part, ...]
    ground: str

    def roles(self) -> tuple[str, ...]:
        """Return the roles this identity is written over, in the order it writes them."""
        return tuple(dict.fromkeys(part.role for part in self.parts))


def band(text: str) -> Band | None:
    """`hue 20-70`, `chroma >= 25` or `light <= 12` as a band, or None when it is neither."""
    found = _BAND.match(text.strip())
    if found is None:
        return None
    name = found.group("measure")
    if found.group("low") is not None:
        return Band(name, float(found.group("low")), float(found.group("high")), text.strip())
    value = float(found.group("value"))
    if found.group("op") == ">=":
        return Band(name, value, CEILING[name], text.strip())
    return Band(name, 0.0, value, text.strip())


def part(text: str) -> Part | None:
    """`role: band, band` as a part, or None when the span is not one."""
    role, colon, bounds = text.partition(":")
    if not colon:
        return None
    bands = tuple(band(one) for one in bounds.split(","))
    if not bands or any(one is None for one in bands):
        return None
    return Part(role.strip(), tuple(one for one in bands if one is not None), text.strip())


def table(text: str, header: tuple[str, ...]) -> list[tuple[str, ...]]:
    """Every row of the one table whose header cells are `header`, with markup kept."""
    rows: list[tuple[str, ...]] = []
    reading = False
    for line in text.splitlines():
        if not line.lstrip().startswith("|"):
            reading = False
            continue
        cells = tuple(cell.strip() for cell in line.strip().strip("|").split("|"))
        if tuple(cell.strip("* ") for cell in cells) == header:
            reading, rows = True, []
            continue
        if not reading or set("".join(cells)) <= set("-: "):
            continue
        rows.append(cells)
    return rows


def roles(text: str) -> dict[str, tuple[str, ...]]:
    """Each role the document names, with the tokens that carry it (none for the gradient one)."""
    found: dict[str, tuple[str, ...]] = {}
    for row in table(text, ROLE_HEADER):
        if len(row) < 2:
            continue
        name = row[0].strip("`* ")
        found[name] = tuple(
            span for span in _SPAN.findall(row[1]) if _TOKEN.match(span) is not None
        )
    return found


def signatures(text: str) -> tuple[Signature, ...]:
    """Every rejected identity the document writes, in the order it writes them."""
    found: list[Signature] = []
    for row in table(text, SIGNATURE_HEADER):
        if len(row) < 3:
            continue
        parts = tuple(part(span) for span in _SPAN.findall(row[1]))
        if not parts or any(one is None for one in parts):
            continue
        found.append(
            Signature(row[0].strip("* "), tuple(one for one in parts if one is not None), row[2])
        )
    return tuple(found)


def convention(root: Path) -> tuple[dict[str, tuple[str, ...]], tuple[Signature, ...]]:
    """Return the document's two tables, or two empty answers when it is not in this tree.

    ⛔ **No document, no rejected identities, and therefore no findings** — the
    floor runs over trees that are not this repository, and a check that failed
    on a tree with no UI would fail every one of them.
    """
    text = config.read_text(root / UI_CONVENTION)
    if text is None:
        return {}, ()
    return roles(text), signatures(text)


__all__ = [
    "CEILING",
    "GRADIENT_ROLE",
    "ROLE_HEADER",
    "SIGNATURE_HEADER",
    "UI_CONVENTION",
    "Band",
    "Part",
    "Signature",
    "band",
    "convention",
    "part",
    "roles",
    "signatures",
    "table",
]
