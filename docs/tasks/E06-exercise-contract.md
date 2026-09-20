# E06 — Exercise contract

What an exercise *is* to the framework, independent of how any source produces
one, and the reader-facing surface that presents it.

**Shared context for this epic.** Two rulings govern everything here.

**There are THREE exercise states, not two** (spec §7, C5): **none**,
**ungraded** (a prompt with nothing to check it), and **graded**. This was
verified against real material — all 19 SPARQL lessons end in an exercise and
none ships a test, so a two-state model would have deleted their exercises to
satisfy the schema. Only a graded exercise can complete a practice.

**Zero remains a first-class outcome.** Many Java units will have none, because
a pair failing a gate ships nothing rather than something weak. A unit with no
exercise renders as a clean reading page, not a broken practice page.

⛔ **RE-SCOPED 2026-09-19 (`W389`, user direction): zero is NAMED, never silent.** ⭐ **The
contract property above is unchanged** — a unit with no exercise still renders as a clean
reading page, and a gate that refuses still ships nothing rather than something weak.
⚠️ **What changed is what zero MEANS.** From `M10` an exercise is authored for material the
source did not grade, so zero is a reading the gates produced and the coverage report names
the gate that produced it — ⛔ **never a default nobody tried to move**
([`E14`](E14-authored-exercises.md), [spec
§7](../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389)).

**R5 — nothing generated is presented as more authoritative than it is.** The
vocabulary is deliberately small and deliberately enforced in code, not in
review: provenance is `bundled`, `generated` or `user`; trust is
`authoritative` or `advisory`; and a `generated` grader **cannot** be recorded
or rendered as authoritative. CodeSignal needs this because its real grader is
hidden and unknowable. The Java corpus earns `authoritative` honestly, by
mechanical proof (E08) — which is exactly why the contract must be able to
express the difference rather than assuming one answer.

**This epic defines the contract. It generates nothing.** Generation is E08.

---

### SF-23 — Exercise and workspace contract
**Milestone** M1 · **Depends on** SF-09 · **Team** solo
**Owns** `exercise/`
**Context** ~35k — spec §7, `CS/.pipeline/tools/study/scaffold.py` — **the `workspace` and test-record helpers and the vocabulary only. Do not read the generators.**

**Definition.** An exercise declares a **workspace** — where the reader's code
lives, where the grader lives, the command that runs their program, and the
command that runs the grader — plus its provenance and trust.

⛔ **Where it lives is ruled** (CTO on Q2,
`handoffs/CTO-2026-09-09-rulings-q1-q3.md`, carried into spec §7): an
`exercise` object inside the **practice archive document**,
`raw/<variant>/unit-NN/practice-M.json`, versioned by that document's existing
`raw_api` and written by the **adapter** (R2). ⛔ Not a sixth versioned contract,
not the authored overlay, not the manifest.

⭐ **§7's three states are structural here, and that is what this task must
encode** — there is no `state` field to set and none to forget:

| State | How it appears | Common case |
|---|---|---|
| **none** | no `practice-M.json` at all | ISO: 38 units, no practice document written — ⚠️ **dated by `W389`: a reading of the corpus as its source ships it, and `M10` re-ingests it with exercises authored for it** |
| **ungraded** | a `practice-M.json` with blocks and **no `exercise` key**, or an `exercise` naming **a file and no grader** | SPARQL: 19 prompts, no workspace |
| **graded** | the `exercise` names **a grader** | the Java repo — the *exception* |

⭐ **Amended by `W357`: graded is the grader's presence, not the key's.** A
record may carry `main_path` and `run_command` and nothing else, and that
record is **ungraded** — a file the reader runs, which nothing checks. The
grader half is written whole or not at all. ⛔ **The shapes and their refusals
are §7's, in [*A file with no test*](../specs/2026-09-08-studyforge-v1-design.md#a-file-with-no-test-w357),
and are not restated here**; the argument for one record rather than a second
declaration is [`W357`'s handoff](handoffs/W357.md). ⚠️ The Definition and
Acceptance below were written before it and speak of *the key*; read *the
grader* wherever they mean the graded state.

⛔ **Read that table before designing anything.** A corpus that must declare its
own emptiness is a contract fitted to the one source that ships 168 graders
(§11.0). The reading floor is complete without any of this.

Two commands rather than one, because Run and Submit are different acts
(E05/SF-22) and the distinction has to exist in the data, not only in the UI:
if a unit document carried one command, nothing downstream could stop a
program that merely printed from completing a practice.

Path and identifier values are validated against a safe pattern **before they
can reach a generated document**, because those values end up in a file the
runner executes against and in an editor's task file.

⚠️ **Context discipline.** `scaffold.py` is 1,793 lines and is mostly
CodeSignal-specific *generation* — the part this task must not inherit. Read
only the contract surface. Everything about guessing at a hidden grader stays
in CodeSignal; the Java corpus's generation is E08 and works differently.

### ⛔ Carried ruling — **`exercise` must become a known key, not a tolerated one**

⚠️ **Carried by the PO from CTO round 17, finding 20 `[structural]`, measured
before this task starts. Quoted rather than summarised, because a ruling relayed
as somebody's paraphrase has been through a lossy channel.** The measurement:

> ⛔ An archive document carrying an unknown top-level `"exercise"` object
> **validates green — 0 findings, 0 unchecked claims** — because the digest is
> taken over `blocks`. Owner is `archive.document.parse` (SF-02), **not**
> `validate`; re-asking in `validate` would be the "two readings from one parser"
> mistake E10 warns about. ⚠️ **What SF-23 must inherit: adding `exercise` has to
> change the known-key set, not be silently tolerated — otherwise a typo in the
> key is tolerated too and the graders are invisible.**

⭐ **This is the failure the board predicted when it put `SF-23` behind `SF-25`
with the same developer — *a corpus validates green with its graders invisible* —
and it is now measured rather than predicted.** ⛔ **A typo in `"exercise"` must
be a refusal, not a silently ungraded unit**, because §7's three states are
**structural**: there is no `state` field to set, so *absent* and *misspelled*
are indistinguishable to every reader downstream. ⚠️ **The change lands in
`archive.document`'s known-key set** (SF-02's surface), not in `validate`.

**Acceptance.** A `bundled` + `authoritative` record is accepted; a
`generated` + `authoritative` one is refused, in code. **All three states round-
trip** — a missing document, a document with no `exercise` key, and a full
record — and an ungraded exercise cannot complete a practice, asserted. A unit
with zero exercises is a valid, complete unit. A path outside the safe pattern is
refused. The depth-1 fixture (zero exercises) validates. ⛔ **A document with a
misspelled `exercise` key is refused, not silently treated as ungraded** — per
the carried ruling above.

⛔ **Two fixtures this task ships, both additively (R3), because neither exists:**

1. **The `graded` fixture.** **Measured 2026-09-09:**
   `grep -rln '"exercise"' tests/fixtures/` returns **nothing**, while two
   `practice-1.json` exist. ⚠️ Of §7's three states the fixtures carry **none**
   and **ungraded** — ⛔ **`graded`, the state this task is about, has none.**
2. **`W14` — the count-mismatch invalid fixture.** `E10`'s acceptance names
   **six** invalid fixtures and FND-04 ships **five**; ⛔ **the count-mismatch
   clause has never been exercised.** It is a practice-count mismatch, so it
   belongs to the task already opening practice documents. Digest recomputation
   is part of the work, not a follow-up.

⭐ **GROWN by `W389`, and NOT re-opened.** ⛔ **Nothing above changes.** The record gains
`cases`, `report`, `origin` and an exercise `kind` at
[`AX-00`](E14-authored-exercises.md#ax-00-cases-kinds-and-origin-in-the-exercise-record),
in a module beside this one and in `W357`'s shape: structural, no flag, no `raw_api` bump,
every older document still valid. ⚠️ **The known-key ruling above binds that task too** —
a misspelled new key is a refusal, for exactly the reason a misspelled `exercise` is.

---

### SF-24 — Practice panel
**Milestone** **M7** · **Depends on** SF-22, SF-23 · **Team** pair
**Owns** `render/page/practice.py`, `render/assets/practice.{js,css}`, and the
served-page insertion of the run client in `serve/routes/assets.py` (`W384`)
**Context** ~50k — SF-22 output, TC-05 consuming document, and
[`E05` § how a served page loads the run client](E05-serving-execution.md#how-a-served-page-loads-the-run-client-one-way-w370-from-sf-221),
which is the one statement of that insertion's rule

**Definition.** The reader-facing exercise surface on a unit page: the
statement, the embedded editor opened on the workspace, Run and Submit, and the
streamed result.

Three behaviours that are honesty requirements rather than polish:

- **The editor container is deliberately not auto-started** — it is an IDE with
  a shell, and starting one because somebody opened a reading page is not a
  decision the page gets to make. A panel with no container up says so and says
  how to start it, rather than rendering blank and looking broken.
- **An advisory grader is labelled on the page** (R5). A reader must be able to
  see the difference between "the tests that ship with this material passed"
  and "something we generated locally passed".
- **A reading-only unit shows no practice controls at all** — not disabled
  ones. A dead button is a promise the page cannot keep.

**Acceptance.** Editing, running and submitting work end to end against the
toolchain container. A panel with no container shows the stated message and
remedy. An advisory grader is visibly labelled. A unit with no exercise renders
with no practice affordance. Fully keyboard accessible.

⛔ **PO round 74 — `M7`, with the browser editor it embeds** (user direction, 2026-09-12: *"that functionallity is needed mostly for when exercises are in the picture"*). ⭐ **It gains `SF-22`'s editor clause: the IDE's build task follows the open practice.**

⭐ **EXTENDED by `W389` at `M10`, on this same surface, by
[`AX-09`](E14-authored-exercises.md#ax-09-the-practice-panel-the-breakdown-the-reference-and-the-label)** —
⛔ **a later row on an owned surface, not a re-scope of this one.** Three additions, each
the user's ruling of 2026-09-19: the Submit breakdown (*main ask ✓*, *edge cases n/m*, each
failed case named); the reference solution, **always available** and never gated behind a
pass; and the label, **worded for a learner**, which is this row's *"an advisory grader is
labelled"* made concrete — ⛔ **R5's `provenance` and `trust` never reach the page.**
⚠️ **A quiz renders in this panel with no editor, no Run and no Submit** — ⛔ **not disabled
ones**, by this row's own rule about a dead button.
