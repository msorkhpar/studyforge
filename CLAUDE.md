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
2. `docs/tasks/README.md` — **87** tasks, 13 epics, 9 milestones; ordering and the
   critical path. ⚠️ **`FND-08` and `FND-09` were added 2026-09-10** (Ruling 43's
   two walks), so a count of 85 quoted anywhere else is stale.
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

✅ **M0 is CLOSED**, and so are **M1 steps 1.1–1.3**. **In flight: M1 step 1.4 —
`SF-10`, the unit document builder.** ⛔ **Do not start on M0.**

⛔ **`SF-10` is BUILT and `in-review`, not waiting to be started.** ⚠️ **1,989
lines of it sit on `feat/SF-10-unit-builder`, unmerged**, and the board carried it
as *"unblocked, waiting on nothing"* for a round. ⭐ **Anything that renders or
reads a unit document — `SF-12` first — reads that branch, not the release tip.**
⛔ **Starting `SF-10` from scratch would rewrite a finished package.**

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
