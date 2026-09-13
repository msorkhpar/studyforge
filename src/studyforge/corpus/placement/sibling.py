"""`sibling` — artifacts land beside the source file they were generated from.

**What it does.** Places a unit's page, audio, images, video and practice in the
directory holding that unit's `origin`, named from its container's address and
the unit's own stem (`names.contained_stem`).

**How you use it.** `profile_for("sibling")`.

**Depends on.** `profile`, `names`, `locations`.

## Why this profile exists

⭐ **It is what lets the framework enhance a repository instead of restructuring
it** (R3). A consuming corpus's reader already knows their way around
`16-streams-api/`; a generated site that moved their material somewhere else
would be a site they had to learn twice. So the page appears beside the
`README` it was made from, and the `README` is untouched.

## ⛔ Every name carries the container (`W254`)

Two containers whose series mirror each other in one source directory once
placed two units at one path. Every call was correct and the pair was wrong,
and a build replaced pages it had written in the same run. ⭐ The address makes
two containers' names distinct by construction, whatever their ordinals, titles
or labels. ⚠️ The cost: every page and media name of every `sibling` corpus
moves, by exactly that prefix and nothing else.

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
    UNIT_MEDIA_DIRNAMES,
    UNIT_SUFFIX,
    VIDEO_DIRNAME,
    contained_stem,
    container_page_name,
)
from studyforge.corpus.placement.profile import Profile, origin_directory, register


class SiblingProfile(Profile):
    """Output beside the source file it was generated from."""

    name = "sibling"
    describes = "each artifact beside the source file it was generated from"

    def unit(self, address, ordinal, title, *, origin=None, label=None) -> UnitLocations:
        """Where one unit's artifacts go, beside its own source file."""
        directory = origin_directory(origin, address, "unit")
        stem = contained_stem(address, ordinal, title, label)
        return UnitLocations(
            page=directory / f"{stem}{UNIT_SUFFIX}",
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

    def media_ignore_lines(self) -> tuple[str, ...]:
        """`*.audio/` and its three siblings, unanchored because the material is.

        ⭐ **This is Ruling 91's cheapest half.** Under this profile the
        generated names are the unit's own stem, so a corpus cannot enumerate
        them — one measured `sibling` build wrote 79 artifacts, 67 of them
        content-hash-named, and `content.exclude` refuses globs by design.
        `.gitignore` takes them, which is why the ignore declaration is where
        this belongs and `content` never was.

        ⚠️ **The stem suffix is the discriminator and it is not unique to us.**
        A repository that already keeps a directory called `lecture.audio/`
        has one git will now ignore. That is stated here rather than guarded
        against: the alternative is enumerating names that do not exist yet,
        which is the thing this ruling refused.

        ⛔ **These lines have no home** (`ignore_home`), so they are only ever
        refused by `ignore_file`, never written.
        """
        return tuple(f"*.{kind}/" for kind in UNIT_MEDIA_DIRNAMES)

    def ignore_home(self) -> None:
        """None: no generated directory encloses media placed beside the material.

        ⛔ The only file that does is the repository's root ignore file (R3). A
        file inside each unit's media directory would work, and minting one is
        a build's write this profile cannot make (`W242`).
        """
        return None


SIBLING = register(SiblingProfile())
