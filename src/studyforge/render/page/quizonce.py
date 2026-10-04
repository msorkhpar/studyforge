"""A quiz is shown once: the interactive quiz stands where the lesson's static copy was.

**What it does.** A lesson sometimes ends with a section that lists the same questions its quiz
practice asks (a heading, the questions with their options, a folded answer key). The practice is
the copy that checks an answer and keeps the reader's progress, so it is the copy that stays, and it
stays IN PLACE: the quiz is drawn where the lesson's section was, under that section's own heading,
and the static questions and their key are not drawn at all. The practice is then not listed again
below or opened in a workspace, because it is already on the page. `once(document, panel)` returns
the document to render.

**How you use it.** `page.document.compose` calls it first, over the served document, with `panel`,
a function that renders one practice section's quiz markup, and renders what it returns.
⛔ It reads the document and never changes the one it is given.

**Depends on.** `exercise` for a practice's record. Nothing else.

## ⭐ Decided by the text, never by a name

A range of a lesson's blocks is the quiz when it starts at a heading, runs to the next heading of
the same or a higher level, and contains EVERY stem of one quiz practice of the unit verbatim. A
heading called `Quiz` that holds different questions is left alone, so is a unit with no quiz
practice, and so is a section no practice matches: such a page is the page it was, byte for byte.
A mock exam is a quiz for this purpose: its page lists the questions and folds the key away just
the same, and the key must not be readable before the sitting. A review bank and a deck are other
shapes and are never what a lesson repeats. One practice stands in at most one place.

## ⛔ Block positions do not move

Every block keeps its position, because the ids a page's headings and links carry are positions. The
first block after the heading becomes the quiz (an html block) and the rest become empty html
blocks, which draw nothing. The matched practice's own section leaves the document, so no card,
outline entry or panel is made for it a second time.
"""

from __future__ import annotations

from collections.abc import Callable

from studyforge.exercise import from_document
from studyforge.exercise.errors import ExerciseError

def once(document: dict, panel: Callable[[dict, dict], str]) -> dict:
    """Return `document`, with a lesson's repeat of a quiz practice replaced by that quiz."""
    sections = document.get("sections")
    if not isinstance(sections, list):
        return document
    quizzes = _stems(sections)
    if not quizzes:
        return document
    changed = False
    taken: set[int] = set()
    drawn = []
    for section in sections:
        blocks = section.get("blocks") if isinstance(section, dict) else None
        if not isinstance(section, dict) or section.get("kind") == "practice" or not blocks:
            drawn.append(section)
            continue
        replaced = _replace(blocks, quizzes, taken, sections, lambda one: panel(one, document))
        if replaced is blocks:
            drawn.append(section)
        else:
            changed = True
            drawn.append({**section, "blocks": replaced})
    if not changed:
        return document
    kept = [one for index, one in enumerate(drawn) if index not in taken]
    return {**document, "sections": kept}


def _stems(sections: list) -> list[tuple[int, tuple[str, ...]]]:
    """`(position, stems)` of every plain quiz practice, in the document's order."""
    found = []
    for position, section in enumerate(sections):
        record = section.get("workspace") if isinstance(section, dict) else None
        if not isinstance(record, dict) or section.get("kind") != "practice":
            continue
        try:
            exercise = from_document(record, "a unit's practice")
        except ExerciseError:
            continue
        if exercise.is_quiz and exercise.review is None:
            stems = tuple(one.stem for one in exercise.questions or ())
            if stems:
                found.append((position, stems))
    return found


def _replace(blocks: list, quizzes: list, taken: set[int], sections: list, panel):
    """Return `blocks` with each repeated quiz range replaced, or the same list when none is."""
    out = list(blocks)
    index = 0
    while index < len(out):
        head = out[index]
        if isinstance(head, dict) and head.get("type") == "heading" and head.get("level"):
            end = _end(out, index)
            if end - index > 1:
                text = " ".join(_text(block) for block in out[index + 1 : end])
                match = next(
                    (
                        position
                        for position, stems in quizzes
                        if position not in taken and all(stem in text for stem in stems)
                    ),
                    None,
                )
                if match is not None:
                    taken.add(match)
                    out[index + 1] = {"type": "html", "text": panel(sections[match])}
                    for place in range(index + 2, end):
                        out[place] = {"type": "html", "text": ""}
                    index = end
                    continue
        index += 1
    return blocks if out == list(blocks) else out


def _end(blocks: list, start: int) -> int:
    """The index of the next heading of the same or a higher level, or the end."""
    level = blocks[start]["level"]
    for index in range(start + 1, len(blocks)):
        block = blocks[index]
        is_heading = isinstance(block, dict) and block.get("type") == "heading"
        if is_heading and block.get("level", 9) <= level:
            return index
    return len(blocks)


def _text(value: object) -> str:
    """Every string a block holds, joined, however deep."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_text(part) for part in value.values())
    if isinstance(value, list):
        return " ".join(_text(part) for part in value)
    return ""
