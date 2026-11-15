r"""The toolchain's build context, copied from its pinned checkout into a learner's tree.

**What it does.** Copies each input root the toolchain's builds name (`vendor.ask`'s
`inputs`) from the checkout into the target, byte for byte, leaving out what an interpreter
wrote beside it, and returns the relative paths it wrote.

**How you use it.**

    copied = copy(checkout, target, asked.inputs)     # ('docker/minimal/Dockerfile', ...)

**Depends on.** `vendor` for its refusal, `VendorRefused`, and the filesystem. ⛔ **It parses
nothing it copies**: the context is copied as bytes (R18).

## ⛔ An input root stays inside the checkout

The inputs arrive as data the toolchain printed. ⛔ **An entry that is empty, absolute or climbs
with `..` is refused before anything is read**: `checkout / "/"` is `/`, so such an entry would
walk the whole disk, or copy what the toolchain never held. ⚠️ So is one string handed where the
list belongs: a string is a sequence of its characters, and its first may be `/`.
"""

from __future__ import annotations

import shutil
from collections.abc import Sequence
from pathlib import Path

from studyforge.archive.scrub import scrub
from studyforge.skills.execution.standalone.vendor import VendorRefused

#: Files the interpreter writes beside an input, never copied.
SKIPPED = ("__pycache__",)


def copy(checkout: Path, target: Path, inputs: Sequence[str]) -> tuple[str, ...]:
    """Copy each input root from `checkout` into `target`, as bytes; return what was written."""
    checkout, target = Path(checkout), Path(target)
    if isinstance(inputs, str):
        raise VendorRefused("the toolchain's inputs must be a list of paths, not one string")
    for entry in inputs:
        if not entry or Path(entry).is_absolute() or ".." in Path(entry).parts:
            raise VendorRefused(f"a toolchain input is outside its checkout: {scrub(entry)}")
    written: list[str] = []
    for entry in inputs:
        source = checkout / entry
        if source.is_file():
            files = [source]
        elif source.is_dir():
            files = sorted(p for p in source.rglob("*") if p.is_file())
        else:
            raise VendorRefused(f"the toolchain names an input it does not hold: {scrub(entry)}")
        for one in files:
            relative = one.relative_to(checkout)
            if any(part in SKIPPED for part in relative.parts) or one.suffix == ".pyc":
                continue
            (target / relative).parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(one, target / relative)
            written.append(relative.as_posix())
    return tuple(sorted(written))
