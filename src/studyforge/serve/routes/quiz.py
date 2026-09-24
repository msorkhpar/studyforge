r"""The quiz namespace: the local study server grades a quiz, and the page never holds its key.

**What it does.** Answers under `/api/v1/quiz/`:

- `GET` (empty) → `quiz-index`: the one endpoint, spelled as a template;
- `POST <corpus>/<practice key>/<question>=<option>/…` → `quiz-verdict`: every question
  of that practice's quiz read against the answers the path names, each row saying
  whether it was answered, whether it was right, and the sentence for the option the
  reader CHOSE — plus the count and whether the quiz is complete.

**How you use it.** `serve.instance.namespaces_of` registers
`partial(route, discovered, sources)` under `NAMESPACE`, with `NAMESPACE` among
`app`'s writers; the page reaches it through `window.studyforge.quiz`, which the
served client publishes (`serve/assets/run-client.js`).

**Depends on.** `exercise` for what a quiz IS and `exercise.quiz.grade` for the rule
— ⛔ the framework's ONE grading rule, never a second spelling of it here —
`progress` for the practice key, `unit.served` for the document, and
`serve.response`. ⛔ **Not `execute`, not a socket, not a model**: this module
imports nothing that can start a process, reach a network or touch a container,
and `tests/studyforge/serve/test_init.py` reads that of the whole package.

## ⛔ THE USER'S RULING, 2026-09-23, AND WHAT IT REVERSED

> *"the quiz itself again should not require an online or agent check for the answer
> user provided. It will be just a test with the correct answer residing on the
> server side. When user answers it will get validated and result will be returned
> to the user with explanation if needed"*

⛔ **Until that ruling the key and every per-option sentence shipped INSIDE the page** and
the page graded itself, identically over `file://`. ⭐ **Now no built page and no
asset a page loads carries either**: the page sends what the reader chose, and this
route reads the key from the unit's generated document — built, per request, from
the corpus's archive on disk, which is where the exercise bundle's quiz record
lives — and answers. ⛔ **No model, no network, no container: a fixed comparison.**

## ⭐ One request grades the WHOLE quiz, not one answer

⭐ **Completion is a property of the whole quiz** — every question answered
correctly (`exercise.quiz.completes`) — so a request that carries every answer
the reader has chosen lets `grade` decide it ONCE, here, in Python. ⛔ A
per-answer route would leave the page to add the verdicts up itself, which is a
second spelling of the completion rule in a file that cannot import the first.
⚠️ The path carries the answers because a `Request` carries no body — `serve.app`
drains and DISCARDS one — and that is a property of this package, not a choice
this module may undo.

## ⭐ A wrong answer reveals ITS OWN sentence, and never which option was right

⭐ **The explanation is the chosen option's sentence, right or wrong** — every
option carries one (gate `Q4`), and it says why THAT option is or is not the
answer, which is *"with explanation if needed"* read literally. ⛔ **The key is
never named in a verdict.** A reader told the answer on their first wrong choice
has been told instead of taught; one told why their choice fails can try again,
and a quiz has no attempt limit. ⚠️ Named for what it is: with three options a
reader can still find the key by trying each, and nothing here pretends
otherwise — the key is kept out of the PAGE, which is the ruling, not made
unguessable.

## ⛔ A quiz produces no run, and this route records nothing

⭐ **A verdict is a response and nothing else**: nothing is written to the
progress store, which holds RUN outcomes (`progress.is_pass` is untouched), and
the reader's completion stays the reader's — the page shows it from this
verdict. ⛔ So this is `POST` because grading is an act a prefetch must never
take, not because anything is stored.

## ⛔ The guards are `serve.app`'s, and one more is this module's

⭐ Every request reaches this module only past `serve.security.refusal` — the
loopback peer, the `Host` allow-list, `Sec-Fetch-Site` and `Origin` (R8). ⛔ And
`Origin: null` — a page opened from a file — is refused here, exactly as the run
namespace refuses it: a file page says the quiz needs the local study server and
asks nothing.
"""

from __future__ import annotations

from collections.abc import Mapping

from studyforge.archive.scrub import PersonalDataLeak
from studyforge.exercise import ExerciseError, from_document
from studyforge.exercise.quiz import QUIZ_ID, Verdict, grade
from studyforge.progress import RAISES as PROGRESS_RAISES
from studyforge.progress import parse_practice_key
from studyforge.serve.discovery import Discovered
from studyforge.serve.response import API_PREFIX, Request, Response, error, json_response
from studyforge.serve.routes.content import ContentSource
from studyforge.unit import served
from studyforge.unit.errors import ContentError

#: The name this namespace is registered under. ⭐ The framework's one spelling of
#: it: the served client reads it (`tests/studyforge/serve/routes/test_quiz_client.py`).
NAMESPACE = "quiz"

#: What joins a question's id to the option chosen for it, inside one segment.
#: ⛔ A character `QUIZ_ID` never admits, so a segment splits exactly one way —
#: and one a practice key never holds either, which is how the answers are told
#: apart from the key's own segments.
CHOSE = "="

#: The section kind a quiz lives in — the archive's word, as `routes.run` reads it.
PRACTICE = "practice"

NO_SUCH_CORPUS = "no such corpus"
NO_SUCH_PRACTICE = "no such practice"
NOT_A_QUIZ = "this practice is not a quiz, so there is nothing here to grade"
MALFORMED = "the answers are not question=option segments, one per question"
UNRECOGNISED = "the unit document or its quiz failed validation"
GATED = "the unit document failed the personal-data gate"
NOT_FROM_A_FILE = "a page opened from a file cannot have a quiz graded"
GRADE_BY_POST = "a quiz is graded by POST"


def route(
    discovered: Discovered, sources: Mapping[str, ContentSource], request: Request, rest: str
) -> Response:
    """Answer one request under `/api/v1/quiz/`; `rest` is the path after it."""
    if rest == "":
        if request.method == "POST":
            return _not_allowed("GET, HEAD")
        return json_response(200, index())
    if request.method != "POST":
        return _not_allowed("POST")
    if request.headers.get("Origin", "").strip() == "null":
        return error(403, NOT_FROM_A_FILE)
    return verdict_of(discovered, sources, rest)


def index() -> dict:
    """Return what this namespace offers: one endpoint, and how its path is spelled."""
    return {
        "resource": "quiz-index",
        "grade": f"{API_PREFIX}/{NAMESPACE}/{{corpus}}/{{practice}}/{{question}}{CHOSE}{{option}}",
    }


def verdict_of(discovered: Discovered, sources: Mapping[str, ContentSource], rest: str) -> Response:
    """Answer `<corpus>/<practice key>/<question>=<option>/…` with the quiz's verdict."""
    name, _, tail = rest.partition("/")
    corpus = discovered.by_source.get(name)
    if corpus is None or name not in sources:
        return error(404, NO_SUCH_CORPUS)
    key, answers = split(tail)
    if answers is None:
        return error(400, MALFORMED)
    try:
        address, ordinal, section = parse_practice_key(key, corpus.depth)
    except PROGRESS_RAISES:
        return error(404, NO_SUCH_PRACTICE)
    try:
        workspace = workspace_of(sources[name], address.unit_key(ordinal), section)
        exercise = None if workspace is None else from_document(workspace, "this quiz")
    except PersonalDataLeak:
        return error(500, GATED)
    except ContentError, ExerciseError:
        return error(422, UNRECOGNISED)
    except LookupError:
        return error(404, NO_SUCH_PRACTICE)
    if exercise is None or not exercise.is_quiz:
        return error(409, NOT_A_QUIZ)
    return json_response(200, verdict(name, key, grade(exercise.questions, answers)))


def split(tail: str) -> tuple[str, dict[str, str] | None]:
    """Split `<key>/<question>=<option>/…` into the key and the answers, or `None` for them.

    ⛔ **The answers are every segment from the first that carries `CHOSE`**, and
    every one after it must carry it too — a key segment is lowercase letters,
    digits and hyphens and never holds one. ⭐ No answers at all is an answer:
    a quiz with nothing chosen is graded as nothing answered, which is what
    `grade` says of it.
    """
    segments = tail.split("/")
    first = next((at for at, one in enumerate(segments) if CHOSE in one), len(segments))
    key = "/".join(segments[:first])
    answers: dict[str, str] = {}
    for segment in segments[first:]:
        question, chose, option = segment.partition(CHOSE)
        if not chose or not QUIZ_ID.match(question) or not QUIZ_ID.match(option):
            return key, None
        if question in answers:
            return key, None
        answers[question] = option
    return key, answers


def verdict(corpus: str, practice: str, graded: Verdict) -> dict:
    """Return what a reader is told: one row per question, the count, and completion.

    ⛔ **No row names the keyed option.** `chosen` is the reader's own choice
    echoed back, `says` is THAT option's sentence, and a question nobody answered
    says nothing — so nothing here tells a reader which option they should have
    picked (see *A wrong answer reveals ITS OWN sentence* above).
    """
    return {
        "resource": "quiz-verdict",
        "corpus": corpus,
        "practice": practice,
        "asked": graded.asked,
        "right": graded.right,
        "complete": graded.complete,
        "questions": [
            {
                "id": row.question.id,
                "answered": row.answered,
                "chosen": None if row.chosen is None else row.chosen.id,
                "correct": row.correct,
                "says": row.says,
            }
            for row in graded.answered
        ],
    }


def workspace_of(source: ContentSource, unit: str, section: str) -> dict | None:
    """Return the practice section's quiz record from the unit's generated document.

    Raises `LookupError` when the unit has no document or no practice `section`;
    `None` is a practice that carries no record at all. ⚠️ The same read
    `routes.run.workspace_of` takes, spelled here rather than imported: that
    module imports `execute`, and this one must never (see *Depends on*).
    """
    text = source.unit(unit)
    if text is None:
        raise LookupError(unit)
    document = served.parse(text, served.UNIT_FILENAME)
    for found in document["sections"]:
        if found.get("key") == section and found.get("kind") == PRACTICE:
            return found.get("workspace")
    raise LookupError(section)


def _not_allowed(allow: str) -> Response:
    """Answer `405` naming the one method this path takes."""
    answer = error(405, GRADE_BY_POST if allow == "POST" else "method not allowed")
    return Response(405, (*answer.headers, ("Allow", allow)), answer.body)
