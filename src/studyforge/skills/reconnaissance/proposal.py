r"""The draft `corpus.json` — a proposal, and every place it had to choose.

**What it does.** Turns what reconnaissance measured into a manifest a person
can edit, and raises an `Uncertainty` for every field the material did not
determine.

**How you use it.** `draft(inventory, record, capability)` returns
`(manifest, uncertainties)`.

**Depends on.** `inventory`, `record`, `capability`, `furniture`, `runtimes`,
`report`, and `studyforge.address` for what a slug is. ⛔ Not on
`corpus.manifest`'s reader — this writes a **draft for a person**, and a draft
that had to satisfy the reader would be unable to leave a field open.

⚠️ **Open is not the same as refused.** A field this skill *does* fill is
filled with a value the manifest reader accepts, and the question beside it
says it was chosen. A `source` of `""` or `variants` of `[]` left nothing open:
it made every draft unpromotable until a person retyped both (R19).

## ⛔ It proposes. It does not decide.

⚠️ **The level vocabulary is the clearest case.** This skill can measure that a
corpus has two levels of grouping; it cannot know whether the outer one is
called a *section*, a *part*, a *chapter*, a *module* or a *group*, and §4 says
the names are the corpus's own. So it proposes generic names and **asks**.

⭐ A proposal a person edits is worth more than a decision they have to notice
was made.

## ⚠️ Where the numbers here come from

Every default below is a measurement on real material rather than a taste:

- **`variants` is one variant, `prose`, until something says otherwise.**
  Three of the four designed shapes have one variant, and a skill that proposed
  two would be fitting the exception. ⭐ The word is the one this framework's
  own worked examples use (`docs/authoring/examples.md`), so four corpora do not
  invent four words for it. ⛔ A filing key, never a language.
- **`source` is the slug of the curriculum record's title**. A
  worktree, a clone and an archive of one commit carry that title byte for
  byte, and their directories are named anything. ⛔ Never the directory's
  name, never git: a remote URL is off-limits (R7), and an archive has no git.
  With no record it is `corpus`. Both are asked about.
- **Exclusion is only for what an include reads.** Everything else the draft
  leaves unread is proposed as a `not_material` glob with its reason open
  (`furniture`).
- **`exercises` follows `capability`**, and *false* is a complete answer.
- **`runtimes` follows what the material evidences**, only beside
  `exercises: true`, and the draft then declares `corpus_api` 4 so it reads
  back. ⛔ Prose gets no key; `runtimes` holds the evidence and the rule.
- **`placement` follows whether the material shares its directories with
  anything else.** `sibling` puts a page in a `study/` directory beside the
  file it was made from, which is right when a reader already knows the layout
  (R3); `tree` is right when the material is only prose and has no layout worth
  preserving.
"""

from __future__ import annotations

import re
from collections.abc import Iterator
from pathlib import PurePosixPath

from studyforge.address import slugify as slug_of
from studyforge.skills.onboarding import NOT_MATERIAL_API  # the owner's version for the key
from studyforge.skills.reconnaissance.capability import Capability
from studyforge.skills.reconnaissance.furniture import Furniture, propose
from studyforge.skills.reconnaissance.inventory import Inventory
from studyforge.skills.reconnaissance.record import Record
from studyforge.skills.reconnaissance.report import Uncertainty
from studyforge.skills.reconnaissance.runtimes import propose as evidenced

#: What this skill calls the levels it found, pending a person naming them.
#: ⚠️ **Measured conventions rather than invented placeholders**: of the four
#: designed source shapes, the flat ones name their single level `course` and
#: `group`, and the two-level one names its levels `section` and `module`.
#: ⛔ Still proposed and still asked about — §4 rules the vocabulary is the
#: corpus's own — but a proposal that matches what real corpora chose is a
#: proposal a person more often just accepts.
FLAT_LEVEL = "course"
GROUPED_LEVEL = "group"
NESTED_LEVELS = ("section", "module")

#: The one variant a draft proposes. ⚠️ A filing and presentation key and
#: nothing more (§4): it never says what language a fence is or what runs.
#: ⛔ The word is the framework's, stated once in spec §4 (`Q9`), not a
#: placeholder a corpus replaces.
SINGLE_VARIANT = "prose"

#: The `source` proposed when there is no record, or its title has no slug —
#: a title written entirely outside ASCII. ⚠️ Still proposed and asked about.
UNNAMED_SOURCE = "corpus"

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
    furniture = propose(inventory.root, include, exclude)
    runtimes = evidenced(capability)
    content: dict[str, object] = {"include": include, "exclude": exclude}
    if furniture.entries:
        content["not_material"] = [dict(entry) for entry in furniture.entries]
    manifest = {
        "corpus_api": max(NOT_MATERIAL_API if furniture.entries else 1, runtimes.api),
        "source": _source(record),
        "title": _title(record, inventory),
        "levels": levels,
        "variants": [SINGLE_VARIANT],
        "exercises": capability.graded,
        **({"runtimes": list(runtimes.names)} if runtimes.names else {}),
        "placement": _placement(inventory, capability),
        "content": content,
    }
    open_questions += list(_choices(manifest, inventory, record, capability))
    open_questions += list(runtimes.questions())
    open_questions += list(_unread(furniture))
    return manifest, open_questions


def _levels(record: Record | None, open_questions: list[Uncertainty]) -> list[str]:
    """How many **container** levels the record evidences, and what to call them.

    ⛔ **A grouping is not automatically a second level, and getting this wrong
    costs an entire ingestion.** A record that names three groups of units has
    **one** container level; a record whose units sit inside modules which sit
    inside sections has **two**. Both look like "it has groups".

    ⭐ The signal that separates them is **ordinal depth**, and the author
    writes it down in both measured corpora. ⛔ `SKILL.md` step 6 holds that
    table and is the only copy of it.

    ⚠️ Where every entry of a group shares one leading ordinal component, the
    group is *already inside* the numbering, and counting it again produces
    three levels for a two-level corpus. Where the ordinals restart per group
    without naming it, the group **is** the level.
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


def _source(record: Record | None) -> str:
    """Return a slug of the curriculum record's title, the corpus's own recorded name.

    ⛔ **Not the surveyed directory's name**: a worktree named `int` and
    a clone named after the repository drafted two sources for one corpus. The
    slug rule is the address package's (`studyforge.address.slugify`), so what this proposes is
    what the manifest reader calls a slug.
    """
    title = record.title if record is not None else ""
    return slug_of(title) or UNNAMED_SOURCE


def _title(record: Record | None, inventory: Inventory) -> str:
    """Return the corpus's own name, taken from the record's own first heading.

    ⚠️ Not the filename. `README` is not what anybody calls their course, and a
    title is one of the few things a curriculum document always states outright.
    """
    if record is not None and record.title:
        return record.title
    return inventory.root.resolve().name


def _content(inventory: Inventory, record: Record | None) -> tuple[list[str], list[str]]:
    """Return what to read and what to leave out, as patterns a person can check.

    ⛔ **An include glob never matches the curriculum record.** The record sits
    beside the units it lists often enough — a root `README.md` linking a root
    chapter — and a directory wildcard over it makes the record a unit. So a
    directory whose wildcard would catch the record is listed file by file.
    ⚠️ The record is still not *declared* anything here; what it is stays a
    person's question.
    """
    if record is None:
        directories = sorted(
            {
                PurePosixPath(p.relative_to(inventory.root)).parent.as_posix()
                for p in inventory.material
            }
        )
        return [f"{d}/*.md" if d != "." else "*.md" for d in directories], []
    listed = {PurePosixPath(target) for target in record.order}
    patterns = sorted({_pattern(target, record.path) for target in listed})
    everything = {p.relative_to(inventory.root).as_posix() for p in inventory.material}
    unlisted = everything - set(record.order) - {record.path.as_posix()}
    # ⛔ Withheld only where an include would read it; the rest is `furniture`'s.
    return patterns, sorted(
        where for where in unlisted if any(PurePosixPath(where).full_match(p) for p in patterns)
    )


def _pattern(target: PurePosixPath, record: PurePosixPath) -> str:
    """Return the directory wildcard for `target`, or `target` itself if it would catch `record`."""
    parent = target.parent.as_posix()
    wildcard = f"{parent}/*{target.suffix}" if parent != "." else f"*{target.suffix}"
    return target.as_posix() if PurePosixPath(record).full_match(wildcard) else wildcard


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
        question=f"is {manifest['source']!r} the right source slug?",
        why=(
            "derived from the curriculum record's title, the same in every checkout"
            if record is not None
            else "nothing records the corpus's name, so a placeholder was proposed"
        ),
        settles_it="replace it with the slug this corpus is filed under, if it has one",
    )
    yield Uncertainty(
        question="is this one variant of the material, or several?",
        why="nothing in the tree distinguishes two renderings of the same unit",
        settles_it=(
            "name the variants if a unit exists in more than one form (a language, "
            f"a difficulty). ⭐ One is the common case, and {SINGLE_VARIANT!r} is its name"
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
            "'sibling' puts each page in a 'study' directory beside the file it "
            "was made from, which is right when a reader already knows the layout;"
            " 'tree' puts everything under one generated root"
        ),
    )
    if record is not None:
        yield from _collisions(record)


def _unread(furniture: Furniture) -> Iterator[Uncertainty]:
    """Ask for every reason the proposed `not_material` globs leave open.

    ⛔ A proposal that stands down says so by name, even when it proposes nothing.
    """
    if not furniture.entries:
        if furniture.stands_down:
            yield Uncertainty(
                question="the not_material proposal stood down: is nothing here furniture?",
                why=f"no glob was proposed, and {furniture.stands_down}",
                settles_it=(
                    "survey the corpus root as its own git working tree, outside any other "
                    "repository's ignored directory, or declare content.not_material by hand"
                ),
            )
        return
    ignore = "read" if furniture.consulted else "not read, as this is not a git working tree"
    yield Uncertainty(
        question=(
            f"are these {len(furniture.entries)} glob(s) never material, and why? "
            f"{furniture.globs[:6]}"
        ),
        why=(
            f"of {furniture.judged} file(s) validate will classify (git's ignore rules "
            f"{ignore}), these match no include and no exclude; every reason is open. "
            f"{furniture.covered} file(s) a glob the manifest declares already covers "
            f"are not re-proposed"
        ),
        settles_it=(
            "give each glob its reason in promote's reasons mapping, keyed by the glob; "
            "a reason is a person's, never generated. Move a file that is material "
            "into include or exclude instead"
        ),
    )


def _collisions(record: Record) -> Iterator[Uncertainty]:
    """Titles that would become one address if anybody derived one.

    ⚠️ **Accents do not collide** — `Café` and `Cafe` differ: an accent is a
    non-alphanumeric, so it collapses to a **separator**, and those two give `caf` and `cafe`.
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
                "collides by construction"
            ),
        )
