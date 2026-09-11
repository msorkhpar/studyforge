r"""What is written, in what order, out of which templates — the page's format.

**What it does.** Composes one unit page: the skeleton every page has, and the
regions a particular page may or may not carry.

**How you use it.** `compose(document, placement, links)` returns the page's
text; `page.render` is the public entry point and turns it into bytes.

**Depends on.** `render.templates` for the markup, `page.section`,
`page.navigation`, `page.assets`, `corpus.placement.identity` for R4's block,
and `page.errors`.

## ⛔ This module *is* the format (R10)

⚠️ **The order of the slots below is the page**, and an unchanged document must
re-render to identical bytes. ⛔ So: no clock, no filesystem enumeration, no set
iteration, and every optional region is a value that is either exactly empty or
exactly its markup plus one newline — never a conditional newline somewhere else.

## ⛔ The identity block is on every page, and it is not decoration (R4)

⚠️ **Discovery reads this block and never the path.** A page moved to another
directory, or renamed, is still exactly the unit it says it is. ⭐ It is
rendered by `corpus.placement.identity`, which owns both halves and is tested
round-trip — this module chooses **where** it sits and nothing about what it
says.

## ⭐ The seam this module divides on, named before anybody needs it

⚠️ **This is the module the composer grows into**: every new page region — the
player, the read control at M5, a container page — adds a slot. ⛔ Its next split
is **not** at a convenient line number: it is between the **skeleton** (which
regions exist, in what order, and the one `page.html` substitution that fills
them) and the **regions themselves**, each of which is *optional and gated on
something*. When this file crosses R11's 400 it divides into `document.py` and
`regions.py` along that line, and not elsewhere.

## ⛔ The player is *derived*, not declared — and that is the answer to a real tension

⚠️ **`SF-12` lands at M1 and the ids it must not invent land at M3.** The
extraction source's own docstring states the invariant: *"Ids come from
`speakable.py`, never from here … two numbering schemes that agree today are
exactly the coupling that breaks silently tomorrow."* ⛔ At M1 there is no such
module, so this task mints no speech id and writes no audio attribute.

⭐ **So the player's gate reads what the page actually emitted**: a page carries
a player when its body carries `assets.AUDIO_ATTRIBUTE`, and nothing else. At M1
that is never true and the region is absent; at M3 `SF-18` writes the attribute
and the player appears with it, in one change. ⚠️ **No document field was
invented to hold a gate** — which is what a declared version of this would have
required, one milestone before the task that owns it.

⚠️ **The stated consequence:** M1's golden pages **do** change at M3, when
narration arrives. ⛔ That is a product change — a reading floor gaining a
narrator — not a regression, and R10 pins that *a rerun is identical*, never
that a page is frozen across milestones. It is recorded here so it is a decision
rather than a surprise.
"""

from __future__ import annotations

from collections.abc import Sequence

from studyforge.address import Address, AddressError
from studyforge.corpus.placement import PlacementError
from studyforge.corpus.placement import identity as identity_block
from studyforge.render import templates
from studyforge.render.markup import escape, escape_attribute
from studyforge.render.page import navigation
from studyforge.render.page import section as section_module
from studyforge.render.page.assets import AUDIO_ATTRIBUTE, Placement
from studyforge.render.page.errors import PageError
from studyforge.render.page.navigation import Crumb, Links

#: The skeleton every unit page is filled from.
SKELETON = "page.html"

#: The panel that says a unit is not finished.
PENDING_TEMPLATE = "pending-practices.html"

#: The narration transport. ⛔ Its region is gated, and at M1 the gate is never
#: open — see this module's docstring.
PLAYER_TEMPLATE = "player.html"

#: What separates two rendered sections, and what closes an optional region.
JOIN = "\n"

#: What separates the parts of the masthead's second line.
META_SEPARATOR = " · "

#: Every page ends in exactly one newline. ⚠️ Appended here rather than left as
#: a trailing blank line in `page.html`, because the loader strips one trailing
#: newline so an editor cannot silently lengthen an inline template — and a file
#: ending in a blank line is what an editor tidies away.
TRAILING_NEWLINE = "\n"


def compose(
    document: dict,
    placement: Placement,
    links: Links | None = None,
    trail: Sequence[Crumb] | None = None,
) -> str:
    """Return one unit page's exact text.

    ⛔ Pure: the same document and the same placement give byte-identical
    output, every run, on every machine (R10).

    ⚠️ `trail` is optional for the reason `links` is: only something that has
    walked the corpus's hierarchy can build one, so a page renders without it
    exactly as it will once a build does — minus the region (`SF-15`).
    """
    title = _title(document)
    body = JOIN.join(section_module.render(section, placement) for section in _sections(document))
    return (
        templates.fill(
            SKELETON,
            title=escape(title),
            heading=escape(title),
            identity=_region(identity(document, placement)),
            stylesheet=escape_attribute(placement.stylesheet()),
            script=escape_attribute(placement.script()),
            meta=_region(meta(document)),
            breadcrumb=_region(navigation.breadcrumb(trail)),
            outline=_region(navigation.outline(document)),
            body=body,
            pending=_region(pending(document)),
            player=_region(player(body)),
            nav=_region(navigation.between_units(links)),
        )
        + TRAILING_NEWLINE
    )


def identity(document: dict, placement: Placement) -> str:
    """Return R4's block, saying what this page is wherever it ends up.

    ⛔ Built from the served document's own fields and never from the page's
    path: inferring identity from a location is the thing R4 forbids, and this
    is the module a reader would expect to find it done in.
    """
    try:
        record = identity_block.Identity(
            corpus=placement.corpus,
            address=Address(tuple(document.get("address") or ())),
            variant=str(document.get("variant") or ""),
            kind="unit",
            unit=document.get("unit"),
        )
    except (PlacementError, AddressError) as error:
        # ⛔ Re-typed, not re-worded: `placement` owns what an identity may say,
        # and re-spelling its sentence here would be two descriptions of one
        # rule. The name is this package's so a caller catches one family.
        #
        # ⛔ **Narrow on purpose.** `PersonalDataLeak` is deliberately outside
        # this pair and travels through as itself (Ruling 58): a caller
        # rendering a site catches `PageError` per unit and carries on, and an
        # R7 refusal folded into that family would be logged as one more page
        # that did not render, with the leak the thing nobody looked at.
        raise PageError(f"this unit cannot identify itself: {error}") from None
    return identity_block.render(record)


def meta(document: dict) -> str:
    """Return the masthead's quieter second line: where the unit sits, in which variant.

    ⚠️ Assembled from the document's own recorded fields and from no wording of
    this framework's own — a corpus's material names itself, and a sentence
    typed here would be one every corpus had to live with (R1).
    """
    parts = [*(document.get("address") or ()), document.get("variant")]
    line = META_SEPARATOR.join(escape(part) for part in parts if part)
    return f"<p>{line}</p>" if line else ""


def pending(document: dict) -> str:
    """Return the panel that says a unit is short, or `''` when it is not.

    ⛔ **Without this the page lies by omission.** A unit whose practices were
    never ingested renders exactly like a unit that has none: lesson, then the
    end, which reads as finished. ⚠️ `declared is None` is *also* outstanding
    and not fine — nothing having said how many practices a unit has is not the
    same as it having none.
    """
    practices = document.get("practices")
    if not isinstance(practices, dict):
        return ""
    archived = practices.get("archived") or 0
    declared = practices.get("declared")
    if declared is not None and archived >= declared:
        return ""
    if declared is None:
        count = (
            f"{archived} archived. Nothing declared how many this unit has, "
            f"so it cannot be called finished."
        )
    else:
        count = f"{archived} of {declared} archived{META_SEPARATOR}{declared - archived} to come."
    return templates.fill(PENDING_TEMPLATE, count=escape(count))


def player(body: str) -> str:
    """Return the narration transport, or `''` when this page has nothing to play.

    ⛔ **Derived from the body, never from a document field** — see this
    module's docstring for why the gate is here rather than in a key `SF-12`
    would have had to invent one milestone early.
    """
    return templates.fill(PLAYER_TEMPLATE) if AUDIO_ATTRIBUTE in body else ""


def _region(markup: str) -> str:
    """Return one optional region: exactly empty, or its markup and one newline.

    ⭐ The conditional newline lives here and nowhere else. Spread across the
    slots it is one chance per slot to emit a page that differs from its golden
    file by one blank line, which is the least interesting diff a reviewer can be
    handed. ⛔ A count here would be a second statement of `page.html`'s slot
    list, wrong the next time the skeleton grows — which `SF-15` is.
    """
    return f"{markup}{JOIN}" if markup else ""


def _title(document: dict) -> str:
    """Return what this unit is called."""
    title = document.get("title")
    if not isinstance(title, str) or not title.strip():
        raise PageError("a unit page is titled, and this document records no usable title")
    return title


def _sections(document: dict) -> list:
    """Return the sections to render, in the order the document records them.

    ⛔ **The document's order is used, never re-derived.** `unit.builder` splits
    derived ordering from authored ordering into two modules precisely so that
    nothing downstream re-computes it; a renderer that sorted would be the
    second orderer that module exists to prevent.
    """
    sections = document.get("sections")
    if not isinstance(sections, list) or not sections:
        raise PageError(
            "a unit page renders at least one section; a document with none would "
            "render as a title and nothing else, which is indistinguishable from a "
            "unit that has nothing to say"
        )
    return sections
