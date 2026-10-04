"""Which corpora have revision aids, so their shared files are written: decks and review banks.

**What it does.** `has_decks(corpus)` is true when any unit holds a practice document whose record
is a deck of flashcards; `has_reviews(corpus)` when one holds a quiz that declares a `review`
schedule. `generate.site` then writes the matching shared files (`deck.css`, `deck.js`,
`review.css`, `review.js`) beside the shared assets; every other corpus builds the files it always
did.

**Depends on.** `generate.declarations`, `archive.scrub`. ⛔ It reads a record's `kind` and `review`
keys and decides nothing about their values: `exercise` is the rule.
"""

from __future__ import annotations

import json

from studyforge.archive.scrub import assert_clean
from studyforge.generate.declarations import Corpus

#: Where a unit's practice documents sit, relative to the unit's archive directory.
PRACTICE_GLOB = "practice-*.json"

#: What a refusal names in place of a path (R7): a practice document, never where it sits.
WHERE = "a unit's practice document"


def has_decks(corpus: Corpus) -> bool:
    """Does any unit carry a deck of flashcards?"""
    return any(_records(source.directory, "flashcards") for source in corpus.units)


def has_reviews(corpus: Corpus) -> bool:
    """Does any unit carry a quiz that declares a review schedule?"""
    return any(_records(source.directory, None) for source in corpus.units)


def _records(directory, kind: str | None) -> bool:
    """Does a practice document here carry a deck (`kind`), or a `review` key (`None`)?"""
    for path in sorted(directory.glob(PRACTICE_GLOB)):
        try:
            document = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        assert_clean(document, WHERE)
        record = document.get("exercise") if isinstance(document, dict) else None
        if not isinstance(record, dict):
            continue
        if kind is not None and record.get("kind") == kind:
            return True
        if kind is None and "review" in record:
            return True
    return False
