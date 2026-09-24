r"""`--pack` and `--upload`: the narrate verb's two release requests, and what each prints.

**What it does.** `pack_command` packs a corpus's recorded clips into release
volumes, writes the restore scripts into the corpus, and prints what it wrote
and the upload's dry run to type next. `upload_command` checks a release
directory and prints the upload it would make (`--dry-run`), or hands that one
command to `gh`.

**How you use it.** Through `cli.main`: `studyforge narrate <root> --pack
<dir> --tag <tag>` and `studyforge narrate <root> --upload <dir> --tag <tag>
[--dry-run]`. Each function returns `(lines, exit code)`.

**Depends on.** `narrate.release` for the work, and `validate` for the exit
codes. ⛔ Neither request builds a narration client or reaches the service.

## The line format

⭐ `<verb> <subject>  <detail>`, the narrate report's shape. ⛔ The release
directory is named as it was typed and every corpus path relative to the
corpus root, so nothing printed carries a home directory (R7).

## ⛔ The exit codes

`0` done; `1` refused, with the sentence that says why and nothing written or
published; for a real upload, `gh`'s own exit code.
"""

from __future__ import annotations

from studyforge.narrate.release import (
    PackRefused,
    UploadRefused,
    pack,
    plan_upload,
    run_upload,
    valid_tag,
    write_scripts,
)
from studyforge.validate.report import INVALID, OK

#: What a tag no script may carry is told.
BAD_TAG = (
    "a release tag is letters, digits, dots, dashes and underscores, and starts with "
    "a letter or a digit; nothing was packed"
)

#: What a dry run says it did not do.
DRY_RUN = "dry run: nothing was uploaded. Run the same command without --dry-run to publish"

#: What a pack says the owner does next, and that it is the owner's to do.
NEXT = (
    "next    commit the restore scripts, then publish with --upload (see --dry-run first); "
    "nothing is uploaded until you run it"
)


def pack_command(root: str, out: str, tag: str) -> tuple[list[str], int]:
    """Pack the corpus at `root` into `out` under `tag`, and write its restore scripts."""
    if not valid_tag(tag):
        return [f"refused {BAD_TAG}"], INVALID
    try:
        packed = pack(root, out)
    except PackRefused as refused:
        return [f"refused {refused}"], INVALID
    written = write_scripts(root, tag)
    lines = [
        f"packed  {packed.clips} clip(s), {packed.clip_bytes} byte(s), "
        f"into {len(packed.volumes)} volume(s) in {out}",
    ]
    lines += [
        f"volume  {volume.name}  {volume.size} byte(s)  sha256 {volume.sha256}"
        for volume in packed.volumes
    ]
    lines += [f"wrote   {where}" for where in written]
    lines.append(NEXT)
    lines.append(f"upload  studyforge narrate {root} --upload {out} --tag {tag} --dry-run")
    return lines, OK


def upload_command(root: str, out: str, tag: str, *, dry_run: bool) -> tuple[list[str], int]:
    """Check the release in `out` and print it (`dry_run`), or publish it through `gh`."""
    try:
        upload = plan_upload(root, out, tag)
        if dry_run:
            return [*upload.lines(), DRY_RUN], OK
        return [], run_upload(upload)
    except UploadRefused as refused:
        return [f"refused {refused}"], INVALID
