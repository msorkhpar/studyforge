"""Reading one declared field, and refusing it without reproducing it.

**What it does.** Reads the small values a container map declares — required
text, optional text, an optional source path, an optional slug — and refuses
each of them in a message that names the field and the fault.

**How you use it.** `required_text`, `optional_text`, `optional_path`,
`optional_slug`, and `said(value)` when you need to describe something you will
not print.

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
from studyforge.corpus.container.errors import ContainerError


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
