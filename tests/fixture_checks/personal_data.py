"""R7's gate, asked of a fixture — the framework's gate, never a second copy.

**What it does.** Reports the first personal-data shape reachable from a
document, and names the shape rather than the text.

**How you use it.** `check_personal_data(value, where)` yields
`(rule_id, message)`. `shape_in(text)` for one string — re-exported from the
framework so a caller never needs a pattern.

**Depends on.** `studyforge.archive.scrub`, and nothing else.

## ⛔ This module holds no patterns, and that is the whole of it

⚠️ **It used to hold three, and they were the weaker of two copies — in the one
place where personal-data-shaped content is *permitted*.** Measured against
`studyforge.archive.scrub`, which the archive itself uses:

| shape | the copy that was here | `scrub.leaks` |
|---|---|---|
| a bare home directory | ⛔ **missed** — its pattern required a trailing `/` | caught |
| a home directory with a file beneath | caught | caught |
| the macOS spelling, bare | ⛔ **missed** | caught |
| one inside a shell command | ⛔ **missed** | caught |
| a leak in a **dict key** | ⛔ **missed** — `strings_in` walks `values()` | caught |

⛔ **Three of four, plus the keys.** And the project had already ruled this
shape — *do not re-derive the patterns; one owner holds them*, a duplication
refused five times — but nobody had swept for a **third** copy. There was one,
it was already weaker, and it was guarding the negative fixtures' R7
exception.

⭐ **Deleted rather than reconciled.** Reconciling two lists produces a third
list. `tests/test_fixture_consistency.py` asserts this module defines no pattern
of its own, which is what makes a **fourth** copy unrepresentable rather than
merely discouraged.

⚠️ **One behaviour changed with the deletion, and it is a correction.** This
module claimed *"any address is wrong content whether or not it is
deliverable, so there is no allow-list at all"* — but the gate it is supposed to
mirror skips each shape's **own placeholder** by identity, so the claim was
already untrue of the thing being checked. A fixture checker that is stricter
than the gate reports failures the build will not have.
"""

from __future__ import annotations

from studyforge.archive.scrub import leaks, shape_in

__all__ = ["check_personal_data", "shape_in"]


def check_personal_data(value, where):
    """The first personal-data shape reachable from `value`, named but not quoted.

    ⛔ The location comes from the framework's walker, so it names the field —
    `content.json.sections[0].heading` — rather than only the file. ⚠️ The
    matched text is never echoed: a refusal that quotes the leak has relocated
    it into a build log, which is read by more people than the file was.
    """
    for at, name in leaks(value, where):
        article = "an" if name[:1].lower() in "aeiou" else "a"
        yield "personal-data", f"{at} carries {article} {name}"
        return
