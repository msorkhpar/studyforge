"""The one exception the unit package raises for an authored overlay.

**What it does.** Names every way a `content.json` can be unacceptable, so a
caller catches one type rather than five.

**How you use it.** Catch `ContentError`.

**Depends on.** Nothing.

⚠️ **`ValueError`, following SF-01's split and `corpus.manifest`'s reading of
it:** an overlay is a *value read from a document*, so both halves fail the
same way and one base is enough.

⛔ **Loud and specific, because this is the only file in the whole contract a
person edits by hand.** A typo must name itself rather than produce a page that
is quietly wrong — and the failures that matter each write a *plausible* page if
they are not caught: a unit filed under the wrong address, a section keyed on a
variant the corpus does not have, and a unit with no blocks at all.
"""

from __future__ import annotations

#: Values safe to quote back: a closed set's members and small integers are
#: this framework's own vocabulary, and quoting them is what makes a refusal
#: actionable.
SAFE_TO_QUOTE = (int, bool)


def describe(value: object) -> str:
    """Describe a value from an authored file without reproducing it.

    ⛔ **Rubric §1f, the emission clause.** Every R7 check so far asked whether
    an identifier reached a *file*; none asked whether the code would write one
    into a *log*. A refusal that quotes the field it refuses does exactly that,
    and this module reads a file **a person edits by hand** — so any string in
    it can be an absolute path.

    ⭐ **Type, not value** — the same answer `studyforge.version._said` gives,
    for the same reason: a wrong *value* and a wrong *type* are different
    mistakes and deserve different sentences, and naming the type describes an
    unexpected payload rather than reproducing it.

    ⚠️ Integers are quoted. They are the one shape that cannot carry an
    identifier, and a refusal that would not say `unit 4` is a refusal nobody
    can act on.
    """
    if value is None:
        return "nothing"
    if isinstance(value, SAFE_TO_QUOTE):
        return repr(value)
    name = type(value).__name__
    return f"a {'n' if name[:1] in 'aeiou' else ''} {name}".replace("  ", " ").strip()


class ContentError(ValueError):
    """An authored overlay this build will not accept.

    ⛔ The message names the file, the section index and the field — and never
    the offending *value* where that value is a path (R7), nor an exception
    object, which formats itself with an absolute path.
    """
