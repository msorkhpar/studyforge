r"""The one module a person writes, and it ships as signatures plus a refusal.

**What it does.** Renders `read.py` — the three steps that turn this source's
own material into containers, document fields and a unit count.

**How you use it.** Through `PARTS`. `READ_PART` is this module's whole export.

**Depends on.** `parts.compose` and `plan`. ⛔ Nothing else, and above all not
on anything that reads material: a renderer that knew how to read a source
would be the framework knowing about one (R1).

## ⛔ Why the reading step is the only hand-written module

⚠️ Reading unfamiliar material is genuinely source-specific, and a scaffold
that guessed at it would emit plausible code that reads the wrong thing — which
costs more than an empty function, because it looks finished. ⭐ So the seam is
drawn where the knowledge actually changes: **everything downstream of "here are
the units" is identical for every corpus**, and generating that is what stops
the next integration re-deriving path arithmetic, staging order and the document
build.

## ⛔ Three steps, one module — and the third is why

⚠️ `expected_units` is the count `studyforge validate` cannot make, and it lives
here rather than in `audit` because **counting the source is reading the
source**. ⭐ A scaffold with two hand-written modules has already lost the
property R19 depends on: that a reader can name what is theirs in one breath.

## ⚠️ A refusal, not a stub that returns nothing

⛔ `containers` and `documents` raise, and the message names what to return. An
empty list would let the whole pipeline run and emit an archive with no
material in it — which validates, because there is nothing wrong with it.
"""

from __future__ import annotations

from studyforge.skills.adapter.parts.compose import Part, module
from studyforge.skills.adapter.plan import Plan

#: The step every scaffold leaves to a person: reading a unit's material into
#: blocks. ⭐ Shared by both shapes of `read.py`, so the refusal is worded once.
_DOCUMENTS = [
    "def documents(root: Path, container: Container) -> list[dict]:",
    '    """Return the fields for each document of `container`, in reading order.',
    "",
    "    Each dict is the keyword arguments of `studyforge.archive.document.build`",
    "    minus `source` and `ingested`, which `emit` supplies: `address`,",
    "    `variant`, `unit`, `kind`, `ordinal`, `title`, `blocks`.",
    "",
    "    ⛔ **Every block comes from the block vocabulary** (`studyforge.archive.blocks`).",
    "    A construct the reader does not recognise is reported, never dropped: a",
    "    dropped block is absent from the digest and from the counts alike, so",
    "    nothing downstream can notice it went missing.",
    "",
    "    ⭐ **Markdown material has a reader already**:",
    "    `studyforge.archive.markdown.parse(text)` returns the blocks, and raises",
    "    `MarkdownError` naming what it cannot hold rather than dropping it.",
    "",
    "    ⛔ **Return the source's own material only.** Every exercise the",
    "    authoring pass committed under `exercises/`, code and quiz alike, is",
    "    joined to its unit by `emit` (`studyforge.skills.adapter.practices`),",
    "    which also raises the unit's practice count: reading one here as well",
    "    is kept only when it is that exercise's own document.",
    '    """',
    "    raise NotImplementedError(",
    "        UNWRITTEN.format(",
    '            step="documents",',
    '            what="Return a list of build() keyword dicts, one per document.",',
    "        )",
    "    )",
    "",
    "",
]


def _read(plan: Plan) -> str:
    """Render the one module a person writes: signatures, and a refusal naming what to return.

    ⭐ **Where `corpus.json` declares its record's groups** and the
    corpus has one variant, `containers` and `expected_units` are written from
    the declaration and only `documents` is left to write: the filing is
    manifest data, so a second corpus never retypes it (R19).
    """
    if plan.filed and plan.sole_variant is not None:
        return _declared(plan)
    return module(
        summary="Read this source. ⛔ THE ONE MODULE IN THIS PACKAGE YOU WRITE BY HAND.",
        does=(
            "Turns this repository's material into the two things the archive is made of — "
            "one `Container` per container, and one document's worth of fields per unit. "
            "⛔ Nothing here knows about the archive's layout, its filenames or its digests; "
            "those are the framework's and are already written."
        ),
        uses=(
            "Write the three steps below — two refuse, the third returns None until you "
            "write it. Run the tests beside this package after each one: they fail "
            "carrying the refusal's own message, and pass when the archive validates."
        ),
        depends=(
            "`studyforge.corpus.container` for the `Container` and `Unit` shapes, "
            "`studyforge.address` for the `Address` a container is filed at, and "
            "`studyforge.archive.markdown` for reading Markdown into blocks. "
            "⚠️ Add whatever this source needs — this is the one module where a "
            "source-specific import belongs."
        ),
        body=[
            "",
            "from pathlib import Path",
            "",
            "from studyforge.corpus.container import Container",
            "",
            "#: What every unwritten step says. ⭐ One sentence of what to return, and",
            "#: one of why a guess would be worse than a refusal.",
            "UNWRITTEN = (",
            f'    "{plan.package}.read.{{step}} is not written yet. {{what}} "',
            '    "Until it is, this adapter refuses rather than emitting an archive "',
            '    "that validates and holds the wrong material."',
            ")",
            "",
            "",
            "def containers(root: Path) -> list[Container]:",
            '    """Return one `Container` per container this source records.',
            "",
            "    ⛔ **The address is recorded, never derived** (§6). Read it from whatever",
            "    document records this corpus's own structure; do not slugify a title.",
            "",
            "    ⭐ Each container carries `origin` — the path of the file the material",
            "    was read from, verbatim — and one `Unit` per unit, with its declared",
            "    practice count.",
            '    """',
            "    raise NotImplementedError(",
            "        UNWRITTEN.format(",
            '            step="containers",',
            '            what="Return a list of studyforge.corpus.container.Container.",',
            "        )",
            "    )",
            "",
            "",
            *_DOCUMENTS,
            "def expected_units(root: Path) -> dict[str, int] | None:",
            '    """Return `{address key: unit count}` counted from the SOURCE, or None.',
            "",
            "    ⛔ **This is the check `studyforge validate` cannot make.** Count from",
            "    whatever records this corpus's curriculum, and never from the archive: a",
            "    number taken from the thing being checked has checked nothing.",
            "",
            "    ⚠️ It lives here rather than in `audit` because counting the source is",
            "    reading the source, and this is the one module that reads.",
            "",
            "    ⚠️ `None` means unwritten. The audit reports it as an unchecked claim and",
            "    exits non-zero; it is not a way to switch the check off.",
            '    """',
            "    return None",
        ],
    )


def _declared(plan: Plan) -> str:
    """Render `read.py` for a corpus whose manifest files its units."""
    return module(
        summary="Read this source. ⛔ THE ONE MODULE IN THIS PACKAGE YOU WRITE BY HAND.",
        does=(
            "Turns this repository's material into the two things the archive is made of. "
            "⭐ `containers` and `expected_units` are already written: `corpus.json` "
            "declares where the curriculum is recorded and what each group is filed at, "
            "and `studyforge.skills.adapter.curriculum` reads it and refuses a tree that "
            "disagrees. `documents` is yours."
        ),
        uses=(
            "Write `documents`. Run the tests beside this package after it: they fail "
            "carrying the refusal's own message, and pass when the archive validates. "
            "⛔ Change the filing in `corpus.json`, never here."
        ),
        depends=(
            "`studyforge.corpus.manifest` for the declaration, "
            "`studyforge.skills.adapter.curriculum` for the filing and the name count, and "
            "`studyforge.corpus.container` for `Container`. ⭐ "
            "`studyforge.archive.markdown` reads Markdown into blocks for `documents`; "
            "⚠️ add whatever else it needs to read this source's material."
        ),
        body=[
            "",
            "from pathlib import Path",
            "",
            "from studyforge.corpus.container import Container",
            "from studyforge.corpus.manifest import MANIFEST_FILENAME, load",
            "from studyforge.skills.adapter.curriculum import counted, filed",
            "",
            "#: What every unwritten step says. ⭐ One sentence of what to return, and",
            "#: one of why a guess would be worse than a refusal.",
            "UNWRITTEN = (",
            f'    "{plan.package}.read.{{step}} is not written yet. {{what}} "',
            '    "Until it is, this adapter refuses rather than emitting an archive "',
            '    "that validates and holds the wrong material."',
            ")",
            "",
            "#: The one variant this corpus declares.",
            f"VARIANT = {plan.sole_variant!r}",
            "",
            "",
            "def containers(root: Path) -> list[Container]:",
            '    """Return one `Container` per group `corpus.json` declares, filed by its record.',
            "",
            "    ⛔ **The address is recorded, never derived** (§6): the manifest records",
            "    it, and the filing refuses when the record or a declared prefix disagrees.",
            "    ⚠️ `ingested` is replaced by `emit` with the run's own date.",
            '    """',
            "    manifest = load(Path(root) / MANIFEST_FILENAME)",
            "    return [",
            "        Container(",
            "            address=group.address,",
            "            titles=group.titles,",
            "            variant=VARIANT,",
            '            ingested="1970-01-01",',
            "            units=group.units,",
            "            origin=group.origin,",
            "        )",
            "        for group in filed(root, manifest)",
            "    ]",
            "",
            "",
            *_DOCUMENTS,
            "def expected_units(root: Path) -> dict[str, int] | None:",
            '    """Return `{address key: unit count}` counted from the names on disk, or None.',
            "",
            "    ⭐ **The second reading**: every included file carrying a declared prefix,",
            "    or under a linked level, every included file in each linked file's",
            "    directory, taken without the record. ⚠️ `None` while a declared group",
            "    has no prefix, and the audit then reports an unchecked claim — count",
            "    that group here.",
            '    """',
            "    return counted(Path(root), load(Path(root) / MANIFEST_FILENAME))",
        ],
    )


#: The one part of a scaffold that a person writes.
READ_PART = Part(
    where="{package}/read.py",
    step=5,
    why="the one module you write. Signatures and a refusal that names what to return",
    generated=False,
    render=_read,
)
