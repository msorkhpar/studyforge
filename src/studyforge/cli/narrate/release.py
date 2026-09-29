r"""`--pack` and `--publish`: the narrate verb's two release requests, and what each prints.

**What it does.** `pack_command` packs a corpus's recorded clips into release
volumes, writes the restore scripts into the corpus, and prints what it wrote
and the dry run to type next. `publish_command` is that dry run: it checks a
release directory and the corpus's scripts and prints every asset and the one
`gh release create` command the owner runs to upload them.

**How you use it.** Through `cli.main`: `studyforge narrate <root> --pack
<dir> --tag <tag>`, then `studyforge narrate <root> --publish <dir> --tag
<tag>`. Each function returns `(lines, exit code)`.

**Depends on.** `narrate.release` for the work, and `validate` for the exit
codes. ⛔ Neither request builds a narration client, reaches the service,
starts a process or uploads anything.

## The line format

⭐ `<verb> <subject>  <detail>`, the narrate report's shape. ⛔ The release
directory is named as it was typed and every corpus path relative to the
corpus root, so nothing printed carries a home directory (R7).

## ⛔ The exit codes

`0` done; `1` refused, with the sentence that says why and nothing written.
"""

from __future__ import annotations

from pathlib import Path

from studyforge.narrate.release import (
    SUMS,
    PackRefused,
    PublishRefused,
    media_ignores,
    pack,
    plan_publish,
    valid_tag,
    write_media_ignores,
    write_release_record,
    write_scripts,
)
from studyforge.validate.report import INVALID, OK

#: What a tag no script may carry is told.
BAD_TAG = (
    "a release tag is letters, digits, dots, dashes and underscores, and starts with "
    "a letter or a digit; nothing was packed"
)

#: What the dry run says it did not do, and whose the upload is.
DRY_RUN = (
    "dry run: nothing was uploaded. The command above publishes the release with your "
    "own gh login; run it yourself, from this directory, when you mean to"
)

#: What a pack says the owner does next.
NEXT = "next    commit the files written above, then read the publish dry run below"


def pack_command(root: str, out: str, tag: str) -> tuple[list[str], int]:
    """Pack the corpus at `root` into `out` under `tag`, and write its restore scripts."""
    if not valid_tag(tag):
        return [f"refused {BAD_TAG}"], INVALID
    try:
        ignores = media_ignores(root)
        packed = pack(root, out)
    except PackRefused as refused:
        return [f"refused {refused}"], INVALID
    sums = (Path(out) / SUMS).read_text(encoding="utf-8")
    written = (
        *write_scripts(root, tag),
        *write_release_record(root, sums, packed.clip_sums),
        *write_media_ignores(root, ignores),
    )
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
    lines.append(f"publish studyforge narrate {root} --publish {out} --tag {tag}")
    return lines, OK


def publish_command(root: str, out: str, tag: str) -> tuple[list[str], int]:
    """Check the release in `out` and print what publishing it takes. ⛔ Uploads nothing."""
    try:
        publish = plan_publish(root, out, tag)
    except PublishRefused as refused:
        return [f"refused {refused}"], INVALID
    return [*publish.lines(), DRY_RUN], OK
