r"""Whether a file the record links is cut into regions, each of which is a unit.

**What it does.** Reads one linked file's ATX headings and says whether they cut
it into sub-file units (a unit's `origin` may be `{path, section}`),
and if not, why not, in words a person can check.

**How you use it.** `cut(root, target)` returns a `Regions`. Its `sections` are
the exact heading texts that open each region, in file order; `why` is `None`
when the file is cut, and the reason when it is not.

**Depends on.** `studyforge.validate.headings`, and the standard library.
⭐ **Deliberately the validator's heading scan and not a second regex here:**
`check_completeness` bounds a region with that scan, so a section this module
proposes is one the validator resolves to exactly one region, by construction
of the same reading rather than by two readers agreeing by luck.

## ⛔ A file's headings are regions only when they cut the WHOLE file

The unit depth is the shallowest depth that carries **two or more** headings.
Anything shallower may only be a title above the first region. ⚠️ A shallower
heading *after* a region would end it early (a region ends at the next heading
of the same or shallower depth), leaving text that belongs to no unit, so that
file is not proposed. ⛔ **Every section must be unique among all the file's
headings**, or the manifest is refused — a duplicate is named here
rather than proposed and refused later.

⚠️ **The shape alone does not make a container.** A unit with two subsections
has the same shape. `grouping` decides by position first; this answers only the
second question, and `record.observe` asks a person about every container it
proposes.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from pathlib import Path

from studyforge.validate.headings import headings


@dataclass(frozen=True, slots=True)
class Regions:
    """What one linked file's headings make of it."""

    path: str
    depth: int
    sections: tuple[str, ...]
    why: str | None

    @property
    def cut(self) -> bool:
        """Say whether the file is cut into regions, each a proposed unit."""
        return self.why is None


def cut(root: Path, target: str) -> Regions:
    """Read `target` under `root` and say whether its headings are regions."""
    try:
        text = (Path(root) / target).read_text(encoding="utf-8")
    except OSError, UnicodeDecodeError:
        return Regions(target, 0, (), "it could not be read as UTF-8 text")
    found = headings(text)
    depths = Counter(heading.depth for heading in found)
    shared = sorted(depth for depth, count in depths.items() if count >= 2)
    if not shared:
        return Regions(target, 0, (), "no heading depth in it occurs twice, so it is one unit")
    depth = shared[0]
    first = next(index for index, heading in enumerate(found) if heading.depth == depth)
    late = [heading.text for heading in found[first:] if heading.depth < depth]
    if late:
        return Regions(
            target,
            depth,
            (),
            f"a heading shallower than its regions follows one ({late[0]!r}), "
            f"so its regions do not cut the whole file",
        )
    sections = tuple(heading.text for heading in found if heading.depth == depth)
    seen = Counter(heading.text for heading in found)
    repeated = [section for section in sections if seen[section] != 1 or not section]
    if repeated:
        return Regions(
            target,
            depth,
            (),
            f"the section {repeated[0]!r} does not occur exactly once, "
            f"and a region must be named by a heading that does",
        )
    return Regions(target, depth, sections, None)
