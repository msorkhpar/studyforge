"""Reading modes — the `languages`, `modes`, `default_mode` and `outside_mode` keys.

**What it does.** Validates the four optional top-level keys with which a corpus
declares the languages its sections may be tagged with and the modes a reader
may choose between, and returns one immutable `Reading`.

**How you use it.** `parse_reading(document, where)`; a document with none of
the four keys yields `None`, so no caller asks "did they declare one?" and a
corpus that declares nothing is exactly what it was before the keys existed.

**Depends on.** `errors` and `describe`.

⛔ **This is the declaration and nothing else.** It reads no unit, builds no page
and shows no question; the sections, the page and the client read the value
this module returns. ⛔ **It names no language** (R1): the ids are the corpus's
data, and no line here branches on one.

## ⭐ Absent means today

No key is required, and none gives another a default it did not have: a corpus
with `languages` alone is valid (its sections may be tagged, nothing offers a
choice), and a corpus with none of the four keys has no `Reading`.

## ⛔ What is refused, each by name

- `modes`, `default_mode` or `outside_mode` without the keys they rest on
  (`modes` needs `languages`; the other two need `modes`);
- a duplicate language id or mode id;
- a fence label claimed by two languages (or twice by one);
- a mode whose `prose`, `tabs` or `practices` names a language not declared;
- a tab or a practice language listed twice in one mode;
- a `default_mode` that is not a declared mode;
- an `outside_mode` that is not `open` or `locked`;
- a `practice_choice` that is not a boolean;
- an unknown key inside a language or a mode, and an empty `languages` or `modes`.

⭐ It never requires a unit to have anything in a language: that is a question
about the material, which this module has not read.

⚠️ **`corpus_api` is not raised for these keys** (they are optional and absent
means today); each is nonetheless in `document.py`'s `KEY_VERSIONS` at the
version this build already writes, so a manifest declaring them under an older
version is refused naming both numbers, as every optional key is.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from studyforge.corpus.manifest.errors import ManifestError
from studyforge.describe import describe

#: What `outside_mode` may say, and what absent means.
OUTSIDE_MODES = ("open", "locked")
DEFAULT_OUTSIDE_MODE = "open"

#: The top-level keys this module owns.
READING_KEYS = ("languages", "modes", "default_mode", "outside_mode")

#: An id: lowercase, starts with a letter or digit, then letters, digits, `-`, `_`.
ID = re.compile(r"[a-z0-9][a-z0-9_-]*")
#: A fence label as a markdown fence writes it: no whitespace, no backtick.
FENCE_LABEL = re.compile(r"[^\s`]+")

DECLARED_FIELDS = {"id", "label", "fence_labels"}
MODE_REQUIRED = ("id", "label", "summary", "prose", "tabs", "practices")
MODE_KEYS = {*MODE_REQUIRED, "practice_choice"}


@dataclass(frozen=True, slots=True)
class Language:
    """One declared language: its id, display name and code-fence labels."""

    id: str
    label: str
    fence_labels: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Mode:
    """One declared reading mode, with languages as ids already checked against `languages`."""

    id: str
    label: str
    summary: str
    prose: str
    tabs: tuple[str, ...]
    practices: tuple[str, ...]
    practice_choice: bool = False


@dataclass(frozen=True, slots=True)
class Reading:
    """A corpus's declared languages and modes. Immutable once validated."""

    languages: tuple[Language, ...]
    modes: tuple[Mode, ...] = ()
    #: ⭐ The first declared mode when `default_mode` is absent; `None` only with no modes.
    default_mode: str | None = None
    outside_mode: str = DEFAULT_OUTSIDE_MODE


def parse_reading(document: dict, where: str) -> Reading | None:
    """Return the declared `Reading`, or `None` when none of the four keys is present."""
    if not any(key in document for key in READING_KEYS):
        return None
    if "modes" in document and "languages" not in document:
        raise ManifestError(
            f"{where} declares 'modes' without 'languages'; a mode names declared languages"
        )
    for key in ("default_mode", "outside_mode"):
        if key in document and "modes" not in document:
            raise ManifestError(f"{where} declares '{key}' without 'modes'; it describes a mode")
    languages = _languages(document["languages"], where)
    known = {language.id for language in languages}
    modes = _modes(document["modes"], known, where) if "modes" in document else ()
    default = _default_mode(document, modes, where)
    return Reading(
        languages=languages,
        modes=modes,
        default_mode=default,
        outside_mode=_outside_mode(document.get("outside_mode", DEFAULT_OUTSIDE_MODE), where),
    )


def _named(value: object) -> str:
    """Quote `value` only when it is shaped like an id or a label; otherwise describe its type.

    ⛔ A value that is not id-shaped is never reproduced (R7): it may be a path.
    """
    if isinstance(value, str) and FENCE_LABEL.fullmatch(value) and not {"/", "\\"} & set(value):
        return repr(value)
    return describe(value)


def _object_list(value: object, key: str, where: str) -> list[dict]:
    if not isinstance(value, list) or not value:
        raise ManifestError(f"{where} '{key}' must be a non-empty list, got {describe(value)}")
    for position, entry in enumerate(value):
        if not isinstance(entry, dict):
            raise ManifestError(
                f"{where} '{key}[{position}]' must be an object, got {describe(entry)}"
            )
    return value


def _text(entry: dict, field: str, name: str, where: str) -> str:
    value = entry.get(field)
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(
            f"{where} '{name}.{field}' must be a non-empty string, got {describe(value)}"
        )
    return value


def _id(entry: dict, name: str, where: str) -> str:
    value = entry.get("id")
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ManifestError(
            f"{where} '{name}.id' must be lowercase letters, digits, '-' or '_' starting "
            f"with a letter or digit, got {describe(value)}"
        )
    return value


def _languages(value: object, where: str) -> tuple[Language, ...]:
    entries = _object_list(value, "languages", where)
    languages: list[Language] = []
    claimed: dict[str, str] = {}
    for position, entry in enumerate(entries):
        name = f"languages[{position}]"
        unknown = sorted(set(entry) - DECLARED_FIELDS)
        if unknown:
            raise ManifestError(
                f"{where} '{name}' has unknown key(s) {unknown}; it reads {sorted(DECLARED_FIELDS)}"
            )
        ident = _id(entry, name, where)
        if any(language.id == ident for language in languages):
            raise ManifestError(f"{where} 'languages' declares the id {_named(ident)} twice")
        label = _text(entry, "label", name, where)
        labels = entry.get("fence_labels", [])
        if not isinstance(labels, list):
            raise ManifestError(
                f"{where} '{name}.fence_labels' must be a list, got {describe(labels)}"
            )
        for fence in labels:
            if not isinstance(fence, str) or not FENCE_LABEL.fullmatch(fence):
                raise ManifestError(
                    f"{where} '{name}.fence_labels' entries must be non-empty strings with no "
                    f"whitespace or backtick, got {describe(fence)}"
                )
            if fence in claimed:
                raise ManifestError(
                    f"{where} 'languages' lets the fence label {_named(fence)} belong to "
                    f"both {_named(claimed[fence])} and {_named(ident)}; a label belongs to "
                    f"one language"
                    if claimed[fence] != ident
                    else f"{where} '{name}.fence_labels' names {_named(fence)} twice"
                )
            claimed[fence] = ident
        languages.append(Language(ident, label, tuple(labels)))
    return tuple(languages)


def _language_list(
    entry: dict, field: str, known: set[str], name: str, where: str, *, nonempty: bool
) -> tuple[str, ...]:
    value = entry[field]
    if not isinstance(value, list) or (nonempty and not value):
        raise ManifestError(
            f"{where} '{name}.{field}' must be a {'non-empty ' if nonempty else ''}list of "
            f"language ids, got {describe(value)}"
        )
    for ident in value:
        if not isinstance(ident, str) or ident not in known:
            raise ManifestError(
                f"{where} '{name}.{field}' names {_named(ident)}, which 'languages' does "
                f"not declare; declared: {sorted(known)}"
            )
    repeated = sorted({ident for ident in value if value.count(ident) > 1})
    if repeated:
        raise ManifestError(f"{where} '{name}.{field}' names {repeated} more than once")
    return tuple(value)


def _modes(value: object, known: set[str], where: str) -> tuple[Mode, ...]:
    entries = _object_list(value, "modes", where)
    modes: list[Mode] = []
    for position, entry in enumerate(entries):
        name = f"modes[{position}]"
        unknown = sorted(set(entry) - MODE_KEYS)
        if unknown:
            raise ManifestError(
                f"{where} '{name}' has unknown key(s) {unknown}; it reads {sorted(MODE_KEYS)}"
            )
        missing = [key for key in MODE_REQUIRED if key not in entry]
        if missing:
            raise ManifestError(f"{where} '{name}' is missing required key(s) {missing}")
        ident = _id(entry, name, where)
        if any(mode.id == ident for mode in modes):
            raise ManifestError(f"{where} 'modes' declares the id {_named(ident)} twice")
        prose = entry["prose"]
        if not isinstance(prose, str) or prose not in known:
            raise ManifestError(
                f"{where} '{name}.prose' names {_named(prose)}, which 'languages' does not "
                f"declare; declared: {sorted(known)}"
            )
        choice = entry.get("practice_choice", False)
        if not isinstance(choice, bool):
            raise ManifestError(
                f"{where} '{name}.practice_choice' must be true or false, got {describe(choice)}"
            )
        modes.append(
            Mode(
                id=ident,
                label=_text(entry, "label", name, where),
                summary=_text(entry, "summary", name, where),
                prose=prose,
                tabs=_language_list(entry, "tabs", known, name, where, nonempty=True),
                practices=_language_list(entry, "practices", known, name, where, nonempty=False),
                practice_choice=choice,
            )
        )
    return tuple(modes)


def _default_mode(document: dict, modes: tuple[Mode, ...], where: str) -> str | None:
    if "default_mode" not in document:
        return modes[0].id if modes else None
    value = document["default_mode"]
    if not isinstance(value, str) or value not in {mode.id for mode in modes}:
        raise ManifestError(
            f"{where} 'default_mode' must name a declared mode, got {_named(value)}; "
            f"declared: {[mode.id for mode in modes]}"
        )
    return value


def _outside_mode(value: object, where: str) -> str:
    if not isinstance(value, str) or value not in OUTSIDE_MODES:
        raise ManifestError(
            f"{where} 'outside_mode' must be one of {list(OUTSIDE_MODES)}, got {describe(value)}"
        )
    return value
