# E14 — Authored exercises

Exercises for **every** corpus: built from the source's own examples, its practice code
and its tests where it has them, and authored from the page's material where it has none
— each one a real-life ask, graded by tests of the main ask and of every edge case.

**Shared context for this epic — read this before any task.**

⛔ **The authority is [spec §7, *Exercises authored for every
corpus*](../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389),
and it should be read whole before any row here is started.** ⭐ **The argument, with the
user's words unabridged and the four answers that closed its open questions, is
[`W389`](rows/W389.md) and its [proposal](handoffs/W389.md).**

⭐ **The user's sentence this epic exists to satisfy:** *"we are building CodeSignal or
LeetCode with the idea of LLM extracting the content from a given source and make it an
enjoyable interactive easy to read and navigate website."*

## ⛔ Four properties, and every row here is judged against them

1. ⛔ **Nothing the source already has is lost.** The reading floor is untouched and every
   example still renders verbatim. The **source ledger** is the proof: every fenced example
   and every test file is either the basis of an exercise or carried with a written reason
   it is not, and an entry with neither is refused.
2. ⛔ **Authoring happens ONCE, at ingestion**, by a skill the converting agent runs, into
   the **corpus repository**. ⛔ **No model runs at build time and none at serve time.** The
   site stays offline (R8) and the build stays byte-reproducible from the committed
   bundles (R10).
3. ⛔ **R5's honesty survives as GATES, not as a promise.** An authored grader is
   `generated`, therefore `advisory`, and ships only with a gate record `studyforge
   validate` re-reads. ⛔ **No gate may be disabled by configuration, and a shortfall is
   reported rather than engineered away.**
4. ⛔ **The framework still knows nothing about any source** (R1). Every source-specific
   fact arrives as data — the bundle on disk, the manifest, the ledger — and the adapter
   seam stays where R2 put it.

## ⭐ What the user ruled, 2026-09-19, and what it changed

| the question | the answer | what it binds here |
|---|---|---|
| a corpus whose subject is not code | ⭐ **the quiz shape is IN this milestone** | `AX-05`, `AX-06`, and `AX-09`'s second surface |
| is the reference solution shown | ⭐ **always available to the reader** | `AX-04` ships it; `AX-09` offers it, never gated on a pass |
| is an authored grader labelled | ⭐ **yes, worded for a learner** | `AX-09`; R5's vocabulary stays internal |
| the three-page ISO pilot | ⭐ **the user reviews it once**, then the rest run on the gates | step 10.4, and `AX-11`'s reading |

## ⚠️ What is NOT in this epic, and where it is instead

- ⛔ **The spec amendment is LANDED, not a task.** It went in with `W389`'s second stage,
  at §1's table note, C5, R5, §7's new subsection, §7's two-gates scoping, §11.0, §11.2 #14
  and §12. ⚠️ **A row that re-proposes it is re-deriving a settled thing.**
- ⛔ **The runner's per-corpus warm cache is [`W390`](rows/W390.md), a board row already in
  flight — cite it, never re-derive it.** Every ISO page leans on jPOS, so an exercise
  faithful to the page needs a third-party artifact resolved under `--network none`; that
  is `W390`'s, and this epic depends on its outcome rather than restating it.
- ⛔ **Nothing here re-opens the derivation gates of [`E08`](E08-java-exercises.md).** A
  `bundled` exercise keeps its mechanism and its `authoritative` label unchanged.

---

### AX-00 — Cases, kinds and origin in the exercise record
**Milestone** **M10** · **Depends on** SF-23 · **Team** solo
**Owns** `exercise/cases.py`, and the record's reading of the three new keys
**Context** ~30k — `exercise/`, spec §7, `W357`'s argument in [`E06`](E06-exercise-contract.md)

**Definition.** The contract half of everything below: a graded exercise record may carry
`cases` — an `id` as its test report spells it, a `kind` of `main` or `edge`, and `says`,
the one sentence a reader is shown — plus the `report` (its format and its path) and the
`origin` of the material it was built from. The record also gains the exercise's own
`kind`: `code`, which is today's shape and the default, or `quiz` (`AX-05`).

⛔ **A new module, not a wider one.** `exercise/record.py` is already near R11's bound, and
the remedy for that is a split at a named seam, never a trim: this module owns the case
vocabulary and the record keeps the document.

⛔ **Structural, with no flag and no version bump**, following `W357`: every older document
stays valid and an older build refuses the new keys. ⭐ **Read `W357`'s handoff first** —
this is the same shape and the same test.

**Acceptance.** `cases`, `report`, `origin` and `kind` round-trip. A case map on an
**ungraded** record is refused, naming the key. An unknown case `kind` is refused; an
unknown exercise `kind` is refused. A record written before this task still reads
unchanged, and a document carrying the new keys is refused by the previous reader. ⛔ Not a
`raw_api` change, asserted by `W357`'s own instrument.

---

### AX-01 — The case report
**Milestone** **M10** · **Depends on** AX-00 · **Team** solo
**Owns** `exercise/report.py`
**Context** ~20k — AX-00 output, spec §7

**Definition.** Folding a test run's machine-readable report through the record's `cases`
into *main ask* plus *edge cases n/m*, naming each failed edge case by its `says`.

⭐ **The channel is JUnit XML**, and that was chosen rather than console text: Maven's
surefire writes it with no configuration, pytest writes it on one flag, and the standard
library reads it. ⛔ **Console output is not a channel** — the quiet run modes rewrite that
stream by design, so parsing it would make the breakdown depend on a display decision.

**Acceptance.** A report folds to *main* plus *edge n/m*. A test the case map does not
name is refused rather than counted. A **stale** report — older than the run that should
have written it — is refused and never read. A malformed report is a named failure, not an
empty breakdown. A run that wrote no report yields no breakdown and no error.

---

### AX-02 — Submit records the breakdown
**Milestone** **M10** · **Depends on** AX-01, SF-22 · **Team** pair
**Owns** `last.cases` in `progress/document.py`, and the recording in `serve/routes/runs.py`
**Context** ~35k — AX-01 output, SF-22's verdict path, `progress/`

**Definition.** A Submit's verdict is an exit code and nothing else today, so *edge cases
n/m* has nowhere to live. This records the breakdown beside the verdict it came from.

⛔ **The pass rule does not change, and this task may not touch it.** `is_pass` stays what
it is — a test-mode run that exited zero — so a practice still completes only when every
case passes. ⭐ **The breakdown is a REPORT, never a second definition of a pass**, and a
reader who sees *edge cases 2/3* sees an incomplete practice.

**Acceptance.** A test run carries its breakdown into the progress document. `is_pass` is
unchanged and its existing test is untouched — asserted, not asserted about. A run with no
report records no breakdown. A progress document written before this task reads unchanged.

---

### AX-03 — The authoring gates and the gate record
**Milestone** **M10** · **Depends on** AX-00, AX-01, TC-00 · **Team** pair
**Owns** `exercise/gates/` — G1–G5 and the gate record
**Context** ~40k — spec §7's gate table, [`E08`](E08-java-exercises.md)'s shared context

**Definition.** The five gates a code exercise clears before it ships, run in the pinned
runner image, plus the record that carries their outcome: the digest of every input —
statement, starter, reference, tests, each planted solution — and each gate's verdict.

⭐ **`E08`'s per-method argument is the model, and G3 is the same argument per edge case.**
A gate coarser than the claim it backs is theatre; that was measured once and is not being
re-learned here.

**Acceptance.** Each gate refuses its planted defect, one plant per gate: a vacuous test
(G2), a flaky test (G1's second run), an edge test the ignoring solution passes (G3), a
test the map does not name (G4), an origin whose digest drifted (G5). ⛔ **No gate can be
disabled, skipped or weakened by configuration** — asserted by trying. A bundle clearing
every gate produces a record whose digests match the files beside it.

---

### AX-04 — The exercise bundle
**Milestone** **M10** · **Depends on** AX-00, AX-03, SF-25 · **Team** pair
**Owns** `exercise/bundle/` — the on-disk shape, the emission an adapter calls, and
`validate`'s gate-record arm
**Context** ~35k — spec §7, R2, R3, SF-25's refusal vocabulary

**Definition.** What an authored exercise **is** on disk inside a corpus repository, and
how it becomes `practice-M.json`. The bundle carries the statement, the starter, the
reference solution, the tests, the plants, the `cases` and the gate record. The adapter
reads it and emits; the framework never authors and never reaches into a corpus.

⭐ **The reference solution is reader-facing material in the bundle** (the user's ruling):
it is shipped, and `AX-09` offers it at any time. ⛔ **Withholding it would be a pretence**
— the bundle is already on the reader's disk.

**Acceptance.** An adapter emits a valid `practice-M.json` from a bundle with no
corpus-specific code in the framework (R1). A bundle whose digests no longer match is
refused by `studyforge validate`, naming the file. A `generated` exercise with no gate
record is refused. Several exercises on one page take ordinals `1..n` with no gap. ⛔ An
emission writes no existing file in the source repository (R3).

---

### AX-05 — The quiz shape
**Milestone** **M10** · **Depends on** AX-00, FND-04 · **Team** pair
**Owns** `exercise/quiz/` — the question record, the key, and the grading rule
**Context** ~35k — spec §7 § *A corpus whose subject is not code*, `FND-04`'s `depth1/`

**Definition.** A checkable practice for material that admits no coding task. A quiz is an
exercise whose `kind` is `quiz`: in place of a workspace it carries **questions** — a stem,
an ordered set of options, exactly one keyed correct, one sentence per option saying why it
is right or wrong, and an `origin` naming the passage it came from.

⛔ **SUPERSEDED 2026-09-23 by the user's ruling below (`W451`) — kept readable, and not in
force where it puts the key in the page or grades there:**

> ⛔ **It is graded with no compiler, no container, no network and no model.** The key and the
> sentences ship inside the practice document and the grading rule is the framework's, so the
> reading is identical over `file://` and over a served origin (R8).
>
> ⚠️ **The key is in the material and the site does not pretend otherwise.** An offline page
> cannot hide the answer it grades with, exactly as an offline workspace cannot hide its test
> file, and claiming to hide either is the theatre R5 exists to prevent.

⛔ **AMENDED 2026-09-23 (`W451`, USER RULING):** *"the quiz itself again should not require an
online or agent check for the answer user provided. It will be just a test with the correct
answer residing on the server side. When user answers it will get validated and result will
be returned to the user with explanation if needed"*. ⭐ **Still no compiler, no container, no
network and no model — and the grading rule is still the framework's** (`exercise.quiz`),
⛔ **but it runs on the LOCAL STUDY SERVER, never in the page.** No built page and no asset a
page loads carries the key or a per-option sentence; a `serve` route reads the key from the
unit's generated document and answers right or wrong with the chosen option's sentence.
⭐ Over `file://` the quiz shows its questions and says checking needs the study server, as
Run and Submit do. [Spec §7 §7](../specs/2026-09-08-studyforge-v1-design.md) carries the
amendment whole.

⛔ **A quiz completes only when every question is answered correctly**, and that completion
is recorded through the reader's own state — ⛔ **never through a run verdict.** A quiz
produces no run, and `is_pass`'s rule for a run is untouched by this task.

⭐ **Proved on the prose fixture**, `FND-04`'s `depth1/` — the 1-level, zero-exercise shape
— because that is the corpus this shape exists for.

**Acceptance.** A quiz record round-trips and grades: all-correct completes, one wrong does
not. A question with no keyed option is refused; one with two is refused; options identical
after normalisation are refused; an option with no sentence is refused. Grading is
byte-identical over `file://` and over a served origin. A quiz record is refused
`trust: "authoritative"` (R5). A corpus with no quiz is unaffected.
⛔ **AMENDED 2026-09-23 (`W451`):** *"Grading is byte-identical over `file://` and over a
served origin"* is SUPERSEDED — grading happens only over a served origin, and over
`file://` the quiz says so. ⭐ The rest of this Acceptance stands.

---

### AX-06 — The quiz authoring gates
**Milestone** **M10** · **Depends on** AX-03, AX-05 · **Team** pair
**Owns** `exercise/gates/quiz/` — Q1–Q5 and their half of the gate record
**Context** ~35k — spec §7's quiz gate table, AX-03's record

**Definition.** The five gates a quiz clears, and — as much as the design — the honest
statement of how they differ from the code gates. ⛔ **Q1–Q3 are model judgements taken
ONCE at authoring and shipped as a record; Q4 and Q5 are mechanical and `validate` re-runs
them.** ⭐ **So a quiz grader is `generated`/`advisory` always, and this task must close
every path by which one could become `authoritative`.**

⭐ **In-step edge on `AX-03`, declared:** this owns a sub-package inside the gates package
`AX-03` creates, and shares its gate record rather than opening a second one.

**Acceptance.** Q4 and Q5 refuse their planted defects mechanically: two keyed options, a
duplicate option, a missing sentence, an `origin` whose digest drifted. Q1–Q3 are recorded
with the prompt, the pass and the outcome, and a question whose Q1–Q3 record is absent or
whose recorded inputs no longer match is refused at `validate`. ⛔ **No gate is
configurable off.** A quiz that cleared every gate is `generated`/`advisory`, and asserting
`authoritative` anywhere in the chain fails.

⛔ **AMENDED 2026-09-23 (`W451`, user ruling — the key resides on the server):** ⭐ **Q1–Q5 and
the gate record are UNCHANGED**, and so is the bundle's quiz record. ⚠️ What moved is only
where a reader MEETS what they guarantee: Q4's *"every option carries its one sentence"*
now reaches the reader in the server's verdict, for the option they chose, and never in the
page.

---

### AX-07 — The source ledger and the page plan
**Milestone** **M10** · **Depends on** AX-04, SF-36 · **Team** pair
**Owns** `skills/exercises/ledger.py`, `skills/exercises/plan.py`
**Context** ~30k — spec §7 §§ 3–4, SF-36's sub-file origins

**Definition.** The two readings the authoring skill is built on. The **ledger** accounts
for every fenced example and every test file a source carries: each is the basis of at
least one exercise, named by that exercise's `origin`, or carried with a written reason it
is not. The **plan** says how many exercises a page gets before any are written — a count
inside a band set by the page's length, moved by its distinct checkable skills and a
difficulty tier, with every reason recorded.

⛔ **The plan is a CEILING, never a quota** (R6): what ships is what clears the gates, and
every shortfall is named with the gate that refused it.

**Acceptance.** Every fenced example and test file in a fixture corpus appears in the
ledger. An entry with no exercise and no reason is refused. A plan's count stays inside its
page's band, and each reason that moved it is recorded. A page whose plan is zero says why.
Re-running on an unchanged corpus produces a byte-identical ledger and plan (R10).

---

### AX-08 — The authoring skill
**Milestone** **M10** · **Depends on** AX-03, AX-04, AX-06, AX-07 · **Team** team
**Owns** `skills/exercises/` — its skill document and the authoring loop
**Context** ~40k — spec §7 and §9, `AX-03`–`AX-07` outputs, [`E11`](E11-skills-authoring.md)

**Definition.** The product half of this epic (R19): the skill a converting agent runs once,
at ingestion, which plans a page, authors its exercises from the three source cases, runs
the gates, and commits the bundles into the corpus repository.

⛔ **§9 binds it**: this skill lands before the artifact it produces, so it precedes any
corpus's authored exercises rather than being written up from one.

⛔ **A gate failure is re-authored within a fixed attempt budget and NEVER by loosening a
gate, dropping a case or deleting a question.** When the budget runs out the coverage report
names the page, the exercise, the gate, the case and the run's last output.

**Acceptance.** The three source cases each run on a fixture — code with tests, code
without, neither — and the quiz case runs on the prose fixture. A planted gate failure is
re-authored inside the budget; a plant that cannot clear exhausts the budget and is reported
rather than shipped. Re-running with nothing changed rewrites nothing (R10). ⛔ **The skill
writes only inside the corpus repository and only additively** (R3). ⛔ It supersedes
[`SK-04`](E11-skills-authoring.md#sk-04-exercise-derivation)'s refusal of a grader-less
source, and that is asserted by running it on one.

---

### AX-09 — The practice panel: the breakdown, the reference and the label
**Milestone** **M10** · **Depends on** SF-24, AX-02, AX-05 · **Team** pair
**Owns** `SF-24`'s surface — `render/page/practice.py`, `render/assets/practice.{js,css}`
**Context** ~40k — SF-24 output, spec §7 §§ 8–9, [`E06`](E06-exercise-contract.md)

**Definition.** What the reader sees. Three things land together because they are one
screen: the Submit breakdown (*main ask ✓*, *edge cases n/m*, each failed case named by its
`says`), the reference solution, and the label.

- ⭐ **The reference solution is ALWAYS available** (the user's ruling) — offered at any
  time, before a first Submit included. ⛔ **Never revealed automatically**, and asking is
  never recorded as a failure.
- ⭐ **The label is a sentence in a learner's words**, fixed by [spec
  §7](../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389)
  and held as the framework's own constant, never a corpus's string (R1). ⛔ **R5's
  vocabulary stays internal**: a reader never sees `provenance` or `trust`.
- ⭐ **A quiz renders in the same panel** with no editor, no Run and no Submit — ⛔ **not
  disabled ones**, which is `SF-24`'s standing rule about a dead button.

**Acceptance.** A Submit shows the breakdown, naming each failed edge case. A passing Submit
shows every case passed. The reference is reachable before any Submit and is never shown
unasked. Each of the four label cases renders its stated sentence and no token of R5's
vocabulary appears in the page. A quiz page shows questions, grades them, and shows no run
affordance. ⛔ **Fully keyboard accessible**, and the breakdown is announced to a screen
reader rather than only coloured.

---

### AX-10 — The authoring guide catches up
**Milestone** **M10** · **Depends on** AX-08 · **Team** solo
**Owns** [`docs/authoring/exercises.md`](../authoring/exercises.md) — `SK-05`'s surface
**Context** ~25k — AX-08 output, spec §7

**Definition.** The document somebody converting their own material reads. It gains the
three source cases, the quiz shape, the gates, the ledger and the plan, and it loses the
stance that a source without graders should write no assertions.

⛔ **`SK-05`'s standing rule binds: every claim in it is true of the shipped code, checked
rather than assumed.** ⚠️ **The guide is under `tests/test_authoring_reference.py`, which is
already near its bound** — a claim added here is a claim that instrument must be able to
read.

**Acceptance.** The three cases and the quiz shape are each written up with a worked
example. *"Do not invent assertions"* is replaced by *author, then prove*, with the gates
named. Somebody following the guide authors exercises for a small new source without
reading the spec. Every claim is checked against the code.

---

### AX-11 — `M10`'s acceptance, read on ISO and on the prose fixture
**Milestone** **M10** · **Depends on** AX-09, AX-10 · **Team** solo
**Owns** nothing — this row produces evidence
**Context** ~40k — the ISO corpus's generated site, the coverage report, spec §11

**Definition.** The reading that closes the milestone, taken and written down rather than
asserted. ⛔ **It owns no code**: a row that could edit what it measures measures nothing.

**Read on ISO.** Every page has a plan, and ships its planned exercises or is named with the
gate that refused each one. Every shipped exercise's gate record verifies against the files
beside it. On a planted partial solution, Submit shows *main ask ✓* with the edge cases it
missed named. The ledger accounts for every Java fence in the corpus. ⛔ **The reading floor
is byte-unchanged over `file://`** — the whole point of *nothing is lost*.

**Read on the prose fixture.** A quiz practice completes on all-correct answers and not
otherwise, offline, with no container started.

**Acceptance.** Each condition above is recorded with the ref it was taken at and the
environment it was taken in, or it is not a reading. ⛔ **A shortfall is reported, never
closed by an edit from this row** — it becomes a finding against the row that owns it.
