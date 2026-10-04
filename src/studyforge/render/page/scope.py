"""How wide a deck or a review bank reaches, which decides the sentence naming its source.

**What it does.** `deck_template(exercise)` and `review_template(exercise)` answer the name of the
grader sentence a deck or a review bank is owed. ⭐ **The signal is the record's own citations**:
items that cite more than one page were written from several pages, so the sentence says that; items
that cite one page, or none, were written from this page, so the sentence is the one a quiz has.
⛔ No new key and no flag: a record written before this module draws the sentence it always drew.

**Depends on.** `exercise` only; the sentences are templates (`render.templates`).
"""

from __future__ import annotations

from studyforge.exercise import Exercise

#: The sentence a deck is owed, for a page's worth of cards and for several pages' worth.
DECK_PAGE = "practice-grader-deck.html"
DECK_SEVERAL = "practice-grader-deck-several.html"

#: The sentence a review bank is owed, for a page's worth and for several pages' worth.
REVIEW_PAGE = "practice-grader-quiz.html"
REVIEW_SEVERAL = "practice-grader-quiz-several.html"


def _pages(exercise: Exercise) -> int:
    """Return how many distinct pages the record's items cite."""
    cited = [item.origin for item in (*(exercise.cards or ()), *(exercise.questions or ()))]
    return len({origin.path for origin in cited if origin is not None})


def deck_template(exercise: Exercise) -> str:
    """Return the template naming where a deck's cards were written from."""
    return DECK_SEVERAL if _pages(exercise) > 1 else DECK_PAGE


def review_template(exercise: Exercise) -> str:
    """Return the template naming where a review bank's questions were written from."""
    return REVIEW_SEVERAL if _pages(exercise) > 1 else REVIEW_PAGE
