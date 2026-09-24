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

## The procedure

### 1. Read each page, and write down what you read

For each page you want exercises for, build one `Page`. It gives the material
file, the unit it becomes (address, variant, unit number), its kind (`code` or
`quiz`), the test files the corpus declares for it, its `aspects` and a `tier`
(`introductory`, `core` or `advanced`).

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
  `QuizDraft`. The brief carries the page, its case, its ledger entries,
  which of the planned exercises this is, the aspects it must check, where
  its bundle and its workspace will be, and, on a retry, the previous draft, every gate that refused it
  and the last run's output.
- **`author.excuse(entry)`** writes the one sentence saying why no exercise
  was built from a ledger entry. It is asked only about entries nothing
  shipped accounts for.
- **`judge(brief, questions)`** returns the `Q1`–`Q3` judgements for a quiz.
  One `Q1` and one `Q2` per question, one `Q3` per wrong option, each taken
  over `question_digest(question)`.
- **`runner(root, command)`** runs one test command from `root` in the pinned
  runner image and returns a `Ran`: its exit code and its output. The gate
  suite stages every run in a fresh directory, so nothing a run leaves behind
  reaches the next one.

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

### 3. Run the pass

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
last run's output.

⛔ **Never by loosening a gate, dropping a case or deleting a question.** No
gate takes an option. A retry that drops a case id or a question id the
previous draft carried is refused outright, and the pass stops. It is not
shipped and not re-tried.

⭐ **When the budget runs out, the exercise does not ship.** The unit's
coverage report names the page, which planned exercise it was, the gate, the
gate's own sentence (which names each failing case by what the reader would
read), and the last run's output, made relative to the run and scrubbed (R7).

## Where it writes, and what it never touches

| path | what it holds |
|---|---|
| `exercises/<address>/<variant>/unit-NN/practice-M/` | one bundle, in `exercise.bundle`'s shape, with `gates.json` beside it |
| `…/practice-M/tests/quiz.json` | a quiz's own document: its identity and its record |
| `practice/<address>/<variant>/unit-NN/practice-M/` | the reader's starter and tests, from `emit` |
| `exercises/<address>/<variant>/unit-NN/coverage.json` | the unit's plan (every aspect and how it ended), what shipped, and every shortfall |
| `exercises/ledger.json` | the source ledger, every entry accounted for |

⛔ **`M` follows the practices the unit already carries**. A unit
whose archive holds `practice-1` from the source gets its first authored
exercise at `practice-2`. The pass reads what the unit carries from its
archive, so you declare no offset. The source's practice is never renumbered
or rewritten, and an authored exercise that would repeat or skip past one is
refused by the practice's name before anything is written.

⛔ **Only inside the corpus root, and only additively** (R3). A file that is
already there with the same bytes is left alone. A file that is there with
different bytes stops the whole pass, **before anything is written**, and the
refusal names it.

⭐ **Re-running with nothing changed rewrites nothing** (R10). A unit whose
recorded coverage matches its page's digests and its plan is not re-authored,
so the author, the judge and the runner are never called for it. A ledger
entry keeps the reason it was given while its bytes are unchanged.

⚠️ **A page whose source changed is refused, naming its unit's directory.**
Its bundles were proven against material that has moved, and rewriting them
is exactly what R3 forbids. Remove that directory from the corpus, and run
the pass again. ⛔ **Never remove `exercises/ledger.json`** to get past a
refusal: it holds every other page's rows.

⭐ **A pass over part of a corpus owns only the files it read**. The
ledger is one file for the whole corpus, and it is the one file a pass
rewrites: the rows of the files handed in as `material` and `graders` are
replaced, and every other row is kept byte for byte, so containers can be
passed one at a time in any order. A row leaves only when its file is gone.
`authored.ledger` reports every row as `kept`, `added`, `changed` or
`dropped`; read it after every pass, and treat a `dropped` row whose page you
did not delete as a defect. `studyforge validate` refuses a ledger that no
longer accounts for a page the corpus carries (`ledger-unaccounted`).

## What this skill does not do

- ⛔ **It writes no practice document.** The adapter emits `practice-M.json`
  from each bundle (R2). `emit` is called here only to stage the gate runs.
- ⛔ **It runs no container itself.** The runner is yours, and it runs in
  the pinned runner image.
- ⛔ **It never lowers a bar to meet a count.** The plan is a ceiling (R6).
  A page that ships fewer than planned is named with the gate that refused
  each missing exercise.
