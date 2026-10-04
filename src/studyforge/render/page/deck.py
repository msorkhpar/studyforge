"""A deck of flashcards: the section a `flashcards` exercise draws, and the two files it links.

**What it does.** Renders a deck's cards, each as its front and its back, inside one section the
shared deck script turns into cards the reader flips and marks known or to see again. With no script
every card shows both sides, in order: the reading floor. The marks live in the reader's own browser
(`studyforge.deck.v1`, behind a guard that tolerates a refused store), never on a server.

**How you use it.** `page.practice.render` calls `render(exercise, key=..., corpus=..., grader=...,
assets=...)` for a record of kind `flashcards`; `files()` is what a corpus with a deck writes
beside the shared bundle (`generate.revision.wanted`).

**Depends on.** `exercise.deck` for the cards, `render.templates`, `render.markup`,
`render.pageassets.source`.

## Absent means today, byte for byte

A corpus with no deck writes neither file and renders no section of this kind. ⛔ The section wears
`data-practice-quiz`, so the workspace opens it as it opens a quiz, and the shared quiz script,
finding none of its parts, does nothing to it.
"""

from __future__ import annotations

from collections.abc import Callable

from studyforge.exercise import Exercise
from studyforge.render import templates
from studyforge.render.markup import escape_attribute, inline
from studyforge.render.pageassets.source import text

STYLESHEET_NAME = "deck.css"
SCRIPT_NAME = "deck.js"

#: The two files, as `pageassets` finds them on disk.
PARTS = (STYLESHEET_NAME, SCRIPT_NAME)

DECK_TEMPLATE = "practice-deck.html"
CARD_TEMPLATE = "practice-deck-card.html"

#: What separates two rendered rows. ⚠️ The same shape the quiz uses: a row is exactly its markup
#: plus one newline (R10).
JOIN = "\n"


def render(
    exercise: Exercise,
    *,
    key: str,
    corpus: str,
    grader: str,
    assets: Callable[[str], str],
) -> str:
    """Return one deck's section; `assets` turns a shared file's name into this page's link."""
    cards = exercise.cards
    if not exercise.is_deck or not cards:
        return ""
    return templates.fill(
        DECK_TEMPLATE,
        key=escape_attribute(key),
        corpus=escape_attribute(corpus),
        total=str(len(cards)),
        grader=grader,
        cards="".join(card(one) + JOIN for one in cards),
        stylesheet=escape_attribute(assets(STYLESHEET_NAME)),
        script=escape_attribute(assets(SCRIPT_NAME)),
    )


def card(one) -> str:
    """Return one card: its front and its back, in the markup the page's own prose gets."""
    return templates.fill(
        CARD_TEMPLATE,
        id=escape_attribute(one.id),
        front=_paragraph(one.front),
        back=_paragraph(one.back),
    )


def files() -> dict[str, str]:
    """`filename -> content` of what a corpus with a deck writes beside the bundle."""
    return {STYLESHEET_NAME: text(STYLESHEET_NAME), SCRIPT_NAME: text(SCRIPT_NAME)}


def _paragraph(words: str) -> str:
    """One side of a card as the paragraphs it is written in (a blank line starts a new one)."""
    return "".join(f"<p>{inline(part.strip())}</p>" for part in words.split("\n\n") if part.strip())
