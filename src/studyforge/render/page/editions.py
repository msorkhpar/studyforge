r"""One practice written in several languages: the editions that make one card and one panel.

**What it does.** A practice that differs only by language is ONE practice. Its language
editions are practice sections of one unit that name the same `edition` (an id) and each its
own `lang`. This module says which sections are editions of one practice, in what order, under
what title, and what the card and the panel say about them.

**How you use it.** `page.practices`, `page.practice`, `page.anchors` and `page.section` ask it:

    editions.entries(document)       # the page's practices: one `Entry` per card
    editions.entry_of(document, s)   # the `Entry` a practice section belongs to
    editions.title(heading, entry)   # the card's title, with no language in it

**Depends on.** `studyforge.exercise` (whether a section sets code work) and `render.modes` for
the declared names of the languages. ⛔ Not on `page.anchors`, which asks this module.
It names no language (R1): ids and labels are the corpus's data.

## ⭐ What an edition is, and what stays per edition

An edition is a whole practice document: its own statement, starter, tests, plants and gate
record, its own section key and its own progress key. ⛔ Nothing is merged: grading, Run and
Submit target the edition shown, and each edition passes on its own. What is shared is only the
card, the one workspace entry and the switch at the top of the panel.

⭐ **Document order is the edition order.** The first edition's position is the card's position
in the list; every edition's statement and panel still follow it on the page, so a reader with
no script finds each of them, in order, under the list (R8).

## ⛔ Absent means today, byte for byte

A section with no `edition`, a quiz or deck that names one, and an `edition` carried by one
section alone are ordinary practices: no entry here has more than one section, so no page,
card, panel or outline line changes for a corpus that does not use the key.

## ⭐ The language the panel opens in

`preference(offer)` is, per reading mode, the languages in the order a practice opens in:
the mode's `practices`, then its `prose` language, then its `tabs`. The page carries it on the
workspace (`data-edition-modes`); the client opens the first edition in the current mode's
list, or the first edition the practice has. A corpus with no modes opens the first edition.
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from dataclasses import dataclass

from studyforge.exercise import ExerciseError, from_document
from studyforge.render import modes, templates
from studyforge.render.markup import escape, escape_attribute

#: The section kind that can be an edition; the archive's word, as `page.practice` spells it.
PRACTICE = "practice"

#: The key a section names its practice by, and the one language each edition is written in.
EDITION = "edition"
LANG = "lang"

#: What the workspace carries to say, per mode, which language a practice opens in.
MODES_ATTRIBUTE = "data-edition-modes"

#: What an edition's section and panel carry: the language it is an edition in.
ATTRIBUTE = "data-edition"


@dataclass(frozen=True, slots=True)
class Entry:
    """One practice on a page: its section, or the sections that are its language editions."""

    sections: tuple[dict, ...]

    @property
    def first(self) -> dict:
        """The section that stands for the practice: where its card sits and what it links to."""
        return self.sections[0]

    @property
    def edited(self) -> bool:
        """Whether this practice has language editions to choose between."""
        return len(self.sections) > 1


def edition_of(section: object) -> str | None:
    """Return the practice id a section is an edition of, or `None` for a practice of its own.

    ⛔ Only a section that sets CODE work and names one language can be an edition: a quiz or a
    deck is not written in a language, so the key on one is not read.
    """
    if not isinstance(section, dict) or section.get("kind") != PRACTICE:
        return None
    named, lang = section.get(EDITION), section.get(LANG)
    if not (isinstance(named, str) and named and isinstance(lang, str) and lang):
        return None
    workspace = section.get("workspace")
    if not isinstance(workspace, dict):
        return None
    try:
        exercise = from_document(workspace, "this unit's practice workspace")
    except ExerciseError:
        return None
    return None if exercise.is_quiz or exercise.is_deck else named


def entries(document: dict) -> list[Entry]:
    """Every practice of the page, in order, one entry for the editions of one practice.

    ⭐ An entry sits where its first edition sits. A named practice with one section only is an
    entry of one: it is an ordinary practice.
    """
    found: list[Entry] = []
    held: dict[str, list[dict]] = {}
    order: list[list[dict] | dict] = []
    for section in document.get("sections") or ():
        if not isinstance(section, dict) or section.get("kind") != PRACTICE:
            continue
        named = edition_of(section)
        if named is None:
            order.append(section)
        elif named in held:
            held[named].append(section)
        else:
            held[named] = [section]
            order.append(held[named])
    for item in order:
        found.append(Entry(tuple(item) if isinstance(item, list) else (item,)))
    return found


def entry_of(document: dict, section: dict) -> Entry:
    """Return the entry a practice section belongs to; an entry of its own for an ordinary one."""
    for entry in entries(document):
        if any(one is section for one in entry.sections):
            return entry
    return Entry((section,))


def edited_with(document: dict, section: dict) -> Entry | None:
    """Return the entry of a section that is one of several editions, else `None`."""
    entry = entry_of(document, section)
    return entry if entry.edited and any(one is section for one in entry.sections) else None


def label(offer: modes.Offer | None, lang: str) -> str:
    """Return the declared name of a language, or its id where the corpus declares no modes."""
    return dict(offer.languages).get(lang, lang) if offer is not None else lang


def title(heading: str, entry: Entry) -> str:
    """Return the card's title: the first edition's, without the language it names last.

    ⭐ An adapter that titles an edition `Keep a conversation (Python)` gets one title for the
    card, `Keep a conversation`: a trailing parenthesis that names the language of one of the
    editions by its id, in any case, is dropped. Any other title is kept as it is.
    """
    names = {str(one.get(LANG)).casefold() for one in entry.sections}
    text = heading.rstrip()
    if text.endswith(")") and " (" in text:
        cut = text.rindex(" (")
        if text[cut + 2 : -1].strip().casefold() in names and text[:cut].strip():
            return text[:cut].rstrip()
    return heading


def collapsed(document: dict) -> dict:
    """Return the document as the outline reads it: one practice section per practice.

    ⭐ A practice's language editions are listed once, at the first, under the title the card
    carries. Every other section, and a document with no editions, is returned as it came.
    """
    found = entries(document)
    if not any(entry.edited for entry in found):
        return document
    dropped = {id(one) for entry in found for one in entry.sections[1:]}
    renamed = {
        id(entry.first): {**entry.first, "heading": title(str(entry.first.get("heading")), entry)}
        for entry in found
        if entry.edited
    }
    return {
        **document,
        "sections": [
            renamed.get(id(one), one)
            for one in document.get("sections") or ()
            if id(one) not in dropped
        ],
    }


def slots(entry: Entry | None, section: dict, offer: modes.Offer | None) -> dict[str, str]:
    """Return the two slots of a panel template that an edition fills: its attribute and the switch.

    ⭐ Both `''` for a practice with no editions, so its panel is the bytes it was. The switch is
    the first thing in every edition's panel: one button per edition of the practice, each by the
    language's declared name. ⛔ It ships `hidden`, as the editor tabs do: with no script the
    editions simply follow one another on the page, and a switch that does nothing would be the
    dead control the panel refuses.
    """
    if entry is None:
        return {"edition": "", "switch": ""}
    buttons = "".join(
        templates.fill(
            "practice-switch-button.html",
            lang=escape_attribute(lang),
            label=escape(label(offer, lang)),
        )
        for lang in languages(entry)
    )
    return {
        "edition": f' {ATTRIBUTE}="{escape_attribute(str(section.get(LANG)))}"',
        "switch": templates.fill("practice-switch.html", buttons=buttons),
    }


def preference(offer: modes.Offer | None) -> dict:
    """Return what the client needs to open a practice in a mode's language; `{}` with no modes.

    ⭐ `attribute` is the root attribute that holds the chosen mode, and `modes` maps each mode id
    to the languages a practice opens in, first choice first. The shared script names neither the
    attribute nor a mode: it is the page that says them.
    """
    if offer is None:
        return {}
    return {
        "attribute": modes.MODE_ATTRIBUTE,
        "modes": {
            choice.id: list(dict.fromkeys((*choice.practices, choice.prose, *choice.tabs)))
            for choice in offer.choices
        },
    }


def workspace_attribute(offer: modes.Offer | None, document: dict) -> str:
    """Return the workspace's attribute when the page has editions and modes, else `''`."""
    if offer is None or not any(entry.edited for entry in entries(document)):
        return ""
    return f" {MODES_ATTRIBUTE}='{_json(preference(offer))}'"


def _json(value: object) -> str:
    """Compact, key-sorted JSON that is safe inside a single-quoted attribute."""
    return (
        json.dumps(value, sort_keys=True, separators=(",", ":"))
        .replace("&", "&amp;")
        .replace("'", "&#39;")
    )


def languages(entry: Entry) -> Iterable[str]:
    """Return the language of each edition of an entry, in edition order."""
    return (str(one.get(LANG)) for one in entry.sections)
