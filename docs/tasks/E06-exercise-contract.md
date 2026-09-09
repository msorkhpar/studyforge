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
**Context** ~35k — spec §7, `CS/tools/study/scaffold.py` — **the `workspace` and test-record helpers and the vocabulary only. Do not read the generators.**

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
| **none** | no `practice-M.json` at all | ISO: 38 units, no practice document written |
| **ungraded** | a `practice-M.json` with blocks and **no `exercise` key** | SPARQL: 19 prompts, no workspace |
| **graded** | the `exercise` key is present | the Java repo — the *exception* |

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

**Acceptance.** A `bundled` + `authoritative` record is accepted; a
`generated` + `authoritative` one is refused, in code. **All three states round-
trip** — a missing document, a document with no `exercise` key, and a full
record — and an ungraded exercise cannot complete a practice, asserted. A unit
with zero exercises is a valid, complete unit. A path outside the safe pattern is
refused. The depth-1 fixture (zero exercises) validates.

---

### SF-24 — Practice panel
**Milestone** **M5** · **Depends on** SF-22, SF-23 · **Team** pair
**Owns** `render/page/practice.py`, `render/assets/practice.{js,css}`
**Context** ~50k — SF-22 output, TC-05 consuming document

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
