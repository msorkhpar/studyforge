"""Checks about the languages a document is tagged with, and what each reading shows.

**What it does.** Reads the optional `lang` of every archive document against the
languages the manifest declares, and, for a corpus that declares modes, asks
whether every unit has prose and every mode lists a unit.

**How you use it.** `CHECKS` joins `validate.run`'s list; each check takes the
`Walk` and yields `Finding`s.

**Depends on.** `validate.corpus` for the walk and `validate.report`. ⛔ It
names no language (R1): the ids are the corpus's data, and nothing here branches
on one.

## ⭐ A corpus that declares no language is not asked a new question

`language-undeclared` fires on a tag in a corpus with none declared, and a tag
is only ever written by an adapter that means one; the other two rules are asked
only of a corpus that declares modes. So a corpus with no tags and no modes
validates exactly as it did.

## ⛔ What is refused, each by rule

- `language-undeclared`: a document's `lang` is not a language the manifest
  declares (or the manifest declares none). The id is shaped as a manifest's ids
  are, so it is named.
- `unit-prose`: a unit of a corpus that declares modes has no lesson document,
  tagged or common, so the page would hold no prose.
- `mode-empty`: a declared mode lists no unit. A unit is listed in a mode when
  one of its lessons is common or in the mode's `prose` language, or one of its
  practices is common or in a language the mode's `practices` names.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterator

from studyforge.archive.blocks import walk as walk_blocks
from studyforge.validate.corpus import Unit, Walk
from studyforge.validate.report import Finding

RULE_LANGUAGE = "language-undeclared"
RULE_UNIT_PROSE = "unit-prose"
RULE_MODE_EMPTY = "mode-empty"


def check_languages_are_declared(walk: Walk) -> Iterator[Finding]:
    """Every `lang` a document carries, and every language an example's tab names, is declared."""
    assert walk.manifest is not None
    reading = walk.manifest.reading
    declared = {language.id for language in reading.languages} if reading else set()
    for unit in walk.units:
        lang = unit.document.get("lang")
        if lang is not None and lang not in declared:
            yield Finding(
                RULE_LANGUAGE,
                unit.where,
                f"is tagged with the language {lang!r}, which corpus.json does not declare"
                f" under 'languages'; a tag names a declared language",
            )
    yield from _example_tabs(walk, declared)


def _example_tabs(walk: Walk, declared: set[str]) -> Iterator[Finding]:
    """Every language an example's tab names is a language the manifest declares."""
    for unit in walk.units:
        blocks = unit.document.get("blocks")
        for block in walk_blocks(blocks if isinstance(blocks, list) else []):
            if not isinstance(block, dict) or block.get("type") != "example":
                continue
            tabs = block.get("tabs")
            for tab in tabs if isinstance(tabs, list) else ():
                lang = tab.get("lang") if isinstance(tab, dict) else None
                if isinstance(lang, str) and lang not in declared:
                    yield Finding(
                        RULE_LANGUAGE,
                        unit.where,
                        f"has an example with a tab in the language {lang!r}, which corpus.json"
                        f" does not declare under 'languages'; a tab names a declared language",
                    )


def check_units_have_prose(walk: Walk) -> Iterator[Finding]:
    """A unit of a corpus that declares modes holds at least one lesson, tagged or common."""
    if _modes(walk) == ():
        return
    for key, documents in _by_unit(walk).items():
        if not any(unit.document.get("kind") == "lesson" for unit in documents):
            yield Finding(
                RULE_UNIT_PROSE,
                documents[0].where,
                f"unit {key[1]} has practices and no lesson, tagged or common, so its page"
                f" would hold no prose in any mode",
            )


def check_modes_list_a_unit(walk: Walk) -> Iterator[Finding]:
    """Every declared mode lists at least one unit."""
    units = _by_unit(walk)
    for mode in _modes(walk):
        if not any(_listed(mode, documents) for documents in units.values()):
            yield Finding(
                RULE_MODE_EMPTY,
                "corpus.json",
                f"the mode {mode.id!r} lists no unit: no lesson is common or in its prose"
                f" language, and no practice is common or in a language it offers",
            )


def _modes(walk: Walk) -> tuple:
    """The declared modes, or `()` for a corpus that declares none."""
    return walk.manifest.reading.modes if walk.manifest and walk.manifest.reading else ()


def _by_unit(walk: Walk) -> dict[tuple, list[Unit]]:
    """The walk's documents grouped by the unit they belong to, in walk order."""
    grouped: dict[tuple, list[Unit]] = defaultdict(list)
    for unit in walk.units:
        grouped[(tuple(unit.document.get("address") or ()), unit.document.get("unit"))].append(unit)
    return grouped


def _listed(mode: object, documents: list[Unit]) -> bool:
    """Whether a mode shows something of this unit."""
    for unit in documents:
        lang = unit.document.get("lang")
        lesson = unit.document.get("kind") == "lesson"
        shown = (mode.prose,) if lesson else mode.practices  # type: ignore[attr-defined]
        if lang is None or lang in shown:
            return True
    return False


CHECKS = (
    check_languages_are_declared,
    check_units_have_prose,
    check_modes_list_a_unit,
)
