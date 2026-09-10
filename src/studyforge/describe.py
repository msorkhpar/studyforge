"""One way to say what arrived, when saying *what* arrived would be a leak.

**What it does.** Turns any value into a short phrase naming its **type** —
`a str`, `an int`, `nothing` — so a refusal can say what it was given without
reproducing it (R7, rubric §1f).

**How you use it.** `describe(value)` wherever a message would otherwise have
written `{value!r}`:

    raise ContentError(f"section kind must be one of {list(KINDS)}, got {describe(kind)}")

**Depends on.** Nothing, and that is the point — this is the module every
package imports, so a dependency in any direction is a cycle waiting for the
second caller (`studyforge.version`'s argument, for the same reason).

⛔ **Why one module rather than one function per package** (Ruling 10). This
rule was written three times before it was extracted — `version._said`,
`corpus.container.fields.said`, `unit.errors.describe` — and the three had
already drifted: two quoted integers and stated why, the third returned
*"an int"*. ⚠️ Nobody chose that difference; it is what a third copy does.
⭐ The measured spread was 10 sites, 8 modules, 5 packages, and it is the same
finding shape this project has now taken three times: a constant or a rule
written twice is a rule that disagrees with itself.

⭐ **Integers and booleans are quoted, and that is the behaviour the
extraction kept**, because two of the three chose it and said why: an integer
cannot carry an identifier, and a refusal that will not say `unit 4` is a
refusal nobody can act on. ⚠️ `bool` is quoted alongside `int` for the reader's
sake, not the type's — an integrator who wrote JSON `true` where `1` was wanted
is told `True`, and would learn nothing from `a bool`.

⛔ **What this deliberately does not do is guess.** It never truncates, never
hashes, never redacts a substring: a value is named by its type or it is a
number. A describer that emitted "the first eight characters" would be a
policy about how much of an identifier is acceptable in a log, and there is no
acceptable amount (R7).
"""

from __future__ import annotations

#: Types whose *values* a refusal may reproduce. ⛔ Closed, and closed on a
#: property rather than on taste: these are the types that cannot carry a path,
#: an email address, a hostname or a username. Widening it to `str` is the
#: whole defect this module exists to remove, so a fourth entry needs an
#: argument that a string does not also satisfy.
SAFE_TO_QUOTE = (int, bool)


def describe(value: object) -> str:
    """Name what `value` is, without reproducing what it says.

    ⭐ **Type, not value.** A wrong *value* and a wrong *type* are different
    mistakes and deserve different sentences, and naming the type describes an
    unexpected payload rather than reproducing it into a message that lands in
    a log, a bug report or a paste.

    ⚠️ `None` is `nothing` rather than `a NoneType`: the reader's mistake is
    an absent field, and the type name is Python trivia at that point.
    """
    if value is None:
        return "nothing"
    if isinstance(value, SAFE_TO_QUOTE):
        return repr(value)
    name = type(value).__name__
    return f"{'an' if name[:1] in 'aeiou' else 'a'} {name}"
