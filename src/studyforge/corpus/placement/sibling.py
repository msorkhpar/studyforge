"""`sibling` — artifacts land beside the source file they were generated from.

**What it does.** Places a unit's page, audio, images, video and practice in the
directory holding that unit's `origin`, named from the unit's own stem.

**How you use it.** `profile_for("sibling")`.

**Depends on.** `profile`, `names`, `locations`.

## Why this profile exists

⭐ **It is what lets the framework enhance a repository instead of restructuring
it** (R3). The Java corpus's reader already knows their way around
`16-streams-api/`; a generated site that moved their material somewhere else
would be a site they had to learn twice. So the page appears beside the
`README` it was made from, and the `README` is untouched.

## The directories are dot-suffixed, and that is not cosmetic

⛔ **Many units share one directory here**, so `audio/` cannot be a
subdirectory the way it is under `tree` — twenty units would collide in one
folder and no clip could be told from another. Each unit's media sits in
`<stem>.audio/`, `<stem>.images/`, `<stem>.video/` and `<stem>.practice/`, so
every artifact of one unit sorts together beside its page and beside its
source, and a reader deleting a unit deletes one contiguous run of names.

⚠️ **`origin` is required, and its absence is refused rather than guessed
around** (R6). "Beside the source file" has no answer for a unit with no source
file, and inventing a directory would put generated output somewhere the corpus
owner never agreed to (R3).
"""

from __future__ import annotations

from studyforge.corpus.placement.locations import ContainerLocations, UnitLocations
from studyforge.corpus.placement.names import (
    AUDIO_DIRNAME,
    IMAGES_DIRNAME,
    PRACTICE_DIRNAME,
    VIDEO_DIRNAME,
    container_page_name,
    unit_page_name,
    unit_stem,
)
from studyforge.corpus.placement.profile import Profile, origin_directory, register


class SiblingProfile(Profile):
    """Output beside the source file it was generated from."""

    name = "sibling"
    describes = "each artifact beside the source file it was generated from"

    def unit(self, address, ordinal, title, *, origin=None, label=None) -> UnitLocations:
        """Where one unit's artifacts go, beside its own source file."""
        directory = origin_directory(origin, address, "unit")
        stem = unit_stem(ordinal, title, label)
        return UnitLocations(
            page=directory / unit_page_name(ordinal, title, label),
            audio=directory / f"{stem}.{AUDIO_DIRNAME}",
            images=directory / f"{stem}.{IMAGES_DIRNAME}",
            video=directory / f"{stem}.{VIDEO_DIRNAME}",
            practice=directory / f"{stem}.{PRACTICE_DIRNAME}",
        )

    def container(self, address, titles, *, origin=None) -> ContainerLocations:
        """Return the container's page, beside the container's own source file."""
        return ContainerLocations(
            page=origin_directory(origin, address, "container") / container_page_name(titles)
        )


SIBLING = register(SiblingProfile())
