# W389 — handoff

⭐ **STAGE 2** — stage 1's proposal is [its own handoff](W389.md) and is untouched here.

**Kind:** task handoff — W389

## Status

⭐ **Done — STAGE 2: the documents are landed.** Row [W389](../rows/W389.md); stage 1's
proposal is [its first handoff](W389.md) and is **not** edited here — it is a landed
record (Ruling 106). Branch `task/W389-exercises-authored-for-every-corpus`, role
`wt/dev7`. ⛔ **No framework code changed**; the one change under `tests/` is the test
mirror of a plan document this row edits, and it is declared below. Gate readings are in
the hand-back, not here.

⭐ **DECLARED SURFACE:**

| file | state |
|---|---|
| [`docs/specs/2026-09-08-studyforge-v1-design.md`](../../specs/2026-09-08-studyforge-v1-design.md) | ⭐ amended in eight places |
| [`docs/tasks/E14-authored-exercises.md`](../E14-authored-exercises.md) | ⭐ **NEW** |
| [`docs/tasks/README.md`](../README.md) | ⭐ `M10`'s steps, the epic table, the two-agent split, one dated clause |
| [`docs/capability-index.md`](../../capability-index.md) | ⭐ **REGENERATED** by the delivery skill's own step-1 command |
| [`docs/tasks/E06-exercise-contract.md`](../E06-exercise-contract.md) | ⭐ four amendments |
| [`docs/tasks/E08-java-exercises.md`](../E08-java-exercises.md) | ⭐ the header sentence scoped |
| [`docs/tasks/E10-validation-qa.md`](../E10-validation-qa.md) | ⭐ `QA-04`'s zero-is-a-pass clause dated |
| [`docs/tasks/E11-skills-authoring.md`](../E11-skills-authoring.md) | ⭐ `SK-04`'s refusal struck |
| [`docs/authoring/exercises.md`](../../authoring/exercises.md) | ⭐ the stance replaced |
| `tests/test_acceptance_clauses.py` | ⭐ `E14` added to the framework side |
| this handoff | ⭐ **NEW** |

⛔ **Not touched:** [the board](../BOARD.md), [`BOARD-ARCHIVE.md`](../BOARD-ARCHIVE.md),
`docs/tasks/rows/`, [`CLAUDE.md`](../../../CLAUDE.md) (see `W389/6`), `src/`, `tools/`,
`docker/`, every other epic. ⛔ **The ISO repository was not read and not written in this
stage**; stage 1's readings of it stand and are not re-taken.

⭐ **Author line declared:** every commit is `dev7 <dev7@example.invalid>`, passed with
`git -c`. Nothing was written to any git config, no identity was printed, no file carries
an absolute path, and nothing left this host.

## What landed

### 1. The spec amendment, in eight places

⭐ **Every one is a DATED block beside the text it supersedes; nothing was deleted**
(Ruling 106), and two clauses are struck in place with `~~` rather than removed.

| where | what it now says |
|---|---|
| §1's table note | the *Graders* column records what a source **ships**; the ISO cell is deliberately **not** rewritten, and moves only when the corpus re-onboards with `exercises: true` |
| C5 | the three states stand; a source with no grader is no longer a source with no exercises, and ungraded stays first-class |
| R5 | an **authored** grader is `generated`, therefore `advisory`; no third trust level; the reader sees a sentence, not the vocabulary |
| §7, new subsection | *Exercises authored for every corpus* — eleven numbered parts, below |
| §7's two gates | *"no assertion is authored by an LLM"* **scoped to this epic's derived exercises**, not struck |
| §11.0 | the track's gate is the **material**, not what the source packaged; the quiz shape needs no container and sits on the reading floor |
| §11.2 #14 | every page whose material admits a checkable task carries its planned exercises, or the report names the gate that refused each |
| §12, clause 2 and the round-74 amendment's clause 2 | zero is a pass only for material with no checkable task; ISO enters the track at `M10` and its two earlier finish lines are not reopened |

⭐ **The new subsection carries:** the three source cases as one pipeline; authoring once,
at ingestion, into the corpus repository, with no model at build or serve time; the source
ledger that makes *nothing is lost* checkable; the per-page plan as a ceiling; what an
exercise says; the five code gates **G1–G5**; the **quiz shape** with its five gates
**Q1–Q5**; the reference solution always available; the learner-facing label table; what is
recorded and what `validate` refuses; and what happens when a gate refuses.

### 2. The user's four answers, built to rather than recommended around

⛔ **Two of them reverse stage 1's recommendation, and the built version follows the
user, not the proposal.**

| the question | the answer | where it landed |
|---|---|---|
| a corpus whose subject is not code | ⭐ **the quiz shape is IN `M10`** (stage 1 proposed a v2 backlog) | spec §7 § 7, `AX-05`, `AX-06`, `AX-09`, step 10.1/10.2 |
| is the reference solution shown | ⭐ **always available** (stage 1 proposed gating it behind a first pass) | spec §7 § 8, `AX-04`, `AX-09` |
| is an authored grader labelled | ⭐ **yes, in a learner's words** | spec §7 § 9's four-row label table, `AX-09` |
| the three-page pilot | ⭐ **reviewed once**, then the gates alone | [the plan](../README.md#m10-every-corpus-has-practices)'s step 10.4, `AX-11` |

⭐ **The quiz is designed, not deferred:** a question form (stem, ordered options, exactly
one keyed, one sentence per option, an `origin`); authored from one passage of the page,
recorded by address; graded by the framework from data shipped in the practice document —
no compiler, no container, no network, no model, identical over `file://`; and five gates
of its own. ⛔ **Q1–Q3 are model judgements taken once and shipped as a record; Q4 and Q5
are mechanical and `validate` re-runs them** — so a quiz grader is `generated`/`advisory`
**always**, with no path to `authoritative`. ⭐ **That asymmetry is stated in the spec
rather than smoothed over**, because it is the honest difference between a proof anyone can
re-take and a reading somebody took for you.

### 3. The epic — [`E14`](../E14-authored-exercises.md), *Authored exercises*, prefix `AX`

⭐ **`E14` was the next free number and `AX` the next free prefix**, re-measured on this
branch. Every task carries `Owns`, `Depends on`, `Context`, a `Definition` and an
`Acceptance` asserted both ways.

| task | what it is |
|---|---|
| `AX-00` | cases, kinds and origin in the exercise record |
| `AX-01` | the case report |
| `AX-02` | Submit records the breakdown |
| `AX-03` | the authoring gates and the gate record |
| `AX-04` | the exercise bundle |
| `AX-05` | the quiz shape |
| `AX-06` | the quiz authoring gates |
| `AX-07` | the source ledger and the page plan |
| `AX-08` | the authoring skill |
| `AX-09` | the practice panel: the breakdown, the reference and the label |
| `AX-10` | the authoring guide catches up |
| `AX-11` | `M10`'s acceptance, read on ISO and on the prose fixture |

### 4. `M10`'s steps, and the index regenerated

- **10.1** `AX-00`, `AX-01`, `AX-05` · **10.2** `AX-02`, `AX-03`, `AX-04`, `AX-06` ·
  **10.3** `AX-07`, `AX-08`, `AX-09`, `AX-10` · **10.4** the ISO rows, pilot first ·
  **10.5** `AX-11`.
- ⭐ [`docs/capability-index.md`](../../capability-index.md) was **regenerated with the
  delivery skill's own step-1 command**, never hand-edited (R19).

### 5. What changed in each existing document

- **`SK-04` ([`E11`](../E11-skills-authoring.md))** — the refusal of a grader-less source is
  **struck in place**, and so is its Acceptance line. `SK-04` becomes case (a) of `AX-08`'s
  skill and keeps its milestone, its scope and its corpus. Its derivation and its
  `bundled`/`authoritative` label are untouched.
- **[`E08`](../E08-java-exercises.md)** — the header's *"no LLM-authored assertions"* is
  **scoped to this epic**, with the two seams `E14` takes over named as edges to declare
  when it lands (`EX-04`'s emission, `EX-05`'s report format).
- **[`E06`](../E06-exercise-contract.md)** — *"zero remains a first-class outcome"* is
  re-scoped to **zero is named, never silent**; the table's ISO row is dated; `SF-23` gains
  `AX-00` as growth rather than a re-opening; `SF-24` gains `AX-09`'s three additions.
- **[`E10`](../E10-validation-qa.md)** — `QA-04`'s *"a source that yields zero exercises is
  a pass"* is dated: it stands for `M8`, which closed under it, and not past `M9`.
- **[The authoring guide](../../authoring/exercises.md)** — *"Do not invent assertions"* is
  struck and replaced by **author, then prove**, ⛔ **explicitly flagged as a stance and not
  a procedure**, because no skill authors anything today and this page must not describe
  behaviour that does not ship.
- **`tests/test_acceptance_clauses.py`** — `E14` added to `FRAMEWORK_EPICS`. Its three
  tests failed on the new epic before this change and pass after it.

## Decisions

- ⛔ **§1's ISO *Graders* cell was NOT changed, and that is deliberate.**
  `tests/test_spec_corpus_table.py` refuses a cell claiming graders against a manifest
  saying `exercises: false`, and ISO's pinned manifest still says so. ⭐ **The instrument is
  right and the cell is true today**; the honest move is a dated note saying when it moves,
  which is `M10`'s last step. ⚠️ **This resolves stage 1's `W389/1` as *not yet*, rather
  than as a table edit.**
- ⛔ **The spec amendment is NOT an epic task.** Stage 1 proposed it as `AX-00`; it is
  landed here under this brief, so `E14` says so in its preamble and mints nothing for it.
  ⭐ **A task that re-proposes a settled amendment is a round spent re-deriving it.**
- ⛔ **The runner's per-corpus warm is NOT a task here.** [`W390`](../rows/W390.md) is
  minted and in flight for exactly that, out of stage 1's `W389/2`. ⭐ **`E14` cites it and
  depends on its outcome** rather than restating it as an `AX` row.
- ⭐ **The quiz is a `kind` on the exercise record, not a fourth state.** §7's three states
  are structural and adding a fourth would have put a flag where the structure is the
  answer. A quiz is a **graded** exercise whose grader is a key rather than a test command.
- ⭐ **A quiz completes through the reader's own state, never through a run verdict.** It
  produces no run, so `is_pass` is untouched — and that is written into `AX-02` and `AX-05`
  as a clause each may not cross.
- ⭐ **The label words are the framework's constant, not a corpus's string** (R1), and the
  four cases are fixed in the spec so `AX-09` renders them rather than inventing them.
- ⭐ **`AX-06` owns a sub-package inside `AX-03`'s gates package**, with the edge declared
  and both in the same step. That is the shape `W156` asks for, and it keeps one gate
  record instead of two.
- ⭐ **[`CLAUDE.md`](../../../CLAUDE.md) was left alone.** Its sentence is outside this brief's surface, and it is
  still true until `M10` closes. Recorded as `W389/6`.

## Surprises

- ⚠️ **The corpus-table instrument would have caught a confident wrong edit.**
  `tests/test_spec_corpus_table.py` reads the *Graders* column against a pinned manifest, so
  writing stage 1's proposed ISO cell — *"authored at ingestion"* — would have turned the
  suite RED at once. ⭐ **A plan clause and a live instrument disagreed, and the instrument
  was right.**
- ⚠️ **Adding an epic is a code change whether or not you touch code.**
  `tests/test_acceptance_clauses.py` carries the epic roster as a typed tuple, so `E14`
  failed three tests on arrival. ⭐ **That is the test doing its job** — an epic nobody
  assigned to a side is exactly what it exists to catch — ⛔ **and anyone minting an epic
  should expect to update it.**
- ⚠️ **The anchor slug for an `M<n> — <name>` heading collapses to ONE hyphen**
  (`m10-every-corpus-has-practices`), not two. Three pointers were written wrong and the
  floor caught every one.

## Findings

| id | marker | against | what |
|---|---|---|---|
| `W389/6` | `[local]` | [`CLAUDE.md`](../../../CLAUDE.md) | Its *"A corpus with no graders is complete at the reading floor, not short"* is true today and **goes stale when `M10` closes**. ⛔ Outside this brief's surface, so not edited. The register owns the timing |
| `W389/7` | `[structural]` | [`E08`](../E08-java-exercises.md), `EX-04`, `EX-05` | Two seams `E14` takes over — `EX-04`'s emission through the bundle, `EX-05`'s report in the ledger's format — are **named in prose and carried by no `Depends on` edge**, because `E08` is `M9` and `E14` is `M10`. ⭐ The edge is declarable only once the order of `M9` and `M10` is settled by whoever schedules them |
| `W389/8` | `[local]` | [the authoring guide](../../authoring/exercises.md) | The replaced stance is a **forward statement flagged as such**, and `AX-10` rewrites the page from shipped code. ⚠️ Until then the page says *what will be true*, which is the one shape `SK-05`'s standing rule dislikes — the flag is the mitigation, not a fix |
| `W389/9` | `[local]` | `tests/test_authoring_reference.py` | Its exercise-keys assertion reads the **first** JSON fence carrying an `exercise` key. ⚠️ A future edit adding a fence above that one changes what the test reads without changing the test. Not touched here; no fence was added |

⭐ **Stage 1's `W389/1`–`W389/5` stand as recorded**, and `W389/1` is answered above:
the cell moves at step 10.4, not now. `W389/2` became [`W390`](../rows/W390.md).

## Clause → test

| clause of this stage | measured by | the reading |
|---|---|---|
| the spec amendment lands where stage 1 quoted it | `grep -n` for each quoted clause on this branch | eight places, each with a dated block beside the text it supersedes |
| the ISO *Graders* cell must not claim graders yet | `tests/test_spec_corpus_table.py` on this branch | GREEN — the cell is unchanged and the note carries the timing |
| `E14` and `AX-` are free | `ls docs/tasks/E*.md`; `git grep -nE "\bAX-[0-9]"` before the write | `E00`–`E13`; no `AX-` id |
| every `AX` row is a readable capability | the delivery skill's step-1 command, re-run | `M10` prints all twelve, each with its `Owns` and its edges |
| the milestone order is unchanged by this edit | the regenerated index's order line | `M0`…`M6` → `M8` → `M5` → `M7` → `M10` → `M11` → `M9` |
| the epic roster names one side per epic | `tests/test_acceptance_clauses.py` | RED before `E14` was assigned, GREEN after |
| every new pointer and anchor resolves | `python3 -m tools.quality` | floor clean at the tip |
| the guide's shipped-state assertions still hold | `tests/test_authoring_reference.py` | GREEN — no fence added, no state vocabulary moved |

## For dependents

- ⭐ **The register:** `M10`'s steps are in [`README.md`](../README.md) and its tasks in
  [`E14`](../E14-authored-exercises.md). ⛔ **`W389/6` needs the register's call on when
  [`CLAUDE.md`](../../../CLAUDE.md)'s sentence is dated** — it is not stale yet.
- ⭐ **Whoever carries `AX-00`:** read `W357`'s handoff first. The new keys follow its
  pattern exactly — structural, no flag, no `raw_api` bump — and its instrument is the one
  that proves it.
- ⭐ **Whoever carries `AX-03` or `AX-06`:** [`E08`](../E08-java-exercises.md)'s per-method
  argument is the model. ⛔ **A gate coarser than the claim it backs is theatre**, and
  `AX-06` must additionally close every path by which a quiz grader could be recorded
  `authoritative`.
- ⭐ **Whoever carries `AX-09`:** the four label sentences are fixed in
  [spec §7](../../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389).
  ⛔ **Render them; do not reword them**, and keep R5's vocabulary off the page.
- ⭐ **The integration agent, step 10.4:** the corpus is **regenerated**, never patched, and
  the pilot is **three pages, reviewed once**. ⚠️ Stage 1 measured the densest page of each
  container; that reading is in [stage 1's handoff](W389.md) and is not re-taken here.
- ⛔ **Anyone minting the next epic:** `tests/test_acceptance_clauses.py` carries the epic
  roster as a typed tuple. Add the epic to a side, or three tests go RED.
