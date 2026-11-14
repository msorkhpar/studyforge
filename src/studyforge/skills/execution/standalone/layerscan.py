"""What a course image adds to its base, written out as files for the personal-data sweep.

**What it does.** Reads a `docker save` archive of one course image and the layer list of the
base it starts from (`docker image inspect --format '{{json .RootFS.Layers}}'`), and writes
every layer the image adds on top of that base under one folder, for
`python -m studyforge.archive.scrub check`. Layer `N` (counted from the image's bottom layer)
goes to `layer-N/`, every path and link target the layer holds is listed in `layer-N.paths`,
and the image's configuration (labels, environment and the history after the base's) is
written to `config.json`.

**How you use it.** The owner's command list prints it (`publish.scan_commands`):

    python -m studyforge.skills.execution.standalone.layerscan IMAGE_TAR BASE_LAYERS_JSON OUT

**Depends on.** `json` and `tarfile`, and nothing that starts a process.

## ⛔ The base's own content is out of scope

A base image (the serving base, the toolchain's runner and editor) is published by the
toolchain and is its responsibility; its operating-system and package files carry
maintainers' addresses by the thousand and would bury the course's own findings. ⭐ So only
the layers after the base's are written, and an image whose bottom layers are not exactly
the base's is refused rather than swept whole: a sweep of the wrong layers would pass or
fail for a reason that is not the course's. An empty base list (the record names no base)
sweeps every layer.

## ⭐ Every byte that is pushed, not only the final filesystem

A file a layer adds and a later layer deletes is still in the pushed image, so each layer is
written to its own folder and a whiteout deletes nothing. A link is never followed or made;
its target is listed in `layer-N.paths`, where a path that names a home folder is found too.

## ⭐ The current user can delete everything written

Ownership and permissions are never taken from the archive (a layer's files are root's and
often read-only): each file is written fresh with the user's umask, and a path that would
climb out of its folder is listed and never written.
"""

from __future__ import annotations

import json
import sys
import tarfile
from collections.abc import Sequence
from pathlib import Path, PurePosixPath

USAGE = "usage: layerscan IMAGE_TAR BASE_LAYERS_JSON OUT"


class NotOnBase(ValueError):
    """The image's bottom layers are not the base's, so what it adds cannot be told apart."""


def added(diff_ids: Sequence[str], base: Sequence[str]) -> list[int]:
    """The indexes of the layers `diff_ids` adds on top of `base`; ⛔ refused unless a prefix."""
    if list(diff_ids[: len(base)]) != list(base):
        raise NotOnBase(
            f"the image is not built on the base named: its first {len(base)} layer(s) differ"
        )
    return list(range(len(base), len(diff_ids)))


def _inside(name: str) -> PurePosixPath | None:
    """`name` as a relative path that stays inside its folder, or `None` when it would not."""
    parts = [one for one in PurePosixPath(name.lstrip("/")).parts if one not in ("", ".")]
    if not parts or ".." in parts:
        return None
    return PurePosixPath(*parts)


def write_layer(layer: tarfile.TarFile, folder: Path, listing: Path) -> None:
    """Write `layer`'s regular files under `folder` and list every member in `listing`."""
    lines = []
    for member in layer:
        lines.append(f"{member.name} -> {member.linkname}" if member.linkname else member.name)
        where = _inside(member.name)
        if where is None or not member.isfile():
            continue
        target = folder / where
        target.parent.mkdir(parents=True, exist_ok=True)
        source = layer.extractfile(member)
        if source is None:
            continue
        with source, open(target, "wb") as out:
            while chunk := source.read(1 << 20):
                out.write(chunk)
    listing.write_text("\n".join(lines) + "\n", encoding="utf-8", newline="\n")


def _config_after(config: dict, base_layers: int) -> dict:
    """`config` with the history entries that made the base's layers left out."""
    history = config.get("history") or []
    seen = 0
    start = 0
    for index, entry in enumerate(history):
        if seen == base_layers:
            break
        if not entry.get("empty_layer"):
            seen += 1
        start = index + 1
    return {**config, "history": history[start:] if base_layers else history}


def scan_tree(image_tar: Path, base: Sequence[str], out: Path) -> list[int]:
    """Write what the saved image at `image_tar` adds to `base` under `out`; return the layers."""
    try:
        archive = tarfile.open(image_tar)
    except (OSError, tarfile.TarError) as error:
        # ⛔ The refusal names what failed, never the path it was handed (R7).
        raise ValueError(f"the saved image could not be read: {type(error).__name__}") from None
    with archive:
        manifest = json.load(archive.extractfile("manifest.json"))
        if len(manifest) != 1:
            raise ValueError(f"the archive holds {len(manifest)} images; save exactly one")
        entry = manifest[0]
        config = json.load(archive.extractfile(entry["Config"]))
        diff_ids = config["rootfs"]["diff_ids"]
        if len(diff_ids) != len(entry["Layers"]):
            raise ValueError("the archive's layer list and its configuration disagree")
        indexes = added(diff_ids, base)
        out.mkdir(parents=True, exist_ok=True)
        (out / "config.json").write_text(
            json.dumps(_config_after(config, len(base)), indent=1), encoding="utf-8", newline="\n"
        )
        for index in indexes:
            stored = archive.extractfile(entry["Layers"][index])
            with tarfile.open(fileobj=stored, mode="r:*") as layer:
                write_layer(layer, out / f"layer-{index}", out / f"layer-{index}.paths")
    return indexes


def main(argv: Sequence[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    if len(args) != 3:
        print(USAGE, file=sys.stderr)
        return 2
    base = json.loads(Path(args[1]).read_text(encoding="utf-8")) or []
    try:
        indexes = scan_tree(Path(args[0]), base, Path(args[2]))
    except NotOnBase as refused:
        print(f"layerscan: {refused}; stop", file=sys.stderr)
        return 1
    print(f"layerscan: {len(indexes)} layer(s) on top of the base written for the sweep")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
