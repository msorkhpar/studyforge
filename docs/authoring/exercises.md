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
shortfall — and it is the common case.** A tutorial that ships a test for
every lesson is extraordinary. Most material is not like that, and a framework
that treated the extraordinary case as the standard would report every ordinary
corpus as unfinished forever.

**But a source with no graders does not mean a reader with nothing to
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

**`ungraded` is why three states and not two.** Many tutorials end each lesson
in an exercise and ship a test for none of them. Recording those as *no
exercise* would delete real teaching content from the reader's material in
order to satisfy a two-state model. They are presented as work, marked
clearly as unchecked, and they never complete anything.

---

## The three states fall out of the files — there is no flag to remember

| State | What you write |
|---|---|
| `none` | **no practice document at all** |
| `ungraded` | a `practice-M.json` with blocks and **no `exercise` key** — or an `exercise` that names **a file and no grader** |
| `graded` | a `practice-M.json` whose `exercise` names **a grader** |

**Graded is the grader's presence, not the key's.** An `exercise` may name the
reader's file and how it runs, and nothing that checks it: that record is
ungraded, the same as a practice with no key at all. The record is shown in
full under *A file with no test*, below.

**So the common case is a corpus that writes nothing.** A design in which every
corpus had to declare its emptiness would be a design fitted to the one
repository that is full.

---

## Where a practice may live

**A practice belongs in the unit whose material it practises.** It is a
`practice` document in that unit's directory, so it renders on that unit's
page, under the prose it is practising. **Not in a container of its own.** A
reader who finishes a chapter and then navigates somewhere else to practise has
left the material behind.

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
non-destructive, and the manifest's edit policy refuses an edit to any
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
records carry the first six and nothing else; the last seven arrive with an
exercise somebody authored for this site.

**This fence is the key list and not a record to copy.** Two of the keys in it
are never written together with the rest: `"kind": "code"` is what a record
with no `kind` already means, so the build leaves it out again, and `questions`
and `mock` belong to a **quiz**, which carries none of the workspace keys above
it and is shown here empty only so the list is complete. A quiz is written whole
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
    "questions": [],
    "mock": {"pass_mark": 70, "domains": [{"id": "d-1", "title": "Greeting a caller"}]},
    "concepts": ["A greeting is built from the name it is given."],
    "files": [],
    "review": null,
    "cards": []
  }
}
```

**A complete practice document carrying that key** writes the fifteen keys
every unit document writes, listed under
[the unit document](archive.md#the-unit-document), then `starting_code`, then
`exercise`. A record written from material a source already ships carries the
first six fields only.

**The first six, in two halves.** `main_path` and `test_path` are the workspace; `run_command`
and `test_command` are how it is exercised; `provenance` says where the grader
came from — `bundled`, `generated` or `user` — and `trust` is either
`authoritative` or `advisory`. **`main_path` and `run_command` are the file;
the other four are the grader**, and the grader is written whole or not at all
(`trust` alone may be left out, and is then defaulted from `provenance`).

A Gradle practice sets `testLogging { exceptionFormat = TestExceptionFormat.FULL }` in its `tasks.test`, so a failed test shows its assertion message and the run filter keeps it.

A lesson's example offers Run for the test its page links, in any language the corpus declares: `python3 -m pytest` for a `.py` test, `node --test` for a `.ts`, `.js`, `.mjs` or `.cjs` test, and for a Java or Kotlin test the command of the build file its module holds: Maven's (a `pom.xml`, unchanged) or Gradle's, `gradle --offline -q -p <build> cleanTest test --tests <package.Class>` (a subproject is addressed as `:<dir>:cleanTest :<dir>:test`). Run is quiet, which hides Gradle's lifecycle log, so a failed Gradle example shows its assertion message only when its `tasks.test` sets `testLogging { quiet { events("failed"); exceptionFormat = TestExceptionFormat.FULL } }`; a passing run prints only the exit line.

**A Python practice** is graded by pytest through the same JUnit report. Its `test_command` is an argv list, for example `["python3", "-m", "pytest", "-q", "-p", "no:cacheprovider", "--junitxml=<workspace>/target/report.xml", "<workspace>/test_x.py"]`, and its `report` is `{"format": "junit", "path": "target/report.xml"}`. An option may carry a path (`--junitxml=<path>`); the path must be inside the exercise's workspace like any other. A case id is the test's name as pytest reports it: a bare function name, a parametrised test with the id pytest spells (`test_collapses[inner spaces]`, at most one space in a row), or the node id `tests/test_x.py::test_name`, which is read from the report's dotted class name. The starter returns a wrong value so that every test fails on an assertion; a starter that raises `NotImplementedError` fails on an error, which says nothing about the task. A code draft that sets `assertions_only` has `G2` and `G3` refuse a starter or a plant whose tests failed with anything but an assertion. The run page drops pytest's own banner, progress and rootdir lines for a run whose command is `pytest` or `python -m pytest` when the corpus declares `python` beside another tool with rules, and keeps every failure line, frame and the tally.

**A TypeScript practice** is graded by `node --test` through the same JUnit report, on Node's built-in type stripping alone: no compiler and no install. Its files are `.ts`, its `test_command` is an argv list, and its case ids are the test names exactly as the `junit` reporter spells them (`test("blank text is refused", ...)` is `blank text is refused`). The solution is the main file and the tests import it as `./name.ts`, with the extension. ⛔ Type stripping erases types and nothing else: an `enum`, a parameter property (`constructor(private x: number)`), a `namespace` with code and a decorator are refused by Node with `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`, and `import type` is needed for a type-only import. Such a file fails with Node's own message, which the run page keeps; a draft that sets `assertions_only` has `G2` and `G3` refuse a starter or a plant that fails to load, and `G1` and `G4` refuse a reference that does. A failure counts as an assertion when the report's `cause` is an `AssertionError` (`assert.equal`, `assert.throws`, `assert.rejects`); a `TypeError`, an `Error` thrown by an unimplemented starter and a skipped test do not.

⚠️ **Node opens the report's destination before anything runs and does not create its directory**, and a reporter named without a leading `./` is read as a package name. A practice therefore ships one build file, for example `junit-file.mjs`, that writes the built-in reporter's XML next to itself:

```js
import { mkdirSync, writeFileSync } from "node:fs";
import { junit } from "node:test/reporters";

export default async function* (source) {
  let xml = "";
  for await (const chunk of junit(source)) xml += chunk;
  mkdirSync(new URL("./target/", import.meta.url), { recursive: true });
  writeFileSync(new URL("./target/report.xml", import.meta.url), xml);
}
```

and a `test_command` of `["node", "--test", "--test-reporter=spec", "--test-reporter-destination=stdout", "--test-reporter=./<workspace>/junit-file.mjs", "--test-reporter-destination=stdout", "<workspace>/name.test.ts"]`, with `report` `{"format": "junit", "path": "target/report.xml"}`. The `spec` reporter prints a failing run's `AssertionError` for the reader. An option's path may begin with one `./`; it is checked as any other path and must be inside the workspace. A command that sends the built-in `junit` reporter straight to `<workspace>/target/report.xml` leaves no report when the directory is absent, and `G1` and `G4` say so naming the path. The run page drops Node's `suites`, `cancelled`, `skipped`, `todo` and duration tally lines for a run whose command is `node --test` when the corpus declares `node` beside another tool with rules, and keeps every other line, frame and the pass and fail tally.

**An optional type check.** A code draft may set `typecheck_command`, an argv such as `["tsc", "--noEmit", "--strict", "--erasableSyntaxOnly", "<workspace>/name.ts"]`, run in each staged solution's workspace before its tests. A non-zero exit is a failure of its own and not a test case: `G1` names it for the reference, `G2` for the starter and `G3` for a plant, and exit code 127 says the checker is not on the image (only an image that carries `typescript` has `tsc`). `--erasableSyntaxOnly` makes `tsc` refuse the constructs Node refuses, at type-check time. A draft without the field runs no check, so a reference that does not type-check passes as it always did. The check is read at authoring time; a reader's Submit runs the tests only.

### The last seven: what an authored exercise says

**`kind` is `code` or `quiz`**, and `code` is what a record with no `kind`
means. **Write it only where it is not `code`**: the framework writes that
token back only for a `quiz`, and a `"kind": "code"` you write yourself is
read, accepted, and then left out of what the build writes. It is shown above
because this fence lists every key.

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

**`layout` is a plain quiz's: `page` opts it out of one question at a time** (see *A plain quiz is
drawn one question at a time*).

**`mock` is a quiz's too, and says the quiz is a mock exam**: a page of many
questions covering a level, scored per domain. Writing it on any other record
is a refusal; see *A mock exam* below.

**`concepts` is what the exercise practises**: a list of sentences, one per
idea, shown on the exercise's card in the page's *Practice (n)* list before a
reader opens it. It may appear on a code record or a quiz, and is left out
where there is nothing to say. **You do not write it by hand**: a scaffolded
adapter writes it from the unit's `coverage.json`, one sentence for each
aspect the plan gave that exercise to check. An empty list, or anything but
sentences, is refused.

**The breakdown is a report, never a second definition of a pass.** A practice
completes when every case passes.

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

**The key is in the document you write, and the build copies it into that
quiz's own page and nowhere else.** Write `correct` for every option, always.
The built page shows each question and its options, and carries the key and
every sentence in one data block local to the page; when the reader checks
their answers, the page itself answers each question right or wrong with the
sentence of the option the reader chose. The page puts its own *Right.* or *Not this one.*
in front of that sentence, so do not open a sentence with a verdict of your
own: say why, and leave the verdict to the page.

**A quiz is graded by the framework with no compiler, no container, no network
and no model** — a fixed comparison made in the page itself, the same opened as
a file or served, and answering makes no request. **It
completes only when every question is answered correctly**, and it produces no
run: there is nothing to Run and nothing to Submit.

**A quiz is always `generated` and `advisory`, and both may be left out.** Its
honesty gates are judgements taken once when it was authored and cannot be
re-run by whoever holds the corpus, so no quiz may claim to be your material's
own grader — `bundled` and `authoritative` are refused on one.

### A mock exam

**A mock exam is a quiz that covers a whole level and is scored per domain.** It is
the same record with `kind` `quiz`, so every rule above holds for it: one keyed
option per question, a sentence per option, a passage per question, `generated` and
`advisory`, and grading in the page with no network, no container and no model. A
quiz with no `mock` key is a quiz as it always was. Two things are added:

```json
{
  "kind": "quiz",
  "mock": {
    "pass_mark": 70,
    "domains": [
      {"id": "AS1", "title": "Prompting and task execution"},
      {"id": "AS2", "title": "Output evaluation and validation"}
    ]
  },
  "questions": [
    {"id": "x1", "domain": "AS1", "stem": "…", "options": ["…"], "origin": "…"}
  ]
}
```

**`mock`** is a `pass_mark`, a whole percent from 1 to 100 of the questions, and the
`domains` the exam reports a score under, each an `id` token and a `title`. **A
question's `domain`** is one of those ids. A `domain` on a quiz with no `mock` is
refused.

**The page** shows how many questions are answered and keeps the answers in the
reader's own browser, so a reader who closes the tab resumes where they were. A
submit with a question open names each one by its number and grades nothing. When
every question is answered, the page grades it, shows each question's verdict and
the sentence of the option the reader chose, a score per domain, and the whole exam's
score against the pass mark, rounded down so that two of three is 66 and never a 67.
The answers lock until the reader starts again. The page works at phone width.

**The gates.** `Q1` to `Q5` run over every question unchanged: `Q4` and `Q5` are
mechanical and name the question that fails, and `Q1` to `Q3` are judgements taken
for each question and recorded for each. One gate is added for what a mock needs:
`P1` holds when every question names a domain, every domain a question names is
declared, and every declared domain has a question. A gate record for a mock exam
names the `mock` family beside `quiz` and is complete only with `P1`. Draft one with
`QuizDraft(title=…, questions=…, mock=Mock(…))`.

#### The exam form

**A mock exam may sit like a real certification sitting.** Everything below is opt-in on the
`mock` record and on its questions: a mock that uses none of it is the page described above, in
bytes. Any one key switches that mock to the exam form, and a question with `select` does too.

```json
{
  "mock": {
    "pass_mark": 70,
    "domains": [
      {"id": "AS1", "title": "Prompting and task execution", "weight": 60},
      {"id": "AS2", "title": "Output evaluation and validation", "weight": 40}
    ],
    "minutes": 90,
    "layout": "exam",
    "scenarios": [
      {"id": "support-bot", "title": "A support bot that forgets",
       "context": "Two to four sentences that set the situation. A second sentence."}
    ],
    "difficulties": [
      {"id": "foundational", "title": "Foundational"},
      {"id": "scenario-hard", "title": "Scenario, hard"}
    ],
    "sittings": [
      {"id": "full", "title": "Full sitting", "questions": 60, "minutes": 90},
      {"id": "short", "title": "Short sitting", "questions": 20},
      {"id": "scenarios", "title": "Scenario sitting", "scenarios": 3}
    ],
    "scale": {"min": 100, "max": 1000, "pass": 720}
  },
  "questions": [
    {"id": "p1", "domain": "AS1", "scenario": "support-bot", "difficulty": "scenario-hard",
     "stem": "…", "options": ["…"], "origin": "…"},
    {"id": "p2", "domain": "AS2", "select": 2, "shuffle": false,
     "stem": "Which two …", "options": ["…"], "origin": "…"}
  ]
}
```

**The `mock` keys**, each optional beyond `pass_mark` and `domains`:

- **`minutes`**, a whole number from 1 to 1440: the time of the exam. The page shows the time
  remaining, keeps it across a reload (the start time is stored in the reader's browser with the
  answers), and submits by itself at zero. A reader who opens the page after the time ran out finds
  it submitted. No `minutes`, no clock.
- **`layout`**, only `"exam"`: one question to a view, with a navigator of question numbers (each
  says answered, not answered and flagged, in words as well as in look), previous and next,
  and filters by domain and by flagged. Left out, every question is on the page, as before.
- **`scenarios`**, a list of `id` (a token), `title` and `context`: a situation several questions
  are asked about. A question names one in its own `scenario`, and the page shows the card with the
  question (once for each run of questions that share it, in the all-on-one-page layout).
- **`difficulties`**, a list of `id` and `title`: the labels a question may carry in `difficulty`.
  The label is shown with the question in the exam layout and the results report a score for each.
- **`sittings`**, a list of `id`, `title` and at most one of `questions` (a whole number to draw)
  or `scenarios` (a whole number of scenarios to draw, with all their questions), and an optional
  `minutes`. A sitting with neither asks every question. The questions of the record are a **pool**
  and may be many more than one sitting asks. A sitting that draws `questions` draws them by domain
  weight, keeping each scenario's questions together; a sitting that draws `scenarios` draws that
  many whole ones. Without its own `minutes` a sitting takes the mock's `minutes` in proportion to
  the questions it draws against the largest sitting that names a number of questions (or the pool,
  for a sitting that asks everything). A mock with no `sittings` asks every question in the order
  written, with no shuffling.
- **`scale`**, `min`, `max` and `pass`, whole numbers with `pass` between: a score the results
  show as a linear illustration, `min + (max - min) * right / asked` rounded, beside the scale's
  pass, with the note that it is a linear illustration and not the exam's own scaling. The
  verdict stays the percent pass mark.
- A domain may carry **`weight`**, a whole percent; give it to every domain or to none, summing to
  100. Drawing questions follows the weights, else each domain's share of the pool.

**The question keys**, written after `domain` and only where present: `scenario` (an id of the
mock's `scenarios`), `difficulty` (an id of `difficulties`), `select` and `shuffle`. All four are
refused on a quiz with no `mock`.

- **`select: n`** makes a **multiple-response question**: a whole number of at least 2, the number
  of options the reader must choose. Exactly `n` options are keyed `correct`, and at least one is
  left to rule out. The page says "Choose n.", stops the reader at `n` boxes, and scores the
  question all or nothing: right only when exactly the keyed options are chosen. A question with
  no `select` keys exactly one option, as always.
- **`shuffle: false`** keeps one question's options in the order written. The default, in a mock
  with `sittings`, is that the page shuffles them.

**Sittings, seeds and what is remembered.** The reader chooses a sitting and begins it. The page
draws the set with a random seed, shuffles the order of the questions (a scenario's questions stay
together, in the order written) and the options, and stores the seed and the drawn set with the
answers, the flags and the start time, so a reload shows the same exam with the clock still running.
**Start again** draws a new set that prefers questions the reader has not yet met in earlier
sittings (the ids met are kept in the same place; once the whole pool has been met the preference
starts over). Everything is kept in the reader's own browser; a browser that refuses storage still
runs the exam and forgets on reload.

**The results**, after the reader submits (a submit with questions open names them and asks once
more, and a question left open is wrong): the score against the pass mark, the optional scaled
score, a score per domain and per difficulty over the questions the sitting asked, and every
question's verdict with **every option's sentence**, the keyed options marked and the reader's choice
marked. A filter reviews all, only the missed, or only the flagged questions. The page works at phone
width and by keyboard alone, and makes no request.

**The checks.** The record refuses what is wrong in one value (a `minutes` that is not a whole
number, a `scale` whose pass lies outside it, a `select` that is not a whole number of at least 2, a
question keying a different number than its `select`, two sittings with one id) and, because the page
cannot draw otherwise, a question under a scenario nobody declared, a declared scenario with no
question, a difficulty used and not declared, a sitting that draws more than the pool holds, and a
pool too thin in one domain for the largest sitting by the domain weights. `Q4` holds a
multiple-response question to the count it states and says so in its own words; `Q3` owes one
judgement for every option that is not keyed; `Q1` and `Q2` are taken per question as before.
`P1` also holds when every scenario named is declared and asked about, every scenario's context is
two to four sentences, and every difficulty is declared and carried by a question.

**Authoring one.** The exam covers a level, so it is authored from the pages of the whole level,
and each question's `origin` names the page and passage it is built from.

- **Domains.** Declare each domain once with an `id` token and a `title`, as the source's own exam
  guide names them, and tag **every** question with exactly one. `P1` refuses a question with no
  domain, a domain nobody declared and a declared domain with no question, naming the question by
  its stem, so a domain is never a label left over from a plan. Spread the questions over the
  domains the way the guide weights them, and say so in the page; the framework counts none of it.
- **One judgement set per question, taken by a reader who did not write it.** `Q1` (the page
  holds the answer), `Q2` (the wording alone gives nothing away) and `Q3` (a passage rules out each
  wrong option) are taken for every question and recorded for every question, whatever the number
  of questions. `judge(brief, questions)` returns one `Q1` and one `Q2` per question and one `Q3`
  per wrong option, each over `question_digest(question)`, for all of the exam at once. A question
  reworded after a refusal needs fresh judgements: the earlier ones are over the old wording.
- **Scenario questions.** A question the page's own quiz already asks is not repeated: the mock
  is the level's check, so a reader meets a new situation that needs two or three pages together.
  The score is only as good as the least careful question, and `Q4` and `Q5` refuse the mechanical
  faults one question at a time.
- **The pass mark is the corpus's number** (`mock.pass_mark`); the page states only whether the
  score reached it. Do not write the mark into a question.

### Revision aids: a review bank and a deck of flashcards

**Two opt-in shapes for revising a level, both opened in the practice workspace like a quiz, both
kept entirely in the reader's own browser (no network, no account).** A corpus that uses neither is
the corpus it was, byte for byte.

**The line naming where the items came from follows what they cite.** A deck or bank whose items
cite one page, or none, says it was written from this page. One whose items cite more than one
page says it was written from several pages of the level. There is no flag to set: cite the pages
the items were written from, and the sentence follows.

**A plain quiz is drawn one question at a time.** A quiz with no `mock` and no `review` is shown by
the exam form's own parts, in a kind of its own: one question per view, **Previous** and **Next**, a
progress line (*Question 2 of 7. 3 answered.*), a navigator of numbered buttons that say answered or
open, and a **Finish quiz** button. Each answer is explained **as it is given**: the verdict and the
sentence for the option chosen, never the key, so a reader told why a choice fails can try again. The
answers live in the reader's own browser (`studyforge.mockform.v1`, behind a guard that tolerates a
refused store), so a reload comes back on the same question with the same answers. **Finish quiz**
asks once about questions left open, then shows a summary: *Question n: Right.* or *Not this one.*
for every question, each a button that jumps to that question, and below it every question with the
key marked and every option's sentence (a review filter narrows it to the missed ones). The quiz is
complete, and its card reads *Passed*, as soon as every question is right, as before. There is no
pass mark, clock, flag or domain table. It is the default; a quiz that wants every question on one
page with one **Check answers** control writes the opt-out:

```json
{"kind": "quiz", "layout": "page", "questions": ["…"]}
```

`layout` is `steps` (what leaving it out gives) or `page`. It belongs to a plain quiz only: it is
refused on a record that is not a quiz and beside `mock` or `review`, which draw themselves. The
build writes the exam form's four files beside the shared bundle for a corpus that has a stepped
quiz, and a corpus whose quizzes all say `page` writes none of them. Draft one with
`QuizDraft(title=…, questions=…, layout="page")`.

**A lesson that lists its quiz shows the quiz once, in place.** A lesson sometimes ends with a
section (a heading, numbered questions, a folded *Answer key*) that lists the same questions as its
quiz practice. The match is by the text: a range of blocks from a heading to the next heading of the
same or a higher level that contains every stem of one plain quiz practice verbatim. The page then
draws the interactive quiz **where that section was**, under its heading, and does not draw the
static questions or the folded key; each question's explanation appears after answering. The
practice is not listed again in *Practice (n)* or opened in a workspace. A section that holds
different questions and a unit with no quiz practice are untouched, and a page with no match is the
page it was. **A mock exam counts as a quiz here**: a mock page that lists its questions and folds
an answer key away is replaced the same way, so the key is not in the page as readable text and each
explanation appears after submit. The key the page grades from stays in its own data block. A
review bank and a deck are never what a lesson repeats. A quiz that no lesson section lists is
opened from its card in the workspace, where it reads as a page that scrolls as one.

**A review bank is a quiz with a `review` key.** Every item is a quiz question under every quiz rule:
one keyed option, a sentence per option, a passage per question, `generated` and `advisory`.
`review` adds the schedule:

```json
{"kind": "quiz", "review": {"intervals_days": [1, 3, 7, 14, 30]}, "questions": ["…"]}
```

`intervals_days` is 1 to 12 strictly growing whole days, 1 to 730. The page shows the items that
are due and grades them from the key it carries. An item never seen, or last answered wrong, is due;
an item answered right `n` times in a row is due again once `intervals_days[min(n, last)-1]` local
days have passed since it was last got right (`exercise.quiz.review.due` is the rule, and a browser
test reads the page against it). A wrong answer resets the streak, so the item is due again at once.
The streak and the day are kept in the reader's browser under `studyforge.review.v1`, behind a guard
that tolerates a refused store. A bank is never a mock exam: the two keys are refused together.
Draft it with `QuizDraft(title=…, questions=…, review=Review((1, 3, 7)))`.

**A deck is a `flashcards` exercise.** It carries `cards` in place of a workspace or questions:

```json
{"kind": "flashcards", "cards": [
  {"id": "fc-001", "front": "What does a language model do at each step?",
   "back": "It scores every token for how likely it is next …",
   "origin": {"path": "course/01/page.md", "section": "How it generates"}}
]}
```

A card is `id` (a plain token), `front`, `back` and `origin`, the passage it was written from. The
page shows each front, turns a card on a button, and marks it known or to see again; the marks live
in the reader's browser under `studyforge.deck.v1`. With no script every card shows both sides. A
deck completes nothing and has no run, and it is `generated` and `advisory` like a quiz. Draft it with
`DeckDraft(title=…, cards=(Card(id, front, back, Origin(path, section)), …))`.

**The gates.** A bank answers `Q1` to `Q5` over its items and `S1` (the schedule fits the bank: at
least as many questions as steps). A deck answers two mechanical gates: `C1` (a front and a different
back no longer than 800 characters, and no two fronts that ask the same thing) and `C2` (every card
cites a passage whose digest the ledger still holds). `gate_deck(draft, brief, ledger, where=…)`
needs no runner and no judge, writes `tests/deck.json` and `gates.json`, and `deck_of` reads the
document back; the adapter reads it as it reads a quiz. Nothing is re-run by `validate`: it re-reads
the record and re-digests the bundle.

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
because both are facts about a grader and there is none. The design reasoning
behind this record is in
[the design specification](../specs/2026-09-08-studyforge-v1-design.md).

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

## Languages and profiles

**One line per language a practice and an example run in.** `runtimes` names the tools a runner
carries, never a version; a practice's `test_command` is argv, its `report` is the JUnit report,
and the same five gates read every language.

| Language | Graded by | Declare in `runtimes` |
|---|---|---|
| Java | JUnit through Maven (`pom.xml`) or Gradle, the JUnit XML report | `java` and `maven` or `gradle` |
| Kotlin | JUnit or `kotlin.test` through Gradle or Maven, the JUnit XML report | `java`, `kotlin` and `gradle` or `maven` |
| Python | `pytest` through `--junitxml`, the JUnit XML report | `python` |
| TypeScript | `node --test` on Node's type stripping, a build file writing the JUnit report, an optional `tsc --noEmit` | `node` |

**Profiles.** A toolchain may carry an image profile that holds what not every course needs, and a
corpus names it in `profile`. `claude-sdks` holds the Python wheels, npm packages and JVM jars of the
Claude SDKs, offline, for practices and examples in all four languages above, and a Python language
server in the editor; a course that names it declares `python`, `node`, `java`, `gradle` and `kotlin`
and is exported thin. A corpus that names no profile is built on the plain bases.

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

**The answer describes your source. It does not decide whether your reader
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
  `Q2` (the question's wording does not give the answer away), `Q3` (the page rules out
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
2. Describe each page: the important ideas it teaches (its *aspects*),
   which exercise checks each one or why none does, and its tier. That sets
   its *plan*.
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

**Every command and fence in this section runs as written**, from a shell
whose `PYTHONPATH` holds the framework's `src/`. `path/to/studyforge` is your
checkout of the framework, and `path/to/your-corpus` is your corpus:

```
export PYTHONPATH=path/to/studyforge/src
```

1. **Your corpus is onboarded.** `corpus.json` exists, and this exits `0`:

```
python3 -m studyforge.validate path/to/your-corpus
```

Wherever this page says `studyforge validate`, it means that command. The
two spellings run the same code; `studyforge validate` is the installed
command, and a checkout you have not installed has only the form above.

2. **Your manifest says `"exercises": true`.**
3. **Your manifest marks the two trees the pass writes as `not_material`.** The
   pass writes into `exercises/` and `practice/`. Without these two entries,
   `studyforge validate` refuses every file in both trees before any exercise
   check runs. `not_material` needs `corpus_api` 2 or later, and the
   onboarding skill raises it for you.

**Do not edit `corpus.json` by hand, for either step.** Onboarding generated
it, and `.studyforge/installed.json` records its digest. A hand-typed entry is
named by `hand_edited`, as a generated file somebody edited. Give both
changes to the onboarding skill as data, and regenerate:

```python
import json
from pathlib import Path

from studyforge.skills.onboarding import hand_edited, reonboard

corpus = "path/to/your-corpus"
trees = [
    {"glob": "exercises/**", "why": "authored exercise bundles and their gate records"},
    {"glob": "practice/**", "why": "the reader's workspace, from each bundle's starter"},
]
recorded = json.loads(Path(corpus, "corpus.json").read_text(encoding="utf-8"))
declared = {entry["glob"] for entry in recorded["content"].get("not_material", [])}
made = reonboard(
    corpus,
    not_material=[tree for tree in trees if tree["glob"] not in declared],
    settle={"exercises": True},
)
made.write(corpus, regenerate=True)
print(hand_edited(corpus))  # [] -- nothing generated was edited by hand
```

`reonboard` reads your corpus's recorded manifest and pin, and uses them as
the draft. Every answer you already gave is kept. Each `not_material` entry
your manifest already declares is kept byte for byte, and each glob the skill
generates is derived again, so you pass only the new ones.
`settle` names a recorded answer you mean to change. Any other answer that
would change is refused by name, and nothing is written.

⛔ **Pass only the globs your manifest does not declare yet.** The fence reads
`corpus.json` to find them, and reading it is not editing it. A glob your
manifest already declares keeps its own reason, so leaving it out loses
nothing. Passed again with a different reason, it is refused by name, and the
refusal tells you to leave it out. `settle` cannot change it either: it takes
only the manifest's top-level answers, never `content`, and a regenerate never
gives a recorded glob another reason.

4. **Your corpus ignores every run's output.** A test run writes into the
   reader's workspace, under `practice/`, and a JUnit report records the
   machine's hostname. Every run's output, the report included, lands in one
   directory inside the workspace, `target/` (`RUN_OUTPUT_DIRNAME`). So one
   line ignores all of it: create `practice/.gitignore` holding the line
   `RUN_OUTPUT_IGNORE` names, from `studyforge.exercise.bundle`:

```
target/
```

It is your corpus's own file, under a tree the manifest declares
`not_material`. Never add the line to your corpus's root ignore file instead:
generation never edits a file it did not write. A report path outside
`target/`, and any bundle file under a `target` directory, is refused.

5. **Your gates run in the pinned runner image, and it holds every library
   your exercises import.** Gate runs must happen in the same pinned toolchain
   the reader's runs use, or the proof applies to a different machine, and
   they run with the network off. An exercise whose tests need only the
   language needs nothing more. One whose tests import a library needs two
   things, both your corpus's own data:

- **The exercise's build role.** The draft's `build` field maps each build
  file, such as a `pom.xml` naming the library, to its text. It ships in the
  bundle's `build/` directory and is laid into the reader's workspace beside
  the starter and the tests. The test command names it by its path inside the
  workspace (`mvn -o -q -f practice/…/pom.xml test`). Never a jar, a
  repository or an absolute path.
- **A runner primed with the library.** Declare the runtimes in `corpus.json`,
  through `reonboard` as above (`runtimes` is an answer `settle` takes). Give
  your corpus one build of its own that declares every library any exercise's
  build role names, outside `exercises/` and outside every exercise's
  workspace: exercise material is never read into the prime. Then run the
  [execution skill](../../src/studyforge/skills/execution/SKILL.md). It writes
  that build as `.studyforge/execution/prime/<tool>/`, one project per tool,
  and `EXECUTION.md` prints the flag the runner's build takes, with your
  corpus's directory in its slot. Build the runner from the toolchain's
  checkout with that flag, and have your `runner` run every gate in it.

⚠️ **In an unprimed runner, every draft that imports a library fails `G1`**,
naming what was never downloaded. That is correct. The remedy is your
corpus's build and a rebuilt runner, never the exercise.

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

⚠️ **A page with tests gets `generated` exercises from this pass too.** The pass
never turns a source's own solution into an `authoritative` exercise.

### The worked corpus

| page | kind | case | aspects | plan |
|---|---|---|---|---|
| `lessons/greeting.md` | `code` | `code-and-tests` | 1 | 1 |
| `lessons/shout.md` | `code` | `code-no-tests` | 1 | 1 |
| `lessons/basket.md` | `code` | `neither` | 2 | 1 |
| `notes/gauge.md` | `quiz` | `neither` | 2 | 1 |

⭐ **The basket's two aspects, *a basket totals its prices* and *a negative
price is refused*, are one exercise**, and so are the gauge's two: one quiz
with a question on each. The aspects are in `ASPECTS` in
`tests/studyforge/skills/exercises/authoring.py`.

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
| `plants` | for each edge case's id, a solution that solves the main ask and ignores exactly that edge: its full text, or a `PlantSpec` of replacements against the reference (see *A plant as replacements*) |
| `build` | only when the tests import a library: each build file's path, relative to the workspace, mapped to its text, such as a `pom.xml` naming the library. Leave it out otherwise |
| `files` | optional, empty by default: the further files the reader edits beside `main_file`, each workspace-relative path mapped to `EditedFile(starter, reference)`; see *A practice of several files* |
| `assertions_only` | optional, `False` by default: `True` has `G2` and `G3` refuse a starter or a plant whose tests failed with an error that is not an assertion, such as a starter that raises `NotImplementedError` |
| `typecheck_command` | optional, empty by default: an argv (such as `tsc --noEmit ...`) run in each staged solution's workspace before its tests; a non-zero exit is a named failure of `G1`, `G2` or `G3`, never a test case. Nothing is run when it is empty |

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
            f"{ws}/target/report.xml",
            f"{ws}/test_total.py",
        ),
        cases=(Case("test_totals_a_basket", MAIN, "a basket adds up"), NEGATIVE),
        report="target/report.xml",
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

### A practice of several files

A configuration practice has the reader edit a settings file, a memory file and a hook script,
and the tests judge what the files say. `CodeDraft.main_file` is the first of them and
`CodeDraft.files` names the rest:

```python
from studyforge.skills.exercises import CodeDraft, EditedFile

draft = CodeDraft(
    title="Project setup",
    lang="json",
    main_file="settings.json",
    test_file="test_setup.py",
    run_command=("python3", f"{ws}/check.py"),
    test_command=("python3", "-m", "pytest", f"{ws}/test_setup.py"),
    cases=cases,
    report="target/report.xml",
    origin=origin,
    statement=statement,
    starter=STARTER_SETTINGS,
    reference=REFERENCE_SETTINGS,
    tests=tests,
    plants=plants,
    files={"docs/memory.md": EditedFile(STARTER_NOTES, REFERENCE_NOTES)},
)
```

- **The bundle** holds `starter/<path>` and `reference/<path>` for each further file, and
  `bundle.json` lists them under `files`. The gate record digests each as `starter:<path>`
  and `reference:<path>`, so a changed starter drifts the record like any other input.
- **A plant** that changes a further file is a `PlantSpec` whose replacement names that file
  (`Replacement("docs/memory.md", old, new)`); a file no replacement names stays as the
  reference has it. A full-text plant is the main file's text alone. A replacement naming a
  file the reader does not edit is refused, so no plant reaches the tests.
- **The exercise record** gains `files`, the corpus-relative paths in the order declared,
  written only for a practice that has some. The workspace is written with every edited file
  in its starter state, the page names every file the reader edits, and the editor opens the
  practice's own folder with one tab for each file; the files are editable and everything
  else is read-only. `studyforge check` accepts any of the files.
- **Nothing changes for a practice of one file**: no key, no input, no block.

### A plant as replacements

A plant usually differs from the reference by a line or a few. Instead of the
whole text, a plant may be written as an ordered list of exact replacements
against the reference:

```python
from studyforge.skills.exercises import PlantSpec, Replacement

plants={
    NEGATIVE.id: PlantSpec((
        Replacement(
            "total.py",
            '    if any(price < 0 for price in prices):\n'
            '        raise ValueError("a price is never negative")\n',
            "",
        ),
    )),
}
```

Both forms are accepted in one draft, edge by edge. A text is the plant as it
is; a `PlantSpec` is the reference with its replacements applied.

- Each replacement is `file`, `old` and `new`. `file` is the exercise's
  `main_file`, since a plant is that one file. `old` must occur exactly once
  in the text the replacement is applied to, counting an occurrence that
  overlaps another.
- Replacements apply in order, each to the text the one before it left.
- The gate materialises the full plant from the reference into its own staging
  directory, runs it like any plant, and discards it. Nothing writes the full
  text into a source tree.
- A draft is refused, before any run, when a replacement's `old` is absent or
  occurs more than once, when it is empty or equals `new`, when `file` is not
  the main file, when the list is empty, or when the result is identical to
  the reference. The refusal names the plant by its edge position and the
  replacement by its position, and quotes none of the text.
- Gates `G1` to `G5` read a spec plant exactly as they read the equivalent
  full plant: same runs, same verdicts, same sentences.

**What the bundle holds.** A full plant is the file
`plants/edge-N/<main file>`. A spec plant is the file
`plants/edge-N/<main file>.plant.json`:

```json
{
  "plant_version": 1,
  "replacements": [
    {"file": "total.py", "old": "...", "new": "..."}
  ]
}
```

An edge has one of the two files, never both and never neither; `emit` refuses
a bundle that files both or neither. The gate record digests whichever file the
bundle holds under the same `plant:<case id>` role, so `validate` re-digests a
spec plant as it does a full one. Fixing the reference changes the plants at
the next gate run, and a replacement the fix leaves with nothing to find is
refused instead of skipped, so the author sees which plants the fix touched.

**What a learner receives.** Plants stay in `exercises/`, as before. The
learner's workspace is made of the starter and the tests, and the site, runner
and editor images leave `exercises/` out of their build contexts, so a spec
plant, like a full one, is in no image. The standalone export keeps the
`exercises/` tree on `main` and writes the same files for both forms.

**Converting a course once.** `studyforge.exercise.bundle.convert` reads every
bundle under `exercises/`, derives for each full plant the smallest list of
replacements, widened with the lines around each change until the text is
unique, and materialises it again:

```python
from studyforge.exercise.bundle.convert import convert_plants

report = convert_plants(root)               # reads and proves, writes nothing
report = convert_plants(root, write=True)   # then writes what was proven
report.converted, report.left               # bundles changed; each plant left, with why
```

Without `write=True` nothing is written. With it, a plant is
replaced only when its spec materialises to the same bytes and is smaller than
the file, and the plant's input in `gates.json` is re-digested; the verdicts are
left as they were, because every gate ran over the same text. A plant is left,
with its reason in `report.left`, when the spec would not be smaller, when it equals the
reference, when the record does not hold the plant's current digest, or when the
record does not re-encode to its own bytes. A bundle is written whole or
restored.

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
from studyforge.exercise.gates.quiz import (
    Q1,
    Q2_PROMPT,
    Q3,
    WHOLE_QUESTION,
    Judgement,
    page_free,
    question_digest,
)


def judge(brief, questions):
    taken = []
    for question in questions:
        over = question_digest(question)
        free = ask_a_page_free_reader(Q2_PROMPT, question.stem, question.options)
        taken.append(page_free(question, free.picked, free.because, free.taken_by))
        asked = [(Q1, WHOLE_QUESTION)]
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

`ask_an_independent_pass` and `ask_a_page_free_reader` are yours to write.
**`held` is the verdict.** A pass that answered badly is recorded with
`held=False`, and no sentence in `outcome` can change that.

**`Q2` looks for a giveaway, not for knowledge.** Its reader sees the stem and
the options, never the page, and is asked `Q2_PROMPT` word for word: answer from
the wording alone, with no knowledge of the subject, and say *none* unless the
wording itself clearly singles out one option (a weak cue, or one two options
share, decides nothing). `page_free` takes what it answered
(`picked` is an option's id, or `None` for *none*) and the cue it named, and
decides `held`: *none* or a wrong option holds. A `Q2` judgement taken under
another prompt, or without its reason, is refused. The cue is quoted in the
refusal, so the next attempt's brief says what gave the key away. A correct
question on a well-known subject passes as long as its wording does not
betray it: write options of like length and grammar, and do not repeat the
stem in the key. The worked corpus's `Judging` class holds every judgement, so
its tests exercise the pass rather than a model.

### A quiz beside a page's code

**A lesson page with code usually also teaches ideas no test can observe**: a
compile-time rule, how an expression is parsed, a claim about timing. A short
quiz checks those. ⭐ So a `code` page may carry one quiz as well as its code
exercises. Give those aspects one exercise name of their own, and name it on
the page as `quiz`:

```python
from studyforge.address import Address
from studyforge.skills.exercises import CORE, Aspect, Page

parses = Aspect(
    "precedence",
    "unary ! binds tighter than the binary operators",
    ("section:Logical Operators",),
    exercise="check",
)
operators = Page(
    path="01-java-basics/README_1.1.4.md",
    address=Address(["01-java-fundamentals", "01-java-basics"]),
    variant="prose",
    unit=4,
    kind="code",
    aspects=(*code_aspects, parses),
    tier=CORE,
    quiz="check",
)
```

**The quiz is drafted after the page's code exercises**, so it takes the unit's
last ordinal and sits at the end of the page. Its brief says `kind` `quiz`, and
it is gated by `Q1`–`Q5` like any quiz. It is committed as a quiz's
`tests/quiz.json`. The unit keeps one `coverage.json`, which records the name
under `quiz`. ⛔ Only a `code` page may name a quiz, and the name must be one
its aspects give. Anything else is refused before an author is asked.

⚠️ **Naming a quiz on a unit already authored changes its plan**, so the pass
refuses the unit as it refuses any page whose plan moved. Delete the unit's
directories under `exercises/` and `practice/`, then run the pass again.

---

## The plan

**A page's plan is set by the important ideas it teaches, not by how long its
prose is.** The aim is to cover every idea that matters, with as few exercises
as do it well: a single practice can cover more than several small, unrelated
ones.

**Each page gets a plan before anything is written.** You read the page, its
prose and its code, and list its *aspects* on the `Page`. An aspect is one
important idea the page teaches that a reader could be checked on. **Each
aspect ends one of two ways: a named exercise checks it, or a written reason
says why nothing does.** The plan has one exercise for each distinct name the
aspects give, and each exercise's brief lists the aspects it checks.

**Exercises ship in the order you give them.** Set the page's `order` to every
planned exercise name, each once, in teaching order. The first gets the unit's
next free number. Without an `order`, the plan keeps the names in sorted order.
Do not add prefixes such as `p01-` to names to control the order. An `order`
that misses a name, or repeats one, is refused.

**What makes a good aspect:**

- **It matters to the page.** Dates, names and incidental numbers are not
  aspects. The idea they illustrate may be. A version number can matter if the
  page depends on it.
- **One exercise can check several aspects, and often should.** One exercise
  that practises related ideas together is better than several small,
  unrelated ones.
- **A minor aspect can be carried by a short reason**, such as *"incidental
  detail, not practised"*. It does not need an exercise.
- **A quiz asks few questions.** For a short conceptual page, one or two, each
  about something that matters.
- **There is no ceiling and no quota.** The plan records what you judged
  important and why. It is not a coverage score to push up.

**An aspect carries these fields:**

| field | what you write |
|---|---|
| `id` | a short token naming the aspect, unique on the page |
| `says` | one sentence: what a reader who has it can do or knows |
| `basis` | what you read it from: `example:<path>:<n>` or `tests:<path>` for the page's own code, `section:<heading>` for its prose |
| `exercise` | the name of the planned exercise that checks it |
| `reason` | instead of `exercise`: why nothing checks it |

**The plan refuses:**

- an aspect with neither an `exercise` nor a `reason`, or with both;
- two aspects with the same `id`, or with the same sentence in `says`. Two
  exercises checking one idea are one exercise, so merge them;
- a `basis` the page does not carry: an example or test file that is not the
  page's own, or a heading the page has none or two of.

**A page can plan zero, and zero says why.** If every aspect carries a reason,
the plan is zero and each reason is in it. If the page teaches nothing
checkable at all, name no aspect and write the reason in `nothing_checkable`.
A page with no aspects and no reason is refused.

**The `tier` does not change the count.** It says how hard each exercise
should be, and it is handed to the author with the page.

⛔ **The plan is a ceiling, never a quota.** Only exercises that pass the gates
ship. A page that ships fewer than its plan names the gate that stopped each
missing one. Never lower a bar to reach a count.

**Where to read a thin plan:** each unit's `coverage.json` holds the plan, with
every aspect and how it ended. `authored.reasoned` lists every aspect no
exercise was planned for, page by page.

---

## The ledger

**The ledger is the proof that nothing your source already has is lost.** The
pass reads every file you list as material and every test file you declare,
once, before gating anything. Each fenced example and each test file becomes an
entry. **Each entry either is the basis of an exercise, named by that
exercise's `origin`, or carries a written reason why not.** An entry with
neither is refused.

- An example's key is `example:<path>:<n>`, where `<n>` counts the file's
  fenced blocks from 1. **The ledger reads fences exactly as the archive
  reader does.** A fence is a run of backticks indented up to three spaces,
  or indented any amount inside a list item. It closes on a line of backticks
  at least as long, indented at most three spaces more than its opening line.
  A `~~~` run is not a fence, because the archive keeps none. So `<n>` counts
  exactly the code blocks the reader sees on the page.
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
| `G3` | for each edge case, its plant passes every main case and fails that edge | each edge test catches the one mistake it names |
| `G4` | every test the report names maps to one case, and every case is reported | the reader's breakdown is complete |
| `G5` | the passage the exercise cites still has the digest the ledger read | it is built from what the source has |

### The quiz gates

| gate | what must hold | what it proves |
|---|---|---|
| `Q1` | an independent pass given the page and the question picks the key | the page contains the answer |
| `Q2` | a reader given only the question's wording, and no knowledge of the subject, answers *none* or a wrong option | the key is not given away by the wording |
| `Q3` | a passage of the page rules out every wrong option | no distractor is a trick |
| `Q4` | exactly one option is keyed, the options are distinct, and every option has its sentence | the reader is told why, whatever they chose |
| `Q5` | every question's passage still has the digest the ledger read | the question is built from the page |

**The gate record ships beside the exercise, as `gates.json`.** It holds the
digest of every file the gates read and each gate's verdict.
`studyforge validate` refuses a `generated` exercise with no record, a record
in which any gate failed, and a bundle whose files no longer match their
recorded digests.

| `S1` | (a review bank only) the bank holds at least as many questions as its schedule has steps | every step of the schedule has something to show |
| `C1`, `C2` | (a deck, instead of the five) the cards are sound and each cites a passage the ledger still holds | a card is a front and a different back, built from the page |

⚠️ **What `validate` does not do is re-run the gates.** It re-reads the record
and re-digests the bundle's files. A quiz record whose key breaks `Q4`'s rules
is refused wherever it is read, because the quiz record itself refuses that.
But `validate` does not re-run the tests, and it does not check `G5` or `Q5`
against your source again. `Q1`–`Q3` can never be re-taken, which is why a
quiz is always `generated` and `advisory`.

---

## What the gates cannot see

**The gates prove the plants you wrote, and no others.** A wrong solution you
did not think of can pass every test and ship. The cases below are the ones
that did, on a real course. The skill asks for an adversary before the pass:
a reader other than the author writes subtle wrong solutions, starting from
this list, and every survivor that breaks its statement is fixed.

### Equal, but not the same object

When a practice teaches equality, copying or immutability, build the objects
the tests compare **at run time**, so two equal values are two distinct
objects.

- ⚠️ A string literal is interned, `Integer.valueOf` caches -128 to 127, and a
  constant is one shared instance. A test built from them compares an object
  with itself, and a solution that returns its input, or copies nothing,
  passes.
- Use `new String(...)`, values outside the cache, or objects built by a
  helper for each use.
- ⭐ Ship a plant that returns the same instance, or shares a mutable part,
  and check that the tests catch it.

### The common silent passes

- **`ZonedDateTime` compared with AssertJ `isEqualTo`.** It compares the
  instant only, so the right moment in the wrong zone passes. Compare
  `toString()`, or the zone and the local time as well. `equals`-based
  assertions (`containsExactly`, `Optional.contains`) are not affected.
- **The default locale, time zone or clock.** A solution that reads the
  machine's default passes on your machine. Test under a default that
  differs: a Turkish or German locale, a zone that is not UTC, a winter date.
  Or pass the locale, zone or clock in explicitly.
- **An unanchored regex.** `find()` where `matches()` was meant, or a pattern
  with no `^` and `$`, accepts a valid value with other text around it. Test
  one: `on 2024-03-15, late`.
- **Boundaries and rounding.** Test both sides of every boundary, inclusive
  and exclusive, and a value where rounding and truncation disagree.
- **A shared mutable result.** A solution that returns its own internal list,
  or one list to every caller, passes a test that reads the result once.
  Change the result, then call again.
- **A near-miss type.** A `Set` where a `List` was asked, or a `Long` for an
  `Integer`, can pass a loose comparison.
- **Test order through static state.** A test that changes a singleton, a
  static counter or a cached formatter can make a later test pass or fail. Reset
  that state before each test, or assert on the change rather than the total.
  Where a plant's change could reach a later case, fix the order with
  `@TestMethodOrder`. `G1` runs the reference twice, the same way both times,
  so it cannot find this for you.

### Python and TypeScript silent passes

Both languages have their own ways for a test to pass whatever the code does. `G2` (every test
fails on the starter) refuses a test that passes on a starter returning its input, which is the
first reading; the cases below also pass a wrong plant, or a wrong solution nobody planted, so
look for each before the pass.

**Python (pytest)**

- **A test that asserts nothing.** A function that calls the code and ends passes whatever the
  code returns. So does an `assert` inside a loop over an empty sequence, inside an `except`
  branch no run reaches, or in a helper the test never calls.
- **Truthiness.** `assert normalise(x)` passes for any non-empty result, and `assert result is not
  None` for any result at all. Compare the exact value, and for a collection its exact contents.
- **A tuple asserted.** `assert (got == want, "message")` is a non-empty tuple and is always true.
  Write the message after a comma, not inside parentheses.
- **Identity against equality.** `==` on two lists compares contents, so a solution that returns
  its own input list passes a test that only compares; `is` on small integers, short strings
  and tuples of them compares one cached object with itself and passes for the wrong reason.
  Build the values at run time, assert `is not` where a copy is the point, and assert `==`
  where equality is.
- **A mutable default argument.** `def add(item, bucket=[])` keeps one list for every call, so
  a test that calls it once passes. Call it twice, and assert the second result.
- **`pytest.raises(Exception)`** accepts any error, including the `NotImplementedError` of an
  unwritten starter. Name the exact exception and check its message where the message matters.

**TypeScript (`node --test` on type stripping)**

- **A missing `await`.** `assert.rejects(...)` and `assert.doesNotReject(...)` return a promise;
  left unawaited, the test body ends first. Node 24 then reports the late failure against the
  test **file**, not the test, so the test itself shows as passed and the file as failed, which
  the case ids cannot map. `await` it, or `return` it, and make an async test `async`.
- **A promise chain with no `return`.** `fn().then((v) => assert.equal(...))` settles after the
  test ended, with the same effect. Prefer `await`.
- **Truthiness.** `assert.ok(value)` and `assert(value)` pass for any non-empty value. Use
  `assert.equal` or `assert.deepEqual` with the expected value.
- **Loose equality.** `node:assert` (not `node:assert/strict`) compares with `==`, so `"1"`
  equals `1` and a starter returning a string passes. Import `node:assert/strict`, whose `equal`
  is `===` and whose `deepEqual` is strict.
- **An `any` that hides a type error.** Type stripping reads no type, so a test run never sees a
  wrong signature, and an `any` or a cast makes the optional `tsc --noEmit --strict` pass on
  one. Declare real types in the starter and the reference, and run the type check
  (`typecheck_command`) where the signature is part of the ask.
- **`enum`, parameter properties and `namespace` under type stripping.** Node refuses them with
  `ERR_UNSUPPORTED_TYPESCRIPT_SYNTAX`: a file that does not load. A draft that sets
  `assertions_only` has `G2` and `G3` refuse such a starter or plant as *not an assertion*, and
  `G1` refuses such a reference; `--erasableSyntaxOnly` in the type check names it earlier.
- **A skipped or nested test.** A `test.skip`, a `todo` and a `test(...)` inside another test do
  not run as a case of their own. A case that was never run is not a pass.
- **A stub that returns without asserting.** A test whose body calls the code and ends passes.
  Every test ends in an assertion on the value the ask names.

⭐ **Prove the plant of each language's own trap before the pass:** a wrong solution that is
the mistake, never the deletion of the code, and the test that must fail on it.

### Threads

- **Coordinate with latches, barriers or forced interleavings, never with
  time.** A `sleep` that is long enough on a quiet machine is too short under
  load.
- ⚠️ **Polling `getState()` does not show reliably that a thread is blocked.**
  The JVM blocks threads briefly for its own reasons, so a wrong solution can
  pass. Read the lock owner and the waiting frames from `ThreadMXBean`
  instead.
- **Read the verdict before the bound expires, not after.** A holder and a
  probe with equal bounds, or a check made after the timeout, let a plant
  pass one run in ten.
- **A main case must not race.** Every plant must pass every main case, so a
  main case that races can fail a correct plant.
- ⭐ **Prove each threaded plant fails 10 times out of 10**, and the reference
  passes 10 times out of 10, before the pass. The pass runs each plant once,
  so it cannot see a plant that fails only most of the time.

---

## Running the pass

**There is no command for this.** The pass is a Python function,
`author_corpus`, and your agent calls it from a short script it writes, like
the one below. `tests/studyforge/skills/exercises/test_corpus.py` calls it the
same way over the worked corpus.

```python
from pathlib import Path

from studyforge.address import Address
from studyforge.skills.exercises import CORE, Aspect, Page, author_corpus

root = Path("path/to/your-corpus")


def page(path, unit, aspects, graders=()):
    return Page(
        path=path,
        address=Address(["kata"]),
        variant="python",
        unit=unit,
        kind="code",
        aspects=aspects,
        tier=CORE,
        graders=graders,
    )


greets = Aspect(
    "greets-by-name",
    "the greeting names who it greets",
    ("example:lessons/greeting.md:1", "tests:checks/test_greeting.py"),
    exercise="greet",
)
totals = Aspect(
    "totals", "a basket totals its prices", ("section:A basket of prices",), exercise="total"
)


authored = author_corpus(
    root,
    source="demo",
    material=["lessons/greeting.md", "lessons/basket.md"],
    graders=["checks/test_greeting.py"],
    pages=[
        page("lessons/greeting.md", 1, (greets,), ("checks/test_greeting.py",)),
        page("lessons/basket.md", 3, (totals,)),
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
  `CodeDraft` when `brief.kind` is `code` and a `QuizDraft` when it is
  `quiz`: a `quiz` page's exercises, or the one quiz a `code` page names.
  `excuse(entry)` returns the one sentence saying why no exercise was built
  from a ledger entry. In real use a model writes the drafts. The worked
  corpus's `Scripted` returns drafts it was given ahead of time.
- **`judge`**: the independent pass for `Q1`–`Q3`, shown above. Only a corpus
  with a quiz needs one.
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
| `name` | that planned exercise's name. It says `brief.kind`: `quiz` for the quiz a code page names, the page's own kind otherwise |
| `aspects` | the aspects the plan gave this exercise to check. Write the exercise so it practises them |
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
| `exercises/<address>/<variant>/unit-NN/coverage.json` | the unit's plan (every aspect and how it ended), the quiz a code page names, what shipped, and every shortfall |
| `exercises/ledger.json` | the ledger, with every entry accounted for |

**Exercises on a page are numbered `1..n` in the order they ship.** An exercise
that failed leaves its number for the next one, so a page never has a gap.

⛔ **The pass only writes inside your corpus, and only adds files.** Every file
is checked before any is written. A file already there with the same bytes is
left alone. One with different bytes stops the whole pass, names the first such
file, and nothing is written.

⛔ **A file your corpus's git would ignore also stops the pass, before anything
is written.** `git add` would leave that file out, so your repository would
never hold the exercise. The refusal names the first ignored file. A course
that ignores `build/` also hides every bundle's `build/pom.xml`. Un-ignore it
with a `!build/` line in `exercises/.gitignore`, then run the pass again.

⭐ **The ledger is the one file a pass rewrites, and it only ever adds.** It is
one file for your whole corpus, so you can run the pass over one container at a
time, in any order. A pass replaces the rows of the files you handed it as
`material` and `graders`, and keeps every other row exactly as it was. A row
leaves only when its file is gone from the corpus. `authored.ledger` says what
the pass did, row by row: `kept`, `added`, `changed` and `dropped`. A fence that
a re-read page no longer carries is listed under `changed`, because the page
changed but is still there.

**Running it again with nothing changed writes nothing.** A unit whose
`coverage.json` still matches its page and its plan is not authored again, so
the author, the judge and the runner are not called for it.

⚠️ **A page whose source changed is refused, and the refusal names its unit.**
Its exercises were proven against material that has since moved. To author it
again, delete that unit's directory under `exercises/`, then run the pass
again. ⛔ **Do not delete `exercises/ledger.json`**: the pass keeps every row
for a file it did not read, so deleting the ledger loses every other page's
rows, and `validate` then names each page a pass had authored
(`ledger-unaccounted`).

**You can author one container at a time, and `validate` stays clean between
passes.** A page that no pass has been given yet is *pending*, not missing.
`validate` lists one unchecked claim, `ledger-pending`, with the number of
pending pages in each module. It is not a finding. The first pass that reads a
page ends its pending state. Pending is not an excuse. An excuse is a written
reason that no exercise is built from an entry, and it stays that reason.
**Delete the unit's directory under `practice/` as well.** The refusal does not mention it, but a
new draft whose starter or tests differ would otherwise land on the old
workspace files, and the pass refuses any file that exists with different
bytes.

**Your archive still holds the practices you deleted** until the adapter runs
again, and that is fine: the pass counts only the source's own practices, never
one an earlier pass generated, so the unit's exercises are numbered as they
were the first time.

### Then the adapter, then `validate`

**The pass writes no practice document. Your adapter does.** If you
scaffolded the adapter with the [adapter skill](../../src/studyforge/skills/adapter/SKILL.md)
and your manifest says `exercises: true`, the generated `emit.py` already does
it. It reads every committed bundle, code and quiz alike, through
`studyforge.skills.adapter.practices`. It checks each one against its gate
record, adds it to its unit as a practice document, and raises the unit's
practice count. Your `read.documents` then returns only your source's own
material. An adapter you wrote by hand builds each code practice from its
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

⚠️ **The framework has no `emit` for a quiz.** Your adapter builds a quiz's
practice document itself, from the `exercise` record in its `tests/quiz.json`.
Read that file through `quiz_of`, which refuses a `quiz_api` this framework
does not speak and an identity that does not name the bundle's own directory:

```python
import json
from pathlib import Path

from studyforge.skills.exercises import QUIZ_DOCUMENT, quiz_of

root = Path("path/to/your-corpus")
where = "exercises/kata/python/unit-03/practice-2"
quiz = quiz_of(json.loads((root / where / QUIZ_DOCUMENT).read_text(encoding="utf-8")), where)
quiz.places, quiz.title, quiz.record  # the record goes under the document's `exercise`
```

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
