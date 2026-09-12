r"""Which narrated element carries which clip, and how the page addresses it.

**What it does.** Holds the one lookup a renderer needs while it is building a
page — *where am I, and is there a clip for here?* — and turns the answer into
the attribute the transport reads.

**How you use it.**

    from studyforge.render.page.narration import Narration

    narration = Narration.of(clips, placement)   # clips: position -> filename
    narration.attribute(section_key, block_path)          # a whole block
    narration.attribute(section_key, block_path, index)   # an item or a row

**Depends on.** `render.markup` for escaping, `page.assets` for the attribute's
spelling and for `Placement`, and `corpus.placement` for the name of the
directory a unit's audio was placed in. ⛔ **Not on `narrate`** — see below.

## ⛔ THE KEY IS `SpeechUnit.position`, AND THIS MODULE IMPORTS NOTHING TO KNOW IT

⚠️ **`narrate.speakable` is where a speech unit is minted, and this package must
not reach for it.** ⭐ The record was designed for exactly this hand-off and says
so in its own contract: *"`position` exists so the lookup key has one
spelling … a renderer attaching an id to a node it is building must find the
unit by where it is, not by recomputing the numbering — that second numbering
scheme is the whole defect this package exists to prevent."*

⛔ **So a caller passes the mapping in, keyed by that tuple, and the renderer
never derives a position of its own.** A `render` that imported the walker would
be a renderer that could disagree with the minter about what a unit is called —
and `narrate/speakable/naming.py` records what that costs: the synthesis runner
was handed a bare speech id while the page asked for the digest form, every clip
was missing, and every run re-synthesised the lot.

## ⛔ FILENAMES IN, HREFS OUT — and `Placement` is asked exactly once

⚠️ **The caller supplies a *filename*, never a path.** `audio/<clip>.mp3` is the
`tree` profile's answer and `<stem>.audio/<clip>.mp3` is `sibling`'s; a caller
that composed either would be right under one profile and silently wrong under
the other, with the page rendering identically both ways (R4).

⭐ **`of()` resolves every one of them through `Placement.media` up front**, so
what the block renderers hold is a finished href and no renderer below this line
addresses a file at all. ⛔ That is deliberate: `blocks/prose.py` states *"Not on
`page.assets`: nothing here addresses a file"*, and it is still true after this.

## ⚠️ WHERE THE FILENAME COMES FROM, AND WHY IT IS NOT COMPUTED HERE

⛔ **A clip's filename is `<speech-id>-<8 hex of sha256(spoken text)>.<format>`
(spec §8.2), and the format is NOT knowable at render time.** `narrate/client.py`
builds the placed name from a format the **synthesis service** answered with, so
a renderer that assumed `mp3` would be a second authority on it — and the symptom
is a page linking files that are not on disk, with the suite green. ⭐ The record
that settles it is `.studyforge/narration.json` (`SF-17`), whose
`clips.<speech id>.filename` is what was actually placed. ⛔ **This module takes
what a build read out of that record and resolves it; it computes no name and
guesses no suffix.**
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass, field
from types import MappingProxyType

from studyforge.corpus.placement import AUDIO_DIRNAME
from studyforge.render.markup import escape_attribute
from studyforge.render.page.assets import AUDIO_ATTRIBUTE, Placement

#: The lookup key a renderer holds while it walks: the served section's key, the
#: block indices from that section down, and the item or row inside the block —
#: or `None` for the block as a whole. ⛔ It is `SpeechUnit.position`'s tuple and
#: is never spelled a second way.
Position = tuple[str, tuple[int, ...], "int | None"]


@dataclass(frozen=True, slots=True)
class Narration:
    """Every clip this page links, by where the element that plays it sits.

    ⭐ A value, not a service: it is built once per page and read while the page
    is composed, so no renderer holds a placement decision or a filename.
    """

    #: `position -> the href the page writes`, already relative to this page.
    hrefs: Mapping[Position, str] = field(default_factory=dict)

    @classmethod
    def of(cls, clips: Mapping[Position, str], placement: Placement) -> Narration:
        """Return the narration for one page, resolving each filename to an href.

        ⛔ **`Placement.media` is asked once per clip and never bypassed** — the
        profile knows where a unit's audio was placed and nothing here does.
        ⚠️ A clip whose filename is blank is the same answer as no clip at all:
        the record has an entry and synthesis has not produced one, and a page
        that linked `""` would give the reader a control that loads the page
        itself.
        """
        resolved = {
            position: placement.media(AUDIO_DIRNAME, filename)
            for position, filename in dict(clips).items()
            if isinstance(filename, str) and filename.strip()
        }
        return cls(MappingProxyType(resolved))

    def attribute(
        self,
        section: str,
        block_path: tuple[int, ...],
        sub_index: int | None = None,
    ) -> str:
        """Return the audio attribute for one element, with its leading space, or `''`.

        ⭐ The leading space is here rather than at every call site: a renderer
        writing `<p{audio}>` cannot then emit `<p >` for an unnarrated paragraph,
        which would be a golden page that differs by one character per block for
        no reason a reader could see (R10 makes that a diff somebody has to read).
        """
        href = self.hrefs.get((section, tuple(block_path), sub_index))
        if not href:
            return ""
        return f' {AUDIO_ATTRIBUTE}="{escape_attribute(href)}"'

    def __bool__(self) -> bool:
        """Whether this page narrates anything at all."""
        return bool(self.hrefs)


#: The narration of a page that has none. ⛔ A value rather than `None`, so every
#: renderer below calls the same method and no module grows a branch on whether
#: narration exists — which is the branch that would be forgotten in one renderer
#: and leave one block type silently unnarrated.
SILENT = Narration(MappingProxyType({}))
