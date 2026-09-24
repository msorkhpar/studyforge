r"""A quiz's own document, read back: the one versioned reader of `tests/quiz.json`.

**What it does.** Reads the document `gating.gate_quiz` writes into a quiz's
bundle and returns the quiz it describes: where it sits, its title and its
exercise record. ⛔ It refuses, by name, a document at a `quiz_api` this build
does not speak, a document whose keys are not the written ones in the written
order, an identity that does not name the directory the document sits in, and
a record that is not a quiz.

**How you use it.** An adapter reads each committed quiz through it, then
builds the quiz's practice document from what it returns:

    from studyforge.skills.exercises import QUIZ_DOCUMENT, quiz_of

    where = "exercises/kata/python/unit-03/practice-2"
    text = (root / where / QUIZ_DOCUMENT).read_text(encoding="utf-8")
    quiz = quiz_of(json.loads(text), where)
    quiz.places, quiz.title, quiz.record    # the record goes under `exercise`

**Depends on.** `studyforge.version` for R9's one guard, `exercise` for the
record and `exercise.bundle.Places` for where a quiz sits. Standard library
only. ⛔ No I/O: the caller reads the file. ⭐ The document's name, version and
keys live here, beside their reader, and `gating` writes with them.

## ⛔ ONE READER, SO AN UNKNOWN VERSION IS REFUSED THE SAME WAY EVERYWHERE

⭐ The framework writes `quiz_api`, so it reads it back too, through
`version.check`, rather than leave every adapter to compare the number by hand.
A hand-written comparison reads a JSON `true` as `1`, and a second one drifts
from the first the day the version moves.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass

from studyforge.address import Address
from studyforge.exercise import Exercise, from_document
from studyforge.exercise.bundle import Places
from studyforge.version import check

#: ⭐ Where a quiz's own document sits inside its bundle. ⚠️ `tests/` because a
#: quiz's key IS its grader, and because `bundle.layout` closes a bundle's file
#: set: no other name would pass `studyforge validate`'s contents check.
QUIZ_DOCUMENT = "tests/quiz.json"

#: The quiz document's version, and its key order (R10).
QUIZ_API = 1
QUIZ_KEYS = ("quiz_api", "address", "variant", "unit", "ordinal", "title", "exercise")


class QuizRefused(ValueError):
    """A quiz document this build cannot read, and why."""


@dataclass(frozen=True, slots=True)
class Quiz:
    """One committed quiz: where it sits, its title, its record and that record read."""

    places: Places
    title: str
    #: The record as the document holds it, which is what an archive carries.
    record: Mapping[str, object]
    exercise: Exercise


def quiz_of(document: object, where: str) -> Quiz:
    """Read one quiz's own document, found in the bundle directory `where`.

    ⛔ `where` is the bundle's directory relative to the corpus root, and the
    document's identity must name exactly it: a quiz emitted under an identity
    that names another directory is one nobody can find by that identity.
    """
    at = f"{where}/{QUIZ_DOCUMENT}"
    if not isinstance(document, dict):
        raise QuizRefused(f"{at} is not a JSON object, so it is not a quiz's document")
    check("quiz_api", document.get("quiz_api"), (QUIZ_API,), where=at, error=QuizRefused)
    if tuple(document) != QUIZ_KEYS:
        raise QuizRefused(
            f"{at} does not carry {list(QUIZ_KEYS)} in that order, so it is not the "
            f"document the authoring pass writes; re-run the pass rather than editing it"
        )
    places = _places(document, at)
    try:
        bundle = places.bundle
    except ValueError:
        raise QuizRefused(f"{at} carries an identity that names no bundle directory") from None
    if bundle != where:
        raise QuizRefused(
            f"{at} declares an identity whose directory is '{bundle}', so it is "
            f"refused rather than emitted under an identity nobody can find it by"
        )
    title = document["title"]
    if not isinstance(title, str) or not title.strip():
        raise QuizRefused(f"{at} carries no title")
    exercise = from_document(document["exercise"], at)
    if not exercise.is_quiz:
        raise QuizRefused(f"{at} carries an exercise record that is not a quiz")
    return Quiz(places, title, document["exercise"], exercise)


def _places(document: Mapping[str, object], at: str) -> Places:
    """Return where the document says its quiz sits, refusing a malformed identity."""
    segments, variant = document["address"], document["variant"]
    unit, ordinal = document["unit"], document["ordinal"]
    if (
        not isinstance(segments, list)
        or not all(isinstance(one, str) for one in segments)
        or not isinstance(variant, str)
        or not all(isinstance(one, int) and not isinstance(one, bool) for one in (unit, ordinal))
    ):
        raise QuizRefused(
            f"{at} carries an identity that is not an address of segments, a variant, "
            f"a unit and an ordinal"
        )
    try:
        return Places(Address.of(*segments), variant, unit, ordinal)
    except ValueError:
        raise QuizRefused(f"{at} carries an address that does not read") from None
