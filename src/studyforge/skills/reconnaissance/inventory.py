r"""What is actually on disk: files, directories, and the groups a name implies.

**What it does.** Walks a source tree once and answers the questions that need
no interpretation — how many files, of what kinds, how deep, and whether a flat
directory's filenames carry a prefix that partitions it.

**How you use it.** `take(root)` returns an `Inventory`. `prefix_groups(names)`
answers the filename question on its own.

**Depends on.** `report`; `studyforge.validate.source` for what the corpus root's
own directories are and which nested repository stores `validate` refuses; and
the standard library.

## ⛔ A nested `.studyforge` or `.git` is what `validate` says it is (`W272`)

⭐ **The survey mirrors `validate` rather than keeping a second rule** (`W259`).
Only the corpus root's own `SKIP_DIRS` are skipped. A nested `.studyforge` is a
source's own directory, walked like any other. A nested repository store is
never entered, and the stores are `source_files(root).stores`, `validate`'s own
answer, so a store the repository declares output is named by neither. ⛔ Each
is counted and asked about by `validate`'s rule id, so a person who surveys and
then validates never meets that refusal first.

⚠️ **Every other name in `NOT_MATERIAL`, and every other dot-directory, is still
skipped at any depth, unchanged.** `validate` walks those, and the draft's
`not_material` proposal is what speaks for them.

## ⛔ A prefix partition is a cross-check, never the source

⚠️ **This is the correction one integration paid for, and it is the part that
generalises.** A flat directory whose names carry a prefix — `1.md`, `s1.md`,
`c1.md` — does encode a grouping. ⛔ But reading the names is **derivation**,
and §6 prices derivation at one link in eight going nowhere. The grouping is
almost always *also written down* somewhere a human reads, and ⭐ **reading
that document is a record**.

⛔ So `record.py` looks for the document first, and what this module produces
is the thing that must **agree** with it. ⚠️ On the corpus that taught this,
the two partitions agree exactly — see `SKILL.md`, appendix **A1**, which is
the only copy of that measurement.

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
from studyforge.validate.source import RULE_NESTED_REPOSITORY, SKIP_DIRS, source_files

# ⚠️ Not on `studyforge.validate.source`'s surface, so imported from its module (`W272/1`).
from studyforge.validate.source.classification import REPOSITORY_STORE

#: Suffixes this skill reads as teaching material. ⛔ Closed, and widened by a
#: decision rather than by a file appearing.
MATERIAL_SUFFIXES = (".md", ".markdown", ".rst", ".txt", ".adoc")

#: Directories that are never material: tooling, state, and generated output.
#: ⛔ `.git` and `.studyforge` are not here: they are `validate`'s (`W272`).
#: ⚠️ Not an "ignore list" in the sense the docstring refuses — these are named
#: because they are *known infrastructure*, and anything not named here is
#: still classified rather than skipped.
NOT_MATERIAL = (
    ".idea",
    ".vscode",
    "node_modules",
    "__pycache__",
    "target",
    "build",
    "dist",
    ".venv",
)

#: A leading ordinal, with or without an alphabetic series prefix: `1.md`,
#: `s1.md`, `c11.md`, `01-basics`. ⭐ The series letter is captured
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
    #: ⛔ `W272`: the nested repository stores `validate` refuses, never entered.
    stores: list[Path] = field(default_factory=list)

    @property
    def depth(self) -> int:
        """The deepest directory nesting any material file sits at."""
        return max((len(p.relative_to(self.root).parts) - 1 for p in self.material), default=0)

    @property
    def flat(self) -> bool:
        """Is every material file in one directory? ⚠️ Two of four designed shapes."""
        return self.depth <= 1

    def named(self) -> list[str]:
        """Every material file's name, sorted — the input to `prefix_groups`."""
        return sorted(p.name for p in self.material)


def take(root: Path) -> Inventory:
    """Walk `root` once, classifying every file as material or not."""
    inventory = Inventory(root=Path(root))
    for path in sorted(inventory.root.rglob("*")):
        parts = path.relative_to(inventory.root).parts
        if parts[0] in SKIP_DIRS or not all(_enters(part) for part in parts[:-1]):
            continue
        if path.is_dir():
            if _enters(path.name):
                inventory.directories.append(path)
        elif path.suffix.lower() in MATERIAL_SUFFIXES:
            inventory.material.append(path)
        elif not path.name.startswith("."):
            inventory.unrecognised.append(path)
    inventory.stores = list(source_files(inventory.root).stores)
    return inventory


def _enters(name: str) -> bool:
    """Whether the walk enters a directory of this name beneath the root (`W272`)."""
    if name == REPOSITORY_STORE:
        return False
    if name in SKIP_DIRS:
        # ⭐ A nested `.studyforge` is a source's own directory, as `validate` walks it.
        return True
    return name not in NOT_MATERIAL and not name.startswith(".")


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
    yield Observation("nested repository stores validate refuses", str(len(inventory.stores)))
    if inventory.stores:
        names = [store.relative_to(inventory.root).as_posix() for store in inventory.stores]
        yield Uncertainty(
            question=f"are these {len(names)} nested repository store(s) part of the corpus?",
            why=(
                f"validate refuses each as {RULE_NESTED_REPOSITORY}, and this survey "
                f"entered none of them: {names[:6]}"
            ),
            settles_it=(
                "move that repository out of the corpus root, or declare its directory as "
                "output in this repository's ignore rules; its history is never material"
            ),
        )
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
                "the draft proposes a 'content.not_material' glob for each, with its "
                "reason open; or say which suffix should be read as material"
            ),
        )
