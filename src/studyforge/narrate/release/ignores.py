r"""The ignore files that keep a released corpus's restored clips out of git.

**What it does.** A corpus that delivers its clips as a release restores them
into the checkout, and git must read them as ignored or every restore leaves
the tree dirty. Where a placement's media sits under one generated directory
its onboarding wrote that rule; where the media is enclosed by one generated
directory per source directory (`sibling`) no single file can hold it, so the
pack writes one inside each `study/` directory that holds clips.

**How you use it.** `media_ignores(root)` returns the `IgnoreFile`s the
corpus's placement names for the clips its record locates;
`write_media_ignores(root, files)` writes them and returns their paths.
`studyforge narrate <root> --pack` does both.

**Depends on.** `corpus.placement` for what each profile answers, `corpus.manifest`
for the placement and what the content policy classifies, `volumes` for the
clips the record locates. ⛔ It composes no path (R4): every directory comes
from the record, and every home from the profile.

## ⛔ Never the root ignore file, and never an unclassified file

⭐ A file written inside a generated directory is a file `validate` reads: one
the manifest classifies nowhere is an `unclassified` finding, so a pack refuses,
before it writes a byte, a corpus whose manifest does not classify the file it
would add, and names the glob to declare.
"""

from __future__ import annotations

from pathlib import Path, PurePosixPath

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.manifest import MANIFEST_FILENAME, RAISES, load
from studyforge.corpus.manifest.content.policy import Classification
from studyforge.corpus.placement import IgnoreFile, PlacementError, profile_for
from studyforge.narrate.release.volumes import PackRefused, clips_of, require_released_policy


def media_ignores(root: Path | str) -> tuple[IgnoreFile, ...]:
    """Return the ignore files the corpus's placement names for its clips, or refuse.

    ⛔ Raises `PackRefused` for a manifest that does not read, a placement that
    cannot place a clip's directory, and a file the manifest would leave
    unclassified. An empty answer is a placement whose one ignore file
    onboarding wrote.
    """
    base = Path(root)
    require_released_policy(base)
    try:
        manifest = load(base / MANIFEST_FILENAME)
        directories = {PurePosixPath(member).parent for member, _ in clips_of(base)}
        files = profile_for(manifest.placement).media_ignore_files(directories)
    except PersonalDataLeak, PackRefused:
        raise  # ⛔ R7's refusal, and the clips' own, are never swallowed or re-worded.
    except PlacementError as refused:
        raise PackRefused(str(refused)) from None
    except RAISES as refused:
        raise PackRefused(f"the corpus's {MANIFEST_FILENAME} does not read: {refused}") from None
    unclassified = [
        one.home.as_posix()
        for one in files
        if manifest.content.classify(one.home.as_posix()) is Classification.UNCLASSIFIED
    ]
    if unclassified:
        raise PackRefused(
            f"the ignore file(s) {unclassified} that keep the restored clips out of git "
            f"are declared by no include, exclude or not_material glob of {MANIFEST_FILENAME}; "
            f"declare them in content.not_material, with a reason, and pack again"
        )
    return files


def write_media_ignores(root: Path | str, files: tuple[IgnoreFile, ...]) -> tuple[str, ...]:
    """Write `files` into the corpus at `root`; return the paths written or changed.

    ⭐ A file that already holds every line is left as it is, and one that holds
    other lines keeps them and gains the missing ones.
    """
    written: list[str] = []
    for one in files:
        path = Path(root) / one.home
        have = path.read_text(encoding="utf-8").splitlines() if path.is_file() else []
        missing = [line for line in one.lines if line not in have]
        if path.is_file() and not missing:
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        appended = "".join(f"{line}\n" for line in (*have, *missing))
        text = appended if path.is_file() else one.text()
        path.write_text(text, encoding="utf-8", newline="\n")
        written.append(one.home.as_posix())
    return tuple(written)
