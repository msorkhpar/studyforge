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
| `ungraded` | a prompt the reader works, with nothing to check it | **no** |
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
| `ungraded` | a `practice-M.json` with blocks and **no `exercise` key** |
| `graded` | a `practice-M.json` whose `exercise` key is present |

**So the common case is a corpus that writes nothing.** A design in which every
corpus had to declare its emptiness would be a design fitted to the one
repository that is full.

---

## The `exercise` key

**It lives inside the practice document**, not in a file of its own and not in
anything a person types. It rides the version that document already has, and
the adapter writes it — because the adapter is the only thing that knows what
your build command is or where a grader came from.

```json
{
  "exercise": {
    "main_path": "practice/basics-01/src/main/java/Greeter.java",
    "test_path": "practice/basics-01/src/test/java/GreeterTest.java",
    "run_command": ["mvn", "-q", "-pl", "practice/basics-01", "compile"],
    "test_command": ["mvn", "-q", "-pl", "practice/basics-01", "test"],
    "provenance": "bundled",
    "trust": "authoritative"
  }
}
```

**A complete practice document carrying that key is in this repository**, at
[`tests/fixtures/depth2/.../practice-1.json`](../../tests/fixtures/depth2/archive/basics/01-getting-started/raw/java/unit-01/practice-1.json)
— fifteen keys, then `starting_code`, then `exercise`, in that order.

**Six fields.** `main_path` and `test_path` are the workspace; `run_command`
and `test_command` are how it is exercised; `provenance` says where the grader
came from — `bundled`, `generated` or `user` — and `trust` is either
`authoritative` or `advisory`.

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
  with prompts, **no `exercise` key**. The reader gets the work, marked as
  unchecked.
- **It teaches and sets no work.** `"exercises": false`, no practice documents,
  and you are finished at the reading floor.

**Do not invent assertions to fill the third case.** A grader nobody wrote,
checking an answer nobody specified, is theatre — and a corpus that refuses to
put on that show is behaving correctly, not failing.

---

## Next

- [What an adapter must produce](archive.md) — where the practice document
  goes.
- [Worked examples](examples.md) — one corpus with `exercises: true` and one
  with `false`.
