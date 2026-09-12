r"""What wraps one section of a unit, and what sits above it.

**What it does.** Renders one served section — its wrapper, its blocks, and the
narrated deck the archive filed against it — from the section record
`unit.builder.parts` writes.

**How you use it.**

    from studyforge.render.page import section

    markup = section.render(document["sections"][0], placement)

**Depends on.** `page.blocks` for the blocks, `page.assets` for where the deck's
file sits, `page.navigation` for the wrapper's anchor, `render.templates` for
the markup, and `page.errors`.

## ⛔ The wrapper shows its heading only when the material carries none

⚠️ **A section's `heading` is usually the archive document's title, and the
document's own first block is usually a heading saying the same words.**
Emitting both puts the sentence on the page twice, under the unit's `<h1>` which
is often a third copy. ⛔ **But a section whose material has no heading at all —
an authored `shared` section, typically — would otherwise reach the reader as an
unlabelled run of prose they cannot locate from the outline.**

⭐ **So the test is structural and never textual:** the recorded heading is shown
when the section's blocks contain no heading of any kind, and is otherwise left
to `data-label`. ⚠️ Comparing the *words* instead — *"emit it unless it matches
the first block"* — would put the heading back the day an author changed one
character, and take it away again the day they changed it back.


## ⛔ The section's identity is `data-section`, and it is the key, not the title

⚠️ **`unit.sections` mints the key from kind and variant**, both structural,
*because* a retitled section must not renumber the audio filed under it. ⭐ The
page carries that key verbatim, so the player at M3, progress at M5 and an
in-page link all address the same thing, and none of them has to read a heading.

## ⭐ The deck sits above the section, not inside it

⚠️ The unit's own video is the whole lesson in one narrated deck, so it reads as
an *alternative* to the section rather than as its first block — and keeping it
outside `<section>` keeps it out of the outline. ⛔ Per section rather than once
per unit, because the archive files a video against the document it came from
and dropping the later ones would be a silence.

⚠️ **`remote` and `poster_remote` are provenance and never reach the page.**
They are the addresses the source served, kept so a re-fetch is possible from
the document alone; rendering one would make a page fetch from the network on
open, which is the one thing R8 forbids outright.
"""

from __future__ import annotations

from studyforge.render import templates
from studyforge.render.markup import escape, escape_attribute
from studyforge.render.page import blocks
from studyforge.render.page.assets import Placement
from studyforge.render.page.errors import PageError
from studyforge.render.page.narration import SILENT, Narration
from studyforge.render.page.navigation import section_anchor

#: The unit media directory a section's own deck was placed in.
DECK_KIND = "video"


def render(section: dict, placement: Placement, narration: Narration = SILENT) -> str:
    """Render one section: its deck, when it has one, then the section itself.

    ⚠️ **The section's own key is what a clip is addressed under**, which is the
    reason `data-section` is minted from kind and variant rather than from a
    heading: *"the page carries that key verbatim, so the player at M3, progress
    at M5 and an in-page link all address the same thing"*. ⛔ Narration is
    looked up under that key and never under a title.
    """
    if not isinstance(section, dict):
        raise PageError("a served section is an object, and this one is not")
    key = section.get("key")
    contents = list(section.get("blocks") or ())
    body = blocks.render_all(contents, placement=placement, section=key, narration=narration)
    wrapper = templates.fill(
        "section.html",
        id=escape_attribute(section_anchor(key)),
        key=escape_attribute(key),
        kind=escape_attribute(section.get("kind") or ""),
        label=escape_attribute(section.get("heading") or ""),
        heading=_heading(section, contents),
        body=body,
    )
    deck = _deck(section.get("video"), placement)
    return f"{deck}{blocks.JOIN}{wrapper}" if deck else wrapper


def _heading(section: dict, contents: list) -> str:
    """Return the section's recorded heading, or `''` when the material has one.

    ⛔ **Structural, never textual** — see this module's docstring. `heading` is
    the only test, so a section whose first block is an `h4` counts as headed
    just as much as one whose first block is an `h2`: the reader can see where
    they are either way, which is the whole question.
    """
    if any(isinstance(block, dict) and block.get("type") == "heading" for block in contents):
        return ""
    heading = str(section.get("heading") or "").strip()
    return f"<h2>{escape(heading)}</h2>{blocks.JOIN}" if heading else ""


def _deck(video: object, placement: Placement) -> str:
    """Return the unit's own narrated video, or `''` when the archive filed none.

    ⛔ `None` and *"the archive had no video"* are the same answer here and a
    different one from *"this build could not see it"* — which is why
    `unit.builder.parts` always writes the key and this reads it rather than
    inferring anything from its absence.
    """
    if not isinstance(video, dict):
        return ""
    source = video.get("src")
    if not isinstance(source, str) or not source.strip():
        return ""
    poster = video.get("poster")
    return templates.fill(
        "video.html",
        src=escape_attribute(placement.media(DECK_KIND, source)),
        poster=(
            f' poster="{escape_attribute(placement.media(DECK_KIND, poster))}"'
            if isinstance(poster, str) and poster.strip()
            else ""
        ),
        caption="",
    )
