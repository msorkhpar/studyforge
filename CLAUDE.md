# CLAUDE.md — studyforge

Guidance for Claude Code working in this repository.

## What this is, and what state it is in

`studyforge` is a source-agnostic framework that converts any body of teaching
material into a local, offline study site — reading pages, narration, contents,
navigation, progress, and graded practices where the material supports them.

⚠️ **Nothing is implemented. This repository is a design and a backlog.** There
is no `src/`, no tests, no package. The first work is milestone **M0**.

Do not start writing framework code without reading the spec first. The design
encodes decisions that were expensive to reach and are not recoverable from the
code — because there is no code.

## Read before doing anything

1. `docs/specs/2026-09-08-studyforge-v1-design.md` — §1–§4, **all of R1–R21**,
   and **§12** (what the second source is for).
   The rulings are the authority you appeal to when a task is ambiguous.
2. `docs/tasks/README.md` — ordering and the critical path. ⛔ **THIS LINE
   CARRIES NO COUNT, and its removal is Ruling 150 (CTO round 40).** ⚠️ **It
   claimed **87** while citing a document that claimed **89**, and the measured
   answer was **91** live capabilities and **92** rows across **14** epics —
   ⭐ **a reader who followed the citation was corrected by two and a reader who
   did not was wrong by four.** ⛔ **The authority is the generated derivation:
   `docs/capability-index.md`.** ⭐ **This file's own *Where to start* already
   rules that a fact written in two places goes stale in the copy nobody
   re-measures — and a count is a fact.**
3. The **epic document** for whatever you are working on (`docs/tasks/E*.md`) —
   it carries shared context so neighbouring tasks do not re-derive it.
4. `docs/conventions/` — module structure, graphify, the agent working
   agreement.

## Hard rules

These are the ones most likely to be violated by someone moving fast. The full
set is R1–R21 in the spec.

- ⛔ **Never write an absolute home path into any file.** It carries the user's
  home directory, which is personal data (R7). Paths in documents are relative
  to the workspace root. This rule has already been violated once in this
  repository's own documents and corrected.
- ⛔ **No personal data anywhere** — no email, name, account identity, hostname
  or absolute path, in any file, commit message, log or outbound request. Use
  placeholders.
- ⛔ **No file over 400 lines** (600 for tests), or the exception is justified
  in the module's own docstring (R11). CodeSignal's largest modules are ported
  **as packages, during extraction** — never as files. `FND-01` makes this a
  build failure.
- ⛔ **The framework knows nothing about any source** (R1). No import, no name,
  no branch on an adapter. Every source-specific fact arrives as data.
- ⛔ **The adapter seam is on disk, not in Python** (R2). An adapter writes an
  archive and nothing else; `studyforge validate` is its definition of done.
- ⛔ **Generation is non-destructive** (R3). No existing file in a source
  repository is moved, renamed or rewritten. An edit exists only where the
  corpus manifest **declares** it, it must be additive, and `OPS-05` reads the
  declaration rather than knowing any corpus's exception.
- ⛔ **The consuming half of a corpus is generated, not hand-authored** (R19).
  Anything a second source would have to retype is a hole in the skills. A
  hand-edit to a generated artifact is a **finding**, not a fix — customisation
  enters as manifest data.
- ⛔ **A skill precedes the artifact it produces** (§9). A skill written after
  the thing it "produces" has been validated against exactly one source.
- ⛔ **The extraction is one-way** (R20). CodeSignal is *this framework's*
  source. A consumer repository's task never cites a path inside it — what a
  consumer needs is carried here, in a ruling, a contract, a skill, or the
  integration catalogue. Otherwise every integration re-derives from a moving
  repository and the expertise lives nowhere.
- ⛔ **The Docker socket is never mounted into the serving process** (spec
  §8.3). Not behind a flag, not "only locally".
- **Tests are part of every task** (R12), never a follow-up.
- **Standard library only** in framework source; test-only dependencies are fine.

## Working practice

- **Ask the knowledge graph before exploring** (R14, `docs/conventions/graphify.md`).
  Task context budgets assume it. `graphify query "..."` answers in a few
  thousand tokens where equivalent exploration costs tens of thousands.
- **Write a handoff** at `docs/tasks/handoffs/<TASK-ID>.md` before finishing a
  task with dependents. That is how parallel agents share findings instead of
  re-deriving them. Format is in `docs/conventions/agent-protocol.md`.
- **Stay inside your task.** A defect noticed outside it goes in the handoff as
  a finding, not into the diff. Unrequested scope is how parallel work collides.
- **Verify claims by counting.** Every "measured fact" in these documents was
  counted against the real repositories, and doing so corrected several things
  that had been asserted confidently and wrongly. If a document states a number,
  it is checkable — check it rather than inheriting it.
- **Refining a task as the project grows is expected.** Silently expanding one
  is not.

## The workspace

Components are separate repositories that are **siblings on disk**, pinned by
`workspace.json` and checked by `python3 -m tools.workspace verify` (R18,
amended — `docs/conventions/workspace.md`). ⛔ **Git submodules are not used in
this project**, because nothing is ever pushed to any remote and every submodule
form needs a URL that resolves. The components are:
`CodeSignal` (extraction source, untouched in v1),
`Claude-senior-java-engineer` (consumer 1), `ISO-8583-jPOS-tutorial` and
`Claude-SPARQL-tutorial` (v2 targets), plus `code-server-toolchain` and
`narrate-service` still to be created by E12 and E13.

## Where to start

✅ **M0 and M1 are both CLOSED.** **M1 closed 2026-09-10 at `2fe56a4`**, all nine
of its close conditions true at that one ref. ✅ **M2 step 2.1 closed 2026-09-10
at `a00337b`**, all five of its rows re-taken at that one ref. ✅ **M2 step 2.2
closed 2026-09-10 at `ce80120`**, all four of its rows re-taken at that one ref.
⏳ **Open: M2 — a corpus is readable. In flight: M2 step 2.3.** ⛔ **Do not start
on M0 or M1.**

⚠️ **CORRECTED 2026-09-10 (PO round 33, check 5), and it is the SECOND time this
section has been wrong about which step is live.** ⛔ **It said *"In flight: M2
step 2.2"*, and that became false at `176621c` — the merge of `SK-08`, step
2.2's last row — three merges before this correction was written.** ⭐ **Check 5
predicted this exact liability IN ADVANCE, by name, in round 32, and named it
the next round's first job** — ⚠️ **which is check 5 earning its place on the
wave-open checklist rather than being justified by it.**

⚠️ **CORRECTED 2026-09-10 (PO round 28, check 5). This section said *"In flight:
M2 step 2.1"*, which was true when it was written and false the moment that step
closed** — ⛔ **and the round that closed the step is the round that made this
file wrong.** ⭐ **The sentence was REPLACED, not annotated below (Ruling 106
governs merged handoffs; a correction to a live instruction replaces it, because
a reader stops at the first sentence that answers their question).**

⛔ **TWICE IS A MECHANISM, NOT AN ACCIDENT: the round that closes a step is
always the round that makes this file wrong**, because the close is what changes
the answer and this file is the copy nobody re-measures while the close is being
written. ⭐ **The remedy is the one already in force — the board is the
instrument, this file says only which milestone is open, and check 5 runs at
every wave-open.**

⛔ **THE TASK LIST THAT USED TO STAND HERE HAS BEEN REMOVED, and its removal is
the point.** ⚠️ **This line named five step-2.1 tasks; two of them — `SF-31` and
`SF-04` — merged, and this file said *in flight* about both of them anyway.**
⭐ **A step's MEMBERSHIP belongs in `docs/tasks/README.md`; a task's STATE belongs
in `docs/tasks/BOARD.md`; ⛔ this file carries neither, because a fact written in
two places goes stale in the copy nobody re-measures — and the copy nobody
re-measures is always the one that is not the instrument.** ⚠️ **PO round 25
found EIGHT stale board rows by exactly that mechanism.**

⚠️ **`SF-35` and `SF-36` were added to step 2.1 at round 24 and they are not new
scope: they are two CTO rulings that had no task id.** ⛔ **A ruling that names
*"a framework task"* and no id has described a task, not created one** — ⭐ **the
id space has exactly one minter, and check 3 is what finds the gap.**

⚠️ **M2 is not M1 with different task ids: the skills come with it, not after
it** (`docs/tasks/README.md`, M2). ⛔ **`SK-02` is in step 2.1 for that reason,
and a corpus built before its skill exists is one the skill can only claim
retrospectively** (spec §9).

⚠️ **CORRECTED 2026-09-10 (PO round 19, check 5). This section said *"In flight:
M1 step 1.4 — `SF-10`"* directly above a paragraph saying `SF-10` was done and
step 1.4 closed.** ⛔ **The correction had been *appended below* the stale
sentence instead of replacing it**, so the file contradicted itself in adjacent
paragraphs — ⭐ **and the wrong half was the one that reads like the answer,
because a reader stops at the first sentence that answers their question.**
⛔ **A correction that leaves the original standing is not a correction; it is a
second copy, and the reader picks the first one.**

⚠️ **This section said *"Milestone M0 — FND-01…FND-05, all parallel"* for sixty
seconds after M0 closed, and it was the second time in two rounds that this file
was the last to learn.** ⭐ **That matters more here than anywhere else: this file
is loaded into *every* session in this project**, so a stale sentence here does
not mislead one reader — ⛔ **it misdirects every agent that starts.**

⭐ **Live state, and this file is not it:** `docs/tasks/BOARD.md` carries what is
open, in flight and assigned. ⛔ **This section says only which milestone is
open; the board says what to do in it.** ⚠️ **If the two disagree, the board is
right and this file is a defect** — ⭐ **which is why `CLAUDE.md` is now on the
wave-open checklist by name.**

⭐ **The first consumer is a small corpus, not the Java tutorial.** The plan's
spine is the **reading floor** (spec §11.0) — narrated, navigable, offline, no
server — which is a *complete product* for prose material and lands by M4. The
**execution track** (containers, Run and Submit, graded practices) starts at M5,
and a corpus enters it only if its material is runnable. ⛔ **A corpus with no
graders is complete at M4, not short** (§7's three states, C5).

⛔ **`EX-00` still gates the whole of E08** and is still the first thing done
whenever E08 starts — a one-agent-day spike whose negative result is a success.
It left M0 because exercises are no longer on the first delivery's path. ⚠️ It
needs `TC-00`'s pinned image: its deliverable is a wall-clock measurement that
decides the shape of E08, and one taken on a host JDK is not reproducible (R15).

## Two agents

The plan is built to be run by two agents. The **framework agent** owns
`studyforge`, `code-server-toolchain` and `narrate-service` (E00–E06, E10–E13,
**including all the skills**). The **integration agent** owns one corpus
repository (E07, E08, and what survives of E09). Three seams cross between them
and all three have a contract: the archive (`studyforge validate`), placement
(`studyforge plan`), and each shared component's `consuming.json`.

⛔ **During M8 the integration agent does not modify `studyforge`** — findings,
not patches. A test of extensibility run by somebody who can edit the thing
being tested measures nothing (§12).
