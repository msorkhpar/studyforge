"""A mock exam's material: six questions over three domains, as raw record values.

⭐ **Raw values, not objects**, so each reading reaches the record the way a build does: through
`from_document`. The questions are written from whatever passage the caller names, so the same six
serve a record test over `depth1`, a gate test over the authoring corpus's prose page, and the
browser test over a built page.

⚠️ **The key sits in a different position in different questions** (`a`, `b` and `c`), so a
scoring rule that always answered `a` would not pass every question by luck.
⛔ Mirrors no source module (R12 is one-way): it is material, not a test.
"""

from __future__ import annotations

#: The three domains, in the order the exam reports them.
DOMAINS = [
    {"id": "D1", "title": "Reading the gauge"},
    {"id": "D2", "title": "Writing it down"},
    {"id": "D3", "title": "Comparing readings"},
]

PASS_MARK = 60

#: `(question id, domain, stem, key letter)` and the three options' texts, in order.
ROWS = [
    ("x1", "D1", "At what hour is the gauge read?", "a",
     ("At the same hour every day", "Whenever it rains", "At the end of the month")),
    ("x2", "D1", "Beside what is the hour written?", "b",
     ("Beside the date only", "Beside the number", "Beside the weather")),
    ("x3", "D2", "On which day is a reading copied into the book?", "c",
     ("At the end of the month", "On the next quiet day", "On the same day")),
    ("x4", "D2", "What is a reading nobody wrote down?", "a",
     ("A reading nobody has", "A reading kept for later", "A reading that is lost and found")),
    ("x5", "D3", "Why can two readings at different hours not be compared?", "b",
     ("The gauge resets daily", "The hour changes the number", "The book has no room")),
    ("x6", "D3", "What makes readings comparable?", "c",
     ("A bigger gauge", "A second observer", "The same hour each day")),
]


def question(row: tuple, origin: dict, **changes) -> dict:
    """One raw question from a row, written from `origin`, with `changes` applied."""
    identifier, domain, stem, key, texts = row
    options = [
        {
            "id": letter,
            "text": text,
            "correct": letter == key,
            "says": f"The page's own sentence settles {identifier} option {letter}.",
        }
        for letter, text in zip("abc", texts, strict=True)
    ]
    made = {"id": identifier, "stem": stem, "options": options, "origin": origin, "domain": domain}
    made.update(changes)
    return {key_: value for key_, value in made.items() if value is not None}


def questions(origin: dict) -> list[dict]:
    """All six questions, written from `origin`."""
    return [question(row, origin) for row in ROWS]


def mock(**changes) -> dict:
    """The record's `mock` key, with `changes` applied."""
    return {"pass_mark": PASS_MARK, "domains": [dict(d) for d in DOMAINS], **changes}


def keyed() -> dict[str, str]:
    """`{question id: the keyed option's id}`: the answers that score every question right."""
    return {row[0]: row[3] for row in ROWS}


def wrong() -> dict[str, str]:
    """`{question id: a wrong option's id}`: the first option that is not the key."""
    return {row[0]: next(letter for letter in "abc" if letter != row[3]) for row in ROWS}
