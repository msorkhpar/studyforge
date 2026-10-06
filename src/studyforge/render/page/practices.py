r"""A lesson's practices as one list of titled cards, and the one workspace they open in.

**What it does.** Renders the **Practice (n)** section a unit page carries when
it has practices — one card per practice, each with its title, the concepts it
practises and a slot for its status — and the one workspace every card opens
in: a bar with the practice's title, **Previous**, **Next** and **Close**.

**How you use it.** `page.document` joins its rendered sections through it:

    practices.joined(parts, sections, document, placement)   # the page's body
    practices.region(document, placement)                    # '' for a unit with none

**Depends on.** `page.anchors` for each practice's section anchor and its title,
`page.practice` for the key a practice's runs are recorded under, `exercise`
for what a record says it practises and whether it can pass, and
`render.templates` and `render.markup`. ⛔ Not on `serve` (R8).

## ⭐ A LIST TO CHOOSE FROM, AND A WORKSPACE TO WORK IN

⚠️ **Seven practices laid out one after another** repeated the same three
headings and a panel per practice, and gave the reader no view of what the
lesson asks. ⭐ So the page lists them first, as cards, and a card opens its
practice in a full-screen workspace: the statement on the left, the editor and
the two acts on the right. ⛔ **The practice's own material is not moved or
copied**: each practice's section and panel still follow the list, and
`practice-workspace.js` shows the chosen pair in the workspace's geometry and
hides the rest. With no script they stay where they are, under the list, so
every practice is still readable over `file://` with nothing running (R8).

## ⛔ THE STATUS IS THE READER'S OWN RECORD, NEVER THE PAGE'S

⭐ A card carries its status slot hidden, with both of its words in the markup,
and says which record it is read from (`data-practice-kind`): a code
practice's from the served origin's progress record, where a run established
it; a quiz's from the reader's browser store, where the quiz page recorded it —
nothing about a quiz is a server's. ⛔ A built page says
nothing about any reader, so it is byte-identical whoever opens it (R10).
⚠️ **An ungraded practice carries no slot**: nothing completes it, so the
record could only ever say *not started*.

## ⛔ ONE ENTRY IN THE OUTLINE FOR THE LIST, AND ONE PER CARD

⭐ The outline lists **Practice (n)** and, under it, each practice by its title,
pointing at its CARD — where a reader chooses — rather than at the material
the workspace shows (`page.anchors`).
"""

from __future__ import annotations

from studyforge.exercise import Exercise, ExerciseError, from_document
from studyforge.render import modes, templates
from studyforge.render.markup import escape, escape_attribute, inline
from studyforge.render.page import anchors, editions
from studyforge.render.page import practice as practice_module
from studyforge.render.page.assets import Placement
from studyforge.render.page.errors import PageError

#: The section kind a practice is. ⛔ The archive's word.
PRACTICE = practice_module.PRACTICE

#: The list's own region, its heading's words, one card, and a card's parts.
REGION_TEMPLATE = "practices.html"
CARD_TEMPLATE = "practice-card.html"
CONCEPTS_TEMPLATE = "practice-concepts.html"
STATE_TEMPLATE = "practice-state.html"

#: What a card of several language editions adds: the sentence naming them, each edition in it,
#: and the status that summarises them (`page.editions`).
EDITIONS_TEMPLATE = "practice-editions.html"
EDITION_TEMPLATE = "practice-edition.html"
STATE_EDITIONS_TEMPLATE = "practice-state-editions.html"
EDITIONS_ATTRIBUTE = " data-practice-editions"

#: The one workspace every card opens in.
WORKSPACE_TEMPLATE = "practice-workspace.html"

#: What a card says its practice is, so its status is read from the right record:
#: a quiz's from the reader's browser store, a code practice's from the server.
QUIZ_KIND = "quiz"
CODE_KIND = "code"

#: What separates two cards, and two concepts.
JOIN = "\n"


def of(document: dict) -> list[dict]:
    """Return the page's practice sections, in the document's own order."""
    return [
        section
        for section in document.get("sections") or ()
        if isinstance(section, dict) and section.get("kind") == PRACTICE
    ]


def region(document: dict, placement: Placement) -> str:
    """Return the **Practice (n)** section, or `''` for a unit that sets no practice."""
    found = editions.entries(document)
    if not found:
        return ""
    unit = document.get("title")
    cards = "".join(card(entry.first, document, placement, unit) + JOIN for entry in found)
    return templates.fill(
        REGION_TEMPLATE,
        id=escape_attribute(anchors.PRACTICES_ANCHOR),
        title=escape(anchors.practices_title(len(found))),
        cards=cards,
    )


def card(section: dict, document: dict, placement: Placement, unit: object) -> str:
    """Return one practice's card: its title, what it practises, and its status slot.

    ⭐ A practice with language editions is ONE card: its title carries no language, it lists the
    editions it is available in, and its status summarises theirs (`page.editions`).
    """
    many = editions.edited_with(document, section)
    if many is not None:
        return _edited_card(many, document, placement, unit)
    exercise = _exercise(section)
    deck = exercise is not None and exercise.is_deck
    quiz = deck or (exercise is not None and exercise.is_quiz)
    # ⭐ A deck and a review bank are never passed, so their card has no status to show.
    revising = deck or (exercise is not None and exercise.review is not None)
    graded = (quiz and not revising) or (exercise is not None and exercise.test_command is not None)
    return templates.fill(
        CARD_TEMPLATE,
        id=escape_attribute(anchors.card_anchor(section.get("key"))),
        section=escape_attribute(anchors.section_anchor(section.get("key"))),
        key=escape_attribute(practice_module.key_of(document, section)),
        corpus=escape_attribute(placement.corpus),
        kind=QUIZ_KIND if quiz else CODE_KIND,
        anchor=escape_attribute(anchors.section_anchor(section.get("key"))),
        title=inline(anchors.practice_title(section, unit)),
        concepts=_region(concepts(exercise)),
        state=_region(templates.fill(STATE_TEMPLATE) if graded else ""),
        lang=modes.card_attributes(placement.offer, section.get("lang")),
        carriers=modes.card_note(placement.offer, section.get("lang")),
    )


def _edited_card(
    entry: editions.Entry, document: dict, placement: Placement, unit: object
) -> str:
    """The one card of a practice written in several languages."""
    section = entry.first
    exercise = _exercise(section)
    graded = [
        one
        for one in (_exercise(each) for each in entry.sections)
        if one is not None and one.test_command is not None
    ]
    offer = placement.offer
    items = ", ".join(
        templates.fill(
            EDITION_TEMPLATE,
            lang=escape_attribute(str(each.get("lang"))),
            section=escape_attribute(anchors.section_anchor(each.get("key"))),
            key=escape_attribute(practice_module.key_of(document, each)),
            label=escape(editions.label(offer, str(each.get("lang")))),
        )
        for each in entry.sections
    )
    return templates.fill(
        CARD_TEMPLATE,
        id=escape_attribute(anchors.card_anchor(section.get("key"))),
        section=escape_attribute(anchors.section_anchor(section.get("key"))),
        key=escape_attribute(practice_module.key_of(document, section)),
        corpus=escape_attribute(placement.corpus),
        kind=CODE_KIND,
        anchor=escape_attribute(anchors.section_anchor(section.get("key"))),
        title=inline(editions.title(anchors.practice_title(section, unit), entry)),
        concepts=_region(concepts(exercise)),
        state=_region(
            templates.fill(STATE_EDITIONS_TEMPLATE, total=str(len(entry.sections)))
            if graded
            else ""
        ),
        lang=EDITIONS_ATTRIBUTE,
        carriers=_region(templates.fill(EDITIONS_TEMPLATE, items=items)),
    )


def concepts(exercise: Exercise | None) -> str:
    """Return the list of what a practice practises, or `''` where its record says nothing."""
    if exercise is None or not exercise.concepts:
        return ""
    items = "".join(f"<li>{escape(one)}</li>{JOIN}" for one in exercise.concepts)
    return templates.fill(CONCEPTS_TEMPLATE, items=items)


def joined(parts: list[str], sections: list, document: dict, placement: Placement) -> str:
    """Join a page's rendered sections, with the list before its first practice.

    ⭐ **The list, then the practices' own material, then the one workspace**:
    the reader chooses from the list, and the material stays in the page for a
    reader with no script (R8). ⛔ The document's order is kept: a practice is
    never moved ahead of a section the document put before it.
    """
    listed = region(document, placement)
    if not listed:
        return JOIN.join(parts)
    first = next(
        index
        for index, section in enumerate(sections)
        if isinstance(section, dict) and section.get("kind") == PRACTICE
    )
    return JOIN.join([*parts[:first], listed, *parts[first:], workspace(document, placement)])


def embedded(section: dict, document: dict, placement: Placement) -> str:
    """Return one quiz practice's panel, drawn inside the lesson section that repeated it."""
    panel = practice_module.render(section, document, placement, embedded=True)
    return modes.tag_panel(placement.offer, section.get("lang"), panel)


def workspace(document: dict, placement: Placement | None = None) -> str:
    """Return the one workspace every card opens in, or `''` for a unit with no practice.

    ⭐ A page whose practices have language editions says, on the workspace, which language each
    reading mode opens one in (`page.editions`); every other page's workspace is as it was.
    """
    if not of(document):
        return ""
    offer = placement.offer if placement is not None else None
    said = editions.workspace_attribute(offer, document)
    return templates.fill(WORKSPACE_TEMPLATE, editions=said)


def _exercise(section: dict) -> Exercise | None:
    """Read a practice's record, or `None` for one that names no workspace."""
    workspace_record = section.get("workspace")
    if not isinstance(workspace_record, dict):
        return None
    try:
        return from_document(workspace_record, "this unit's practice workspace")
    except ExerciseError as error:
        raise PageError(f"this practice's card cannot be rendered: {error}") from None


def _region(markup: str) -> str:
    """Return one optional part: exactly empty, or its markup and one newline."""
    return f"{markup}{JOIN}" if markup else ""
