r"""A course's own sections of the learner README, and the pictures they show.

**What it does.** Reads the optional directory `docs/learner-readme/` of a course
checkout: `top.md` (placed right after the README's title), `body.md` (placed in
place of the generated "What you get" and "Two ways to use it" sections) and
`shots/` (pictures the two files show). A course without the directory gets the
README it always had, byte for byte.

**How you use it.** `read(root)` returns an `Own`; `write.release` hands its lines to
`learner.Course` and copies its pictures into `.studyforge/images/readme/`.
A picture is linked in the text as `shots/<name>`; the link is rewritten to the
tree's path.

⛔ **What it refuses**, by naming the file: a link to a picture the directory does
not hold, a picture that is not a `.png` or `.webp`, one over 400 KB, or pictures
over 3 MB together. ⭐ The generated command sections (what you need, how to run,
the ports, where your work is kept, the preview) are never replaced, so the start
instructions stay correct whatever the course writes.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from studyforge.skills.execution.standalone import compose

DIRNAME = "docs/learner-readme"
TOP = "top.md"
BODY = "body.md"
SHOTS = "shots"
SHOT_SUFFIXES = (".png", ".webp")
SHOT_MAX_BYTES = 400 * 1024
SHOTS_MAX_BYTES = 3 * 1024 * 1024

_LINK = re.compile(rf"\({SHOTS}/([^)\s]+)\)")


@dataclass(frozen=True, slots=True)
class Own:
    """The lines before the tour, the lines in place of the features, and the pictures."""

    top: tuple[str, ...] = ()
    body: tuple[str, ...] = ()
    shots: tuple[tuple[str, Path], ...] = ()


def _lines(path: Path, held: set[str], used: set[str]) -> tuple[str, ...]:
    if not path.is_file():
        return ()
    text = path.read_text(encoding="utf-8").rstrip("\n")
    for name in _LINK.findall(text):
        if name not in held:
            raise ValueError(f"{DIRNAME}/{path.name} shows {SHOTS}/{name}, which is not there")
        used.add(name)
    text = _LINK.sub(lambda one: f"({compose.IMAGES}/readme/{one.group(1)})", text)
    return (*text.split("\n"), "")


def read(root: Path) -> Own:
    """Return the course's own sections, or an empty `Own` where it has none."""
    where = Path(root) / DIRNAME
    if not where.is_dir():
        return Own()
    pictures = sorted(one for one in (where / SHOTS).glob("*") if one.is_file())
    for one in pictures:
        if one.suffix not in SHOT_SUFFIXES:
            raise ValueError(f"{one.name} is not a picture the README may show: {SHOT_SUFFIXES}")
        if one.stat().st_size > SHOT_MAX_BYTES:
            raise ValueError(f"{one.name} is over {SHOT_MAX_BYTES // 1024} KB")
    if sum(one.stat().st_size for one in pictures) > SHOTS_MAX_BYTES:
        raise ValueError(f"the pictures together are over {SHOTS_MAX_BYTES // 1024} KB")
    held = {one.name for one in pictures}
    used: set[str] = set()
    top = _lines(where / TOP, held, used)
    body = _lines(where / BODY, held, used)
    return Own(top, body, tuple((one.name, one) for one in pictures if one.name in used))
