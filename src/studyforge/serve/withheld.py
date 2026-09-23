r"""Withheld: a quiz's key and its sentences never leave the serving process (`W452`).

**What it does.** Says what of a quiz the SITE may never serve — which option is
keyed (`correct`) and each option's sentence (`says`) — and applies that on the
two ways a document leaves this process:

- `redacted(document)` — a unit document with every quiz option cut down to its
  id and its words, which is what the content namespace answers;
- `carries(body, marks)` — whether a file's bytes hold a served quiz's key or one
  of its sentences, which is what the static mount refuses.

**How you use it.**

    document = redacted(served.parse(text, served.UNIT_FILENAME))   # content namespace
    found = marks_in(document)                                      # before redacting
    if carries(body, found):                                        # a file's bytes
        return not_found
    withheld = refused_by(source)       # what `serve.app` hands the static mount

**Depends on.** The standard library only. ⛔ It imports no route and no reader,
so `routes.content` and `routes.assets` can both use it and neither imports the
other.

## ⛔ THE USER'S RULING, 2026-09-23

⭐ **A quiz's correct answer resides on the SERVER side, and the reader's answers
are validated there.** ⛔ **What the SITE serves never carries the key**, except the
grading route's answer for the option the reader chose (`routes.quiz`). `W451`
took the key out of every built page; ⛔ **this module closes the URLs a page never
loads but a reader can type** (`W451/1`, and the corpus office's `F10`): the unit
document on the content namespace, the archive's `practice-M.json`, the bundle's
`tests/quiz.json`, and any other file under the served root that repeats them.

## ⭐ Why redact one surface and refuse the other

⭐ **The content namespace ANSWERS a document**, whose contract is the unit's shape,
so it answers that shape with the two withheld fields gone: the questions and each
option's words are what the page already shows. ⛔ **The static mount answers FILES,
byte for byte** — a file is not edited on the way out, so a file that carries a
key or a sentence is refused, `404`, exactly as every other refusal there is.
⭐ **Both hold for both forms of `serve`**, because `serve.app` wires them from the
content source every form already hands it.

## ⛔ What `carries` reads, and what it cannot

1. ⭐ **The key, structurally — and ONLY beside a quiz this instance serves**: a
   JSON `"correct": true|false` pair, or a `data-…-correct` attribute (a page
   from a build before `W451`), in a file that ALSO names one of the served
   quizzes' question ids, quoted (`"q-2003"`). ⛔ **Either half alone withholds
   nothing** (register review of `W452`): a question id is on every quiz page
   and is no secret, and a `"correct"` field with no quiz id is some other
   data's own field — a code practice's test cases (`M9`'s Java corpus) must
   not answer a silent `404`. ⭐ Both together are a quiz record carrying its
   key, which is exactly what the archive, the bundle and a quoting document
   hold. ⚠️ So a key for a quiz this instance does NOT serve is served: it is
   the key to nothing the site grades. ⛔ A key with no structure — prose
   saying *"the answer is b"* — is not detectable either.
2. ⭐ **Every sentence of every quiz the instance serves**, found in the text
   raw, JSON-escaped or HTML-escaped, with every run of whitespace read as one
   space — so a hard-wrapped quotation is still found. ⚠️ **A sentence shorter
   than `MIN_WORDS` words is not searched for**: a sentence as short as
   *"Right."* would withhold every page that happens to say it.

⚠️ **Fail closed is deliberate.** A page from an OLD build carries the key in its
attributes and answers `404` here until the corpus is rebuilt — a page that
would hand out the key is not served at all.

⛔ **The files on disk are never touched** (R3): a reader who holds the corpus
checkout can open the bundle, and the ruling is about what the SITE serves.
"""

from __future__ import annotations

import copy
import html
import json
import re
from collections.abc import Callable, Iterator
from dataclasses import dataclass

#: Where a quiz record keeps its questions, and a question its options.
QUESTIONS = "questions"
OPTIONS = "options"

#: The two fields of an option the site never serves: the key and the sentence.
KEY = "correct"
SAYS = "says"
WITHHELD = (KEY, SAYS)

#: A sentence shorter than this, in words, is not searched for in a file.
MIN_WORDS = 4

#: The key as structure: a JSON pair, or a pre-`W451` page's option attribute.
KEY_PATTERN = re.compile(r'"correct"\s*:\s*(?:true|false)\b|\bdata-[a-z-]*-correct\b')


@dataclass(frozen=True)
class Marks:
    """What identifies the quizzes an instance serves: every sentence and every question id."""

    sentences: frozenset[str] = frozenset()
    questions: frozenset[str] = frozenset()

    def __or__(self, other: Marks) -> Marks:
        """Return both sets of marks, as one instance serving both corpora holds them."""
        return Marks(self.sentences | other.sentences, self.questions | other.questions)


def quiz_questions(document: object) -> Iterator[dict]:
    """Yield every question dict of every quiz a unit document's sections carry.

    ⭐ Read RAW, never validated: what is withheld must not depend on the record
    being valid, or an invalid quiz would be served whole.
    """
    sections = document.get("sections") if isinstance(document, dict) else None
    for section in sections if isinstance(sections, list) else ():
        workspace = section.get("workspace") if isinstance(section, dict) else None
        questions = workspace.get(QUESTIONS) if isinstance(workspace, dict) else None
        for question in questions if isinstance(questions, list) else ():
            if isinstance(question, dict):
                yield question


def quiz_options(document: object) -> Iterator[dict]:
    """Yield every option dict of every quiz a unit document's sections carry."""
    for question in quiz_questions(document):
        options = question.get(OPTIONS)
        for option in options if isinstance(options, list) else ():
            if isinstance(option, dict):
                yield option


def marks_in(document: object) -> Marks:
    """Return every option sentence and every question id of every quiz in a unit document."""
    return Marks(
        frozenset(o[SAYS] for o in quiz_options(document) if isinstance(o.get(SAYS), str)),
        frozenset(q["id"] for q in quiz_questions(document) if isinstance(q.get("id"), str)),
    )


def redacted(document: object) -> object:
    """Return `document` with every quiz option's key and sentence removed.

    ⛔ **A copy**: the document handed in is not changed, so a caller reading the
    key from the same document (the quiz route) still grades.
    """
    answered = copy.deepcopy(document)
    for option in quiz_options(answered):
        for field in WITHHELD:
            option.pop(field, None)
    return answered


def spellings(sentence: str) -> set[str]:
    """Return how `sentence` can appear in a served text, whitespace collapsed."""
    forms = {
        sentence,
        json.dumps(sentence)[1:-1],
        json.dumps(sentence, ensure_ascii=False)[1:-1],
        html.escape(sentence, quote=True),
        html.escape(sentence, quote=False),
    }
    return {collapsed(form) for form in forms}


def collapsed(text: str) -> str:
    """Return `text` with every run of whitespace read as one space."""
    return " ".join(text.split())


def searched(sentences: frozenset[str]) -> frozenset[str]:
    """Return every spelling of every sentence long enough to be searched for."""
    return frozenset(
        form
        for sentence in sentences
        if len(sentence.split()) >= MIN_WORDS
        for form in spellings(sentence)
    )


def marks_of(source: object) -> Marks:
    """Return what a content source says marks its quizzes; none if it cannot say.

    ⚠️ Duck-typed, because a test's stand-in source serves no quiz: both real
    sources (`routes.content.CorpusContent`, `addressing.CorporaContent`) answer.
    """
    found = getattr(source, "withheld", None)
    return Marks() if found is None else found()


def carries(body: bytes, marks: Marks) -> bool:
    """Say whether `body` holds a served quiz's key, or any of its sentences in any spelling."""
    text = body.decode("utf-8", errors="replace")
    if KEY_PATTERN.search(text) and any(f'"{one}"' in text for one in marks.questions):
        return True
    forms = searched(marks.sentences)
    if not forms:
        return False
    flat = collapsed(text)
    return any(form in flat for form in forms)


def refused_by(source: object) -> Callable[[bytes], bool]:
    """Return the static mount's `withheld` for an instance serving `source`'s corpora.

    ⭐ **The marks are asked for per file, never captured once**, so a quiz
    added or edited while the instance serves is withheld from then on.
    """
    return lambda body: carries(body, marks_of(source))
