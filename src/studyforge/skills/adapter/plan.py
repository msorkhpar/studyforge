r"""What the scaffold is allowed to know: one corpus's manifest, and nothing else.

**What it does.** Reads a validated `Manifest` and returns the closed set of
facts the scaffold may vary on — the corpus's own id, its level vocabulary, its
variants, whether it declares exercises, and where its archive goes.

**How you use it.**

    from studyforge.corpus.manifest import parse
    from studyforge.skills.adapter import plan_for

    plan = plan_for(parse(text))
    plan.depth        # how many container levels this corpus has
    plan.kinds        # ('lesson',) or ('lesson', 'practice')

**Depends on.** `corpus.manifest` for the document it reads, `archive.document`
for the closed set of document kinds, and `layout` for the archive directory's
default. ⛔ Not on any adapter and not on any source (R1).

## ⛔ This type exists to make R19 checkable rather than aspirational

⚠️ **R19: the consuming half of a corpus is generated, never hand-authored, and
customisation enters as manifest data.** A generator is only as honest as its
input type: one that took a free-form `dict` — or a `source_name` argument a
caller could pass anything to — would let a source-specific fact enter the
scaffold without ever appearing in the corpus's own manifest, and the hole
would be invisible in the generated output.

⭐ **So every field here comes from the manifest, and there is nowhere else for
one to come from.** A scaffold that needs something this type does not carry is
reporting a hole in `corpus.json`, which is the right place to fix it.

## ⛔ What this deliberately does NOT decide

⚠️ **It does not decide what is material.** That is the reconnaissance skill's
question and the manifest's `content` policy is its answer; by the time an
adapter is being written it has been settled. An adapter-authoring skill that
re-opened it would give a corpus two places to say what it ingests.
"""

from __future__ import annotations

import keyword
from dataclasses import dataclass

from studyforge.archive.document import KINDS
from studyforge.corpus.manifest import Manifest
from studyforge.skills.adapter.layout import ARCHIVE_DIR

#: The directory an adapter occupies in its own repository. ⭐ A **framework**
#: decision rather than a corpus fact, and deliberately fixed: a reviewer who
#: has seen one adapter knows where the next one's reading step lives, and R20
#: says what a consumer needs is carried here rather than re-decided per
#: integration.
PACKAGE = "ingest"

#: The one module a person writes by hand. ⛔ Everything else the scaffold
#: emits is generated, so a hand-edit anywhere else is a finding (R19).
FILLED_IN = "read"


class PlanError(ValueError):
    """A manifest that cannot be scaffolded from, and which field is the reason.

    ⛔ Names the field and the permitted class, never the value (R7).
    """


@dataclass(frozen=True, slots=True)
class Plan:
    """Everything the scaffold may vary on, and it all came from `corpus.json`."""

    source: str
    levels: tuple[str, ...]
    variants: tuple[str, ...]
    exercises: bool
    archive_dir: str
    package: str
    #: Whether `corpus.json` declares the record's groups, so the
    #: scaffold can write the filing into `read.py` instead of a refusal.
    filed: bool = False

    @property
    def depth(self) -> int:
        """How many container levels this corpus has — the manifest's own arity."""
        return len(self.levels)

    @property
    def kinds(self) -> tuple[str, ...]:
        """The document kinds this corpus can produce.

        ⭐ **`exercises: false` is an answer, not a gap** (§7's three states,
        C5): a corpus with no graders is complete at the reading floor. So the
        scaffold emits no practice path at all for one, rather than emitting a
        practice path that is never taken and reads as unfinished work.
        """
        return KINDS if self.exercises else (KINDS[0],)

    @property
    def sole_variant(self) -> str | None:
        """The one variant, when a corpus has exactly one — otherwise `None`.

        ⚠️ `None` is not a failure. A container carries one variant,
        so a corpus declaring two makes the choice **per container**, and the
        scaffold has to leave that to the person rather than pick the first
        and be silently right for one corpus in two.
        """
        return self.variants[0] if len(self.variants) == 1 else None

    def lines(self) -> list[str]:
        """Return the plan a person reads back before anything is written."""
        return [
            f"  source            {self.source}",
            f"  levels            {self.depth}: {', '.join(self.levels)}",
            f"  variants          {', '.join(self.variants)}",
            f"  document kinds    {', '.join(self.kinds)}",
            f"  archive           {self.archive_dir}/",
            f"  adapter package   {self.package}/",
            f"  units filed from  {'corpus.json curriculum' if self.filed else 'read.py'}",
        ]


def plan_for(
    manifest: Manifest,
    *,
    archive_dir: str = ARCHIVE_DIR,
    package: str = PACKAGE,
) -> Plan:
    """Read one corpus's manifest and return what may be scaffolded from it."""
    if not isinstance(manifest, Manifest):
        raise PlanError(
            "plan_for takes a parsed Manifest; parse corpus.json with "
            "studyforge.corpus.manifest.parse first"
        )
    if not manifest.levels:
        raise PlanError("levels must name at least one container level")
    if not manifest.variants:
        raise PlanError("variants must name at least one variant")
    if not _identifier(package):
        raise PlanError("package must be a Python identifier naming a directory")
    return Plan(
        source=manifest.source,
        levels=tuple(manifest.levels),
        variants=tuple(manifest.variants),
        exercises=bool(manifest.exercises),
        archive_dir=archive_dir,
        package=package,
        filed=manifest.curriculum is not None and bool(manifest.curriculum.containers),
    )


def _identifier(name: object) -> bool:
    """Whether `name` may be a package directory and an import at the same time.

    ⛔ Stated as what is permitted, not as what is forbidden. A generated
    `import` statement is the one place a name has to satisfy two grammars at
    once, and a blacklist of separators would have admitted every keyword.
    """
    return isinstance(name, str) and name.isidentifier() and not _is_keyword(name)


def _is_keyword(name: str) -> bool:
    """Whether `name` is a Python keyword, which no import may spell."""
    return keyword.iskeyword(name) or keyword.issoftkeyword(name)
