r"""One pass over a source: measure it, propose a manifest, name what is open.

**What it does.** Joins the five questions into one report. It is the only
place that knows the full list, so *"what does reconnaissance look at"* has one
answer.

**How you use it.** `survey(root)` returns a `Survey`. `survey.lines()` is the
report a person reads; `survey.proposal` is the draft `corpus.json`.

**Depends on.** every other module in this package, and nothing outside it
except `report`.

⛔ **It never raises for difficult material.** Difficult material is a *result*
— a report with more open questions — and a caller that had to catch an
exception to learn the shape of a corpus could not be handed the half that was
determined.

⭐ **The pass list is data, so it is assertable.** A question added without a
place in `PASSES` is a question nobody sees, and a pass that reports nothing at
all is a pass that has stopped asking.
"""

from __future__ import annotations

from pathlib import Path

from studyforge.skills.reconnaissance import capability, duplication, inventory, record
from studyforge.skills.reconnaissance.proposal import draft
from studyforge.skills.reconnaissance.report import Observation, Survey

#: Every question this skill asks, in the order a report reads best. ⛔ One
#: list, so the answer to "what does reconnaissance look at" is not spread
#: across five modules.
PASSES = ("inventory", "record", "duplication", "capability", "proposal")


def survey(root: Path | str) -> Survey:
    """Read one source tree and report its shape, its draft manifest, and its gaps."""
    root = Path(root)
    tree = inventory.take(root)
    found = record.find(tree)
    able = capability.assess(tree)

    items: list[object] = []
    items += list(inventory.observe(tree))
    items += list(record.observe(found, tree))
    items += list(duplication.observe(tree))
    items += list(capability.observe(able))

    manifest, open_questions = draft(tree, found, able)
    items += open_questions
    if found is not None:
        items += list(_unlabelled(found))

    result = Survey.of(root.name, items)  # type: ignore[arg-type]
    result.proposal = manifest
    return result


def _unlabelled(found) -> list[Observation]:
    """Name the entries that sit outside every group, if any do.

    ⚠️ **Reported rather than absorbed.** `record` allows a small number of
    entries above the first group label so that one link in a blockquote cannot
    cost a corpus its hierarchy — measured, 1 of 212 in the Java corpus. ⛔ The
    allowance is not silence: whatever it covered is named here, because an
    entry with no container is an entry somebody has to place.
    """
    if not found.groups:
        # ⚠️ A corpus with no grouping has every entry outside one, which is not
        # a finding — it is the flat shape, and two of the four designed source
        # shapes have it. Saying "19 entries under no group" there would be
        # noise a reader learns to skip.
        return []
    stray = [entry.target for entry in found.entries if entry.group is None]
    if not stray:
        return []
    return [
        Observation(
            "entries under no group (check these are units)",
            f"{len(stray)} {stray[:3]}",
        )
    ]
