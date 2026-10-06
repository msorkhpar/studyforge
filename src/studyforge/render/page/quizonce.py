"""A quiz is shown once: the interactive quiz stands where the lesson's static copy was.

**What it does.** A lesson sometimes ends with a passage that lists the same questions its quiz
practice asks (a heading, the questions with their options, a folded answer key). The practice is
the copy that checks an answer and keeps the reader's progress, so it is the copy that stays, and it
stays IN PLACE: the quiz is drawn where the lesson's questions were, under the lesson's own heading,
and the static questions and their key are not drawn at all. The practice is then not listed again
below or opened in a workspace, because it is already on the page. `once(document, panel)` returns
the document to render.

**How you use it.** `page.document.compose` calls it first, over the served document, with `panel`,
a function that renders one practice section's quiz markup, and renders what it returns.
⛔ It reads the document and never changes the one it is given.

**Depends on.** `exercise` for a practice's record. Nothing else.

## ⭐ Decided by the text, never by a name

A range of a lesson's blocks is the quiz when it is one unbroken run of question blocks that holds
EVERY stem of one quiz practice of the unit verbatim. The run starts at the first block that holds a
stem and ends at the last; between them stand only blocks that hold a stem, option lists, code
samples, images or empty blocks. The closed disclosure right after the run, the folded key, belongs
to it. A heading called `Quiz` that holds different questions is left alone, so is a unit with no
quiz practice, and so is a section no practice matches: such a page is the page it was, byte for
byte.
A mock exam is a quiz for this purpose: its page lists the questions and folds the key away just
the same, and the key must not be readable before the sitting. A review bank and a deck are other
shapes and are never what a lesson repeats. One practice stands in at most one place.

## ⛔ Only the quiz's own blocks, and only when they are certain

A lesson may be one section from its title to its end, so a heading's range can hold the whole
lesson; the range is never a heading's. Every block outside the run and its key stays exactly as
it was: the lesson's heading, its prose before and after, a mock page's intro and domain table. When
the stems are scattered through prose, or two runs could each be the quiz, nothing is removed: the
page stays as written and the practice is drawn after it, as any practice is. The quiz with the most
questions is matched first, so a module quiz that repeats a page quiz's questions takes its own run.

## ⛔ Block positions do not move

Every block keeps its position, because the ids a page's headings and links carry are positions. The
run's first block becomes the quiz (an html block) and the rest of the run and its key become empty
html blocks, which draw nothing. The matched practice's own section leaves the document, so no card,
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


#: Blocks that may stand between two question blocks of one quiz: an option list, a code sample, an
#: image, or nothing at all. A paragraph, a table or a heading between them is lesson text.
_BETWEEN = frozenset({"list", "code", "image"})


def _replace(blocks: list, quizzes: list, taken: set[int], sections: list, panel):
    """Return `blocks` with each repeated quiz range replaced, or the same list when none is."""
    out = list(blocks)
    drawn: set[int] = set()
    # ⭐ The quiz with the most questions claims its range first, so a module quiz that repeats a
    # page quiz's questions does not take the page quiz's range.
    for position, stems in sorted(quizzes, key=lambda one: -len(one[1])):
        if position in taken:
            continue
        runs = _runs(out, stems, drawn)
        ranges = [one for one in runs if all(stem in _span(out, one) for stem in stems)]
        if len(ranges) != 1:
            continue  # ⛔ not delimited with certainty: the page stays as written
        first, last = ranges[0]
        if last + 1 < len(out) and last + 1 not in drawn and _is_key(out[last + 1]):
            last += 1
        taken.add(position)
        out[first] = {"type": "html", "text": panel(sections[position])}
        for place in range(first + 1, last + 1):
            out[place] = {"type": "html", "text": ""}
        drawn.update(range(first, last + 1))
    return blocks if out == list(blocks) else out


def _runs(blocks: list, stems: tuple[str, ...], drawn: set[int]) -> list[tuple[int, int]]:
    """`(first, last)` of every unbroken run of question blocks, each starting and ending on a stem.

    A block already drawn as a quiz breaks a run and is never part of one.
    """
    found = []
    first = last = None
    for index, block in enumerate(blocks):
        if index not in drawn and any(stem in _text(block) for stem in stems):
            first = index if first is None else first
            last = index
        elif first is not None and (index in drawn or not _between(block)):
            found.append((first, last))
            first = last = None
    if first is not None:
        found.append((first, last))
    return found


def _between(block: object) -> bool:
    """Whether `block` may stand between two questions of one quiz."""
    if not isinstance(block, dict):
        return False
    return block.get("type") in _BETWEEN or block == {"type": "html", "text": ""}


def _is_key(block: object) -> bool:
    """Whether `block` is a folded answer key: a closed disclosure."""
    return isinstance(block, dict) and block.get("type") == "disclosure" and not block.get("open")


def _span(blocks: list, run: tuple[int, int]) -> str:
    """Every string the blocks of `run` hold, joined."""
    return " ".join(_text(block) for block in blocks[run[0] : run[1] + 1])


def _text(value: object) -> str:
    """Every string a block holds, joined, however deep."""
    if isinstance(value, str):
        return value
    if isinstance(value, dict):
        return " ".join(_text(part) for part in value.values())
    if isinstance(value, list):
        return " ".join(_text(part) for part in value)
    return ""
