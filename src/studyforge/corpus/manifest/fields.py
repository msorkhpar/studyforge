"""The plain fields of `corpus.json` — `source`, `title`, `levels`, `variants`, `exercises`.

**What it does.** Validates one top-level value each, and raises this
package's `ManifestError` naming the key it read.

⚠️ **One function per key, and the key is spelled inside it**, never passed
in: a key a caller supplies is caller data, and a refusal that quotes caller
data is rubric §1f's echo.

**How you use it.** `document.from_document` calls these; nothing else does.
⛔ They are the manifest's own field rules, not a general validator.

**Depends on.** `studyforge.address` for what a slug is, and `errors`.

⭐ **Split from `document.py` at the seam between the document and its fields**
(`W350`, Ruling 261): the `runtimes` key took `document.py` past R11's bound,
and the field rules are the part that reads one value and knows nothing of the
document's version, its keys or its gate.
"""

from __future__ import annotations

from studyforge.address import AddressError, require_slug
from studyforge.corpus.manifest.errors import ManifestError
from studyforge.describe import describe


def title_of(value: object, where: str) -> str:
    """Return the corpus's human-readable name. ⚠️ A title, deliberately not a slug."""
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{where} 'title' must be a non-empty str, got {describe(value)}")
    return value


def levels_of(value: object, where: str) -> tuple[str, ...]:
    """`levels`: the container level labels, which fix the depth.

    ⚠️ Labels, not slugs. §4 says `levels` supplies the display labels the
    breadcrumb and index use — "Section › Module › Lesson" — so how they are
    capitalised is the renderer's decision (R13) and not this module's to
    constrain.
    """
    entries = _non_empty_list(value, "levels", where)
    for position, entry in enumerate(entries, start=1):
        if not isinstance(entry, str) or not entry.strip():
            raise ManifestError(
                f"{where} 'levels[{position - 1}]' must be a non-empty str, got {describe(entry)}"
            )
    return tuple(entries)


def variants_of(value: object, where: str) -> tuple[str, ...]:
    """`variants`: each already a slug, because each names an archive partition."""
    entries = _non_empty_list(value, "variants", where)
    for position, entry in enumerate(entries, start=1):
        slug_of(entry, f"{where} 'variants[{position - 1}]'")
    return tuple(entries)


def slug_of(value: object, what: str) -> str:
    """SF-01's slug rule, raised as this package's error.

    ⛔ `errors.ManifestError` promises that reading a manifest raises one
    type. SF-01 owns what a slug **is**, so the rule is imported rather than
    restated — but a caller reading `corpus.json` should not have to know that
    a bad `source` fails through a different package, so the refusal is
    re-raised here with SF-01's message intact.

    ⚠️ `Manifest.parse_key` deliberately does **not** do this: that is the
    arity *comparison*, which SF-01 owns outright, and its `AddressError` is
    the honest answer.
    """
    try:
        return require_slug(value, what)
    except AddressError as exc:
        raise ManifestError(str(exc)) from None


def _non_empty_list(value: object, key: str, where: str) -> list:
    """Return a list with something in it, or refuse naming the key."""
    if not isinstance(value, list) or not value:
        raise ManifestError(f"{where} '{key}' must be a non-empty list, got {describe(value)}")
    return value


def exercises_of(value: object, where: str) -> bool:
    """`exercises`: a real bool, refusing anything that merely looks like one.

    ⛔ Not `1`, not `"true"`. A manifest is hand-written, and a string that
    looks like a flag is a mistake worth naming rather than coercing.
    """
    if not isinstance(value, bool):
        raise ManifestError(f"{where} 'exercises' must be true or false, got {describe(value)}")
    return value
