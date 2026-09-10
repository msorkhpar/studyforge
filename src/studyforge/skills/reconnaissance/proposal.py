r"""The draft `corpus.json` — a proposal, and every place it had to choose.

**What it does.** Turns what reconnaissance measured into a manifest a person
can edit, and raises an `Uncertainty` for every field the material did not
determine.

**How you use it.** `draft(inventory, record, capability)` returns
`(manifest, uncertainties)`.

**Depends on.** `inventory`, `record`, `capability`, `report`. ⛔ Not on
`corpus.manifest` — this writes a **draft for a person**, and a draft that had
to satisfy the reader would be unable to leave a field open.

## ⛔ It proposes. It does not decide.

⚠️ **The level vocabulary is the clearest case.** This skill can measure that a
corpus has two levels of grouping; it cannot know whether the outer one is
called a *section*, a *part*, a *chapter*, a *module* or a *group*, and §4 says
the names are the corpus's own. So it proposes generic names and **asks**.

⭐ A proposal a person edits is worth more than a decision they have to notice
was made.

## ⚠️ Where the numbers here come from

Every default below is a measurement on real material rather than a taste:

- **`variants` is `[]` until something says otherwise.** Three of the four
  designed shapes have one variant. A skill that proposed two would be fitting
  the exception.
- **`exercises` follows `capability`**, and *false* is a complete answer.
- **`placement` follows whether the material shares its directories with
  anything else.** `sibling` puts a page beside the file it was made from,
  which is right when a reader already knows the layout (R3); `tree` is right
  when the material is only prose and has no layout worth preserving.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import PurePosixPath

from studyforge.skills.reconnaissance.capability import Capability
from studyforge.skills.reconnaissance.inventory import Inventory
from studyforge.skills.reconnaissance.record import Record
from studyforge.skills.reconnaissance.report import Uncertainty

#: What this skill calls the levels it found, pending a person naming them.
#: ⚠️ **Measured conventions rather than invented placeholders**: of the four
#: designed source shapes, the two flat ones name their single level `course`
#: and `group`, and the two-level one names its levels `section` and `module`.
#: ⛔ Still proposed and still asked about — §4 rules the vocabulary is the
#: corpus's own — but a proposal that matches what real corpora chose is a
#: proposal a person more often just accepts.
FLAT_LEVEL = "course"
GROUPED_LEVEL = "group"
NESTED_LEVELS = ("section", "module")

#: Everything a slug loses. ⛔ Not only accents — see `_collisions`.
SLUG_STRIP = re.compile(r"[^a-z0-9]+")


def slugify(title: str) -> str:
    """Return the address a title would produce, if anybody derived one.

    ⛔ Used **only** to detect collisions. §6 rules an address is recorded,
    never derived, and this skill records what the document said.
    """
    return SLUG_STRIP.sub("-", (title or "").lower()).strip("-")


def draft(
    inventory: Inventory, record: Record | None, capability: Capability
) -> tuple[dict, list[Uncertainty]]:
    """Return `(draft manifest, what it had to guess)`."""
    open_questions: list[Uncertainty] = []
    levels = _levels(record, open_questions)
    include, exclude = _content(inventory, record)
    manifest = {
        "corpus_api": 1,
        "source": inventory.root.name,
        "title": _title(record, inventory),
        "levels": levels,
        "variants": [],
        "exercises": capability.graded,
        "placement": _placement(inventory, capability),
        "content": {"include": include, "exclude": exclude},
    }
    open_questions += list(_choices(manifest, inventory, record, capability))
    return manifest, open_questions


def _levels(record: Record | None, open_questions: list[Uncertainty]) -> list[str]:
    """How many **container** levels the record evidences, and what to call them.

    ⛔ **A grouping is not automatically a second level, and getting this wrong
    costs an entire ingestion.** A record that names three groups of units has
    **one** container level; a record whose units sit inside modules which sit
    inside sections has **two**. Both look like "it has groups".

    ⭐ The signal that separates them is **ordinal depth**, and it is written
    down by the author in both measured corpora:

    | | groups | ordinals | container levels |
    |---|---|---|---|
    | ISO-8583 | 3, as headings | `1.` … `16.`, restarting per group | **1** (`group`) |
    | Java-senior | 10, as bare lines | `1.1.` and `1.1.1.` | **2** (`section`, `module`) |

    ⚠️ Java's group is *already inside* its ordinals — every entry under "Java
    Fundamentals" begins `1.` — so counting the group again would produce three
    levels for a two-level corpus. ISO's groups are **not** in its ordinals, so
    there the group is the level.
    """
    if record is None:
        open_questions.append(
            Uncertainty(
                question="how deep is the hierarchy?",
                why="nothing records a grouping, so only a flat reading is defensible",
                settles_it="confirm one level, or point at the document that groups the units",
            )
        )
        return [FLAT_LEVEL]
    depth = _container_depth(record)
    if depth > len(NESTED_LEVELS):
        # ⛔ Said out loud rather than truncated. Returning two names for a
        # corpus whose ordinals evidence more levels would be this skill
        # smoothing over an uncertainty to look finished.
        open_questions.append(
            Uncertainty(
                question=f"the ordinals evidence {depth} container levels — all containers?",
                why=(
                    f"the deepest ordinal on a linked unit has {depth + 1} components; "
                    f"this skill has proposed names for {len(NESTED_LEVELS)} levels"
                ),
                settles_it=(
                    "name every level, or say which ordinal components are headings "
                    "*inside* a unit rather than containers around it"
                ),
            )
        )
    if depth >= 2:
        return list(NESTED_LEVELS[:depth])
    return [GROUPED_LEVEL if record.groups else FLAT_LEVEL]


def _container_depth(record: Record) -> int:
    """How many container levels the record's own ordinals and groups evidence."""
    tiers = max((len(e.ordinal.split(".")) for e in record.entries if e.ordinal), default=1)
    return max(1, (tiers - 1) + (0 if _group_is_in_ordinal(record) else int(bool(record.groups))))


def _group_is_in_ordinal(record: Record) -> bool:
    """Say whether all of a group's entries share one leading ordinal component.

    ⚠️ When they do, the author has already encoded the group in the numbering
    and counting it as a separate level double-counts it.
    """
    if not record.groups:
        return False
    leading: dict[str, set[str]] = {}
    for entry in record.entries:
        if entry.group and entry.ordinal:
            leading.setdefault(entry.group, set()).add(entry.ordinal.split(".")[0])
    return bool(leading) and all(len(seen) == 1 for seen in leading.values())


def _title(record: Record | None, inventory: Inventory) -> str:
    """Return the corpus's own name, taken from the record's own first heading.

    ⚠️ Not the filename. `README` is not what anybody calls their course, and a
    title is one of the few things a curriculum document always states outright.
    """
    if record is not None and record.title:
        return record.title
    return inventory.root.name


def _content(inventory: Inventory, record: Record | None) -> tuple[list[str], list[str]]:
    """Return what to read and what to leave out, as patterns a person can check."""
    if record is None:
        directories = sorted(
            {
                PurePosixPath(p.relative_to(inventory.root)).parent.as_posix()
                for p in inventory.material
            }
        )
        return [f"{d}/*.md" if d != "." else "*.md" for d in directories], []
    listed = {PurePosixPath(target) for target in record.order}
    patterns = sorted(
        {
            f"{p.parent.as_posix()}/*{p.suffix}" if p.parent.as_posix() != "." else f"*{p.suffix}"
            for p in listed
        }
    )
    everything = {p.relative_to(inventory.root).as_posix() for p in inventory.material}
    return patterns, sorted(everything - set(record.order) - {record.path.as_posix()})


def _placement(inventory: Inventory, capability: Capability) -> str:
    """`sibling` where the reader already knows the layout, `tree` otherwise."""
    return "sibling" if capability.source_files or not inventory.flat else "tree"


def _choices(
    manifest: dict, inventory: Inventory, record: Record | None, capability: Capability
) -> Iterator[Uncertainty]:
    """Every field above that was chosen rather than measured."""
    yield Uncertainty(
        question=f"are these the right names for the levels — {manifest['levels']}?",
        why=(
            f"the material shows {len(manifest['levels'])} level(s) of grouping; "
            f"§4 rules the vocabulary is the corpus's own and this skill cannot know it"
        ),
        settles_it="replace them with the words this corpus uses for its own parts",
    )
    yield Uncertainty(
        question="is this one variant of the material, or several?",
        why="nothing in the tree distinguishes two renderings of the same unit",
        settles_it=(
            "name the variants if a unit exists in more than one form (a language, "
            "a difficulty). ⭐ One is the common case and an empty list is correct for it"
        ),
    )
    yield Uncertainty(
        question=f"is {manifest['placement']!r} the right placement?",
        why=(
            f"chosen because the material {
                'shares its directories with source code'
                if capability.source_files
                else 'stands alone'
            }"
        ),
        settles_it=(
            "'sibling' puts each page beside the file it was made from, which is "
            "right when a reader already knows the layout (R3); 'tree' puts "
            "everything under one generated root"
        ),
    )
    if record is not None:
        yield from _collisions(record)


def _collisions(record: Record) -> Iterator[Uncertainty]:
    """Titles that would become one address if anybody derived one.

    ⚠️ **Measured, and the ruling's own example was wrong.** E10 said accents
    collide — `Café` and `Cafe`. They do not: an accent is a non-alphanumeric,
    so it collapses to a **separator**, and those two give `caf` and `cafe`.
    ⭐ The class that actually occurs is **punctuation**: `'Streams: an API'`
    and `'Streams, an API'` both give `streams-an-api`. A skill built for the
    accent case would miss the case that happens.

    ⛔ Reported, never repaired: §6 rules an address recorded rather than
    derived precisely so this is somebody's decision.
    """
    # ⚠️ Counted by **entry**, not by distinct title. Two units in different
    # containers legitimately share a title — measured, 7 titles used twice
    # across two mirrored series — and a corpus-wide derived slug maps both to
    # one address. Requiring the titles to *differ* would miss exactly that.
    seen: dict[str, list[str]] = {}
    for entry in record.entries:
        seen.setdefault(slugify(entry.title), []).append(entry.title)
    collided = {slug: titles for slug, titles in seen.items() if len(titles) > 1 and slug}
    if collided:
        sample = list(collided.items())[:2]
        yield Uncertainty(
            question=f"{len(collided)} title(s) would produce one address — is that a problem?",
            why=f"distinct titles slugify alike, e.g. {sample}",
            settles_it=(
                "record a distinct address for each, or confirm they are in "
                "different containers where the collision does not arise. ⚠️ "
                "Teaching material that covers the same topics for two audiences "
                "collides by construction — measured at 15 of 38 units in one corpus"
            ),
        )
