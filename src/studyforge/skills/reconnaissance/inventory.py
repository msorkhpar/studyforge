r"""What is actually on disk: files, directories, and the groups a name implies.

**What it does.** Walks a source tree once and answers the questions that need
no interpretation — how many files, of what kinds, how deep, and whether a flat
directory's filenames carry a prefix that partitions it.

**How you use it.** `take(root)` returns an `Inventory`. `prefix_groups(names)`
answers the filename question on its own.

**Depends on.** `report`; `installed` for the framework's own generated half;
`studyforge.validate.source` for what the corpus root's
own directories are and which nested repository stores `validate` refuses; and
the standard library.

## ⛔ The framework's own generated half is never this corpus's material

⚠️ **A corpus that has been onboarded carries `studyforge`'s output inside it**
— an adapter package, two generated checks, a reader's document. ⛔ Read as
material, that output makes a re-survey disagree with the first survey about the
corpus, and the disagreement is silent. ⭐ **Two instruments say what is the
framework's, and both already existed.** `installed.generated` reads the record
onboarding wrote, which names every file it wrote; and `enumerated` is
`source_files`, `validate`'s own population, which stops outside what a *build*
writes — the archive above all, which onboarding never recorded because it did
not write it. ⛔ This walk sets both aside, so every later pass measures the
corpus rather than the framework. ⚠️ A corpus nobody onboarded has no record and
no archive, so a first survey is unchanged.

## ⛔ A nested `.studyforge` or `.git` is what `validate` says it is

⭐ **The survey mirrors `validate` rather than keeping a second rule**.
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

from collections.abc import Iterator
from dataclasses import dataclass, field
from pathlib import Path

from studyforge.corpus.manifest import prefix_of
from studyforge.skills.reconnaissance.installed import INSTALL_RECORD, generated
from studyforge.skills.reconnaissance.report import Observation, Uncertainty
from studyforge.validate.source import (
    REPOSITORY_STORE,
    RULE_NESTED_REPOSITORY,
    SKIP_DIRS,
    source_files,
)

#: Suffixes this skill reads as teaching material. ⛔ Closed, and widened by a
#: decision rather than by a file appearing.
MATERIAL_SUFFIXES = (".md", ".markdown", ".rst", ".txt", ".adoc")

#: Directories that are never material: tooling, state, and generated output.
#: ⛔ `.git` and `.studyforge` are not here: they are `validate`'s.
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

#: The key of the names no prefix places. ⭐ No declared prefix can spell it,
#: because a prefix carries no glob character.
UNPLACED = "?"


@dataclass
class Inventory:
    """One walk of a source tree."""

    root: Path
    material: list[Path] = field(default_factory=list)
    directories: list[Path] = field(default_factory=list)
    unrecognised: list[Path] = field(default_factory=list)
    #: ⛔ The nested repository stores `validate` refuses, never entered.
    stores: list[Path] = field(default_factory=list)
    #: ⛔ The framework's own output here, from onboarding's record —
    #: set aside rather than classified, so no pass reads it as this corpus's.
    generated: frozenset[str] = frozenset()
    #: ⛔ The files `validate` will classify here, `source_files`'s own
    #: answer. ⭐ What a build writes — the archive above all — is outside it,
    #: so this survey stops where `validate` stops.
    enumerated: frozenset[str] = frozenset()

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
    """Walk `root` once, classifying every file as material or not.

    ⛔ **A file this framework wrote is set aside, not classified**:
    reading it back as the corpus's material is what made a re-survey disagree
    with the first survey about the corpus.
    """
    root = Path(root)
    scan = source_files(root)
    inventory = Inventory(
        root=root,
        generated=generated(root),
        enumerated=frozenset(p.relative_to(root).as_posix() for p in scan.files),
    )
    reached: list[Path] = []
    own: list[Path] = []
    for path in sorted(root.rglob("*")):
        parts = path.relative_to(root).parts
        if parts[0] in SKIP_DIRS or not all(enters(part) for part in parts[:-1]):
            continue
        if path.is_dir():
            if enters(path.name):
                inventory.directories.append(path)
            continue
        reached.append(path)
        if not _the_corpus_own(inventory, path):
            continue
        own.append(path)
        if path.suffix.lower() in MATERIAL_SUFFIXES:
            inventory.material.append(path)
        elif not path.name.startswith("."):
            inventory.unrecognised.append(path)
    inventory.directories = _holding(inventory, reached, own)
    inventory.stores = list(scan.stores)
    return inventory


def _the_corpus_own(inventory: Inventory, path: Path) -> bool:
    """Whether `path` is the corpus's own file rather than this framework's.

    ⛔ Two instruments, both already in the tree, and neither invented here: the
    install record names what onboarding wrote, and `source_files` names what
    `validate` will classify — so a build's own output, the archive above all,
    is outside it.
    """
    where = path.relative_to(inventory.root).as_posix()
    return where not in inventory.generated and where in inventory.enumerated


def _holding(inventory: Inventory, reached: list[Path], own: list[Path]) -> list[Path]:
    """Drop a directory holding files, none of which is the corpus's own.

    ⚠️ A directory the walk found empty of files stays: it holds nothing of
    anybody's, and a survey that hid it would be reporting a smaller tree than
    the one on disk. ⭐ A dot-file is the corpus's own here even though it is
    neither material nor unrecognised — a directory it occupies is somebody's.
    """
    kept = {parent for path in own for parent in path.parents}
    holding = {parent for path in reached for parent in path.parents}
    return [path for path in inventory.directories if path not in holding - kept]


def enters(name: str) -> bool:
    """Whether the walk enters a directory of this name beneath the root.

    ⭐ **Public because it is the skill's one walk rule**. `capability`
    walks the whole tree rather than the material, and a second, looser rule of
    its own would enter `__pycache__`, `node_modules`, `build` and `target`, so
    a directory this module calls *never material* would supply a corpus's
    graders. ⛔ Two walk rules over one tree disagree
    eventually, and the disagreement is silent — the scaffolded suite's
    walk follows `validate` for the same reason.
    """
    if name == REPOSITORY_STORE:
        return False
    if name in SKIP_DIRS:
        # ⭐ A nested `.studyforge` is a source's own directory, as `validate` walks it.
        return True
    return name not in NOT_MATERIAL and not name.startswith(".")


def prefix_groups(names: list[str]) -> dict[str, list[str]]:
    """Partition filenames by the prefix each name carries, by the manifest's own rule.

    ⭐ **One prefix rule** (`corpus.manifest.prefix_of`): what this survey
    observes is exactly what a `curriculum` declaration's `prefix` would check,
    so an observed partition and a declared cross-check can never disagree
    about a name. ⚠️ `{"": [...]}` holds names that are only a number, the
    common case and not a failure; `UNPLACED` holds the names no prefix places.
    """
    groups: dict[str, list[str]] = {}
    for name in names:
        prefix = prefix_of(name)
        groups.setdefault(UNPLACED if prefix is None else prefix, []).append(name)
    return groups


def observe(inventory: Inventory) -> Iterator[Observation | Uncertainty]:
    """Report the tree, and the one thing about it that needs a person."""
    yield Observation("material files", str(len(inventory.material)))
    yield Observation("directories holding material", str(len(inventory.directories)))
    yield Observation("deepest nesting of a material file", str(inventory.depth))
    # ⭐ Said out loud, because a reader comparing two surveys of one
    # corpus needs to know which of them was reading the framework's own output.
    yield Observation(
        f"files set aside as this framework's own ({INSTALL_RECORD})",
        str(len(inventory.generated)),
    )
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
