# CLAUDE.md — studyforge

Guidance for Claude Code working in this repository.

## This file carries no live state

⛔ **What is open, who has it and what is next is [`docs/tasks/BOARD.md`](docs/tasks/BOARD.md),
and only there.** This file names no milestone, step, task or count as current, and an empty
answer here is the intended answer, not an omission to fill in.

⚠️ **Why:** this file is read into an agent's context at session start, so what an agent acts
on is a snapshot. A live fact written here goes stale in every session that started before
it changed, and nothing can correct a snapshot already in another agent's context. A pointer
resolves when it is read, in the tree; a fact cannot. So a brief, a task or a handoff cites
the board for anything that moves, never this file.

| The question | Where the answer is |
|---|---|
| What is open, who has it, what is next | [`docs/tasks/BOARD.md`](docs/tasks/BOARD.md) |
| The milestone order, and what each one is done when | [`docs/tasks/README.md`](docs/tasks/README.md) |
| Every capability, and the milestone that delivers it | the packaged index: `python3 -m studyforge.skills.delivery` |

## What this is

`studyforge` is a source-agnostic framework that converts any body of teaching material into
a local, offline study site: reading pages, narration, contents, navigation, progress, and
graded practices where the material supports them.

⭐ **The spine is the reading floor** (spec §11.0) — narrated, navigable, offline, no server —
which is a complete product for prose material. The execution track (containers, Run and
Submit, graded practices) comes after it, and a corpus enters it only if its material admits
a checkable task. ⛔ **A corpus with no graders is complete at the reading floor, not short**
(§7's three states, C5).

## Read before doing anything

1. [`README.md`](README.md) — what the product is, how to install it, and which skill runs in
   which order. It is a stranger's whole reading list.
2. [The spec](docs/specs/2026-09-08-studyforge-v1-design.md) — §1–§4, **all of R1–R21**, and
   §12 (what the second source is for). The rules are the authority you appeal to when a task
   is ambiguous.
3. [`docs/decisions.md`](docs/decisions.md) — every decision that still shapes the product,
   with its reason and the spec rule it serves. An old process id met in a docstring is
   looked up there.
4. The epic for what you are working on (`docs/tasks/E*.md`) — its high-level design and
   shared context. Task text that has left the main line is on `archive/process`.

⛔ **Do not write framework code without reading the spec first.** The design encodes
decisions that were expensive to reach and are far cheaper to read than to re-derive.

## Process history lives on `archive/process`

The tooling, the board's history, the rows, the handoffs, the rulings index, the conventions
and the review rubric that built the framework are on the local branch `archive/process`, in
this repository, byte for byte. Read them with `git show archive/process:<path>` or
`git log archive/process`. ⛔ Nothing on the main line depends on them: the product, its
tests and its floor stand without them.

## Hard rules

The ones most likely to be violated by someone moving fast. The full set is R1–R21 in the
spec.

- ⛔ **No personal data anywhere** (R7) — no email, name, account identity, hostname or
  absolute path, in any file, commit message, log or outbound request. Use obvious
  placeholders (`contact@example.com`, `Jane Doe`); a real value, where one is ever approved,
  comes from an environment variable at runtime and is never written down.
- ⛔ **Never write an absolute home path into any file.** It carries the user's home
  directory, which is personal data. Paths in documents are relative to the workspace root.
- ⛔ **No file over 400 lines** (600 for tests), or the exception is justified in the
  module's own docstring (R11). `python3 -m tests.floor` fails the build on it.
- ⛔ **The framework knows nothing about any source** (R1). No import, no name, no branch on
  an adapter. Every source-specific fact arrives as data.
- ⛔ **The adapter seam is on disk, not in Python** (R2). An adapter writes an archive and
  nothing else; `studyforge validate` is its definition of done.
- ⛔ **Generation is non-destructive** (R3). No existing file in a source repository is
  moved, renamed or rewritten. An edit exists only where the corpus manifest declares it,
  and it must be additive.
- ⛔ **The consuming half of a corpus is generated, not hand-authored** (R19). Anything a
  second source would have to retype is a hole in the skills. A hand-edit to a generated
  artifact is a finding, not a fix — customisation enters as manifest data.
- ⛔ **A skill precedes the artifact it produces** (§9).
- ⛔ **The extraction is one-way** (R20). CodeSignal is this framework's source. A consumer
  repository's task never cites a path inside it; what a consumer needs is carried here, in
  the spec, the decisions file, a contract, a skill, or the integration catalogue.
- ⛔ **The Docker socket is never mounted into the serving process** (spec §8.3). Not behind
  a flag, not "only locally".
- **Tests are part of every change** (R12), never a follow-up.
- **Standard library only** in framework source; test-only dependencies are fine.
- ⛔ **Nothing is pushed to any remote**, and no remote is added.

## Working practice

- ⭐ **The search path is `git grep`, `grep -rn` and `sed -n`.** There is no code-graph or
  index tool in this project, and a document that names one is stale.
- ⛔ **Run every gate; do not transcribe its reading.** Report a gate as GREEN or RED with its
  exit code and quote no figures out of it — except a figure that is the subject, and a RED
  gate's breached bound always is: say which bound broke and by how much. The gates are
  `python3 -m tests.floor`, `ruff check .`, `ruff format --check .` and
  `python3 -m pytest -n auto -q`, each also runnable in the pinned image as
  `./docker/dev/check <command>`.
- **Write a handoff before finishing a task with dependents**, so parallel work shares
  findings instead of re-deriving them. Handoffs are committed to `archive/process`, not the
  main line; a decision in one that still shapes the product goes into
  [`docs/decisions.md`](docs/decisions.md) in the same act.
- **Stay inside your task.** A defect noticed outside it goes in the handoff as a finding,
  not into the diff.
- **Verify claims by counting.** If a document states a number, it is checkable — check it
  rather than inheriting it. A measurement is quoted with the ref, the checkout and the
  environment it was taken in, or it is not a measurement.

## The workspace

Components are separate repositories that are **siblings on disk**, each pinned to a commit
in [`workspace.json`](workspace.json) (R18). ⛔ **Git submodules are not used**, because
nothing is pushed to any remote and every submodule form needs a URL that resolves. The
components are `CodeSignal` (the extraction source, untouched in v1),
`Claude-senior-java-engineer` (the Java corpus), `ISO-8583-jPOS-tutorial` (the first corpus),
`Claude-SPARQL-tutorial` (a v2 target), `code-server-toolchain` and `narrate-service`.

⚠️ **The pin file is a development arrangement.** A stranger converting their own material
installs the library and builds its images locally by tag, as the README says; they do not
check the framework out beside their corpus.

## Two agents

The plan is built to be run by two agents. The **framework agent** owns `studyforge`,
`code-server-toolchain` and `narrate-service`, including all the skills. The
**integration agent** owns one corpus repository. Three seams cross between them and each
has a contract: the archive (`studyforge validate`), placement (`studyforge plan`), and each
shared component's `consuming.json`.

⛔ **While a corpus proves the framework, the integration agent does not modify
`studyforge`** — findings, not patches. A test of extensibility run by somebody who can edit
the thing being tested measures nothing (§12).
