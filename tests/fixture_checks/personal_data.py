"""R7's gate, asked of a fixture — the framework's gate, never a second copy.

**What it does.** Reports the first personal-data shape reachable from a
document, and names the shape rather than the text.

**How you use it.** `check_personal_data(value, where)` yields
`(rule_id, message)`. `shape_in(text)` for one string — re-exported from the
framework so a caller never needs a pattern.

**Depends on.** `studyforge.archive.scrub`, and nothing else.

## ⛔ This module holds no patterns, and that is the whole of it

⚠️ **A second copy of the patterns drifts weaker than the first, and here it
would guard the one place where personal-data-shaped content is *permitted*.**
A copy easily misses a bare home directory, the macOS spelling, one inside a
shell command, or a leak in a **dict key**, while `studyforge.archive.scrub`,
which the archive itself uses, catches all of them. ⭐ *Do not re-derive the
patterns; one owner holds them.*

⭐ **Borrowed, never reconciled.** Reconciling two lists produces a third list.
`tests/test_fixture_consistency.py` asserts this module defines no pattern of
its own, which makes a second copy unrepresentable rather than merely
discouraged.

⚠️ **The gate skips each shape's own placeholder by identity, and so does this
module.** A fixture checker that is stricter than the gate reports failures the
build will not have.
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
