r"""Where an adapter writes every file, computed once so no adapter retypes it.

**What it does.** Turns *(corpus root, address, variant, unit, kind, ordinal)*
into the exact paths `studyforge validate` will walk — the manifest, each
container map, each unit directory, each archive document — plus the staging
path §6 requires a writer to build at before it moves anything into place.

**How you use it.** `Layout(root, archive_dir)`, then ask it for a path:

    layout = Layout(root, archive_dir="archive")
    layout.manifest                                   # <root>/corpus.json
    layout.container_map(address)                     # .../container.json
    layout.document(address, "prose", 3, "lesson", 2)

**Depends on.** `address` (for `Address`, `unit_name` and `require_ordinal`)
and `corpus.container`/`corpus.manifest` for the two filenames they own.
⛔ Not on `validate`: this module says where to *write*, `validate` says
whether what was written is right, and a writer that imported its own judge
would be checking itself.

## ⛔ Why this is framework code and not four lines in every adapter

⚠️ R19: **anything a second source would have to retype is a hole in the
skills.** Path arithmetic is the purest instance — `raw/<variant>/unit-03/
lesson-2.json` is five joins, four of which are silent when wrong. An adapter
that writes to `unit-3/` instead of `unit-03/` produces a tree `validate`
reports as *unit missing*, at the reader rather than at the writer.

## ⛔ The two names below are re-derived, and that is the ruled outcome

⚠️ `ARCHIVE_DIR` and the `raw/` segment are owned by `validate.corpus`, which
puts neither on a package surface. **Ruling 101's table:** a name that is not
on the owner's `__all__` is not shared — export it, or re-derive it. Exporting
is outside this task's `Owns`, so they are re-derived here **and pinned
behaviourally**: `tests/studyforge/skills/adapter/test_layout.py` lays out a
tree with this module and asserts `validate` reads exactly the documents it
wrote. ⛔ A literal compared against the same literal would agree with itself.

⚠️ `unit_name` is *not* re-derived. It is on `studyforge.address.__all__`, so
the same ruling's other row applies and it is imported.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from studyforge.address import Address, require_ordinal, unit_name
from studyforge.archive.document import KINDS
from studyforge.corpus.container import CONTAINER_FILENAME
from studyforge.corpus.manifest import MANIFEST_FILENAME

#: The archive directory §6 leaves to the corpus, and the value every fixture
#: and every check in this repository uses today. ⚠️ A default, never a
#: constant a caller is forced to accept: `Layout` takes it as a field, so a
#: corpus that puts its archive elsewhere changes one argument.
ARCHIVE_DIR = "archive"

#: The directory under a container that holds its documents, by variant.
#: ⚠️ One variant per container (SF-05), so this is one directory and not a
#: search.
RAW_DIR = "raw"

#: What a document file is called. ⛔ The `kind` half is a **closed set** —
#: `archive.document.KINDS` — and this module refuses anything else rather
#: than writing a file `validate` will not recognise as a document at all.
DOCUMENT_SUFFIX = ".json"


class LayoutError(ValueError):
    """A path this module will not compute, because what was written would be unreadable.

    ⛔ The message names the field and the permitted class, never the offending
    value (R7): an adapter's first caller is a person's own script, and any
    string in it can be an absolute path.
    """


@dataclass(frozen=True, slots=True)
class Layout:
    """Every path one corpus's adapter writes, derived from its root."""

    root: Path
    archive_dir: str = ARCHIVE_DIR

    def __post_init__(self) -> None:
        """Normalise the root, and refuse an archive directory that is not one segment."""
        object.__setattr__(self, "root", Path(self.root))
        if not isinstance(self.archive_dir, str) or not self.archive_dir:
            raise LayoutError("archive_dir must be a non-empty str naming one directory")
        if "/" in self.archive_dir or "\\" in self.archive_dir or self.archive_dir.startswith("."):
            raise LayoutError(
                "archive_dir must be a single directory name under the corpus root, "
                "with no separator and no leading dot"
            )

    @property
    def manifest(self) -> Path:
        """The corpus manifest — the first file `validate` reads and the only one it requires."""
        return self.root / MANIFEST_FILENAME

    @property
    def archive(self) -> Path:
        """The archive root: every container map lives somewhere beneath it."""
        return self.root / self.archive_dir

    @property
    def staging(self) -> Path:
        """Where §6 says to build before moving anything into place.

        ⛔ Beside the archive rather than inside it. `validate` walks the
        archive with `rglob`, so a half-written tree left *inside* it is a tree
        the next run reports on — and the failure then reads as the reader's
        rather than the writer's.
        """
        return self.root / f".{self.archive_dir}-staging"

    def container_dir(self, address: Address | list | tuple) -> Path:
        """Return the directory holding one container's map — which **is** its address (§6)."""
        return self.archive / _address(address).key

    def container_map(self, address: Address | list | tuple) -> Path:
        """One container's map file."""
        return self.container_dir(address) / CONTAINER_FILENAME

    def variant_dir(self, address: Address | list | tuple, variant: str) -> Path:
        """Return the directory holding one container's documents for one variant."""
        if not isinstance(variant, str) or not variant:
            raise LayoutError("variant must be a non-empty str")
        return self.container_dir(address) / RAW_DIR / variant

    def unit_dir(self, address: Address | list | tuple, variant: str, unit: int) -> Path:
        """One unit's directory. ⚠️ `unit_name` owns the zero padding, not this module."""
        return self.variant_dir(address, variant) / unit_name(unit)

    def document(
        self,
        address: Address | list | tuple,
        variant: str,
        unit: int,
        kind: str,
        ordinal: int,
    ) -> Path:
        """One archive document.

        ⛔ `kind` is checked against a closed set here rather than left to the
        writer. A file named `chapter-1.json` lands in a unit directory,
        parses as JSON, and is invisible to every check `validate` runs on
        documents — the one failure shape this layout can prevent outright.
        """
        return self.unit_dir(address, variant, unit) / document_name(kind, ordinal)

    def relative(self, path: Path) -> str:
        """`path` as a report may name it: relative to the root, posix, never absolute (R7)."""
        try:
            return path.relative_to(self.root).as_posix()
        except ValueError:
            return path.name


def document_name(kind: str, ordinal: int) -> str:
    """Return the filename one document takes: `lesson-1.json`, `practice-3.json`."""
    if kind not in KINDS:
        raise LayoutError(f"kind must be one of {list(KINDS)}")
    return f"{kind}-{require_ordinal(ordinal)}{DOCUMENT_SUFFIX}"


def _address(address: Address | list | tuple) -> Address:
    """Accept what an archive document carries — a list of slugs — as well as an `Address`."""
    return address if isinstance(address, Address) else Address(address)
