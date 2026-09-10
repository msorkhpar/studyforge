r"""What is actually on disk: files, directories, and the groups a name implies.

**What it does.** Walks a source tree once and answers the questions that need
no interpretation — how many files, of what kinds, how deep, and whether a flat
directory's filenames carry a prefix that partitions it.

**How you use it.** `take(root)` returns an `Inventory`. `prefix_groups(names)`
answers the filename question on its own.

**Depends on.** `report`, and the standard library.

## ⛔ A prefix partition is a cross-check, never the source

⚠️ **This is the correction the ISO integration paid for, and it is the part
that generalises.** A flat directory whose names carry a prefix — `1.md`,
`s1.md`, `c1.md` — does encode a grouping. ⛔ But reading the names is
**derivation**, and §6 prices derivation at one link in eight going nowhere.
The grouping is almost always *also written down* somewhere a human reads, and
⭐ **reading that document is a record**.

**Measured, 2026-09-09:** ISO's `src/` holds 41 files and **zero**
directories, three groups distinguished only by prefix — **and** its
`README.md` records the same three groups in the author's own words. The two
partitions agree exactly. ⛔ So `record.py` looks for the document first, and
what this module produces is the thing that must **agree** with it.

⚠️ A skill that proposes the regex has produced a plausible manifest for that
corpus and an unjustifiable one for the next.

## What counts as material

⛔ **Enumerate the legal, never the illegal.** `MATERIAL_SUFFIXES` is a closed
set: a file this skill does not recognise is **reported**, not swept in and not
silently dropped. An ignore list would be an open set, and the unforeseen
extension would be admitted without anybody deciding.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from studyforge.skills.reconnaissance.report import Observation, Uncertainty

#: Suffixes this skill reads as teaching material. ⛔ Closed, and widened by a
#: decision rather than by a file appearing.
MATERIAL_SUFFIXES = (".md", ".markdown", ".rst", ".txt", ".adoc")

#: Directories that are never material: tooling, state, and generated output.
#: ⚠️ Not an "ignore list" in the sense the docstring refuses — these are named
#: because they are *known infrastructure*, and anything not named here is
#: still classified rather than skipped.
NOT_MATERIAL = (
    ".git",
    ".idea",
    ".vscode",
    "node_modules",
    "__pycache__",
    "graphify-out",
    ".studyforge",
    "target",
    "build",
    "dist",
    ".venv",
)

#: A leading ordinal, with or without an alphabetic series prefix: `1.md`,
#: `s1.md`, `c11.md`, `01-java-basics`. ⭐ The series letter is captured
#: separately from the number because they answer different questions — which
#: group, and which position in it.
NAMED_ORDINAL = re.compile(r"^(?P<series>[A-Za-z]*)(?P<ordinal>\d+)(?P<rest>[-_. ].*|$)")


@dataclass
class Inventory:
    """One walk of a source tree."""

    root: Path
    material: list[Path] = field(default_factory=list)
    directories: list[Path] = field(default_factory=list)
    unrecognised: list[Path] = field(default_factory=list)

    @property
    def depth(self) -> int:
        """The deepest directory nesting any material file sits at."""
        return max((len(p.relative_to(self.root).parts) - 1 for p in self.material), default=0)

    @property
    def flat(self) -> bool:
        """Is every material file in one directory? ⚠️ ISO's shape, and SPARQL's."""
        return self.depth <= 1

    def named(self) -> list[str]:
        """Every material file's name, sorted — the input to `prefix_groups`."""
        return sorted(p.name for p in self.material)


def take(root: Path) -> Inventory:
    """Walk `root` once, classifying every file as material or not."""
    inventory = Inventory(root=Path(root))
    for path in sorted(inventory.root.rglob("*")):
        parts = path.relative_to(inventory.root).parts
        if any(part in NOT_MATERIAL or part.startswith(".") for part in parts[:-1]):
            continue
        if path.is_dir():
            if path.name not in NOT_MATERIAL and not path.name.startswith("."):
                inventory.directories.append(path)
        elif path.suffix.lower() in MATERIAL_SUFFIXES:
            inventory.material.append(path)
        elif not path.name.startswith("."):
            inventory.unrecognised.append(path)
    return inventory


def prefix_groups(names: list[str]) -> dict[str, list[str]]:
    """Partition filenames by the series letters their leading ordinal carries.

    ⚠️ Returns `{"": [...]}` for names with no series letter, which is the
    common case and not a failure — a corpus can be one group.
    """
    groups: dict[str, list[str]] = {}
    for name in names:
        match = NAMED_ORDINAL.match(Path(name).stem)
        if match is None:
            groups.setdefault("?", []).append(name)
        else:
            groups.setdefault(match.group("series").lower(), []).append(name)
    return groups


def observe(inventory: Inventory) -> Iterator[Observation | Uncertainty]:
    """Report the tree, and the one thing about it that needs a person."""
    yield Observation("material files", str(len(inventory.material)))
    yield Observation("directories holding material", str(len(inventory.directories)))
    yield Observation("deepest nesting of a material file", str(inventory.depth))
    groups = prefix_groups(inventory.named()) if inventory.flat else {}
    if len(groups) > 1:
        sizes = " + ".join(str(len(v)) for _, v in sorted(groups.items()))
        yield Observation(
            "filename prefixes partition the flat directory",
            f"{len(groups)} groups, {sizes}",
        )
        # ⛔ Reported as a cross-check that needs a record, never as the answer.
        yield Uncertainty(
            question="is the grouping the filename prefixes imply the real one?",
            why=(
                f"{len(inventory.material)} files in one directory, "
                f"{len(groups)} prefix groups ({sizes}); nothing in the "
                f"filesystem expresses the grouping"
            ),
            settles_it=(
                "a document that records the grouping in the author's words — a "
                "README, a table of contents, an index. If one exists this skill "
                "uses it and keeps the prefixes as a check that must agree; if "
                "none exists, confirm the groups by hand before ingesting"
            ),
        )
    if inventory.unrecognised:
        yield Uncertainty(
            question=f"are these {len(inventory.unrecognised)} file(s) material?",
            why=(
                "their suffixes are outside "
                f"{list(MATERIAL_SUFFIXES)}, so this skill did not read them"
            ),
            settles_it=(
                "name them in the manifest's 'content.exclude' if they are not "
                "material, or say which suffix should be read as material"
            ),
        )
