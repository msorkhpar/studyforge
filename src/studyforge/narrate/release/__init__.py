r"""A corpus's narration as release volumes: packed by its owner, restored by a reader.

**What it does.** Carries narration out of git for a corpus that does not
commit its clips. `volumes` packs the clips the narration record locates into
split, stored zip volumes with a `SHA256SUMS`; `scripts` renders the two
restore scripts (`sh` and PowerShell) a packed corpus carries; `publish` checks
a pack and prints the one `gh release create` command its owner runs.

**How you use it.**

    studyforge narrate <root> --pack <dir> --tag narration-1.0.0
    studyforge narrate <root> --publish <dir> --tag narration-1.0.0
    sh .studyforge/narration-release/restore.sh        # a reader, in a clone

**Depends on.** `narrate.synth` for the record and `corpus.placement` for the
generated root, `checksum` for the volumes' digests; the standard library
otherwise. ⛔ Nothing here opens a socket or starts a process: a reader's
restore script fetches, and the owner's own `gh` uploads.

## ⛔ Narration stays optional

⭐ A reader who never restores has a complete site: pages, practices, quizzes,
contents and progress need no clip, and a page whose clips are absent is the
state `narrate.playable` already names. Restoring adds the voice and nothing else.

## ⛔ Where the clips land

⭐ A restore writes each clip at `<corpus root>/<where>/<filename>`, the record's
own entry: the directory `studyforge narrate` wrote it into, which is the unit's
audio directory under the corpus's placement profile. Last, it writes `present`
into the clip signal, `.studyforge/assets/narration-clips.js`, which the pack
set to `released`, so a site built at the corpus root plays the clips on its
next page load with no rebuild. A site built into another directory has its own
copies and its own signal, and is built again after a restore.
"""

from __future__ import annotations

from studyforge.narrate.release.publish import Publish, PublishRefused, plan_publish
from studyforge.narrate.release.scripts import (
    CLIP_SUMS,
    DEFAULT_TAG,
    RELEASE_DIR,
    RESTORE_PS1,
    RESTORE_SH,
    SIGNAL,
    VOLUME_SUMS,
    restore_scripts,
    valid_tag,
    write_release_record,
    write_scripts,
    write_signal,
)
from studyforge.narrate.release.volumes import (
    PART_BYTES,
    SUMS,
    VOLUME,
    Packed,
    PackRefused,
    clips_of,
    pack,
    read_sums,
    require_released_policy,
)

#: ⛔ The package's whole public surface.
__all__ = [
    "CLIP_SUMS",
    "DEFAULT_TAG",
    "PART_BYTES",
    "RELEASE_DIR",
    "RESTORE_PS1",
    "RESTORE_SH",
    "SIGNAL",
    "SUMS",
    "VOLUME",
    "VOLUME_SUMS",
    "PackRefused",
    "Packed",
    "Publish",
    "PublishRefused",
    "clips_of",
    "pack",
    "plan_publish",
    "read_sums",
    "require_released_policy",
    "restore_scripts",
    "valid_tag",
    "write_release_record",
    "write_scripts",
    "write_signal",
]
