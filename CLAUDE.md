# CLAUDE.md — studyforge

Guidance for Claude Code working in this repository.

## ⛔ THIS FILE CARRIES NO LIVE STATE. READ THE BOARD.

⭐ **`docs/tasks/BOARD.md` is the instrument. Open it now, before anything
else.** It carries which milestone and step are open, what is in flight, what is
assigned, and what to do next. ⛔ **This file names none of those, deliberately
(Ruling 161), and an empty answer here is the intended answer — not an omission
to be helpfully filled in by the next editor.**

⚠️ **Why the rule is absolute, and it is not tidiness.** This file is read into
an agent's context **at session start**, so what an agent acts on is a
**snapshot**, not the tree. ⛔ **A correction landing at 03:00 never reaches a
session that started at 02:00, and there is no instrument that can read another
agent's context** — so a live fact written here cannot be kept true. It can only
be kept freshly wrong. ⚠️ **Measured, `PO-33/9` and Ruling 161** — ⛔ **and the
reading is quoted below in a blockquote deliberately, because check 5's
instrument skips blockquoted lines and this file must not fail its own check by
citing the defect it was rewritten over:**

> The delivered copy said *"In flight: M2 step 2.1"* for five rounds while the
> tree had said step 2.2 since PO round 28 — and the wave-open check that guards
> this file PASSED in every one of those rounds, against a copy no agent reads.
> A second reading, `PO-34/1`: the sentence *"Nothing is implemented… the first
> work is milestone M0"* stood in this file from its first commit until PO round
> 34, false from the day M0 closed, because check 5's instrument was scoped to
> one section and that sentence was in another.

⭐ **A POINTER cannot go stale in a snapshot the way a fact can: it resolves at
read time, in the tree. That is a property the board has and this file
structurally cannot.**

⛔ **The consequence for anyone writing a brief, a task or a handoff: cite
`docs/tasks/BOARD.md` for anything that moves, never this file.** ⭐ **The three
instruments, and this file is none of them:**

| The question | ⛔ **The one instrument** |
|---|---|
| What is open, in flight, assigned, next | `docs/tasks/BOARD.md` |
| Which tasks are in a milestone or a step | `docs/tasks/README.md` |
| How many tasks, epics, capabilities there are | ⭐ the **generated** `docs/capability-index.md` |

⚠️ **The clause this replaces said *"if the two disagree, the board is right and
this file is a defect."*** ⛔ **It is moot now, and that is the improvement: there
is no second copy left to disagree.** ⭐ **A reader who wants state is sent one
place instead of being asked to adjudicate between two.**

## What this is

`studyforge` is a source-agnostic framework that converts any body of teaching
material into a local, offline study site — reading pages, narration, contents,
navigation, progress, and graded practices where the material supports them.

⭐ **The plan's spine is the reading floor** (spec §11.0) — narrated, navigable,
offline, no server — which is a **complete product** for prose material. The
**execution track** (containers, Run and Submit, graded practices) comes after
it, and a corpus enters it only if its material is runnable. ⛔ **A corpus with
no graders is complete at the reading floor, not short** (§7's three states, C5).
⭐ **The first consumer is a small corpus, not the Java tutorial.** ⚠️ **Which
milestone each of those lands in is `docs/tasks/README.md`'s to say, and how much
is built today is the board's.**

⛔ **Do not start writing framework code without reading the spec first.** The
design encodes decisions that were expensive to reach and are far cheaper to read
than to re-derive.

## Read before doing anything

1. `docs/specs/2026-09-08-studyforge-v1-design.md` — §1–§4, **all of R1–R21**,
   and **§12** (what the second source is for). The rulings are the authority you
   appeal to when a task is ambiguous.
2. `docs/tasks/README.md` — ordering and the critical path. ⛔ **THIS LINE
   CARRIES NO COUNT, and its removal is Ruling 150 (CTO round 40)**: it claimed a
   number while citing a document that claimed a different one, and the measured
   answer was a third. ⭐ **The authority for any count is the generated
   derivation, `docs/capability-index.md`** — and a count is a fact, so it obeys
   the rule at the top of this file.
3. The **epic document** for whatever you are working on (`docs/tasks/E*.md`) —
   it carries shared context so neighbouring tasks do not re-derive it, and it is
   where a task's dependencies and its Acceptance live.
4. `docs/conventions/` — module structure, graphify, the agent working
   agreement, the review rubric.

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

- ⛔ **`graphify` IS NOT SOMETHING A TASK'S CONTEXT BUDGET MAY ASSUME, and the
  sentence that said it was is REMOVED rather than softened.** ⭐ **The reason is
  a PROPERTY and not a reading, so it cannot go stale in a snapshot: the index
  directory is UNTRACKED, and an untracked directory does not travel to a linked
  worktree — which is where every agent in this project works.** ⚠️ **Corroborated
  at `98aa0ad`: `git ls-files` returns `0` for it, it is present in the main
  checkout, and it is absent from all four linked worktrees.**
- ⭐ **THE TOOL IS NOT RETIRED and `docs/conventions/graphify.md` still governs
  it (R14).** ⛔ **What changed is that you CHECK whether an index is there before
  planning around one, and you never budget a task on the assumption that it is.**
  ⭐ **The search path that is always present is `git grep`, `grep -rn` and
  `sed -n`.** ⚠️ **Whether the index should be built per worktree, tracked, or
  dropped is UNDECIDED, and this clause forecloses none of the three.**
- ⛔ **RUN EVERY GATE; DO NOT TRANSCRIBE ITS READING.** ⭐ **A merge body,
  handoff, brief, round record or message reports a gate as GREEN or RED plus
  its exit code and quotes NO figures out of it** — ⚠️ **the exception is a
  figure that IS the subject, including a gate's own declared bound.** ⛔ **The
  rule and its ground live ONCE, in `docs/conventions/`; this is a pointer and
  the clause is not restated here.**
- **Write a handoff** at `docs/tasks/handoffs/<TASK-ID>.md` before finishing a
  task with dependents. That is how parallel agents share findings instead of
  re-deriving them. Format is in `docs/conventions/agent-protocol.md`.
- **Stay inside your task.** A defect noticed outside it goes in the handoff as
  a finding, not into the diff. Unrequested scope is how parallel work collides.
- **Verify claims by counting.** Every "measured fact" in these documents was
  counted against the real repositories, and doing so corrected several things
  that had been asserted confidently and wrongly. If a document states a number,
  it is checkable — check it rather than inheriting it.
- **A measurement is quoted with the ref it was taken on**, and with the
  checkout and the environment it was taken in, or it is not a measurement.
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

⛔ **A WORKTREE DOES CARRY THE SIBLINGS, and the sentence that stood here saying
otherwise was FALSE.** ⭐ **The property belongs to the CONTAINER MOUNT, never to
the worktree (Ruling 248(a)); Ruling 159's own reading is DATED by that and its
record stands unedited** (Ruling 106). ⭐ **Why: `tools/workspace` resolves
`git rev-parse --git-common-dir` — the **main** checkout's `.git`, whose
grandparent is the workspace — so it finds every component from any worktree on
this host, and a reading taken from one is NOT host-verified.** ⛔ **What is
genuinely absent is the disk AROUND the tree inside the pinned image, where only
the checkout is mounted** — ⚠️ **so a reading that finds no sibling names the
CONTAINER as its reason, and never the worktree.**

## Two agents

The plan is built to be run by two agents. The **framework agent** owns
`studyforge`, `code-server-toolchain` and `narrate-service` (E00–E06, E10–E13,
**including all the skills**). The **integration agent** owns one corpus
repository (E07, E08, and what survives of E09). Three seams cross between them
and all three have a contract: the archive (`studyforge validate`), placement
(`studyforge plan`), and each shared component's `consuming.json`.

⛔ **During the extensibility milestone the integration agent does not modify
`studyforge`** — findings, not patches. A test of extensibility run by somebody
who can edit the thing being tested measures nothing (§12). ⚠️ **Which milestone
that is, and whether it is live, is `docs/tasks/README.md`'s and the board's.**
