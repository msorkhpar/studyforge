r"""A corpus's narration as release volumes: packed by its owner, restored by a reader.

**What it does.** Carries narration out of git for a corpus that does not
commit its clips. `volumes` packs the clips the narration record locates into
split, stored zip volumes with a `SHA256SUMS`; `scripts` renders the two
restore scripts (`sh` and PowerShell) a packed corpus carries; `upload` builds
the one `gh release create` command the owner runs, and its dry run.

**How you use it.**

    studyforge narrate <root> --pack <dir> --tag narration-1.0.0
    studyforge narrate <root> --upload <dir> --tag narration-1.0.0 --dry-run
    sh .studyforge/narration-release/restore.sh        # a reader, in a clone

**Depends on.** `narrate.synth` for the record and `corpus.placement` for the
generated root; the standard library otherwise. ⛔ Nothing here opens a socket:
the restore scripts fetch, and `gh` uploads, each on a person's own request.

## ⛔ Narration stays optional

⭐ A reader who never restores has a complete site: pages, practices, quizzes,
contents and progress need no clip, and a page whose clips are absent is the
state `narrate.playable` already names. Restoring adds the voice and nothing else.

## ⛔ Where the clips land

⭐ A restore writes each clip at `<corpus root>/<where>/<filename>`, the record's
own entry: the directory `studyforge narrate` wrote it into, which is the unit's
audio directory under the corpus's placement profile. A site built at the
corpus root plays it with no rebuild.
"""

from __future__ import annotations

from studyforge.narrate.release.scripts import (
    DEFAULT_TAG,
    RELEASE_DIR,
    RESTORE_PS1,
    RESTORE_SH,
    restore_scripts,
    valid_tag,
    write_scripts,
)
from studyforge.narrate.release.upload import Upload, UploadRefused, plan_upload, run_upload
from studyforge.narrate.release.volumes import (
    PART_BYTES,
    SUMS,
    VOLUME,
    Packed,
    PackRefused,
    clips_of,
    pack,
    read_sums,
)

#: ⛔ The package's whole public surface.
__all__ = [
    "DEFAULT_TAG",
    "PART_BYTES",
    "RELEASE_DIR",
    "RESTORE_PS1",
    "RESTORE_SH",
    "SUMS",
    "VOLUME",
    "PackRefused",
    "Packed",
    "Upload",
    "UploadRefused",
    "clips_of",
    "pack",
    "plan_upload",
    "read_sums",
    "restore_scripts",
    "run_upload",
    "valid_tag",
    "write_scripts",
]
