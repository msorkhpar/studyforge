r"""The producer-half deviations this tree carries, DECLARED with the ground of each.

⭐ **Part of the product's own floor**, which `python3 -m tests.floor` runs from any
checkout. It began as a copy of the developer tooling's check; that tooling, and its
records, live on the branch `archive/process`, and nothing here depends on them.

**What it does.** Holds `DECLARED`: for each package that some other package reaches
past, the names reached past and the ground the exemption stands on. ⛔ It is DATA and
holds no reading — `tests.floor.surfaces` compares it against the tree, both ways, so
an undeclared deviation and a declaration whose deviation is gone are each a finding.

**How you use it.** `from tests.floor.deviations import DECLARED, Declaration`, or
reach both through `tests.floor.surfaces`, which re-exports them so a caller needs one
import. ⛔ Adding an entry to quiet a red is declaring a defect, not fixing one (`W199`).

**Depends on.** `dataclasses`, and nothing else — ⛔ deliberately nothing from this
package. The seam runs ONE WAY: `surfaces` imports this module and this module imports
nothing back, so the data cannot come to depend on the reading over it.

## ⛔ WHY IT IS A MODULE OF ITS OWN (Ruling 261 — a ceiling is not a budget)

⚠️ **MEASURED: `surfaces.py` reached `423` of R11's `400` when this table landed in it.**
⭐ The split is the one `reach.py` already took when its grammar outgrew it: the READING
stays with the check, and the DECLARATION it reads becomes a sibling. ⛔ The alternative
was a size exception, which would have bought one round and left the next editor the same
choice on a worse file.

## ⭐ THE POPULATION, AND WHY IT IS BIGGER THAN THE ROW THAT NAMED IT

⛔ **MEASURED at `2827409` with `surfaces.reaches` itself rather than with a grep.**
⚠️ Two earlier readings took this population as five packages and then as their
remainder; both were taken before `validate`'s names were closed, and NEITHER counted a
package that declares no `__all__` at all — which is where most of this table now sits.
⭐ That is the whole reason it was measured again rather than the figure inherited.

⛔ **The two grounds are different remedies and are kept apart deliberately.** A package
with a surface is one line from compliance. A package with NO surface needs a surface,
and giving it one costs a ruling per name that collides with one of its own modules —
the shape `validate`'s five needed, and not something a sweep may do to seven packages
in passing.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Declaration:
    """One package's off-surface population, and the ground it stands declared on."""

    ground: str
    names: frozenset[str]


#: ⭐ The ground for a package that HAS a surface and is reached past anyway. The remedy
#: is one line on that package's `__all__`, and this is `W199/3`'s own population.
REACHED_PAST = "on a surface that exists; the remedy is one line on that package's __all__"

#: ⛔ The ground for a package that declares NO `__all__`. Every name it shares is
#: off-surface by construction, so the remedy is a surface with a ruling per colliding
#: name — the shape `validate`'s five needed — and never a line in this table.
NO_SURFACE = "the package declares no __all__ at all, so a surface is a row, not a line"

#: ⛔ **Closed at the ref above.** A pair missing from here is a finding, and a pair here
#: that the tree no longer has is a finding too — see `surfaces._stale`.
DECLARED: dict[str, Declaration] = {
    "studyforge.address": Declaration(REACHED_PAST, frozenset({"SLUG_PERMITTED"})),
    "studyforge.archive": Declaration(
        NO_SURFACE,
        frozenset(
            {
                "ArchiveError",
                "BLOCK_FIELDS",
                "BLOCK_OPTIONAL",
                "BLOCK_TYPES",
                "CONTAINER_TYPES",
                "KINDS",
                "LESSON_HEADING",
                "MEDIA_ENTRY_KEYS",
                "PersonalDataLeak",
                "STARTING_CODE_HEADING",
                "STATEMENT_HEADING",
                "VIDEO_KEYS",
                "assert_clean",
                "build",
                "content_sha256",
                "counts_of",
                "item_parts",
                "leaks",
                "list_start",
                "load",
                "parse",
                "render",
                "scrub",
                "walk",
            }
        ),
    ),
    "studyforge.corpus.container": Declaration(
        REACHED_PAST, frozenset({"FILENAME_PERMITTED_DESCRIBED"})
    ),
    "studyforge.corpus.manifest": Declaration(
        REACHED_PAST,
        frozenset(
            {
                "BY_CONVENTION",
                "BY_POLICY",
                "IGNORE_NAMES",
                "VCS_DIRECTORIES",
                "VCS_NAMES",
                "reads_as_content",
            }
        ),
    ),
    "studyforge.narrate": Declaration(
        NO_SURFACE,
        frozenset(
            {
                "Health",
                "MISFILED",
                "NOT_ON_DISK",
                "NOT_PLACED",
                "NarrateClient",
                "NarrationError",
                "Narrator",
                "Playable",
                "over_http",
                "playable_of",
            }
        ),
    ),
    "studyforge.serve": Declaration(
        REACHED_PAST,
        frozenset({"DEFAULT_PORT", "ServingServer", "discover", "instance_of", "make_server"}),
    ),
    "studyforge.serve.routes": Declaration(
        NO_SURFACE, frozenset({"ContentSource", "CorpusContent"})
    ),
}

__all__ = [
    "DECLARED",
    "NO_SURFACE",
    "REACHED_PAST",
    "Declaration",
]
