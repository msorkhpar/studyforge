r"""Served, whether a site's narration clips are on disk is answered from the disk.

**What it does.** Recognises a request for the clip signal a narrated page links
(`render.pageassets.CLIPS_NAME`, in a corpus's `.studyforge/assets/`), and answers
it with the state the disk is in NOW rather than the state the file last recorded.

**How you use it.** `serve.routes.assets` asks both, after a request has resolved
to a file:

    if is_signal(target):
        body = told(target, private)    # the PRESENT or ABSENT body

**Depends on.** `corpus.placement` for the generated root's, the asset
directory's and the audio directory's names and for every registered profile's
ignore home, `narrate.speakable` for the one
parser of a clip's name, and `render.pageassets` for the signal's name and
bodies — a constant and two lines of text, never a renderer. ⛔ Nothing is
written: the file on disk is left as it is.

## ⛔ Why the server answers, rather than serving the file

⭐ **The file is right over `file://` for as long as whatever last moved the
clips wrote it** — a build, the release pack, a restore. ⚠️ Anything else that
moves them leaves it stale: clips deleted by hand, or a site committed while
the author's clips were still on disk. ⭐ A server can simply look, so a served
page is right whichever of those happened, and a restore is heard on the next
page load with no build between.

⭐ **The look is the served root that holds this `.studyforge/`**, searched for a
file in a directory named `audio` whose name is a clip's (spec §8.2), stopped at
the first clip found. ⛔ **A file the server would not serve does not count**
(`private`), so a serve with narration off, which withholds every clip, never
tells a page that its clips are there.

## ⛔ Where the look goes is the placement's answer, on every profile

⭐ **Each registered profile names where its clips can be**, and the look goes
there and nowhere else. The server does not ask which profile a corpus has: it
asks every one, because a site is recognised by its signal, not by a manifest.

- ⭐ **A profile with an ignore home keeps every clip below that home's
  directory.** Its clips are uncommitted (`UNCOMMITTED_DIRNAMES`) and its ignore
  lines reach nothing outside that directory, so a clip anywhere else would be a
  clip its own rules commit. `tree`'s home is `.studyforge/.gitignore`: its clips
  are under `.studyforge/`, which is looked in whole.
- ⭐ **A profile with none can put them anywhere in the source**, so the rest of
  the root is walked. `sibling` puts them in each `study/audio/<stem>/`.

⛔ **Every dot-directory the placement did not name stays skipped**, in both
looks: `.git`, a toolchain's `.sdkman`, an editor's `.claude` hold no clip this
framework placed, and a walk into them is what makes the look slow. ⚠️ Skipping
every dot-directory, `.studyforge/` included, is how a served `tree` course once
answered `absent` over thousands of clips.

⭐ **Cheap, because it runs on every signal request**: the bounded homes are
looked in first, so a `tree` site with its clips answers from its first unit;
only a site with no clip in any home pays for the walk of its source.
"""

from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path, PurePath, PurePosixPath

from studyforge.corpus.placement import (
    ASSETS_DIRNAME,
    AUDIO_DIRNAME,
    GENERATED_ROOT,
    profile_for,
    registered,
)
from studyforge.narrate.speakable.naming import SpeakableError, parse_clip_name
from studyforge.render.pageassets import ABSENT, CLIPS_NAME, PRESENT, clips_script

#: Whether a resolved file is one the static mount would refuse.
Private = Callable[[Path], bool]


def is_signal(target: Path) -> bool:
    """Whether a resolved file is a corpus's clip signal, `.studyforge/assets/<CLIPS_NAME>`."""
    return (
        target.name == CLIPS_NAME
        and target.parent.name == ASSETS_DIRNAME
        and target.parent.parent.name == GENERATED_ROOT
    )


def told(target: Path, private: Private) -> bytes:
    """Return the signal's body for the disk as it is now, under the site that holds `target`."""
    site = target.parent.parent.parent
    return clips_script(PRESENT if holds_a_clip(site, private) else ABSENT)


def holds_a_clip(site: Path, private: Private) -> bool:
    """Whether any servable clip sits in an audio directory where a placement puts one."""
    homes, anywhere = clip_homes()
    looks = [site / home for home in homes] + ([site] if anywhere else [])
    return any(_holds_a_clip(top, site, private) for top in looks)


def clip_homes() -> tuple[tuple[PurePosixPath, ...], bool]:
    """Return the directories, relative to a served root, that hold every bounded profile's clips.

    ⭐ The second value says whether some profile names no such directory, so its
    clips can be anywhere in the source and the root itself must be walked.
    """
    homes: set[PurePosixPath] = set()
    anywhere = False
    for name in registered():
        home = profile_for(name).ignore_home()
        if home is None:
            anywhere = True
        else:
            homes.add(home.parent)
    return tuple(sorted(homes)), anywhere


def _holds_a_clip(top: Path, site: Path, private: Private) -> bool:
    """Whether a servable clip sits in an audio directory under `top`, dot-directories skipped."""
    for directory, subdirectories, files in os.walk(top):
        subdirectories[:] = sorted(name for name in subdirectories if not name.startswith("."))
        # ⭐ `audio/` under `tree` and `audio/<stem>/` under `sibling`: inside one.
        if AUDIO_DIRNAME not in PurePath(directory).relative_to(site).parts:
            continue
        for name in sorted(files):
            path = Path(directory) / name
            if _is_clip_name(name) and path.is_file() and not private(path):
                return True
    return False


def _is_clip_name(name: str) -> bool:
    """Whether a filename is a narration clip's, by the one parser that mints them."""
    try:
        parse_clip_name(PurePath(name).stem)
    except SpeakableError:
        return False
    return True
