r"""Source reconnaissance: work out the shape of material nobody has read (SK-01).

**What it does.** Given arbitrary material, measures its shape — how deep the
hierarchy is, what the units are, whether anything is duplicated, whether
anything is runnable, whether a grader ships with it — and proposes a draft
`corpus.json` together with **an honest report of what it could not determine**.

**How you use it.** Through the skill document beside this file
(`SKILL.md`), which is the procedure. This package is what the skill *calls*:

    from studyforge.skills.reconnaissance import survey

    found = survey("path/to/material")
    print("\\n".join(found.lines()))    # the report a person reads
    found.proposal                      # the draft manifest they edit

**Depends on.** The standard library. ⛔ Not on `corpus.manifest`: this writes a
**draft for a person**, and a draft that had to satisfy the reader could not
leave a field open — which is the one thing it must be able to do.

## ⛔ This is the only skill that reasons about unfamiliar material

⚠️ Every other skill operates on contracts (R2). If a second skill starts
needing to understand a source, the seam has been drawn wrong.

## ⭐ Its hardest requirement is knowing when it does not know

⛔ **A confident wrong answer about a hierarchy costs an entire ingestion.**
*"These 19 files look flat, but files 12–19 reference a grouping I cannot see —
please confirm"* costs a question. So an `Uncertainty` is the deliverable, not
a weaker `Observation`, and every one carries **what would settle it**.

## The four traps real material sets

⛔ **`SKILL.md` holds them, with their measurements, and is the only copy.** It
sits in this directory; this list points at it and deliberately does not
restate it, because two copies of one table drift — and R1 rules that no module
here names a corpus at all.

1. **The hierarchy is in filenames, not directories** — and is usually *also*
   written down somewhere a person reads.
2. **The same material twice**, as whole files and as a region of one.
3. **A filename sort silently reverses the curriculum**, and flatters, so the
   page anybody opens to spot-check is correct.
4. **Heading level does not identify role** in a curriculum document. Role is
   positional.

⛔ **The countermeasure for trap 1 is *"find the document that records the
grouping"*, not *"learn to read prefixes"*.** Reading the names is derivation;
reading the document is a record (§6), and the prefix rule is the answer that
does **not** generalise.

## What is in the package

| Module | The question it answers |
|---|---|
| `inventory` | what is on disk, and what a filename implies |
| `record` | which document records the curriculum, and what it says |
| `duplication` | is any of this material here twice |
| `capability` | is anything runnable, does a grader ship with it |
| `proposal` | the draft manifest, and every field it had to choose |
| `survey` | one pass, joining all of them |
| `report` | what was measured, and what is still open |

**Skeleton at FND-01.** Filled by SK-01 (E11).
"""

from __future__ import annotations

from studyforge.skills.reconnaissance.capability import Capability, assess
from studyforge.skills.reconnaissance.duplication import Aggregate, Structural
from studyforge.skills.reconnaissance.inventory import Inventory, prefix_groups, take
from studyforge.skills.reconnaissance.proposal import draft
from studyforge.skills.reconnaissance.record import Entry, Record, find
from studyforge.skills.reconnaissance.report import Observation, Survey, Uncertainty
from studyforge.skills.reconnaissance.survey import PASSES, survey

#: ⛔ The package's whole public surface.
__all__ = [
    "PASSES",
    "Aggregate",
    "Capability",
    "Entry",
    "Inventory",
    "Observation",
    "Record",
    "Structural",
    "Survey",
    "Uncertainty",
    "assess",
    "draft",
    "find",
    "prefix_groups",
    "survey",
    "take",
]
