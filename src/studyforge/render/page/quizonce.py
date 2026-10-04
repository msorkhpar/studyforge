"""A quiz is shown once: the practice keeps it, and the lesson's own copy points there.

**What it does.** A lesson sometimes ends with a section that lists the same questions its practice
asks (a heading, the questions with their options, an answer key). The practice is the one that
checks an answer and keeps the reader's progress, so it is the copy that stays; the lesson's copy
becomes one sentence naming where the questions are. `once(document)` returns the document to
render.

**How you use it.** `page.document.render` calls it first, over the served document, and renders
what
it returns. ⛔ It reads the document and never changes the one it is given.

**Depends on.** `exercise` for a practice's record. Nothing else.

## ⭐ Decided by the text, never by a name

A range of a lesson's blocks is the quiz when it starts at a heading, runs to the next heading of
the same or a higher level, and contains EVERY stem of one quiz practice of the unit verbatim. A
heading called `Quiz` that holds different questions is left alone, and so is a unit with no quiz
practice; a mock exam, a review bank and a deck are other shapes and are never what a lesson
repeats.

## ⛔ Block positions do not move

Every block keeps its position, because the ids a page's headings and links carry are positions.
The first block after the heading becomes the sentence and the rest become empty html blocks, which
draw nothing. A page with no repeated quiz is the page it was, byte for byte.
"""

from __future__ import annotations

from studyforge.exercise import from_document
from studyforge.exercise.errors import ExerciseError

#: The sentence that stands where the lesson's copy was. This framework's own words.
POINTER = (
    "These questions are in the practice below, where each answer is checked as you give it "
    "and your progress is kept."
)


def once(document: dict) -> dict:
    """Return `document`, with a lesson's repeat of a quiz practice replaced by a pointer."""
    sections = document.get("sections")
    if not isinstance(sections, list):
        return document
    quizzes = _stems(sections)
    if not quizzes:
        return document
    changed = False
    drawn = []
    for section in sections:
        blocks = section.get("blocks") if isinstance(section, dict) else None
        if not isinstance(section, dict) or section.get("kind") == "practice" or not blocks:
            drawn.append(section)
            continue
        replaced = _replace(blocks, quizzes)
        if replaced is blocks:
            drawn.append(section)
        else:
            changed = True
            drawn.append({**section, "blocks": replaced})
    return {**document, "sections": drawn} if changed else document


def _stems(sections: list) -> list[tuple[str, ...]]:
    """The stems of every plain quiz practice, one tuple each."""
    found = []
    for section in sections:
        record = section.get("workspace") if isinstance(section, dict) else None
        if not isinstance(record, dict) or section.get("kind") != "practice":
            continue
        try:
            exercise = from_document(record, "a unit's practice")
        except ExerciseError:
            continue
        if exercise.is_quiz and exercise.mock is None and exercise.review is None:
            stems = tuple(one.stem for one in exercise.questions or ())
            if stems:
                found.append(stems)
    return found


def _replace(blocks: list, quizzes: list[tuple[str, ...]]):
    """Return `blocks` with each repeated quiz range replaced, or the same list when none is."""
    out = list(blocks)
    index = 0
    while index < len(out):
        head = out[index]
        if isinstance(head, dict) and head.get("type") == "heading" and head.get("level"):
            end = _end(out, index)
            if end - index > 1:
                text = " ".join(_text(block) for block in out[index + 1 : end])
                if any(all(stem in text for stem in stems) for stems in quizzes):
                    out[index + 1] = {"type": "para", "text": POINTER}
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
