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
records carry the first six and nothing else; the last four arrive with an
exercise somebody authored for this site.

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
    "origin": {"path": "docs/01-getting-started.md", "section": "Greeting a caller"}
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

### The last four: what an authored exercise says

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
a grader**, so it is the one of these four an *ungraded* record may carry.

**The breakdown is a report, never a second definition of a pass.** A practice
completes when every case passes, exactly as before. The rules are §7's, in
[*Exercises authored for every corpus*](../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389),
and this page does not restate them.

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
