r"""Adapter authoring: scaffold an adapter against `studyforge validate` (SK-02).

**What it does.** Turns a corpus manifest into the adapter that will fill it —
eight files, seven of them generated and one of them the source reading, which
is genuinely material-specific. It also holds the archive **layout**, so that
no adapter ever computes an archive path for itself.

**How you use it.** Through the skill document beside this file (`SKILL.md`),
which is the procedure. This package is what the skill *calls*:

    from studyforge.corpus.manifest import load
    from studyforge.skills.adapter import plan_for, scaffold

    made = scaffold(plan_for(load("corpus.json")))
    print("\\n".join(made.lines()))     # what it will write, and why
    made.write(corpus_root)

**Depends on.** `corpus`, `archive` and `address` — the three formats an
adapter writes. ⛔ Not on `validate`, and not on any adapter (R1, R2).

## ⛔ The seam is on disk, and this package does not move it

⚠️ An adapter's whole obligation is to write an archive `studyforge validate`
accepts. There is no callback, no plugin registry and no framework API for an
adapter to call, which is what lets adapters be written in any language.
⭐ **What is here is a scaffold, not a runtime**: everything it emits is
ordinary code in the corpus's own repository, and deleting this package would
not stop a single adapter from working.

## ⛔ A skill precedes the artifact it produces (§9)

⚠️ **A skill written after the thing it "produces" has been validated against
exactly one source**, and reads as a description of that source rather than a
procedure for the next. That is why `SK-02` sits inside M2 step 2.1 rather than
after it, and why the acceptance is *following the skill on a source it has
never seen reaches a `validate`-clean archive* — not *this skill describes the
adapter we already wrote*.

## ⛔ The consuming half of a corpus is generated, never hand-authored (R19)

⭐ **Exactly one of the eight files is a person's to write, and this package
names it** — `Scaffold.hand_written`. Every other file is regenerable, so a
diff in one is a defect report about this skill rather than a local fix, and
`write(..., regenerate=True)` rewrites the seven and still refuses the eighth.

⚠️ **What this deliberately does not decide is what is *material*.** The
manifest's content policy is reconnaissance's answer and is settled before an
adapter exists; a second skill re-opening it would give a corpus two places to
say what it ingests.

**Skeleton at FND-01.** Filled by SK-02 (E11).
"""

from __future__ import annotations

from studyforge.skills.adapter.layout import (
    ARCHIVE_DIR,
    RAW_DIR,
    Layout,
    LayoutError,
    document_name,
)
from studyforge.skills.adapter.parts import PARTS, Part
from studyforge.skills.adapter.plan import FILLED_IN, PACKAGE, Plan, PlanError, plan_for
from studyforge.skills.adapter.scaffold import (
    SOURCE_LINE_CEILING,
    Scaffold,
    ScaffoldRefused,
    Written,
    scaffold,
)

#: ⛔ The package's whole public surface.
__all__ = [
    "ARCHIVE_DIR",
    "FILLED_IN",
    "PACKAGE",
    "PARTS",
    "RAW_DIR",
    "SOURCE_LINE_CEILING",
    "Layout",
    "LayoutError",
    "Part",
    "Plan",
    "PlanError",
    "Scaffold",
    "ScaffoldRefused",
    "Written",
    "document_name",
    "plan_for",
    "scaffold",
]
