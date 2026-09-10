"""Reading one declared field, and refusing it without reproducing it.

**What it does.** Reads the small values a container map declares — required
text, optional text, an optional source path, an optional slug — and refuses
each of them in a message that names the field and the fault.

**How you use it.** `required_text`, `optional_text`, `optional_path`,
`optional_slug`, `optional_label`, `is_filename_component` for the one
permitted-set rule a filename component obeys, and `said(value)` when you
need to describe something you will not print.

**Depends on.** `studyforge.address` for what a slug is, and this package's
`errors`.

⛔ **A refusal never quotes the value.** This is not general caution: the field
this module refuses most often is `origin`, and **the one shape being refused
there is precisely the shape that carries a home directory** — so a message
quoting it would copy personal data into a log *from the check that exists to
catch it* (R7). SF-03 measured that on its own first attempt.

⭐ `said` is the same rule `studyforge.version` applies to a declared version:
name the type, describe the fault, and let the caller look at the file. It is
its own function so that a new field reader cannot forget it.
"""

from __future__ import annotations

from pathlib import Path

from studyforge.address import is_slug
from studyforge.address.slug import SLUG_PERMITTED
from studyforge.corpus.container.errors import ContainerError

#: The characters a generated filename component may carry — **a permitted
#: set, and deliberately not a forbidden one (Ruling 8)**.
#:
#: ⛔ A forbidden list is an **open set and cannot be finished**: every
#: character nobody thought of is permitted by default, so it is wrong the
#: moment it is written and stays wrong silently. This module carried one
#: (`"/\\ \t\n\r"`), re-typed by hand in `placement.names`, and it was wrong
#: in duplicate past two reviews and a gate. Measured 2026-09-09 on the merged
#: tree, **seven shapes passed both copies into a filename**: a vertical tab, a
#: form feed, a non-breaking space, U+2028, `"`, `:` and `*`. Two of those —
#: `:` and `"` — break the `file://` floor (R8), so the open set was not a
#: tidiness question.
#:
#: ⭐ **Derived from `is_slug`, never re-typed.** The permitted class is *what a
#: slug accepts*, plus `.` so `4.4.1` passes — and it is computed by asking, so
#: a second spelling of the slug rule cannot exist here to drift from the
#: first. ⛔ A constant exported and then re-typed is what this replaces; a
#: constant *derived* cannot be re-typed at all. `tests/.../test_fields.py`
#: pins the resulting set literally, so a change to `is_slug` is a decision
#: somebody makes rather than one that arrives.
#:
#: ⚠️ **The derivation itself now lives once, in `address.slug`**, and this is
#: `SLUG_PERMITTED | {"."}`. W1 needed the same set to describe a slug fault
#: without reproducing the value; two copies of one *computation* is the same
#: defect as two copies of one constant, one step earlier.
#:
#: ⚠️ **Lowercase, and that is the point, not an oversight.** `A` and `a` are
#: one filename on a case-insensitive filesystem, and `sibling` places twenty
#: units in a single directory — so an uppercase label is a collision this
#: framework would generate and never detect on the machine that generated it.
FILENAME_PERMITTED = SLUG_PERMITTED | {"."}

#: ⛔ A filename component must *begin* with one of these. A leading `.` is a
#: hidden file, and a leading `-` is read as an option by half the tools that
#: will ever list the directory; both are inside `FILENAME_PERMITTED` because
#: they are wanted in the middle (`4.4.1`, `part-two`), and neither is wanted
#: first. ⚠️ This is also what refuses a label of `.` or `..` — **a path
#: traversal every character of which is permitted**, and the thing a permitted
#: set alone does not give you.
FILENAME_MUST_START_WITH = frozenset(
    character for character in FILENAME_PERMITTED if is_slug(character)
)

#: How a refusal says the rule. ⛔ Stated once, so the two callers cannot
#: describe one class two ways — which is the failure this constant replaces.
FILENAME_PERMITTED_DESCRIBED = (
    "lowercase ASCII letters, digits, and . or -, beginning with a letter or digit"
)


def is_filename_component(value: object) -> bool:
    """Return whether `value` may be used, unchanged, as one component of a filename.

    ⭐ **The one predicate, and it lives here** — the container map refuses a
    label where it enters, and `placement.names.label_of` refuses one where a
    filename is minted, and both ask *this*. Two spellings of one rule is the
    defect; the missing character was only how it showed.

    ⚠️ ASCII and lowercase by construction, not by oversight. A label reaches a
    `file://` URL, a directory listing, a shell completion, a case-insensitive
    filesystem and a discovery scan, and the set that survives all five
    unchanged is small. A corpus whose display numbering is not in it records a
    label that is, and keeps the original in its **title**, which is under no
    filename constraint at all.
    """
    return (
        isinstance(value, str)
        and value != ""
        and value[0] in FILENAME_MUST_START_WITH
        and set(value) <= FILENAME_PERMITTED
    )


def required_text(value: object, what: str, where: str) -> str:
    """Return a field that must be present and must be non-empty text."""
    if not isinstance(value, str) or not value.strip():
        raise ContainerError(f"{where} has no {what}; it is required and must be text")
    return value


def optional_text(value: object, what: str, where: str) -> str | None:
    """Return a field that may be absent, but must be non-empty text if present.

    ⚠️ Absent and empty are different: absent says "nothing to say", empty says
    somebody meant to write something here. Only one of those is a decision.
    """
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ContainerError(
            f"{where} declares {what} as {said(value)}; it must be text, or absent"
        )
    return value


def optional_path(value: object, what: str, where: str) -> str | None:
    """Read an `origin`, refusing an absolute or escaping path — **never echoing it**.

    ⛔ The one shape being refused here is precisely the shape that carries a
    home directory, so a refusal quoting the value would copy personal data
    into a log from the check that exists to catch it (R7, measured by SF-03).
    The message describes the fault and names the field.
    """
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        raise ContainerError(
            f"{where} declares {what} as {said(value)}; it must be a path, or absent"
        )
    if value.startswith("/") or value.startswith("~") or ".." in Path(value).parts:
        raise ContainerError(
            f"{where} declares {what} as an absolute or escaping path. It is a "
            f"location inside the source, relative to the corpus root, and it is "
            f"not quoted here because that shape is where a home directory lives."
        )
    return value


def optional_slug(value: object, what: str, where: str) -> str | None:
    """Read a `url_slug`: the source's own addressing for a unit, or absent.

    ⚠️ Required to be a slug, and that is measured rather than assumed: of the
    extraction source's **1290** unit entries, **0** carry a `url_slug` that is
    not one. ⛔ Converted to a `ContainerError` rather than allowed to escape as
    SF-01's `AddressError`, following the manifest's precedent exactly — the
    rule is SF-01's, the document is this contract's.
    """
    if value is None:
        return None
    if not isinstance(value, str) or not is_slug(value):
        raise ContainerError(
            f"{where} declares {what} as {said(value)}; it must be a slug, or absent"
        )
    return value


def optional_label(value: object, what: str, where: str) -> str | None:
    """Read a unit's own display numbering, or absent.

    ⛔ Refused unless it is a usable filename component, because it becomes
    one downstream (SF-03's `label_of`). ⛔ The refusal names the **permitted**
    class and never reproduces the value: a label is read straight out of a
    file somebody else wrote, and describing rather than echoing is this
    module's whole job.

    ⭐ A map that accepted `a/b` would produce a corpus that **validates and
    then fails at render** — a milestone later, in another package, with
    nothing between the two saying why. Refusing it where it enters means the
    failure arrives next to the file that caused it.
    """
    text = optional_text(value, what, where)
    if text is None:
        return None
    if not is_filename_component(text):
        raise ContainerError(
            f"{where} declares {what} as text that cannot become part of a filename. "
            f"A label may carry only {FILENAME_PERMITTED_DESCRIBED}. Accepted here, "
            f"it would validate and then fail at render. It is not reproduced, "
            f"because a declared field is read out of a file somebody else wrote (R7)."
        )
    return text


def said(value: object) -> str:
    """Describe a value by its type, never by reproducing it (R7).

    ⭐ The same rule `studyforge.version` applies to a declared version: a
    wrong type is named, an unexpected payload is described rather than
    printed into a message that lands in a log.
    """
    if value is None:
        return "nothing"
    name = type(value).__name__
    if isinstance(value, str):
        return "an empty string" if not value.strip() else "text"
    return f"{'an' if name[:1] in 'aeiou' else 'a'} {name}"
