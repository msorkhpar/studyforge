r"""Where a lesson says a practice belongs: `<!-- practice N -->`, and the practice drawn there.

**What it does.** A lesson may hold, on a line of its own, the comment `<!-- practice N -->`, N
being the practice's number in its unit, from 1: the N-th practice the page lists, which is the
archived `practice-N` of a unit built from its archive alone. The archive keeps that line as an
`html` block, and this module reads those blocks: `plan(document)` says which practice stands at
which block, and `spliced(section, plan, draw)` puts what `draw` returns in place of the comment.
A practice placed this way is drawn there, its card first and then its statement and panel, and
NOT again after the lesson; every practice no comment names is drawn after the lesson as before.

**How you use it.** `page.document.compose` reads the plan from the served document, narrows it to
what is still on the page once `page.quizonce` has run (`within`), and hands it to the lesson's
rendering and to `page.practices`; `outlined(document, plan)` is the document as the outline reads
it.

**Depends on.** `page.editions` for what a practice of the page is, `page.anchors` for a
practice's title and a block's anchor, and `page.errors`.

## ⛔ Absent means today, byte for byte

A page with no such comment has an empty plan, and an empty plan changes nothing anywhere. Any
other comment, `<!-- practice notes -->` included, is not a marker and renders as it always did.

## ⛔ Refused rather than guessed

A marker naming a practice the unit does not have, a practice named by two markers, a marker
inside a quote, a disclosure or a list item, and a marker inside a practice's own material are each
a `PageError` naming the marker and the section it is in. ⚠️ A marker inside a container would put
the practice's card and its full-screen workspace inside a fold the reader may never open.

## ⭐ The outline lists a placed practice where it stands

The placed card's list carries the marker block's own anchor, so the outline reads the marker as
a heading one level under the heading above it, titled as the practice's card is, and pointing at
that card list; *Practice (n)* counts only the practices still listed after the lesson. ⛔ This is
a reading for the outline only (as `page.editions.collapsed` is): the page is rendered from the
document itself.

## ⭐ A quiz the lesson repeats is already in place

`page.quizonce` draws a quiz where the lesson repeated its questions. A marker naming that quiz
then has nothing left to draw and stays the comment it was. ⛔ The numbering is read from the
document BEFORE that, so `practice 3` names the same practice whether or not a quiz moved.
"""

from __future__ import annotations

import re
from collections.abc import Callable, Mapping
from dataclasses import dataclass, field

from studyforge.render.page import anchors, editions
from studyforge.render.page.errors import PageError

#: The marker, alone in its block. ⛔ Only this shape: any other comment is the lesson's own.
MARKER = re.compile(r"<!--\s*practice\s+(\d+)\s*-->")

#: The section kind a marker may not stand in. ⛔ The archive's word.
PRACTICE = editions.PRACTICE


@dataclass(frozen=True)
class Plan:
    """Which practice stands at which block: `(section key, position) -> practice section keys`."""

    spots: Mapping[tuple[str, int], tuple[str, ...]] = field(default_factory=dict)

    def keys(self) -> frozenset[str]:
        """The section key of every practice this plan places."""
        return frozenset(key for keys in self.spots.values() for key in keys)

    def placed(self, section: object) -> bool:
        """Whether `section` is a practice drawn at a marker rather than after the lesson."""
        return isinstance(section, dict) and section.get("key") in self.keys()

    def at(self, section_key: object, position: int) -> tuple[str, ...]:
        """The practice section keys drawn at one block, or `()`."""
        return self.spots.get((str(section_key), position), ())

    def within(self, document: dict) -> Plan:
        """This plan less every practice that is no longer one of `document`'s sections."""
        present = {
            one.get("key") for one in document.get("sections") or () if isinstance(one, dict)
        }
        kept = {spot: keys for spot, keys in self.spots.items() if set(keys) <= present}
        return self if len(kept) == len(self.spots) else Plan(kept)


#: The plan of a page that places nothing.
NONE = Plan()


def number(block: object) -> int | None:
    """The practice a block names, or `None` when it is not a marker."""
    if not isinstance(block, dict) or block.get("type") != "html":
        return None
    found = MARKER.fullmatch(str(block.get("text") or "").strip())
    return int(found.group(1)) if found else None


def plan(document: dict) -> Plan:
    """Read every marker of `document`, or raise `PageError` naming the one that cannot stand."""
    found = editions.entries(document)
    spots: dict[tuple[str, int], tuple[str, ...]] = {}
    named: set[int] = set()
    for section in document.get("sections") or ():
        if not isinstance(section, dict):
            continue
        key = str(section.get("key"))
        for position, block in enumerate(section.get("blocks") or ()):
            if _nested(block):
                raise PageError(
                    f"a practice marker in section {key!r} (block {position}) stands inside a "
                    "quote, a disclosure or a list; it belongs on a line of its own in the lesson"
                )
            wanted = number(block)
            if wanted is None:
                continue
            where = f"the marker <!-- practice {wanted} --> in section {key!r}"
            if section.get("kind") == PRACTICE:
                raise PageError(f"{where} stands in a practice; a practice is placed in a lesson")
            if not 1 <= wanted <= len(found):
                raise PageError(
                    f"{where} names practice {wanted}, and this unit has {len(found)} "
                    f"practice{'' if len(found) == 1 else 's'}"
                )
            if wanted in named:
                raise PageError(f"{where} names practice {wanted} a second time")
            named.add(wanted)
            spots[(key, position)] = tuple(one.get("key") for one in found[wanted - 1].sections)
    return Plan(spots) if spots else NONE


def spliced(section: dict, placed: Plan, draw: Callable[[tuple[str, ...], str], str]) -> dict:
    """Return `section` with each marker's block drawn as its practice, or `section` itself.

    ⛔ Positions do not move: the marker's block becomes an `html` block holding the practice,
    so every anchor and clip after it is addressed as before. ⭐ `draw` is handed the practice's
    section keys and the marker block's own anchor, which the placed card list carries.
    """
    blocks = section.get("blocks") or []
    out = list(blocks)
    for position in range(len(out)):
        keys = placed.at(section.get("key"), position)
        if keys:
            spot = anchors.block_anchor(section.get("key"), position)
            out[position] = {"type": "html", "text": draw(keys, spot)}
    return section if out == list(blocks) else {**section, "blocks": out}


def outlined(document: dict, placed: Plan) -> dict:
    """Return `document` as the outline reads it: each placed practice a heading at its marker.

    ⭐ The heading is one level under the heading above it, at most the outline's deepest; the
    placed practice's own section is left out. ⛔ With nothing placed, `document` itself.
    """
    if not placed.spots:
        return document
    sections = [one for one in document.get("sections") or () if not placed.placed(one)]
    keyed = {one.get("key"): one for one in document.get("sections") or ()}
    title = document.get("title")
    read = []
    for section in sections:
        blocks, under = list(section.get("blocks") or ()), 1
        for position, block in enumerate(blocks):
            if isinstance(block, dict) and block.get("type") == "heading":
                under = anchors.heading_level(block)
            keys = placed.at(section.get("key"), position)
            if keys and keys[0] in keyed:
                level = min(max(under + 1, 2), anchors.OUTLINE_MAX_LEVEL)
                text = anchors.practice_title(keyed[keys[0]], title)
                blocks[position] = {"type": "heading", "level": level, "text": text}
        read.append({**section, "blocks": blocks})
    return {**document, "sections": read}


def _nested(block: object) -> bool:
    """Whether a marker stands anywhere inside `block` rather than as `block` itself."""
    if isinstance(block, dict):
        return any(number(value) is not None or _nested(value) for value in block.values())
    if isinstance(block, list):
        return any(number(value) is not None or _nested(value) for value in block)
    return False
