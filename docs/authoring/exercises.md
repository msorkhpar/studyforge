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

**Ask one question — does your material ship something that can check an
answer?**

- **It ships tests, or a runner, or an expected output you can diff.**
  `"exercises": true`, and write `exercise` keys where the graders exist.
- **It sets work but checks nothing.** `"exercises": true`, practice documents
  with prompts, **no `exercise` key** — or, where the work is a file the reader
  runs, an `exercise` naming that file and no grader. The reader gets the work,
  marked as unchecked.
- **It teaches and sets no work.** `"exercises": false`, no practice documents,
  and you are finished at the reading floor.

~~**Do not invent assertions to fill the third case.** A grader nobody wrote,
checking an answer nobody specified, is theatre — and a corpus that refuses to
put on that show is behaving correctly, not failing.~~

⛔ **STRUCK 2026-09-19 (`W389`, user direction), and replaced by *author, then prove*.**

⭐ **The three cases above still describe your corpus as its source ships it, and they are
still how you answer the manifest question today.** ⚠️ **What they no longer decide is
whether your reader gets to practise.** An exercise can be **authored** from a page's own
material — its examples, its practice code, its prose — and what keeps that honest is not a
refusal to write one, but **gates it must clear before it ships**: its tests pass on a
reference solution, every test fails on the starter, each edge-case test catches the one
omission it names, and a record of those readings ships beside the exercise for
`studyforge validate` to re-check. An exercise that cannot clear a gate does not ship, and
the coverage report names the gate that refused it.

⛔ **The old sentence's point survives, sharpened:** a grader nobody proved is still
theatre. ⭐ **The remedy changed from *do not write one* to *write one and prove it*.**

⚠️ **THIS IS A STANCE, NOT YET A PROCEDURE.** ⛔ **No skill in this repository authors
exercises today, and nothing here should be read as describing shipped behaviour.** ⭐ **The
authoring skill, its gates and the quiz shape for material with no coding task are
milestone `M10`** ([the plan](../tasks/README.md#m10-every-corpus-has-practices), epic
[`E14`](../tasks/E14-authored-exercises.md)), and this page is rewritten from the code when
they land. ⭐ **The design, whole, is [spec
§7](../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389).**

---

## Next

- [What an adapter must produce](archive.md) — where the practice document
  goes.
- [Worked examples](examples.md) — one corpus with `exercises: true` and one
  with `false`.
