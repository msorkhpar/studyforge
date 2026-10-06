"""The mock exam of the course shape: six scenario questions over the level, two domains.

⭐ Each question is written from one passage of the exam page (`PASSAGES`), names the domain it
belongs to, and keys one option whose sentence says why. The passages are the page's own words,
so `Q1` can be taken from the page and `Q3` rules out every wrong option by a passage.
"""

from __future__ import annotations

from studyforge.exercise import Origin
from studyforge.exercise.quiz import Domain, Mock, Option, Question

PAGE = "course/level-1/02-exam-readiness/01-mock-exam.md"
PASS_MARK = 70
DOMAINS = (
    Domain("AS1", "Prompting and task execution"),
    Domain("AS2", "Output evaluation and validation"),
)

#: `(heading, passage)`: what the page teaches, one section each.
PASSAGES = (
    ("A request holds the whole conversation",
     "The service keeps no memory between requests. An application that wants a follow-up "
     "to make sense sends every earlier turn again, in order, with the new one last."),
    ("A system prompt sets the role once",
     "Instructions that apply to every turn belong in the system prompt, which is a field of "
     "the request of its own and is not one of the turns."),
    ("Ask for the shape you will parse",
     "When a program reads the answer, the prompt names the exact shape wanted, and the "
     "program checks the shape before it trusts the content."),
    ("An answer that parses is not yet correct",
     "A reply can be well formed and still wrong. A check that only parses the reply passes "
     "it, so a test compares the content with an expected value."),
    ("A stop reason says why the reply ended",
     "A reply that stopped because it hit the length limit is cut short. The application "
     "reads the stop reason and treats that case as incomplete, never as a finished answer."),
    ("Retry only what can succeed",
     "A request that failed for being overloaded may succeed later, so it is retried with a "
     "growing wait. A request that failed for being malformed fails again, so it is not."),
)


def _options(key: str, texts: tuple[tuple[str, str], ...]) -> tuple[Option, ...]:
    return tuple(
        Option(id=letter, text=text, correct=letter == key, says=says)
        for letter, (text, says) in zip("abc", texts, strict=True)
    )


def questions() -> tuple[Question, ...]:
    def question(n: int, domain: str, stem: str, key: str, texts) -> Question:
        heading = PASSAGES[n][0]
        return Question(
            id=f"x{n + 1}", stem=stem, options=_options(key, texts),
            origin=Origin(PAGE, heading), domain=domain,
        )

    return (
        question(
            0, "AS1",
            "A support bot answers 'and what about the second one?' as if it had never been "
            "told what the first was. Its code sends only the newest message. What is the fix?",
            "b",
            (("Ask the model to remember harder", "The passage says the service keeps no memory."),
             ("Send every earlier turn again with the new one", "The passage says so."),
             ("Raise the length limit", "The passage ties history to the request, not the limit.")),
        ),
        question(
            1, "AS1",
            "A team repeats 'You are a careful tax assistant' as the first user turn of every "
            "request. Where does that sentence belong instead?",
            "a",
            (("In the system prompt field of the request", "The passage says so."),
             ("At the end of the last turn", "The passage places it outside the turns."),
             ("In a file the model reads at start", "The passage names the request's own field.")),
        ),
        question(
            2, "AS2",
            "A program splits the reply on commas to fill a table. Sometimes the table breaks. "
            "What should the prompt and the program do?",
            "c",
            (("Trust the content and skip the check", "The passage says the shape is checked."),
             ("Ask politely for fewer commas", "The passage asks for the exact shape, not manners."),
             ("Name the exact shape and check it before use", "The passage says so.")),
        ),
        question(
            3, "AS2",
            "A test only checks that the reply is valid JSON, and it passes. A user then finds "
            "a wrong total. What does the test miss?",
            "b",
            (("The reply was not valid JSON", "The test already proved that it was."),
             ("It never compares the content with an expected value", "The passage says so."),
             ("The model was too slow", "The passage is about content, not speed.")),
        ),
        question(
            4, "AS1",
            "A summary ends mid-sentence and the stop reason says the length limit was hit. "
            "How does the application treat it?",
            "a",
            (("As incomplete, never as a finished answer", "The passage says so."),
             ("As finished, because a reply came back", "The passage says it is cut short."),
             ("As an error in the prompt's grammar", "The passage names the limit as the cause.")),
        ),
        question(
            5, "AS2",
            "One call failed because the service was overloaded and another because the body "
            "was malformed. Which are retried?",
            "c",
            (("Both, with the same wait", "The passage says the malformed one fails again."),
             ("Neither, errors are final", "The passage says an overloaded one may succeed."),
             ("Only the overloaded one, with a growing wait", "The passage says so.")),
        ),
    )


def mock() -> Mock:
    return Mock(pass_mark=PASS_MARK, domains=DOMAINS)
