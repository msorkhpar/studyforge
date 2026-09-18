"""`sibling` — artifacts land in a declared subdirectory beside their source file.

**What it does.** Places a unit's page in `<source directory>/study/`, and every
kind of its own files — audio, images, video, practice and attachments — in
`<source directory>/study/<kind>/<stem>/`, named from its container's address
and the unit's own stem (`names.contained_stem`).

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

## ⛔ Beside the source file means beside it in `study/`, not loose in it (`W323`)

⚠️ **"Beside the source file" was read as *in the same directory, unqualified*,
and that is what a reader met.** Measured on the first corpus: one source
directory held its sources, one page per source **and** one media directory per
source, interleaved in one listing; a source file sitting at the repository
root put its page and its media at the repository root. ⛔ Enhancing a
repository and burying its material are not the same thing, and the second is
what the unqualified reading delivered.

⭐ **So one declared segment, `names.STUDY_DIRNAME`, holds everything this
profile writes into a source directory**, and that directory's own listing goes
back to being its own files plus one entry. ⛔ **The segment is declared once
and composed nowhere** (`W322`): every consumer asks this profile, and the page,
the media and the container page all come back already carrying it.

## The media is under one directory per KIND, not one per unit (`W323`)

⛔ **Many units share one `study/`**, so a unit's clips cannot simply be
`audio/` — twenty units would collide in one folder and no clip could be told
from another. ⭐ The stem discriminates one level lower instead:
`study/audio/<stem>/`, one directory per kind and one per unit inside it. So a
source directory's `study/` lists its pages and at most five directories,
whatever the unit count.

⚠️ **The cost, stated rather than hidden: a unit's artifacts no longer sort as
one contiguous run**, which the dot-suffixed `<stem>.audio/` shape did give.
⭐ That was a property of a listing nobody wanted to read; the kinds are a
listing somebody does. ⛔ Deleting one unit is now one page plus one directory
per kind, and `UnitLocations.directories` is what names them — never a glob a
caller composes.

⚠️ **`origin` is required, and its absence is refused rather than guessed
around** (R6). "Beside the source file" has no answer for a unit with no source
file, and inventing a directory would put generated output somewhere the corpus
owner never agreed to (R3).
"""

from __future__ import annotations

from pathlib import PurePosixPath

from studyforge.corpus.placement.locations import ContainerLocations, UnitLocations
from studyforge.corpus.placement.names import (
    ATTACHMENTS_DIRNAME,
    AUDIO_DIRNAME,
    IMAGES_DIRNAME,
    PRACTICE_DIRNAME,
    STUDY_DIRNAME,
    UNIT_MEDIA_DIRNAMES,
    UNIT_SUFFIX,
    VIDEO_DIRNAME,
    contained_stem,
    container_page_name,
)
from studyforge.corpus.placement.profile import Profile, origin_directory, register


class SiblingProfile(Profile):
    """Output in a declared subdirectory beside the source file it was generated from."""

    name = "sibling"
    describes = "each artifact in a study/ directory beside the source file it was generated from"

    def study_dir(self, origin, address, what: str = "artifact") -> PurePosixPath:
        """Return `<source directory>/study` — the one directory this profile writes into.

        ⛔ **Every path this profile answers with goes through here** (`W323`),
        so the declared segment is joined in one place and no caller, no build
        and no test composes it. ⚠️ `origin` is refused before it is joined:
        `origin_directory` is what keeps a generated directory from being
        created outside the source root.
        """
        return origin_directory(origin, address, what) / STUDY_DIRNAME

    def unit(self, address, ordinal, title, *, origin=None, label=None) -> UnitLocations:
        """Where one unit's artifacts go, in the `study/` directory beside its own source file."""
        directory = self.study_dir(origin, address, "unit")
        stem = contained_stem(address, ordinal, title, label)
        return UnitLocations(
            page=directory / f"{stem}{UNIT_SUFFIX}",
            audio=directory / AUDIO_DIRNAME / stem,
            images=directory / IMAGES_DIRNAME / stem,
            video=directory / VIDEO_DIRNAME / stem,
            practice=directory / PRACTICE_DIRNAME / stem,
            attachments=directory / ATTACHMENTS_DIRNAME / stem,
        )

    def container(self, address, titles, *, origin=None) -> ContainerLocations:
        """Return the container's page, in the `study/` directory beside its own source file."""
        return ContainerLocations(
            page=self.study_dir(origin, address, "container") / container_page_name(titles)
        )

    def media_ignore_lines(self) -> tuple[str, ...]:
        """`study/audio/` and its siblings, one per kind, unanchored because the material is.

        ⭐ **This is Ruling 91's cheapest half.** Under this profile the
        generated names are the unit's own stem, so a corpus cannot enumerate
        them — one measured `sibling` build wrote 79 artifacts, 67 of them
        content-hash-named, and `content.exclude` refuses globs by design.
        `.gitignore` takes them, which is why the ignore declaration is where
        this belongs and `content` never was.

        ⚠️ **Unanchored, because the material is**: a corpus has one `study/`
        per source directory and no way to say in advance which directories
        those are. ⭐ **`W323` narrowed what that costs.** The rule was `*.audio/`
        — a bare stem suffix, which a repository keeping its own `lecture.audio/`
        would have had git ignore. It now carries this profile's own declared
        segment in front of it, so it matches only inside a directory this
        framework writes.

        ⛔ **These lines have no home** (`ignore_home`), so they are only ever
        refused by `ignore_file`, never written.
        """
        return tuple(f"{STUDY_DIRNAME}/{kind}/" for kind in UNIT_MEDIA_DIRNAMES)

    def ignore_home(self) -> None:
        """None: this profile's media is enclosed by many generated directories, not one.

        ⚠️ **`W323` changed the reason and not the answer.** A `study/`
        directory *is* generated and *does* enclose the media beneath it — so
        the old reason, that nothing but the repository's root ignore file
        encloses it, is no longer the true one. ⛔ What is still true is that
        there is one such directory **per source directory**, an `IgnoreFile`
        has one home, and a build that wrote an ignore file into each of them
        is a write this profile cannot make (`W242`). The root ignore file
        stays the one thing never edited (R3).
        """
        return None


SIBLING = register(SiblingProfile())
