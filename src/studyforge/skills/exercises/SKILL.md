# Skill — authoring exercises

**Give every page of a corpus the exercises its material supports, once, at
ingestion, and commit them into the corpus repository as bundles an adapter
emits.** You plan each page, author its exercises from what the source has,
run the gates over every one, and ship what clears them. A shortfall is
reported, never engineered away.

⛔ **This skill is where the only non-determinism in the whole pipeline lives.**
You author each exercise once, the gates prove it, and the result is fixed in
the corpus tree. ⛔ **No model runs at build time and none at serve time** (spec
§7 §2): the site stays offline (R8) and the build stays byte-reproducible from
the committed bundles (R10).

⭐ **It supersedes the earlier refusal of a grader-less source.** A source that
ships no test gets exercises authored for it. The honesty that refusal
protected is kept by the gates: an authored grader is `generated`/`advisory`
and ships only with the gate record that says it cleared.

---

## Before you start

1. **The corpus is onboarded.** `corpus.json` exists and `studyforge validate`
   is clean.
2. ⛔ **The manifest classifies the two trees this skill fills.** `exercises/**`
   and `practice/**` are declared under `content.not_material` (which needs
   `corpus_api` 2 or later). Without those lines `studyforge validate` refuses
   every file in both trees before any exercise check runs. This
   skill does not edit `corpus.json`: an existing file is never rewritten (R3).
3. ⛔ **The corpus ignores a run's report.** A JUnit report carries the
   machine's hostname (R7), and it lands in the reader's workspace, so the
   corpus's ignore rules keep it out of every commit. ⭐ Every
   run's output lands in `target/` inside the workspace
   (`exercise.bundle.RUN_OUTPUT_DIRNAME`), and a bundle's report path is
   refused anywhere else, so the rule is the one line `target/`
   (`RUN_OUTPUT_IGNORE`), written once in an ignore file of the corpus's own
   under `practice/`.
4. **The pinned runner image**, for the gate runs. The gates are only as
   reproducible as the toolchain they ran in (R15).

## The three source cases, and the quiz

⭐ **One pass, one set of gates per kind, one bundle shape, one coverage
report.** The case is not chosen. It is read off the ledger for each page:

| the page carries | the case | what you author |
|---|---|---|
| a declared test file | `code-and-tests` | the ask and the edge cases, the source's tests as the basis |
| a fenced example, no test file | `code-no-tests` | the ask, the starter and the tests. The example is the reference |
| neither | `neither` | all of it, from the page's prose |

⛔ **Every exercise this skill writes is `generated`/`advisory`, in every
case.** The provenance is filled in by the skill and a draft cannot name one.
A `bundled`/`authoritative` exercise comes from the blanking derivation over the
source's own exercise, unchanged, and this skill never assigns that label.

⭐ **A page whose subject is not code gets a quiz** (spec §7 §7). You declare
the page's kind as `quiz`, and you author questions from its passages. An
**independent pass** takes the `Q1`–`Q3` judgements over each question. Its
judge is a separate function, never the author grading its own work.

⭐ **A code page may carry one quiz as well.** A lesson with code usually also
teaches ideas no test can observe: a compile-time rule, how an expression is
parsed, a claim about timing. Give those aspects one exercise name, and name it
on the page as `quiz`. That exercise is drafted as a `QuizDraft`
(`brief.kind` is `quiz`), after the page's code exercises, so it takes the
unit's last ordinal. ⛔ Only a `code` page names a quiz, and the name must be
one its aspects give. Do not reason such an idea away with *"the framework
gives a unit one kind of exercise"*: it no longer does.

## The procedure

### 1. Read each page, and write down what you read

For each page you want exercises for, build one `Page`. It gives the material
file, the unit it becomes (address, variant, unit number), its kind (`code` or
`quiz`), the test files the corpus declares for it, its `aspects`, a `tier`
(`introductory`, `core` or `advanced`) and, on a `code` page, the `quiz` it
carries, if any.

#### ⛔ Plan by the page's important ideas

A page may get no practice, one, or several: the target is every important
aspect covered well, not a minimum, and not a university grading knowledge. One
practice often covers more than several unrelated small ones.

⭐ **Read the page, its prose AND its code, and name its aspects.** An `Aspect`
is one important idea a reader could be checked on: an `id`, one sentence
(`says`), what you read it from (`basis`: `example:<path>:<n>` or
`tests:<path>` for the page's own code, `section:<heading>` for its prose), and
exactly one ending — the `exercise` that checks it, or the `reason` nothing
does. The plan is one exercise per distinct `exercise` name.

⭐ **Exercises ship in the order you give them.** Set `Page.order` to every
planned exercise name, each once, in teaching order: the first gets the unit's
next free ordinal. Without it the plan keeps name order. ⛔ Never prefix names
(`p01-…`) to steer the order, and an `order` that misses or repeats a name is
refused.

- **Important ideas, not facts.** A date, a name or an incidental number is
  not an aspect. The idea it illustrates may be; a version the page depends on
  may be.
- **One exercise can check several aspects, and often should.** One exercise
  practising related ideas together beats several small unrelated ones.
- **A minor aspect gets a short reason** (*"incidental detail, not
  practised"*), not an exercise.
- **A quiz asks few questions**: one or two for a short conceptual page, each
  about something that matters.
- ⛔ **No ceiling, and no quota.** Record what you judged important and why.
  It is not a coverage percentage to maximise.

⛔ **The plan refuses** an aspect with neither ending or with both, two aspects
with one id or one sentence (merge them: two exercises never check one idea),
and a basis the page does not carry. ⭐ **Zero is legitimate**: every aspect
reasoned plans zero, and a page teaching nothing checkable names no aspect
and says why in `nothing_checkable`. ⚠️ `tier` says how hard each exercise is,
never how many.

⛔ **The two populations are the corpus's to declare** (R1). What is
material comes from the manifest's `content` policy, and what is a grader
comes from the corpus's own declaration. The framework never guesses a
test-file pattern.

### 2. Write the author, the judge and the runner

- **`author.draft(brief)`** answers one `Brief` with a `CodeDraft` or a
  `QuizDraft`, whichever `brief.kind` names. The brief carries the page, its case, its ledger entries,
  which of the planned exercises this is, the aspects it must check, where
  its bundle and its workspace will be, and, on a retry, the previous draft, every gate that refused it
  and the last run's output.
- **`author.excuse(entry)`** writes the one sentence saying why no exercise
  was built from a ledger entry. It is asked only about entries nothing
  shipped accounts for.
- **`judge(brief, questions)`** returns the `Q1`–`Q3` judgements for a quiz.
  One `Q1` and one `Q2` per question, one `Q3` per wrong option, each taken
  over `question_digest(question)`. ⭐ **`Q2` looks for a giveaway**: its
  reader gets the stem and options, never the page, and is asked `Q2_PROMPT`
  word for word, to answer from the wording alone and say *none* unless it
  singles out an option. Build that judgement with `page_free(question,
  picked, because, taken_by)`, which decides `held`. `picked` is an option's
  id, or `PICKED_NONE` (`None`); the reader's own word `"none"`, in any case,
  is read as `PICKED_NONE` too. ⛔ A `Q2` judgement under another prompt or
  with no `because` is refused.
- **`runner(root, command)`** runs one test command from `root` in the pinned
  runner image and returns a `Ran`: its exit code and its output. The gate
  suite stages every run in a fresh directory, so nothing a run leaves behind
  reaches the next one. ⛔ **`root` is under the host's temporary directory:
  never bind it.** Copy it into the container (`docker cp` into a container
  you created, or a tar stream on `docker run -i`'s stdin) and read the output
  back the same way. Docker Desktop shares no host `/tmp` and Windows has none,
  and the runner must work on both.

#### ⛔ Write a draft the gates can prove

- **A practice has exactly one main file.** `CodeDraft.main_file` is the one
  file the starter, the reference and every plant replace. A hierarchy is
  nested in it as static member types of one class, and a sealed type's
  implicit `permits` come only from that file.

  ```java
  public class Shapes {
      sealed interface Shape permits Circle, Square {}
      record Circle(double r) implements Shape {}
      record Square(double side) implements Shape {}
  }
  ```

- **`G2`: every case fails on the starter**, structural and reflective cases
  included. A constructor check, a `sealed` check or a reflection check must
  fail there too: leave the starter's hierarchy unsealed, and reach what a
  record generates for free through a starter method that is not written
  yet. ⚠️ A starter that throws the exception an edge expects passes that
  edge, and `G2` refuses the draft. Throw one no test expects, for example
  `IllegalStateException` where an edge expects
  `UnsupportedOperationException`.
- **`G3`: every plant passes EVERY main case** and fails its own edge. A main
  case must therefore give the same answer on every run: a threaded main case
  must not race. ⛔ A rule the compiler enforces (constructor order, a static
  call bound to its declared type, a diamond default) has no wrong solution
  that compiles. It goes to the quiz, or to a reason.
- **The idea a practice names is graded.** For each idea the statement
  presents as the point, one edge's plant breaks exactly that idea, as the
  subtle mistake a reader makes and never by deleting the code. Before you
  draft, list each named idea beside its one-line wrong solution. An idea
  no deterministic test can grade goes to the quiz or to a reason, and the
  statement does not present it as a graded requirement.
- ⭐ **Some wrong solutions pass tests that look complete.** Before you draft a
  practice about equality, copying, immutability, time, text, numbers or
  threads, read *What the gates cannot see* in `docs/authoring/exercises.md`.
- ⭐ **A Python or TypeScript practice has silent passes of its own**, listed in *Python and
  TypeScript silent passes* on that page: a test that asserts nothing, truthiness
  (`assert x`, `assert.ok(x)`), a tuple asserted, `is` against `==`, a mutable default
  argument, a missing `await` on `assert.rejects` (Node reports it against the file), loose
  `==` from `node:assert`, an `any` that hides a type error from `tsc`, an `enum` or a
  parameter property that type stripping refuses, and a stub that returns without asserting.
  Set `assertions_only` on such a draft, so `G2` and `G3` refuse a starter or plant that fails
  on anything but an assertion, and write the adversary's wrong solutions from that list.
- ⭐ **A mock exam is a quiz with a `mock` key.** Tag every question with exactly one declared
  domain (`P1` holds when every domain has a question and every question a declared domain),
  and take `Q1` to `Q3` for each question from a reader who did not write it; a reworded
  question needs fresh readings. See *A mock exam* on that page.
- ⛔ **A live-capable example holds no key and no captured secret.** It reads the variable the
  manifest names from its environment, prints neither the environment nor a header, writes the
  key nowhere and reaches the one declared host; its graded test needs no key and no network.
  See *`live`* in `docs/authoring/corpus.md`.

⭐ **Commands are spelled from the corpus root**, and every path argument is
inside the exercise's own workspace (`brief.places.workspace`), or `emit`
refuses the bundle.

⭐ **An exercise whose tests import a library ships its build role**:
`CodeDraft.build` maps each build file's workspace-relative path to its text —
a `pom.xml` naming the library, say — and the command names it inside the
workspace (`-f <workspace>/pom.xml`). Every gate run stages it beside the
tests, and the gate record digests it. ⛔ The library itself is never a file
you write: the pinned runner image carries it, primed from the corpus's own
build (`skills.execution`, step 4a), so a build naming something the prime did
not warm fails `G1` and does not ship.

#### ⛔ Write it once

⭐ **A plant is a few lines away from the reference, so write it as the few
lines.** Give `CodeDraft.plants` a `PlantSpec` for each edge: an ordered list
of `Replacement(file, old, new)`, each `old` occurring exactly once in the
text it is applied to. The gate materialises the full plant from the reference
into its own staging directory, and the bundle stores the spec alone, so
fixing the reference reaches every plant at the next gate run instead of
leaving ten copies to drift. A plant that comes out identical to the
reference, or a replacement whose text is gone or ambiguous, is refused by
position, never silently skipped. A full-text plant is still accepted, for the
plant whose change is most of its file.

- ⛔ **Never hand-copy a file to vary it.** A plant, a second starter, a
  variant of a test: derive it from the file it varies, by a replacement or by
  one function, so the original is the only place it is edited.
- ⭐ **One shared generator or tool per course, never a copy per batch.** A
  script that builds a course's practices, runs its checks or writes its
  examples lives in one place and takes the batch as its argument. A second
  copy for the next batch is a second place to fix, and the two stop agreeing.
- ⭐ **Share test helpers where the runner allows.** A fixture, a runner
  shim or a report reader several practices need belongs in one module the
  tests import. ⛔ **Each learner workspace still stays self-contained and
  readable**: a file a learner opens does not inherit from, import from or
  point to a file they must go and find to understand it, and what the
  workspace needs must be there when it is copied out alone.
- ⚠️ **Keep the duplication that is the material**, and only that:
  a learner's own file (the starter and the tests they edit stay whole, with
  nothing to chase); a page's visible example (what the page shows is what a
  reader sees, shown whole, and it is not reduced to a reference to
  somewhere else); and a language's idiomatic version (the Java and the
  Kotlin of one idea are two solutions, each as that language would write it,
  and not one generated from the other). Remove a copy only when nothing a
  learner reads is harmed by its going.

`studyforge.exercise.bundle.convert` turns a course's existing full plants into
specs once: it proves each by materialising it again and reading the bytes
back, and leaves any plant it cannot prove. See *A plant as replacements* in
`docs/authoring/exercises.md`.

### 3. Run the pass

⭐ **Before the pass, take the two readings it cannot take for you:**

1. **An adversary.** A reader other than the author writes subtle wrong
   solutions for each practice, starting from the silent passes that
   *What the gates cannot see* names. Fix every survivor that breaks its
   statement: add the test that catches it, or correct the reference if the
   reference is what breaks the statement. ⚠️ The gates prove only the plants
   the author thought of. On one course, an adversary found 140 survivors in
   101 practices that had all cleared `G1`–`G5`.
2. **The quiz readings.** Take each quiz's `Q1`–`Q3` readings from
   independent readers first, and have the judge return them. ⛔ A quiz gated
   before its readings exist fails `Q1` and `Q2` on every attempt and uses up
   `ATTEMPTS`. It then ships as a shortfall, and its page's examples are left
   with no exercise and no excuse.

```python
from studyforge.skills.exercises import author_corpus

authored = author_corpus(
    root,
    source="demo",
    material=material,
    graders=graders,
    pages=pages,
    author=author,
    judge=judge,
    runner=runner,
)
authored.shortfalls  # every exercise the gates refused, named
authored.bare  # every page left with nothing shipped (R6)
```

⭐ **In order, and the order is the contract** (the skill's composition):

1. `take` reads the ledger **once**, before any exercise is gated, because
   `G5` and `Q5` ask it about each exercise's origin *during* the gate run.
2. For each page, `plan_page` reads the plan off its aspects and sets the
   ceiling. Each planned exercise is drafted, gated, and re-drafted after a
   refusal, within the attempt budget.
3. `shortfall` checks that what shipped plus what was refused equals the plan.
4. Every ledger entry nothing shipped accounts for gets a written reason, and
   `account` refuses an entry with neither.
5. The accounted ledger is merged into the committed one: rows for files this
   pass did not read are kept.
6. Every file is checked against the tree **before any is written**, then the
   bundles, the reader's workspace files and each unit's coverage report are
   created, and the merged ledger is written.

## ⛔ When a gate refuses

⭐ **The exercise is re-authored within `ATTEMPTS`, a fixed budget no caller
can widen.** The brief for the retry carries every refusing verdict and the
last run's output. ⭐ A refused `Q2` quotes the cue its reader named (the
longest option, a word repeated from the stem), so re-author the wording it
names rather than re-sending the draft.

⛔ **Never by loosening a gate, dropping a case or deleting a question.** No
gate takes an option. A retry that drops a case id or a question id the
previous draft carried is refused outright, and the pass stops. It is not
shipped and not re-tried.

⭐ **When the budget runs out, the exercise does not ship.** The unit's
coverage report names the page, which planned exercise it was, the gate, the
gate's own sentence (which names each failing case by what the reader would
read), and the last run's output, made relative to the run and scrubbed (R7).

⛔ **A draft carrying personal data is refused as that one exercise, and the
pass carries on.** Every draft passes through R7's gate: a statement, starter
or reference naming, say, a `.local` host is refused under `personal-data`
(`PERSONAL_DATA`). The retry is briefed with the refusal, and a draft that
still carries it ends as a shortfall naming `personal-data`. Use `example.org` names and
placeholders in samples.

## Where it writes, and what it never touches

| path | what it holds |
|---|---|
| `exercises/<address>/<variant>/unit-NN/practice-M/` | one bundle, in `exercise.bundle`'s shape, with `gates.json` beside it |
| `…/practice-M/tests/quiz.json` | a quiz's own document: its identity and its record |
| `practice/<address>/<variant>/unit-NN/practice-M/` | the reader's starter and tests, from `emit` |
| `exercises/<address>/<variant>/unit-NN/coverage.json` | the unit's plan (every aspect and how it ended), the quiz a code page names, what shipped, and every shortfall |
| `exercises/ledger.json` | the source ledger, every entry accounted for |

⛔ **`M` follows the practices the unit already carries**. A unit
whose archive holds `practice-1` from the source gets its first authored
exercise at `practice-2`. The pass reads what the unit carries from its
archive, so you declare no offset. ⛔ Only the source's own practices count:
one an earlier pass generated is not carried, so a unit authored again after
its bundles are removed numbers from where the source's practices end, even
while its archive still holds the old ones. The source's practice is never renumbered
or rewritten, and an authored exercise that would repeat or skip past one is
refused by the practice's name before anything is written.

⛔ **Only inside the corpus root, and only additively** (R3). A file that is
already there with the same bytes is left alone. A file that is there with
different bytes stops the whole pass, **before anything is written**, and the
refusal names it.

⛔ **A file the corpus's git would ignore stops the pass, before anything is
written.** A bundle file that `git add` leaves out is an exercise the
repository never holds. The refusal names the first ignored file. Un-ignore it
in the corpus, for example `!build/` in `exercises/.gitignore` when the course
ignores `build/`, and run the pass again.

⭐ **Re-running with nothing changed rewrites nothing** (R10). A unit whose
recorded coverage matches its page's digests and its plan is not re-authored,
so the author, the judge and the runner are never called for it. A ledger
entry keeps the reason it was given while its bytes are unchanged.

⚠️ **A page whose source changed is refused, naming its unit's directory.**
Its bundles were proven against material that has moved, and rewriting them
is exactly what R3 forbids. Remove that directory from the corpus, and run
the pass again. ⛔ **Never remove `exercises/ledger.json`** to get past a
refusal: it holds every other page's rows.

⭐ **To change one exercise that already shipped, re-author its unit.** A
fixed draft on an unchanged page is never read: the unit's coverage matches,
so the pass reuses it (R10). Remove that unit's directory from the corpus with
`git rm -r`, so the change is recorded and can be undone, then pass that page
alone: `pages=[page]`, with its own file as `material` and its test files as
`graders`. Every other unit and every other ledger row stays byte for byte.

⭐ **To prove one exercise without a pass**, gate its draft directly. It stages
every run outside the corpus and writes nothing:

```python
from studyforge.exercise.bundle import Places
from studyforge.skills.exercises import Brief, gate_code, page_entries, source_case, take

ledger = take(root, material, graders, "the ledger")
places = Places(page.address, page.variant, page.unit, 1)
case = source_case(page, ledger)
brief = Brief(page, case, 1, places, 1, page_entries(page, ledger))
gated = gate_code(draft, brief, ledger, runner, source="demo", where="one draft")
gated.clears, gated.refused, gated.output
```

`author_page` does the same for one page's whole plan, and also writes
nothing.

⭐ **Two passes at once over one corpus are safe.** Each pass takes a lock on
the corpus root to read, merge and write the ledger, so the second pass waits
and then merges onto what the first one wrote. Authoring and gate runs still
run side by side.

⭐ **A pass over part of a corpus owns only the files it read**. The
ledger is one file for the whole corpus, and it is the one file a pass
rewrites: the rows of the files handed in as `material` and `graders` are
replaced, and every other row is kept byte for byte, so containers can be
passed one at a time in any order. A row leaves only when its file is gone.
`authored.ledger` reports every row as `kept`, `added`, `changed` or
`dropped`; read it after every pass, and treat a `dropped` row whose page you
did not delete as a defect.

⭐ **A page no pass has been handed yet is pending, not a finding.** Author a
course one module at a time and `studyforge validate` stays clean between the
passes: it reports one `ledger-pending` line with the count of pending pages
by module, and the first pass that reads a page ends its pending state. ⛔ It
refuses a ledger that lost a page a pass already authored, which a coverage
report names (`ledger-unaccounted`). ⚠️ Pending is not an excuse: an `excuse`
is a reason no exercise is built, and it stays that reason.

⭐ **The ledger reads a page's fences as the archive reader does**, with one
grammar (`archive.markdown.fences`). An example is a backtick fence at up to
three spaces, or at any indent inside a list item, closed by a backtick line
at least as long and at most three spaces deeper than its opener. A `~~~` run
is not a fence, because the archive keeps none. So `example:<path>:<n>`
counts exactly the code blocks the page shows.

## What this skill does not do

- ⛔ **It writes no practice document.** The adapter's generated `emit.py`
  joins each committed bundle, code or quiz, to its unit as `practice-M.json`
  (`skills.adapter.practices`, R2). `emit` is called here only to stage the
  gate runs.
- ⛔ **It runs no container itself.** The runner is yours, and it runs in
  the pinned runner image.
- ⛔ **It never lowers a bar to meet a count.** The plan is a ceiling (R6).
  A page that ships fewer than planned is named with the gate that refused
  each missing exercise.
