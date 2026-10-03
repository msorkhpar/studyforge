"""The exam-form mock of the course shape: a pool of twelve questions that uses every opt-in key.

Two domains with weights, three scenarios, a multiple-response question, a question that keeps its
option order, three difficulties, a timer, an exam layout, three sittings that draw from the pool
and a scaled score. Each question is written from one passage of `PAGE`, the pool's own page.
"""

from __future__ import annotations

from studyforge.exercise import Origin
from studyforge.exercise.quiz import (
    Difficulty, Domain, Mock, Option, Question, Scale, Scenario, Sitting,
)
from tests.fixtures.claude_shape import exam

PAGE = "course/level-1/02-exam-readiness/02-exam-pool.md"
PASSAGES = exam.PASSAGES
DOMAINS = (
    Domain("AS1", "Prompting and task execution", 60),
    Domain("AS2", "Output evaluation and validation", 40),
)
DIFFICULTIES = (
    Difficulty("foundational", "Foundational"),
    Difficulty("applied", "Applied"),
    Difficulty("scenario-hard", "Scenario, hard"),
)
SCENARIOS = (
    Scenario("support-bot", "A support bot that forgets",
             "A support team ships a chat bot. Users say it forgets what they said a moment "
             "ago. The team reads its code to find out why."),
    Scenario("report-tool", "A report tool that breaks",
             "A tool asks the model for a table and splits the reply on commas. Some days the "
             "table breaks. A test that only parses the reply keeps passing."),
    Scenario("night-job", "A night job that stops early",
             "A nightly job summarises tickets. Some summaries end in the middle of a sentence. "
             "Some calls fail with errors that differ from one night to the next."),
)
SITTINGS = (
    Sitting("full", "Full sitting", questions=10, minutes=40),
    Sitting("short", "Short sitting", questions=5),
    Sitting("scenarios", "Scenario sitting", scenarios=2),
)

#: `(heading index, domain, difficulty, scenario, stem, key letters, [(text, says)])`, in order.
ROWS = (
    (0, "AS1", "applied", "support-bot",
     "The bot answers 'and the second one?' as if it had never seen the first. It sends only the "
     "newest message. What is the fix?", "b",
     (("Ask the model to remember harder", "The service keeps no memory between requests."),
      ("Send every earlier turn again with the new one", "The history rides on each request."),
      ("Raise the length limit", "The limit does not carry history."))),
    (1, "AS1", "foundational", "support-bot",
     "The team repeats a role sentence as the first user turn of every request. Where does it "
     "belong?", "a",
     (("In the system prompt field of the request", "That field applies to every turn."),
      ("At the end of the last turn", "The passage places it outside the turns."),
      ("In a file the model reads at start", "The request has its own field for it."))),
    (2, "AS2", "applied", "report-tool",
     "What should the prompt and the program do about the broken table?", "c",
     (("Trust the content and skip the check", "The shape is checked before the content is trusted."),
      ("Ask politely for fewer commas", "The passage asks for an exact shape, not manners."),
      ("Name the exact shape and check it before use", "That is what the passage teaches."))),
    (3, "AS2", "scenario-hard", "report-tool",
     "The parse-only test passes while a user finds a wrong total. What does it miss?", "b",
     (("The reply was not valid JSON", "The test already proved that it was."),
      ("It never compares the content with an expected value", "Parsing says nothing of content."),
      ("The model was too slow", "The passage is about content, not speed."))),
    (4, "AS1", "applied", "night-job",
     "A summary ends mid-sentence and the stop reason names the length limit. What does the "
     "application do?", "a",
     (("Treat it as incomplete", "A reply cut by the limit is never a finished answer."),
      ("Treat it as finished", "A reply came back, but it was cut short."),
      ("Blame the prompt's grammar", "The limit is the stated cause."))),
    (5, "AS2", "scenario-hard", "night-job",
     "One call failed overloaded and another malformed. Which are retried?", "c",
     (("Both with the same wait", "The malformed one fails again."),
      ("Neither", "An overloaded one may succeed later."),
      ("Only the overloaded one, with a growing wait", "That is the rule the passage states."))),
    (0, "AS1", "foundational", None,
     "What does a follow-up request carry so that it makes sense?", "c",
     (("Only the new turn", "The service keeps no memory."),
      ("A summary the model wrote", "The passage says every earlier turn."),
      ("Every earlier turn, in order, then the new one", "That is the whole history."))),
    (2, "AS2", "foundational", None,
     "A program reads the answer. What does the prompt name?", "a",
     (("The exact shape wanted", "The program checks that shape."),
      ("The tone wanted", "The passage is about shape."),
      ("The length wanted", "Length is not what the program parses."))),
    (1, "AS1", "applied", None,
     "Which two statements about the system prompt are true?", "ab",
     (("It holds instructions that apply to every turn", "That is its job."),
      ("It is a field of the request of its own", "It is not one of the turns."),
      ("It is the first user turn", "It is not a turn at all."),
      ("It is sent only once per account", "It rides on the request."))),
    (3, "AS2", "applied", None,
     "A reply is well formed. Which check is enough?", "b",
     (("One that only parses it", "A well formed reply can still be wrong."),
      ("One that compares the content with an expected value", "That catches a wrong content."),
      ("One that counts the characters", "Length says nothing of correctness."))),
    (4, "AS1", "foundational", None,
     "Where does an application read why a reply ended?", "a",
     (("In the stop reason", "The stop reason says why the reply ended."),
      ("In the first word of the reply", "The reply's words do not say."),
      ("In the request's headers", "The reason comes with the reply."))),
    (5, "AS1", "applied", None,
     "A request failed for being malformed. What does the application do?", "b",
     (("Retry it with a growing wait", "It would fail again."),
      ("Not retry it", "A malformed request fails again."),
      ("Retry it at once", "Waiting changes nothing about its shape."))),
)


def questions() -> tuple[Question, ...]:
    built = []
    for n, (heading, domain, difficulty, scenario, stem, keys, texts) in enumerate(ROWS, 1):
        letters = "abcd"[: len(texts)]
        built.append(Question(
            id=f"p{n}", stem=stem,
            options=tuple(
                Option(id=letter, text=text, correct=letter in keys, says=says)
                for letter, (text, says) in zip(letters, texts, strict=True)
            ),
            origin=Origin(PAGE, PASSAGES[heading][0]), domain=domain, scenario=scenario,
            select=len(keys) if len(keys) > 1 else None,
            shuffle=False if n == 8 else None, difficulty=difficulty,
        ))
    return tuple(built)


def mock() -> Mock:
    return Mock(
        pass_mark=70, domains=DOMAINS, minutes=40, layout="exam", scenarios=SCENARIOS,
        sittings=SITTINGS, scale=Scale(100, 1000, 720), difficulties=DIFFICULTIES,
    )
