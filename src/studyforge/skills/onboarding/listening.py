r"""The reader document's narration section: whether a corpus speaks, and how to get its clips.

**What it does.** Renders the `## Narration` section of the reader document
onboarding writes: that narration is optional and the site complete without
it, and, for a corpus that does not commit its clips, the two restore commands
that fetch them from the repository's release.

**How you use it.** `narration_section(manifest)` returns the section's lines;
`artifacts.reader_document` places them after what the corpus offers.

**Depends on.** `corpus.manifest` for `narration` and the media policy, and
`narrate.release` for where the restore scripts sit, read from its constants
and never respelled. ⛔ No I/O.

## ⛔ A pure function of the manifest

⭐ Like the rest of the reader document, this states no figure and reads no
disk: whether clips were packed, and how many, moves after the document is
written and nothing rewrites it. ⭐ What it does state follows from
`corpus.json` alone: whether the corpus is voiced, and whether git carries its
clips.
"""

from __future__ import annotations

from studyforge.corpus.manifest import Manifest
from studyforge.narrate.release import RESTORE_PS1, RESTORE_SH


def narration_section(manifest: Manifest) -> list[str]:
    """Say whether this corpus speaks, and how a reader gets its clips when git does not carry them.

    ⭐ **Narration is optional, and the section says so first**: a reader who never
    fetches a clip has a complete site. ⛔ **The restore commands are in prose, never
    fenced**: every fenced line is run as written from a fresh clone, and a restore
    reaches a release host. The script paths are `narrate.release`'s own constants.
    """
    if not manifest.narration:
        return [
            "## Narration",
            "",
            "This corpus is not narrated, as `corpus.json` records, and the site is",
            "complete without a voice.",
            "",
        ]
    lines = [
        "## Narration",
        "",
        "Narration is optional: the site is complete without it. Pages, practices,",
        "quizzes, contents and progress need no clip; the clips add the voice.",
    ]
    if manifest.media.commits:
        return [
            *lines,
            "This corpus commits its clips, so a clone carries them and nothing needs",
            "fetching.",
            "",
        ]
    return [
        *lines,
        "This corpus does not commit its clips; they are published as release",
        "volumes of this repository. From the root of a clone,",
        f"`sh {RESTORE_SH}` downloads them, checks every volume against",
        "its checksum, puts each clip where its page plays it, and deletes the",
        f"downloaded volumes; on Windows, `powershell -File {RESTORE_PS1}` does",
        "the same. A private repository needs `GITHUB_TOKEN` set, or `gh auth login`.",
        "",
    ]
