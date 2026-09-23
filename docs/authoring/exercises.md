# Exercises — including having none

**Read this before you decide your corpus is not finished.**

---

## Two tracks, and the manifest decides which apply

**The reading floor — every corpus, always.** Units readable offline straight
off the filesystem, with no network and no server. Narration. A table of
contents and a root index with working deep links. Navigation between units.
Your own read marks.

**This is a complete product on its own.** A corpus that stops here is not a
degraded one. For prose, a book, a paper collection or a set of notes, it is
the whole thing.

**The execution track — only where the material is runnable.** A workspace, Run
and Submit, a pinned toolchain container, graded practices. Gated on
`exercises` in the manifest.

**A corpus with no graders skipping the entire execution track is a pass, not a
shortfall — and it is the common case.** A tutorial with 168 test classes
paired one-to-one with its lessons is extraordinary. Most material is not like
that, and a framework that treated the extraordinary case as the standard would
report every ordinary corpus as unfinished forever.

**But a source with no graders no longer means a reader with nothing to
practise.** You can write exercises for any page and prove them before they
ship: code exercises where the subject is code, and quizzes where it is not. A
quiz needs no container and no network. See *Author, then prove*, below.

---

## An exercise is in one of three states

| State | What it is | Can complete a practice? |
|---|---|---|
| `none` | the unit teaches; it does not set work | — |
| `ungraded` | a prompt the reader works, or a file they run, with nothing to check it | **no** |
| `graded` | a workspace plus a grader | only on a passing grader run |

**`ungraded` is why three states and not two.** One surveyed tutorial ends all
19 of its lessons in an exercise and ships a test for none of them. Recording
those as *no exercise* would delete real teaching content from the reader's
material in order to satisfy a two-state model. They are presented as work,
marked clearly as unchecked, and they never complete anything.

---

## The three states fall out of the files — there is no flag to remember

| State | What you write |
|---|---|
| `none` | **no practice document at all** |
| `ungraded` | a `practice-M.json` with blocks and **no `exercise` key** — or an `exercise` that names **a file and no grader** |
| `graded` | a `practice-M.json` whose `exercise` names **a grader** |

**Graded is the grader's presence, not the key's.** An `exercise` may name the
reader's file and how it runs, and nothing that checks it: that record is
ungraded, the same as a practice with no key at all. The rule is §7's, in
[*A file with no test*](../specs/2026-09-08-studyforge-v1-design.md#a-file-with-no-test-w357),
and this page does not restate it.

**So the common case is a corpus that writes nothing.** A design in which every
corpus had to declare its emptiness would be a design fitted to the one
repository that is full.

---

## Where a practice may live

**A practice belongs in the unit whose material it practises.** It is a
`practice` document in that unit's directory, so it renders on that unit's
page, under the prose it is practising. **Not in a container of its own.** The
user's words, on the first corpus that tried it: *"the practices should be as
part of each topic page not a separate UI after the entire chapter"*
(2026-09-21). A reader who finishes a chapter and then navigates somewhere else
to practise has left the material behind.

**Its prose comes from one of exactly two files, and you choose by asking one
question: does the unit's own source file already carry the practice?**

| Your source | What the container map declares | What is compared against what |
|---|---|---|
| one file holds the lesson **and** the practice | `origin` only | that file's headings against **all** the unit's documents |
| the practice is new material you are adding | `origin` **and** `practice_origin` | `origin` against the `lesson` documents, `practice_origin` against the `practice` documents |

```json
{
  "n": 4,
  "title": "Message Type Indicators (MTIs)",
  "practices": 1,
  "origin": "src/4.md",
  "practice_origin": "src/p1.md"
}
```

**`practice_origin` needs `container_api: 3`.** It carries the same two shapes
`origin` does: a path, or `{"path": …, "section": …}` for a region.

### ⛔ You may not add the practice to the unit's existing source file

**Not by hand, and not through `permitted_edits`.** Generation is
non-destructive (R3), and the manifest's edit policy refuses an edit to any
file the corpus's own `content` rules classify as **included** — however that
edit is declared. Every prose unit's source file is included by definition,
because that is what makes it a unit. So the practice's material arrives as a
**new file beside the material**, and `practice_origin` names it.

**This is not a workaround; it is the point.** The new file is yours, nothing
you shipped before is touched, and the corpus stays regenerable from a clean
checkout.

### ⛔ And the completeness check is not relaxed to let this through

`studyforge validate` compares a heading count taken from your raw source
against the count the archive records — the one check that can catch material
silently dropped between the two. A unit with a `practice_origin` is compared
**twice**, once per file, and every heading on both sides is still accounted
for by exactly one of them.

**A `practice_origin` that no practice document reads is a short read**, not a
file that goes uncounted: the bucket is opened whether or not a document lands
in it, so its headings are compared against zero and `validate` says so.

### `practice_origin` places nothing

`origin` is what decides where a unit's page is written. `practice_origin` is
read by `validate` and by nothing else. A practice never moves the page it
joins.

---

## The `exercise` key

**It lives inside the practice document**, not in a file of its own and not in
anything a person types. It rides the version that document already has, and
the adapter writes it — because the adapter is the only thing that knows what
your build command is or where a grader came from.

**Every key the record defines is below, in the order it is written.** Most
records carry the first six and nothing else; the last five arrive with an
exercise somebody authored for this site.

**This fence is the key list and not a record to copy.** Two of the keys in it
are never written together with the rest: `"kind": "code"` is what a record
with no `kind` already means, so the build leaves it out again, and `questions`
belongs to a **quiz**, which carries none of the workspace keys above it and
is shown here empty only so the list is complete. A quiz is written whole
further down.

```json
{
  "exercise": {
    "main_path": "practice/basics-01/src/main/java/Greeter.java",
    "test_path": "practice/basics-01/src/test/java/GreeterTest.java",
    "run_command": ["mvn", "-q", "-pl", "practice/basics-01", "compile"],
    "test_command": ["mvn", "-q", "-pl", "practice/basics-01", "test"],
    "provenance": "bundled",
    "trust": "authoritative",
    "kind": "code",
    "cases": [
      {"id": "GreeterTest#greetsByName", "kind": "main", "says": "It greets by name."},
      {"id": "GreeterTest#refusesAnEmptyName", "kind": "edge",
       "says": "An empty name is refused."}
    ],
    "report": {"format": "junit", "path": "practice/basics-01/target/surefire-reports"},
    "origin": {"path": "docs/01-getting-started.md", "section": "Greeting a caller"},
    "questions": []
  }
}
```

**A complete practice document carrying that key is in this repository**, at
[`tests/fixtures/depth2/.../practice-1.json`](../../tests/fixtures/depth2/archive/basics/01-getting-started/raw/java/unit-01/practice-1.json)
— fifteen keys, then `starting_code`, then `exercise`. That one carries the
first six fields only, which is what a record written from material a source
already ships looks like.

**The first six, in two halves.** `main_path` and `test_path` are the workspace; `run_command`
and `test_command` are how it is exercised; `provenance` says where the grader
came from — `bundled`, `generated` or `user` — and `trust` is either
`authoritative` or `advisory`. **`main_path` and `run_command` are the file;
the other four are the grader**, and the grader is written whole or not at all
(`trust` alone may be left out, and is then defaulted from `provenance`).

### The last five: what an authored exercise says

**`kind` is `code` or `quiz`**, and `code` is what a record with no `kind`
means. **Write it only where it is not `code`**: every record ever written is a
code exercise, so the framework writes that token back only for a `quiz`, and a
`"kind": "code"` you write yourself is read, accepted, and then left out of what
the build writes. It is shown above because this fence lists every key.

**`cases` and `report` are one claim and go together**, and only beside a
grader. A case is three fields: `id`, exactly as the test report spells it; a
`kind` of `main` — the ask itself — or `edge`, one named edge of it; and `says`,
the one sentence the reader is shown when it fails. The `report` names the
format the grader writes (`junit`) and the path inside the workspace it lands
at. **At least one case is `main`, the ids are distinct, and every case is
backed by a test** — what the reader is shown is *main ask* plus *edge cases
n/m*, so a map that names no ask describes a run nothing reports.

**`origin` is the material the exercise was built from** — a path inside your
source, or a region of one written `{"path": …, "section": …}`, where `section`
is the exact text of a heading. **It is a fact about the material and not about
a grader**, so it is the one of these an *ungraded* record may carry.

**`questions` is a quiz's, and only a quiz's.** Writing it on any other record
is a refusal; see *A practice for material that is not code* below.

**The breakdown is a report, never a second definition of a pass.** A practice
completes when every case passes, exactly as before. The rules are §7's, in
[*Exercises authored for every corpus*](../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389),
and this page does not restate them.

### A practice for material that is not code

**When your material admits no coding task, write a quiz.** Most material does
not admit one — a history, a standard, a prose tutorial — and a quiz is how a
page checks its reader anyway. **It carries `questions` in place of a
workspace**, so it writes no `main_path`, no `run_command`, no `test_path` and
no `test_command`, and those keys are refused on it:

```json
{
  "exercise": {
    "provenance": "generated",
    "trust": "advisory",
    "kind": "quiz",
    "origin": "docs/01-getting-started.md",
    "questions": [
      {
        "id": "q-1",
        "stem": "What does a greeter return when it is given a name?",
        "options": [
          {"id": "a", "text": "A greeting addressed to that name", "correct": true,
           "says": "The page's first example returns exactly that."},
          {"id": "b", "text": "The name, unchanged", "correct": false,
           "says": "That is the input; the page's example wraps it in a greeting."}
        ],
        "origin": {"path": "docs/01-getting-started.md", "section": "Greeting a caller"}
      }
    ]
  }
}
```

**A question is four fields.** `id`, a plain token the reader's own state is
filed under; `stem`, what is asked; `options`, an ordered set of at least two;
and `origin`, the passage of the page the question was written from — required
here, unlike the record's own.

**An option is four fields**, and the shape of the whole thing is the honesty
rule: `id`, `text`, `correct`, and `says`, the one sentence the reader is shown
for choosing it. **Exactly one option is keyed `correct`** — none is refused and
two are refused — **the options are distinct once case and spacing are
normalised**, and **every option carries its sentence**, so the reader is told
why whichever way they went.

**The key is in the document, and the site does not pretend otherwise.** An
offline page cannot hide the answer it grades with, exactly as an offline
workspace cannot hide its test file. The page shows the reader the answer once
they have answered, and `correct` is written for every option, always.

**A quiz is graded by the framework with no compiler, no container, no network
and no model**, so the reading is the same over `file://` as it is from a
server. **It completes only when every question is answered correctly**, and it
produces no run: there is nothing to Run and nothing to Submit.

**A quiz is always `generated` and `advisory`, and both may be left out.** Its
honesty gates are judgements taken once when it was authored and cannot be
re-run by whoever holds the corpus, so no quiz may claim to be your material's
own grader — `bundled` and `authoritative` are refused on one.

### A file with no test

**When your material ships a file the reader runs but nothing that checks it**,
write the file half and stop:

```json
{
  "exercise": {
    "main_path": "practice/untested/hello.py",
    "run_command": ["python3", "practice/untested/hello.py"]
  }
}
```

**That record is ungraded.** The reader gets the file and Run; there is no
Submit, and it completes nothing. The framework refuses a record in between:
a grader written in part, and a `provenance` or `trust` beside no grader,
because both are facts about a grader and there is none. The shapes and their
refusals are §7's —
[*A file with no test*](../specs/2026-09-08-studyforge-v1-design.md#a-file-with-no-test-w357).

**If your prompts name no file at all, write no `exercise` key.** The record is
for a file that exists; a practice that is only a prompt is still ungraded with
nothing written.

**`trust` is declared but never believed.** Your adapter writes what it claims,
and the framework checks that claim against `provenance`. **A `generated`
grader may never be `authoritative`**, and declaring it so is a refusal, not a
warning. A grader written by a machine has not been reviewed by anybody, and a
site that told the reader they had passed on the strength of one would be
manufacturing a result.

---

## Run and Submit are different acts

**Run executes the reader's program so they can see what it printed.**

**Only a test run can complete a practice.** A program that prints successfully
has demonstrated nothing whatsoever about its tests, and treating the two alike
would let a reader finish a course by writing `println`.

---

## So: should your corpus have exercises?

**First, describe what your source ships. Ask one question: does your material
ship something that can check an answer?**

- **It ships tests, or a runner, or an expected output you can diff.**
  `"exercises": true`, and write `exercise` keys where the graders exist.
- **It sets work but checks nothing.** `"exercises": true`, practice documents
  with prompts, **no `exercise` key**. Or, where the work is a file the reader
  runs, an `exercise` naming that file and no grader. The reader gets the work,
  marked as unchecked.
- **It teaches and sets no work.** `"exercises": false`, no practice documents,
  and you are finished at the reading floor.

**The answer describes your source. It no longer decides whether your reader
gets to practise.** A page with no grader can still get exercises: you write
them for it, and they ship only after they pass the gates. That is the rest of
this page. **Stopping at the reading floor is still a pass.** What you give up
by stopping is a reader who can practise.

**Every practice needs `"exercises": true`, authored ones and quizzes
included.** The build declares zero practices for every unit of a corpus whose
manifest says `false`, whatever the corpus holds.

---

## Author, then prove

**Do not leave a page without practice just because its source ships no
grader.** Write the exercise. Then prove it: before it ships, it must pass
every gate for its kind, and a record of that proof ships beside it.

- **A code exercise passes five gates:** `G1` (the reference solution passes,
  twice, the same way), `G2` (every test fails on the starter), `G3` (each edge
  case's test catches the one mistake it names), `G4` (every test maps to one
  case) and `G5` (the material it cites is still what the source says).
- **A quiz passes five different gates:** `Q1` (the page contains the answer),
  `Q2` (you cannot guess the answer without the page), `Q3` (the page rules out
  every wrong option), `Q4` (exactly one option is keyed, and every option says
  why) and `Q5` (every question cites a passage the source still has).

**An exercise that fails a gate does not ship.** You get a fixed number of
attempts to fix it. If it still fails, the coverage report names the gate that
stopped it. **No gate can be turned off, and a shortfall is reported, never
worked around.** A test nobody proved is still not a check.

**Every exercise you write is labelled `generated` and `advisory`.** The label
is filled in for you, and a draft has no field for either word. The reader is
shown a sentence saying it was written for the site and proven against a
worked solution.

**The route, in order:**

1. Get the corpus ready: see *Before you author*.
2. Describe each page: its words, its skills and its tier. That sets its
   *plan*.
3. Write an author, a judge and a runner: see *Running the pass*.
4. Run the pass once. It takes the *ledger*, plans every page, drafts,
   gates, retries, and commits what passed into your corpus.
5. Read the coverage reports, then have your adapter emit the practice
   documents and run `studyforge validate`.

**The worked example is a real corpus in this repository.**
`tests/studyforge/skills/exercises/authoring.py` holds five small pages. Four
of them are authored for: one for each source case, plus a quiz on a prose
page.
It includes a draft for each and a planted defect for `G2`, `G3` and `Q4`.
`tests/studyforge/skills/exercises/test_corpus.py` runs the whole pass over it,
with every gate run as a real `pytest` process. Everything this page says about
the worked corpus is re-computed from it by the test suite.

---

## Before you author

1. **Your corpus is onboarded.** `corpus.json` exists, and
   `studyforge validate` is clean.
2. **Your manifest says `"exercises": true`.**
3. **Your manifest marks the two trees the pass writes as `not_material`.** The
   pass writes into `exercises/` and `practice/`. Without these two entries,
   `studyforge validate` refuses every file in both trees before any exercise
   check runs. `not_material` needs `corpus_api` 2 or later, and the
   onboarding skill raises it for you.

**Do not edit `corpus.json` by hand, for either step.** Onboarding generated
it, and `.studyforge/installed.json` records its digest. A hand-typed entry is
named by `hand_edited`, as a generated file somebody edited (R19). Give both
changes to the onboarding skill as data, and regenerate:

```python
from studyforge.skills.onboarding import hand_edited, reonboard

corpus = "path/to/your-corpus"
made = reonboard(
    corpus,
    not_material=[
        {"glob": "exercises/**", "why": "authored exercise bundles and their gate records"},
        {"glob": "practice/**", "why": "the reader's workspace, from each bundle's starter"},
    ],
    settle={"exercises": True},
)
made.write(corpus, regenerate=True)
print(hand_edited(corpus))  # [] -- nothing generated was edited by hand
```

`reonboard` reads your corpus's recorded manifest and pin, and uses them as
the draft. Every answer you already gave is kept. Each `not_material` entry
your manifest already declares is kept byte for byte, and each glob the skill
generates is derived again, so you type only the new ones.
`settle` names a recorded answer you mean to change. Any other answer that
would change is refused by name, and nothing is written. If your manifest
already declares one of the two globs with the same reason, it is kept once.
A different reason is refused by name.

4. **Your corpus ignores a run's report.** A test run writes its report into
   the reader's workspace, under `practice/`, and a JUnit report records the
   machine's hostname. Add an ignore rule for it to your corpus (in the worked
   corpus the report is `report.xml` in each workspace), so it never gets
   committed. A report inside a bundle is refused by `studyforge validate`.
5. **You have the pinned runner image.** Gate runs must happen in the same
   pinned toolchain the reader's runs use, or the proof applies to a different
   machine. Take the runs with the network off. An exercise whose tests need a
   library must then find that library offline, or `G1` fails it for a reason
   that has nothing to do with the exercise.

---

## The three source cases

**You do not choose the case. It is read from the ledger, page by page**, from
what the page carries and which test files it declares. Each case decides what
you start from:

| case | the page carries | what you write |
|---|---|---|
| `code-and-tests` | a test file your corpus declares for it | the ask and its edge cases, with the source's own tests as the basis |
| `code-no-tests` | a fenced code example, and no test file | the ask, the starter and the tests. The page's example is the reference solution |
| `neither` | neither of those | all of it (the ask, a reference solution, the starter and the tests) from the page's prose |

**All three produce the same thing:** a code exercise with a main ask and at
least one edge case, proven by `G1`–`G5`. The difference is only how much of it
already existed.

⚠️ **A page with tests gets `generated` exercises from this pass too.** Blanking
a source's own solution into an `authoritative` exercise is a different step,
and this pass does not do it.

### The worked corpus

| page | kind | case | band | plan |
|---|---|---|---|---|
| `lessons/greeting.md` | `code` | `code-and-tests` | `short` | 1 |
| `lessons/shout.md` | `code` | `code-no-tests` | `short` | 1 |
| `lessons/basket.md` | `code` | `neither` | `short` | 1 |
| `notes/gauge.md` | `quiz` | `neither` | `short` | 1 |

- **`code-and-tests`: *Greet somebody by name*.** The page ships `greet(who)`
  and declares `checks/test_greeting.py`. The exercise uses the source's test
  as its main ask and adds one edge case on top, *a blank name is refused*,
  because `G3` needs at least one edge case and the source's test has none.
  The plant for that edge case is the page's own function, which greets and
  never refuses.
- **`code-no-tests`: *Shout a word*.** The page's example, `shout(text)`, is
  the reference solution, unchanged. The ask and the tests are written from
  it. The edge case is *an empty text is only the mark*, and its plant returns
  an empty string for empty text, with no mark.
- **`neither`: *Total a basket*.** The page is only prose: a basket's total is
  the sum of its prices, and a negative price is refused. Everything is written
  from that prose. The draft is below.

### What a code draft carries

| field | what you write |
|---|---|
| `title` | the exercise's name, as the reader sees it |
| `lang` | the language of its files |
| `main_file` | the reader's file, relative to the workspace |
| `test_file` | the tests' file, relative to the workspace |
| `run_command` | how Run executes it, spelled from the corpus root |
| `test_command` | how the tests run, spelled from the corpus root, writing a JUnit report |
| `cases` | the main ask and each edge case: an id as the report spells it, a kind, and the sentence the reader sees |
| `report` | where the report lands, relative to the workspace |
| `origin` | the material it was built from: a path, or a path and a section |
| `statement` | the ask, in Markdown |
| `starter` | what the reader starts from. Every test must fail on it |
| `reference` | the worked solution. Every test must pass on it, and the reader can open it |
| `tests` | the tests, one or more per case |
| `plants` | for each edge case's id, a solution that solves the main ask and ignores exactly that edge |
| `build` | only when the tests import a library: each build file's path, relative to the workspace, mapped to its text, such as a `pom.xml` naming the library. Leave it out otherwise |

⛔ **Every path in a command is inside the exercise's own workspace.** The
brief gives you that directory as `brief.places.workspace`. An argument
containing `/` that points outside it is refused. Arguments with no `/`, such
as `pytest` or `-q`, are left alone. This is the first rule a new author
breaks.

The basket draft from the worked corpus. `author.draft(brief)` returns it:

```python
from studyforge.exercise import EDGE, MAIN, Case, Origin
from studyforge.skills.exercises import CodeDraft

NEGATIVE = Case("test_a_negative_price_is_refused", EDGE, "a negative price is refused")


def basket(brief):
    ws = brief.places.workspace
    return CodeDraft(
        title="Total a basket",
        lang="python",
        main_file="total.py",
        test_file="test_total.py",
        run_command=("python3", f"{ws}/total.py"),
        test_command=(
            "python3",
            "-m",
            "pytest",
            "-q",
            "-p",
            "no:cacheprovider",
            "--junit-xml",
            f"{ws}/report.xml",
            f"{ws}/test_total.py",
        ),
        cases=(Case("test_totals_a_basket", MAIN, "a basket adds up"), NEGATIVE),
        report="report.xml",
        origin=Origin("lessons/basket.md", None),
        statement="Write `total(prices)`: the sum of a basket, refusing a negative price.\n",
        starter="def total(*args):\n    raise NotImplementedError('write me')\n",
        reference=(
            "def total(prices):\n    if any(price < 0 for price in prices):\n"
            '        raise ValueError("a price is never negative")\n    return sum(prices)\n'
        ),
        tests=(
            "from total import total\n\n\ndef test_totals_a_basket():\n"
            "    assert total([2, 3, 5]) == 10\n\n\n"
            "def test_a_negative_price_is_refused():\n    try:\n        total([2, -1])\n"
            "    except ValueError:\n        return\n"
            '    raise AssertionError("a negative price should have been refused")\n'
        ),
        plants={NEGATIVE.id: "def total(prices):\n    return sum(prices)\n"},
    )
```

---

## A quiz, authored

**When a page's subject is not code, declare its kind as `quiz`** and write
questions from its passages. The record a quiz becomes is described above,
under *A practice for material that is not code*. This section covers writing
one. Each question comes from one passage and names it in its `origin`, as a
path and the exact text of a heading:

```python
from studyforge.exercise import Origin
from studyforge.exercise.quiz import Option, Question
from studyforge.skills.exercises import QuizDraft

hour = Question(
    id="q-hour",
    stem="When is the gauge read?",
    options=(
        Option(id="a", text="At the same hour every day", correct=True, says="The page says so."),
        Option(
            id="b",
            text="Whenever it rains",
            correct=False,
            says="The page names an hour, not weather.",
        ),
    ),
    origin=Origin("notes/gauge.md", "Taking a reading"),
)
draft = QuizDraft(title="Field notes", questions=(hour,))
```

**`Q1`–`Q3` are judgements, and a separate judge takes them, never the
author.** A model cannot grade its own questions, so the pass takes a `judge`
as its own argument. The judge returns one `Q1` and one `Q2` judgement per
question, and one `Q3` per wrong option. Each is taken over
`question_digest(question)`, so a question edited afterwards cannot keep a
judgement taken over its old wording:

```python
from studyforge.exercise.gates.quiz import Q1, Q2, Q3, WHOLE_QUESTION, Judgement, question_digest


def judge(brief, questions):
    taken = []
    for question in questions:
        over = question_digest(question)
        asked = [(Q1, WHOLE_QUESTION), (Q2, WHOLE_QUESTION)]
        asked += [(Q3, option.id) for option in question.options if not option.correct]
        for gate, option in asked:
            reading = ask_an_independent_pass(gate, brief.page, question, option)
            taken.append(
                Judgement(
                    gate=gate,
                    question=question.id,
                    option=option,
                    prompt=reading.prompt,
                    taken_by=reading.taken_by,
                    outcome=reading.outcome,
                    held=reading.held,
                    over=over,
                )
            )
    return tuple(taken)
```

`ask_an_independent_pass` is yours to write. **`held` is the verdict.** A pass
that answered badly is recorded with `held=False`, and no sentence in `outcome`
can change that. The worked corpus's `Judging` class holds every judgement, so
its tests exercise the pass rather than a model.

---

## The plan

**Each page gets a plan before anything is written: a ceiling on how many
exercises it may have.** It comes from three readings you give on the `Page`:
`words` (count them with `words_of`, which counts the prose and skips fenced
code), `skills` (how many distinct checkable skills the page teaches) and
`tier`.

**The page's length picks a band.** The count starts at the band's floor, goes
up one for each distinct skill after the first, and moves by the tier. The
band then clamps it. The tables below give the amounts. **A page that teaches
no checkable skill plans zero.**

| band | opens at (words) | floor | ceiling |
|---|---|---|---|
| `stub` | 0 | 0 | 0 |
| `short` | 250 | 1 | 2 |
| `standard` | 700 | 1 | 4 |
| `long` | 1800 | 2 | 6 |

| tier | moves the count |
|---|---|
| `introductory` | -1 |
| `core` | 0 |
| `advanced` | +1 |

⚠️ **These numbers are a convention, and they may change.** Two properties do
not change: the count never leaves its band, and every move is written down as
a reason in the plan. **So a page under the `short` band's opening count plans
zero, and nothing is authored for it.** When a page gets nothing, check its
words first.

⛔ **The plan is a ceiling, never a quota.** Only exercises that pass the gates
ship. A page that ships fewer than its plan names the gate that stopped each
missing one. Never lower a bar to reach a count.

---

## The ledger

**The ledger is the proof that nothing your source already has is lost.** The
pass reads every file you list as material and every test file you declare,
once, before gating anything. Each fenced example and each test file becomes an
entry. **Each entry either is the basis of an exercise, named by that
exercise's `origin`, or carries a written reason why not.** An entry with
neither is refused.

- An example's key is `example:<path>:<n>`, where `<n>` counts the file's
  fenced blocks from 1.
- A test file's key is `tests:<path>`.
- **An `origin` naming a whole file accounts for every example in it. One
  naming a section accounts for every example under that heading.**
- **The author's `excuse(entry)` writes the reason.** It is called only for
  entries that nothing shipped accounts for.

⚠️ **The two lists are yours.** The framework never guesses what a test file
looks like. You tell the pass which files are material and which are graders,
and each `Page` names its own graders.

### The worked corpus's ledger

| entry | how it ends |
|---|---|
| `example:lessons/greeting.md:1` | built on, by the exercise whose origin is `lessons/greeting.md` |
| `example:lessons/shout.md:1` | built on, by the exercise whose origin is `lessons/shout.md`, section `How to shout` |
| `example:lessons/extra.md:1` | a written reason: that page is material, and no exercise is planned for it |
| `tests:checks/test_greeting.py` | a written reason |

⚠️ **An exercise has one `origin`, and it accounts only for entries in that
file.** The greeting exercise's main ask is `checks/test_greeting.py`, but its
origin is the page. So the test file's entry gets a written reason like any
other entry nothing names.

---

## The gates

### The code gates

| gate | what must hold | what it proves |
|---|---|---|
| `G1` | every test passes on the reference solution, on two runs, the same way both times | it can be solved, and its tests are not flaky |
| `G2` | **every** test fails on the starter | no test is vacuous |
| `G3` | for each edge case, its plant passes the main ask and fails that edge | each edge test catches the one mistake it names |
| `G4` | every test the report names maps to one case, and every case is reported | the reader's breakdown is complete |
| `G5` | the passage the exercise cites still has the digest the ledger read | it is built from what the source has |

### The quiz gates

| gate | what must hold | what it proves |
|---|---|---|
| `Q1` | an independent pass given the page and the question picks the key | the page contains the answer |
| `Q2` | the same pass, given the question but not the page, does not | the question tests this page, not general knowledge |
| `Q3` | a passage of the page rules out every wrong option | no distractor is a trick |
| `Q4` | exactly one option is keyed, the options are distinct, and every option has its sentence | the reader is told why, whatever they chose |
| `Q5` | every question's passage still has the digest the ledger read | the question is built from the page |

**The gate record ships beside the exercise, as `gates.json`.** It holds the
digest of every file the gates read and each gate's verdict.
`studyforge validate` refuses a `generated` exercise with no record, a record
in which any gate failed, and a bundle whose files no longer match their
recorded digests.

⚠️ **What `validate` does not do is re-run the gates.** It re-reads the record
and re-digests the bundle's files. A quiz record whose key breaks `Q4`'s rules
is refused wherever it is read, because the quiz record itself refuses that.
But `validate` does not re-run the tests, and it does not check `G5` or `Q5`
against your source again. `Q1`–`Q3` can never be re-taken, which is why a
quiz is always `generated` and `advisory`.

---

## Running the pass

**There is no command for this.** The pass is a Python function,
`author_corpus`, and your agent calls it from a short script it writes, like
the one below. `tests/studyforge/skills/exercises/test_corpus.py` calls it the
same way over the worked corpus.

```python
from pathlib import Path

from studyforge.address import Address
from studyforge.skills.exercises import CORE, Page, author_corpus, words_of

root = Path("path/to/your-corpus")


def page(path, unit, graders=()):
    text = (root / path).read_text(encoding="utf-8")
    return Page(
        path=path,
        address=Address(["kata"]),
        variant="python",
        unit=unit,
        kind="code",
        words=words_of(text),
        skills=1,
        tier=CORE,
        graders=graders,
    )


authored = author_corpus(
    root,
    source="demo",
    material=["lessons/greeting.md", "lessons/basket.md"],
    graders=["checks/test_greeting.py"],
    pages=[
        page("lessons/greeting.md", 1, ("checks/test_greeting.py",)),
        page("lessons/basket.md", 3),
    ],
    author=author,
    judge=judge,
    runner=runner,
)
for where, missed in authored.shortfalls:
    print(where, missed.slot, missed.gate, missed.says)
print("pages with nothing shipped:", authored.bare)
```

**You supply three things:**

- **`author`**: an object with two methods. `draft(brief)` returns a
  `CodeDraft` for a `code` page or a `QuizDraft` for a `quiz` page.
  `excuse(entry)` returns the one sentence saying why no exercise was built
  from a ledger entry. In real use a model writes the drafts. The worked
  corpus's `Scripted` returns drafts it was given ahead of time.
- **`judge`**: the independent pass for `Q1`–`Q3`, shown above. Only a corpus
  with a quiz page needs one.
- **`runner`**: a callable `runner(root, command)` that runs one test command
  from `root` and returns a `Ran`: its exit code and its output. **It runs in
  the pinned runner image.** Each run happens in a fresh directory, so nothing
  one run leaves behind reaches the next. The worked corpus's `Running` runs
  on the host, which is enough for a test and not enough for a real corpus.
  Only a corpus with a code page needs one.

### What a brief carries

**Each call to `draft` gets one brief, for one attempt at one planned
exercise:**

| field | what it is |
|---|---|
| `page` | the `Page` you described |
| `case` | the page's source case, read from the ledger |
| `slot` | which of the plan's exercises this is |
| `places` | where the exercise will sit if it ships. Its commands go under `places.workspace` |
| `attempt` | which attempt this is, counted from 1 |
| `entries` | the page's ledger entries: its fenced examples and its declared test files |
| `previous` | on a retry, the draft that failed |
| `refused` | on a retry, every gate that did not hold, each with its own sentence |
| `output` | on a retry, the last run's output |

---

## When a gate refuses

**The exercise is drafted again, up to `ATTEMPTS` times.** That number is
fixed by the framework, and no corpus or caller can raise it. Each retry's
brief carries the failed draft, every refusing gate's sentence and the last
run's output, so the author fixes the finding rather than starting over.

⛔ **A retry must never ask less.** A retry that drops a case id or a question
id the previous draft had is refused, and the whole pass stops. Swapping a hard
edge case for an easier one drops an id too. Fix the test or the plant instead.

**When the attempts run out, the exercise does not ship.** Its unit's
`coverage.json` records the shortfall under `slot`, `gate`, `says` and
`output`: which planned exercise it was, the gate, the gate's sentence (which
names each failing case by the sentence the reader would see), and the last
run's output, made relative and scrubbed of personal data.
`authored.shortfalls` lists every one, and `authored.bare` names every page
left with nothing shipped.

---

## What the pass writes

| path | what it holds |
|---|---|
| `exercises/<address>/<variant>/unit-NN/practice-M/` | one code exercise's bundle: `bundle.json`, the statement, the starter, the reference, the tests and the plants |
| `exercises/<address>/<variant>/unit-NN/practice-M/gates.json` | its gate record |
| `exercises/<address>/<variant>/unit-NN/practice-M/tests/quiz.json` | a quiz's own document, with its record under `exercise` |
| `practice/<address>/<variant>/unit-NN/practice-M/` | the reader's workspace: the starter and the tests |
| `exercises/<address>/<variant>/unit-NN/coverage.json` | the unit's plan, what shipped, and every shortfall |
| `exercises/ledger.json` | the ledger, with every entry accounted for |

**Exercises on a page are numbered `1..n` in the order they ship.** An exercise
that failed leaves its number for the next one, so a page never has a gap.

⛔ **The pass only writes inside your corpus, and only adds files.** Every file
is checked before any is written. A file already there with the same bytes is
left alone. One with different bytes stops the whole pass, names the first such
file, and nothing is written.

**Running it again with nothing changed writes nothing.** A unit whose
`coverage.json` still matches its page and its plan is not authored again, so
the author, the judge and the runner are not called for it.

⚠️ **A page whose source changed is refused, and the refusal names its unit.**
Its exercises were proven against material that has since moved. To author it
again, delete that unit's directory under `exercises/` and
`exercises/ledger.json`, then run the pass again. **Delete the unit's
directory under `practice/` as well.** The refusal does not mention it, but a
new draft whose starter or tests differ would otherwise land on the old
workspace files, and the pass refuses any file that exists with different
bytes.

### Then the adapter, then `validate`

**The pass writes no practice document. Your adapter does**, from each
bundle:

```python
import json
from pathlib import Path

from studyforge.exercise.bundle import bundle_of, emit

root = Path("path/to/your-corpus")
where = "exercises/kata/python/unit-03/practice-1"
bundle = bundle_of(json.loads((root / where / "bundle.json").read_text(encoding="utf-8")), where)
emission = emit(root, bundle, source="demo", ingested="2026-01-05")
emission.document  # write this as the unit's practice-1.json
```

⚠️ **The pass has already created the workspace files**, so your adapter uses
`emission.document` only. The package's `write` would refuse those files
because they already exist.

⚠️ **The framework has no `emit` for a quiz yet.** Your adapter builds a quiz's
practice document itself, from the `exercise` record in its `tests/quiz.json`.

Then run the checker, and fix what it names:

```
python3 -m studyforge.validate <your-repository>
```

---

## Next

- [What an adapter must produce](archive.md) — where the practice document
  goes.
- [Worked examples](examples.md) — one corpus with `exercises: true` and one
  with `false`.
