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

1. `docs/specs/2026-09-08-studyforge-v1-design.md` — §1–§4 and **all of R1–R18**.
   The rulings are the authority you appeal to when a task is ambiguous.
2. `docs/tasks/README.md` — 75 tasks, 13 epics, 8 milestones; ordering and the
   critical path.
3. The **epic document** for whatever you are working on (`docs/tasks/E*.md`) —
   it carries shared context so neighbouring tasks do not re-derive it.
4. `docs/conventions/` — module structure, graphify, the agent working
   agreement.

## Hard rules

These are the ones most likely to be violated by someone moving fast. The full
set is R1–R18 in the spec.

- ⛔ **Never write an absolute home path into any file.** It carries the user's
  home directory, which is personal data (R7). Paths in documents are relative
  to the workspace root. This rule has already been violated once in this
  repository's own documents and corrected.
- ⛔ **No personal data anywhere** — no email, name, account identity, hostname
  or absolute path, in any file, commit message, log or outbound request. Use
  placeholders.
- ⛔ **No file over 400 lines** (600 for tests), or the exception is justified
  in the module's own docstring (R11). CodeSignal's `backend.py` (2,743 lines)
  and `scaffold.py` (1,793) are ported **as packages, during extraction** —
  never as files. `FND-01` makes this a build failure.
- ⛔ **The framework knows nothing about any source** (R1). No import, no name,
  no branch on an adapter. Every source-specific fact arrives as data.
- ⛔ **The adapter seam is on disk, not in Python** (R2). An adapter writes an
  archive and nothing else; `studyforge validate` is its definition of done.
- ⛔ **Generation is non-destructive** (R3). No existing file in a source
  repository is moved, renamed or rewritten, with one stated exception asserted
  by `OPS-05`.
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

Components are separate repositories composed as submodules of one parent
(R18). They are siblings on disk until `FND-05` stands the parent up:
`CodeSignal` (extraction source, untouched in v1),
`Claude-senior-java-engineer` (consumer 1), `ISO-8583-jPOS-tutorial` and
`Claude-SPARQL-tutorial` (v2 targets), plus `code-server-toolchain` and
`narrate-service` still to be created by E12 and E13.

## Where to start

Milestone **M0** — `FND-01`…`FND-05` and `EX-00`, all parallel, everything else
depends on them.

⛔ **`EX-00` gates the whole of E08.** It measures whether the Java exercise
strategy yields anything usable, for one agent-day, before E08 is built. A
negative result is a successful spike, not a failure — E08 then changes shape
rather than being discovered unworkable at M6.
