"""Which languages a unit, and a module, belongs to when nothing in it is common to every mode.

**What it does.** For a corpus that declares reading modes, reads each unit's built document
and answers, by unit key and by group key, the language ids of the entries that have prose or
a practice in some languages only. An entry with any section that carries no language is
read in every mode and is not listed.

**How you use it.** `entry_languages(corpus)` answers `key -> language ids`, in the corpus's
declared language order; `offer_of(corpus)` is `modes.offer` with that answer in.
A corpus that declares no modes gets `{}` and `None`, and no unit is read for it.

**Depends on.** `unit.builder` for the document and `render.modes` for the offer.
⛔ It names no language (R1): the ids are the corpus's data.

⭐ A module's languages are the union of its units'. A module with one unit that is common, or
one that has no material yet, is not listed: an entry that may hold something every mode reads
is never greyed. ⚠️ A unit with no material is not a unit of any language, so it neither tags
nor untags the module that holds it.
"""

from __future__ import annotations

from studyforge.contents import Group
from studyforge.generate.declarations import Corpus
from studyforge.render import modes
from studyforge.unit.builder import build_unit


def entry_languages(corpus: Corpus) -> dict[str, tuple[str, ...]]:
    """`unit or group key -> language ids` for each entry that belongs to some languages only."""
    reading = corpus.manifest.reading
    if reading is None or not reading.modes:
        return {}
    declared = [language.id for language in reading.languages]
    units: dict[str, tuple[str, ...] | None] = {}
    for source in corpus.units:
        document = build_unit(
            source.directory,
            declared_practices=source.declared_practices,
            mentions=source.mentions,
        )
        found = {section.get("lang") or "" for section in document["sections"]}
        units[source.key] = (
            None if not found or "" in found else tuple(x for x in declared if x in found)
        )
    entries = {key: found for key, found in units.items() if found}
    for group in corpus.contents.groups:
        _group(group, units, entries, declared)
    return entries


def offer_of(corpus: Corpus) -> modes.Offer | None:
    """The offer a corpus makes, with the entries that belong to some languages only."""
    reading = corpus.manifest.reading
    if reading is None or not reading.modes:
        return None
    return modes.offer(reading, entry_languages(corpus))


def _group(
    group: Group,
    units: dict[str, tuple[str, ...] | None],
    entries: dict[str, tuple[str, ...]],
    declared: list[str],
) -> tuple[bool, set[str]]:
    """Walk a group; `(whether every unit with material is tagged, their languages)`."""
    every = True
    found: set[str] = set()
    for child in group.groups:
        tagged, languages = _group(child, units, entries, declared)
        every, found = every and tagged, found | languages
    for entry in group.entries:
        if entry.key not in units:
            continue
        languages = units[entry.key]
        every = every and bool(languages)
        found |= set(languages or ())
    if every and found:
        entries[group.key] = tuple(x for x in declared if x in found)
    return every, found
