"""`corpus.json` — the file that makes a directory a source.

**What it does.** Reads and validates the manifest, and hands back one
immutable `Manifest` carrying every declaration a corpus makes about itself.

**How you use it.** `parse(text)` for the document, `load(path)` for the file.
⛔ `parse` does no I/O and `load` is four lines on top of it, so everything a
test needs to say can be said without a filesystem.

**Depends on.** `studyforge.address` for what a slug is, and this package's
`content`, `edits`, `media` and `errors`. ⛔ Nothing source-specific, ever
(R1) — `tests/studyforge/corpus/manifest/test_document.py` asserts that of the
whole of `src/`, not just of this module.

## The three questions that are three answers

⚠️ **`variants` is a filing and presentation key and nothing more.** It says
how the archive is partitioned and what a variant selector offers the reader.
⛔ It never implies anything is buildable, runnable or gradable — that is
declared per exercise (§7) — and it is **not** a code fence's language, which
is a block's own attribute from the archive. The extraction source blocked
eight SQL courses for exactly this reason: one list answered both *"can this
be filed here?"* and *"can we generate a test for it?"*, so a language with no
grader could not be filed at all. Three questions, three answers, none of them
derived from another.

⭐ **There is a test that would have caught that**, and it is not a comment:
`test_no_module_maps_a_variant_to_a_capability` refuses a module-level
collection under `src/` whose name suggests one — which is what the extraction
source's `LANGUAGES` tuple was.

## Where depth is declared, and where it is checked

**This module declares it.** `levels` names the container levels, and
`len(levels)` is the corpus's depth. ⛔ **It does not check an address against
that depth** — SF-01 owns the comparison, and a second check here with a
different message is how two tasks come to disagree about which is
authoritative.

⭐ `Manifest.parse_key(key)` is where the two halves meet: it supplies this
manifest's depth to SF-01's `parse_key`, so no caller ever writes
`parse_key(key, len(manifest.levels))` and no caller ever gets it wrong.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

from studyforge.address import Address, AddressError, parse_key, require_slug
from studyforge.corpus.manifest.content import ContentPolicy, parse_content
from studyforge.corpus.manifest.edits import PermittedEdit, parse_edits
from studyforge.corpus.manifest.errors import ManifestError
from studyforge.corpus.manifest.media import MediaPolicy, parse_media
from studyforge.version import check as check_version

#: The manifest's filename. One spelling, because "what makes a directory a
#: source" is a question every tool in this project asks.
MANIFEST_FILENAME = "corpus.json"

#: Versions this build can read. ⛔ An unknown one is refused and never
#: migrated in place (R9): a migration that runs because something merely
#: wanted to render a page rewrites the record of what was ingested.
CORPUS_API = 1
KNOWN_CORPUS_API = frozenset({CORPUS_API})

#: The placement profiles that may be declared. ⚠️ **SF-03 owns the profiles;
#: this is only the set a manifest may name**, and the two must not drift.
#: When SF-03 lands, this constant is where a third profile is registered —
#: see `docs/tasks/handoffs/SF-02.md`, which routes the seam.
PLACEMENT_PROFILES = ("tree", "sibling")

#: Every key a manifest may carry, in the order §4 writes them.
MANIFEST_KEYS = (
    "corpus_api",
    "source",
    "title",
    "levels",
    "variants",
    "exercises",
    "placement",
    "content",
    "media",
    "permitted_edits",
)

#: The ones with no default.
REQUIRED_KEYS = (
    "corpus_api",
    "source",
    "title",
    "levels",
    "variants",
    "exercises",
    "placement",
    "content",
)


@dataclass(frozen=True, slots=True)
class Manifest:
    """One corpus's declarations about itself. Immutable once validated."""

    source: str
    title: str
    levels: tuple[str, ...]
    variants: tuple[str, ...]
    exercises: bool
    placement: str
    content: ContentPolicy
    media: MediaPolicy
    permitted_edits: tuple[PermittedEdit, ...] = field(default=())
    corpus_api: int = CORPUS_API

    @property
    def depth(self) -> int:
        """How many container levels this corpus has — SF-01's arity, declared here."""
        return len(self.levels)

    def parse_key(self, key: str) -> Address:
        """Return the `Address` `key` names, checked against **this** corpus's depth.

        ⭐ The one place the declaration and the comparison meet. Call this
        rather than `studyforge.address.parse_key(key, len(manifest.levels))`:
        the second spelling is where a caller eventually passes the wrong
        number.
        """
        return parse_key(key, self.depth)

    def allows_edit_to(self, path: str) -> bool:
        """Whether this corpus declared an edit to `path` (R3).

        ⛔ `OPS-05` asks this rather than knowing any corpus's exception.
        """
        return any(edit.path == path for edit in self.permitted_edits)


def parse(text: str, where: str = MANIFEST_FILENAME) -> Manifest:
    """Build a `Manifest` from the text of a `corpus.json`."""
    try:
        document = json.loads(text)
    except (TypeError, json.JSONDecodeError) as exc:
        raise ManifestError(f"{where} is not valid JSON: {exc}") from None
    if not isinstance(document, dict):
        raise ManifestError(f"{where} must be a JSON object, got {type(document).__name__}")
    return from_document(document, where)


def load(path: str | Path) -> Manifest:
    """Read, parse and version-check one `corpus.json`."""
    path = Path(path)
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        # ⛔ `exc.strerror`, never `exc`: an OSError formats itself with the
        # filename it was given, and a refusal is read in a log and pasted
        # into a bug report. An absolute path in one is the user's home
        # directory (R7).
        reason = exc.strerror or exc.__class__.__name__
        raise ManifestError(f"cannot read {path.name}: {reason}") from None
    return parse(text, path.name)


def from_document(document: dict, where: str = MANIFEST_FILENAME) -> Manifest:
    """Build a `Manifest` from an already-parsed object."""
    _check_version(document, where)
    unknown = sorted(set(document) - set(MANIFEST_KEYS))
    if unknown:
        raise ManifestError(
            f"{where} has unknown key(s) {unknown}; this build reads {list(MANIFEST_KEYS)}"
        )
    missing = [key for key in REQUIRED_KEYS if key not in document]
    if missing:
        raise ManifestError(f"{where} is missing required key(s) {missing}")

    content = parse_content(document["content"])
    return Manifest(
        source=_slug_of(document["source"], f"{where} 'source'"),
        title=_title_of(document["title"], where),
        levels=_labels_of(document["levels"], "levels", where),
        variants=_slugs_of(document["variants"], "variants", where),
        exercises=_flag_of(document["exercises"], "exercises", where),
        placement=_placement_of(document["placement"], where),
        content=content,
        media=parse_media(document.get("media")),
        permitted_edits=parse_edits(document.get("permitted_edits"), content),
    )


def _check_version(document: dict, where: str) -> None:
    """Refuse a `corpus_api` this build does not speak (R9).

    ⛔ The test itself is `studyforge.version`'s, not this module's. It was
    written here first and was correct here; R9 versions **six** contracts,
    and the second copy is the one people forget (SF-33). What stays here is
    the set — `KNOWN_CORPUS_API` — because which versions a manifest may
    declare is this contract's business and nobody else's.
    """
    check_version(
        "corpus_api",
        document.get("corpus_api"),
        KNOWN_CORPUS_API,
        where=where,
        error=ManifestError,
    )


def _title_of(value: object, where: str) -> str:
    """Return the corpus's human-readable name. ⚠️ A title, deliberately not a slug."""
    if not isinstance(value, str) or not value.strip():
        raise ManifestError(f"{where} 'title' must be a non-empty str, got {value!r}")
    return value


def _labels_of(value: object, key: str, where: str) -> tuple[str, ...]:
    """`levels`: the container level labels, which fix the depth.

    ⚠️ Labels, not slugs. §4 says `levels` supplies the display labels the
    breadcrumb and index use — "Section › Module › Lesson" — so how they are
    capitalised is the renderer's decision (R13) and not this module's to
    constrain.
    """
    entries = _non_empty_list(value, key, where)
    for position, entry in enumerate(entries, start=1):
        if not isinstance(entry, str) or not entry.strip():
            raise ManifestError(
                f"{where} '{key}[{position - 1}]' must be a non-empty str, got {entry!r}"
            )
    return tuple(entries)


def _slugs_of(value: object, key: str, where: str) -> tuple[str, ...]:
    """`variants`: each already a slug, because each names an archive partition."""
    entries = _non_empty_list(value, key, where)
    for position, entry in enumerate(entries, start=1):
        _slug_of(entry, f"{where} '{key}[{position - 1}]'")
    return tuple(entries)


def _slug_of(value: object, what: str) -> str:
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
        raise ManifestError(f"{where} '{key}' must be a non-empty list, got {value!r}")
    return value


def _flag_of(value: object, key: str, where: str) -> bool:
    """Return a real bool, and refuse anything that merely looks like one.

    ⛔ Not `1`, not `"true"`. A manifest is hand-written, and a string that
    looks like a flag is a mistake worth naming rather than coercing.
    """
    if not isinstance(value, bool):
        raise ManifestError(f"{where} '{key}' must be true or false, got {value!r}")
    return value


def _placement_of(value: object, where: str) -> str:
    """One of the declared placement profiles (spec §5)."""
    if value not in PLACEMENT_PROFILES:
        raise ManifestError(
            f"{where} 'placement' must be one of {list(PLACEMENT_PROFILES)}, got {value!r}"
        )
    return value
