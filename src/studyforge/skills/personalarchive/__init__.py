r"""Personal archive: export a corpus with or without its progress, and import it anywhere.

**What it does.** Packs a corpus root's material into one zip file. The progress record
goes in too when the file is for its owner, and never when it is for sharing. It
unpacks such a file into a corpus root on another machine, or into the same corpus
elsewhere. Material merges file by file and never overwrites. Progress merges practice
by practice, under the rule `SKILL.md` states, and only through
`studyforge.progress`'s public, locked `record_run`.

**How you use it.** Through the skill document beside this file (`SKILL.md`), which
is the procedure:

    python3 -m studyforge.skills.personalarchive export <corpus-root> <archive-file> --for owner
    python3 -m studyforge.skills.personalarchive import <archive-file> <corpus-root>

    from studyforge.skills.personalarchive import OWNER, export, import_archive
    export(root, archive, kind=OWNER)
    import_archive(archive, other_root)

**Depends on.** `studyforge.progress`, reached only through its public surface and only
from this package's `record` and `merge`. Also `corpus.manifest` for the corpus's
identity and depth, `archive.scrub` for R7, and `version` for R9. ⛔ Not on
`generate/`, `serve/` or any adapter (R1). The site is rebuilt afterwards by the
build-and-serve skill, never by this one.

| Module | Owns |
|---|---|
| `merge` | the merge rule and the belief rule, pure |
| `record` | the one door onto `studyforge.progress` |
| `layout` | the archive's members, its manifest (`personal_archive_api`), path and R7 checks |
| `export` | the material walk and the archive write |
| `restore` | the checked unpack, the material merge, the progress merge |
| `cli` | the command line |

## ⛔ Thin, or the finding is against `studyforge.progress`

⭐ **No store is re-implemented here.** Validation, the R7 gate on a record and the
first-pass rule are all the store's own. A merge that `record_run` cannot express
exactly costs at most two runs more than the larger count. That is a stated
limit rather than worked around through the store's private methods.
"""

from __future__ import annotations

from studyforge.skills.personalarchive.export import export
from studyforge.skills.personalarchive.layout import (
    KINDS,
    OWNER,
    PERSONAL_ARCHIVE_API,
    SHARING,
    ArchiveError,
)
from studyforge.skills.personalarchive.merge import (
    MERGED,
    OUTCOMES,
    REFUSED,
    RESTORED,
    UNCHANGED,
    Merge,
    merged,
    refusal,
)
from studyforge.skills.personalarchive.restore import import_archive

#: ⛔ The package's whole public surface.
__all__ = [
    "KINDS",
    "MERGED",
    "OUTCOMES",
    "OWNER",
    "PERSONAL_ARCHIVE_API",
    "REFUSED",
    "RESTORED",
    "SHARING",
    "UNCHANGED",
    "ArchiveError",
    "Merge",
    "export",
    "import_archive",
    "merged",
    "refusal",
]
