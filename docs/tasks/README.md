# studyforge — task index

The milestone order, what each milestone is done when, and which tasks each step holds.
⭐ **What is open now is [`BOARD.md`](BOARD.md)**, not this file: this one orders the work,
that one says where it is. Every task cites the rules R1–R21 of
[the spec](../specs/2026-09-08-studyforge-v1-design.md).

⭐ **Every capability, the milestone that delivers it and what it waits on** is the capability
index the package ships: `python3 -m studyforge.skills.delivery`. No count is written here.

⭐ **The epics `E00`–`E14` are kept as high-level design.** The text of their tasks — each
Definition, `Owns`, `Depends on` and Acceptance — is on the local branch `archive/process`,
read with `git show archive/process:docs/tasks/<epic>.md`. `E15`'s tasks are live until `M11`
closes.

## Ordering principle

Tasks are ordered into **milestones, not layers.** Each milestone ends in something that
demonstrably works, so the project is usable early and stays usable, rather than
accumulating layers that only become a product at the end. The cost is real: `M1` does a lot
of contract work for one page. The alternative hides all integration risk until the end, and
integration risk is the kind that reorders plans.

**M0–M4 are the reading floor** — a narrated, navigable, offline site, which is the whole
product for prose material. **M5 and M7 are the execution track**, which a corpus enters only
if its material is runnable (spec §11.0). Narration comes before serving, because R8's floor is
`file://` and a reader needs no server.

| | Milestone | What works when it lands |
|---|---|---|
| **M0** | Foundations | An agent can start work without inventing anything |
| **M1** | One page renders | A unit page from a fixture opens in a browser |
| **M2** | **A corpus is readable** | Any corpus, offline, with contents, navigation and read marks — **and the skills that built it** |
| **M3** | It speaks | Narration with highlight sync, and an honest media footprint |
| **M4** | It is served | An origin, an API, and a record of practice passes |

⭐ **A prose corpus is finished at M4**, and a corpus with no graders that stops there is
complete, not short. ⛔ **Below, the order of work is the user's, not the ids':** the first
corpus reads and proves the framework, then the execution track, then authored practices for
every corpus, then the release, and then the Java corpus re-validates.

| | Milestone | What works when it lands |
|---|---|---|
| **M6** | The first corpus reads | `ISO-8583` is a narrated, navigable, offline study site |
| **M8** | **It is a framework** | `ISO-8583` converted by the skills alone, and the findings log written |
| **M5** | It runs code | A reader runs a unit's test from their terminal; Run and Submit from the page |
| **M7** | It has practices | The browser editor and the practice panel |
| **M10** | **Every corpus has practices** | Exercises authored for EVERY corpus — from its examples, its code, its tests, and by an LLM from its pages — each graded by tests of the main ask and every edge case |
| **M11** | It is release-ready | Every repository cleaned for release: process history on an archive branch, a light board, an installable library, skills that stand alone |
| **M9** | The Java corpus re-validates | `Claude-senior-java-engineer` converted under §12's rules, practices included |

---

## Milestones in detail

⚠️ **Steps are sequential, and a step is a batch boundary, not a parallelism guarantee.** A
step says nothing outside it may close before it; it says nothing about edges inside it.
⛔ **In-step edges are read off each task's `Depends on`**, never inferred from step
membership.

### M0 — Foundations
> **Done when:** an agent can pick up any task without inventing a layout,
> hunting for a graph, or building its own fixtures.

- **0.1** — FND-01, FND-02, FND-04
- **0.2** — FND-03, FND-06, FND-05a

### M1 — One page renders
> **Done when:** a unit page from the depth-1 fixture opens in a browser, with
> styles and highlighting, over `file://`.

- **1.1** — SF-01, SF-02, SF-07, SF-08, SF-11, SF-33
- **1.2** — SF-03, SF-05, SF-06
- **1.3** — SF-09, SF-23, SF-25, SK-01, FND-07
- **1.4** — SF-10
- **1.5** — SF-12, QA-03
- alongside 1.4 and 1.5 — FND-08, FND-09

### M2 — A corpus is readable
> **Done when:** a whole corpus opens offline with a working index, deep links,
> prev/next and read marks — **and the skills that produced it exist.**
> **This is the first genuinely useful state.**

- **2.1** — SF-04, SF-31, SF-35, SF-36, SK-02
- **2.2** — SK-07, SK-05, SK-08, SF-13
- **2.3** — SF-14, SF-27
- **2.4** — SF-15, SF-26, SF-30, SF-34

⚠️ **The skills come with this milestone, not after it.** A corpus built before they exist is
a corpus they can only claim retrospectively (spec §9).

### M3 — It speaks
> **Done when:** narration is generated and the highlight tracks playback.

- **3.1** — NS-01, SF-16
- **3.2** — NS-02, NS-03
- **3.3** — NS-04, NS-05, NS-06
- **3.4** — SF-17, SF-32
- **3.5** — SF-18
- **3.6** — SF-42

⭐ **The synthesis run is decoupled from the milestone gate.** A large corpus is plausibly a
multi-day run on a CPU-default engine, so it runs in the background and the next milestone
does not wait for it.

### M4 — It is served
> **Done when:** the site has an origin, an API, and records practice passes.

- **4.1** — SF-21, OPS-05
- **4.2** — SF-19a
- **4.3** — SF-19b, SF-28, SF-37, SF-38, SF-39, SF-40, SF-43
- **4.4** — SK-03, SK-06

⭐ **The order after `M4` is the user's (2026-09-12):** the framework is proved on
`ISO-8583` first (`M6`, `M8`), then the execution track (`M5`, `M7`), and the Java corpus
re-validates last. Spec §8.1 and §12, amended, quote the user's words.

### M6 — The first corpus reads
> **Done when:** `ISO-8583-jPOS-tutorial` opens offline over `file://`, narrated,
> navigable, with read marks recorded — minus what the source genuinely lacks,
> stated positively.

⭐ **Delivered by the corpus**, in its own repository, by the integration agent. Every
framework capability it uses is `M0`–`M4`'s, and each gap it meets is a finding (R19).

### M8 — It is a framework
> **Done when:** `ISO-8583` has been converted **by the skills alone**, and the
> findings that produced are written down.

- **8.1** — QA-04

⭐ **The deliverable is the findings log, not the site** (spec §12). Whoever integrates does
not modify `studyforge` — findings, not patches.

---

⛔ **The execution track is entered by material that admits a checkable coding task**, because
exercises are
[authored at ingestion](../specs/2026-09-08-studyforge-v1-design.md#exercises-authored-for-every-corpus-w389).
Material that admits none gets the quiz shape, which needs no container and sits on the
reading floor. Stopping short of the track is still a pass.

### M5 — It runs code
> **Done when:** a reader edits a unit's file, runs one command from their
> terminal, and the unit's test runs against it through the runner — a file with
> no test is not a failure — and Run and Submit from the page give real output and
> a real verdict.

- **5.1** — TC-00, SF-20
- **5.2** — SF-29, SF-22, SF-44

### M7 — It has practices
> **Done when:** a practice opens in the page's panel with the embedded editor, Run
> and Submit work from it, and only a passing Submit completes the practice.

- **7.1** — TC-01
- **7.2** — TC-02, TC-03, TC-04
- **7.3** — TC-05, TC-06
- **7.4** — SK-09, SF-24
- **7.5** — QA-02

⭐ **The order after `M7` is the user's (2026-09-19):** `M10`, then `M11`, then `M9`. `M10` is,
in the user's words, one of the core ideas of the project: *"Bottom line we are building
CodeSignal or LeetCode with the idea of LLM extracting the content from a given source and make
it an enjoyable interactive easy to read and navigate website."*

### M10 — Every corpus has practices
> **Done when:** a corpus's pages carry exercises authored for it — from the source's own examples, practice code and
> tests where it has them, and by an LLM from the page's material where it has none — each a real-life task that states
> the ask, graded by tests of the main ask and of every edge case, with the number of exercises per page following its
> content, length and difficulty; ⛔ **nothing the source already has is lost**; ⭐ proved on `ISO-8583`.

- **10.1** — AX-00, AX-01, AX-05
- **10.2** — AX-02, AX-03, AX-04, AX-06
- **10.3** — AX-07, AX-08, AX-09, AX-10
- **10.4** — the first corpus's own work, by the integration agent in its repository:
  re-onboard it, the pilot, then the rest of its pages
- **10.5** — AX-11

⭐ **The design principle, the user's:** the goal is to activate the reader — to practise what
they just learned — ⛔ **without losing any existing material or example.** The honesty R5
protects survives as gates: a generated test passes on a reference solution, fails on the
starter, and each edge-case test fails on a planted incomplete solution.

### M11 — It is release-ready
> **Done when:** a clean checkout of each repository's main installs and works; the process history (tooling, board,
> archive, rows, handoffs) lives on an archive branch in the same repository; the board is light; the epics are
> high-level design; and the next corpus needs only the README and the skills.

- **11.1** — REL-01
- **11.2** — REL-02, REL-03
- **11.3** — REL-04, REL-05, REL-06
- **11.4** — REL-07, REL-08, REL-09
- **11.5** — REL-10, REL-11, REL-12, REL-13; and the first corpus's own cleanup, by the
  integration agent in its repository: re-onboard it on the installed library, advance its
  main to its pin, prune its merged branches and idle worktrees
- **11.6** — REL-14

⭐ **The tasks are [`E15`](E15-release-ready.md)**, built on the user's six rulings of
2026-09-19, which are settled and not re-asked. The order is argued there: distil, decouple,
package, sort, move, read.

⛔ **Registry publishing and the Python floor are not in this milestone** — each waits on a
future user ruling.

### M9 — The Java corpus re-validates
> **Done when:** `Claude-senior-java-engineer` is a narrated study site with
> gate-clearing exercises, converted under §12's rules, and the findings that
> produced are written down.

- **9.1** — JS-01, JS-02, EX-00 *(needs TC-00's pinned image)*
- **9.2** — JS-03, JS-04
- **9.3** — JS-05, JS-06, EX-01
- **9.4** — OPS-01, OPS-02, EX-02, EX-03
- **9.5** — OPS-03, EX-04
- **9.6** — EX-05, SK-04, OPS-04
- **9.7** — OPS-06, OPS-07, SF-41
- **9.8** — QA-01, QA-05

⚠️ **This is a consumer, not the framework.** It is the largest and most demanding source
available, which makes it a good proving ground and a bad starting point. ⛔ **`EX-00` gates
all of `E08`**, and is the first thing done whenever `E08` starts. ⛔ **The no-patch rule holds
for the whole of `M9`** (spec §12).

---

## Epics

| Epic | Document | Tasks | Owns |
|---|---|---|---|
| E00 | [Foundations](E00-foundations.md) | FND-01…04, 05a, 06, 07 | scaffolding, dev container, fixtures, the workspace pin file, the R7 check |
| E01 | [Core contracts](E01-core-contracts.md) | SF-01…05, SF-31, SF-33, SF-35, SF-36 | address, manifest, placement, dry-run, discovery, container map, version guard, the third content state, sub-file origins |
| E02 | [Content pipeline](E02-content-pipeline.md) | SF-06…10 | archive, Markdown, gate, overlay, unit document |
| E03 | [Rendering](E03-rendering.md) | SF-11…15, SF-27, SF-34 | assets, page, contents, index, navigation, page chrome |
| E04 | [Narration](E04-narration.md) | SF-16…18, SF-32 | speakable, synthesis, player sync, media footprint |
| E05 | [Serving & execution](E05-serving-execution.md) | SF-19a/b, SF-20…22, SF-29, SF-30, SF-44 | API, runner, progress, reader state, Run/Submit, the terminal command |
| E06 | [Exercise contract](E06-exercise-contract.md) | SF-23…24 | workspace, trust, practice panel |
| E07 | [Java adapter](E07-java-adapter.md) | JS-01…06 | curriculum, lessons, pairing, emission, audit |
| E08 | [Java exercises](E08-java-exercises.md) | EX-00…05 | blanking, the two gates, emission, coverage |
| E09 | [Delivery](E09-delivery.md) | OPS-01…07, SF-28 | compose, build pipeline, guarantees, docs — mostly `SK-07`'s output |
| E10 | [Validation & QA](E10-validation-qa.md) | SF-25, SF-26, QA-01…05 | validate CLI, harness, acceptance, the second source, the re-validation |
| E11 | [Skills & authoring](E11-skills-authoring.md) | SK-01…09 | **the product** (R16, R19) |
| E12 | [Toolchain image](E12-toolchain-image.md) | TC-00…06 | the runner image, then the shared code-server repo (§8.1) |
| E13 | [Narration service](E13-narration-service.md) | NS-01…06 | shared synthesis repo (§8.2) |
| E14 | [Authored exercises](E14-authored-exercises.md) | AX-00…11 | exercises for every corpus — the record's cases, the authoring gates, the bundle, the quiz shape, the skill, the panel |
| E15 | [Release-ready](E15-release-ready.md) | REL-01…14 | the release — the decisions file, the product suite without the tooling, the skills in the package, the archive branch, the light board, the close from a clean checkout |

Future work: [v2-backlog.md](v2-backlog.md).

---

## Working as two agents

The plan is built to be run by **two agents on two sets of repositories**, and the seams that
make that safe exist — R2 puts the adapter contract on disk, and `studyforge validate` is a
green/red signal that depends on nobody's judgement.

| | Owns | Epics |
|---|---|---|
| **Framework agent** | `studyforge`, `code-server-toolchain`, `narrate-service` | E00–E06, E10, E11, E12, E13, E14, E15 |
| **Integration agent** | a corpus repository | E07, E08, and what survives of E09 |

⭐ **The skills belong to the framework agent, not the integrator.** That is what makes the
integrator's job small: supply the source-specific reading, and report what the skills could
not do. The integration agent plans with the delivery-planning skill (`SK-08`), which acts as
the product owner for that repository. ⛔ **Its only channel to the framework is questions and
findings.** It may not patch `studyforge` (§12) and it may not read the extraction source
(R20) — what it would have gone looking for there lives in the
[integration catalogue](../integration-catalogue.md).

**Three seams cross between them, and each has a contract:**

1. **The archive** — R2 plus `studyforge validate` (`SF-25`).
2. **Placement** — `studyforge plan` (`SF-31`).
3. **Runtime** — each shared component's `consuming.json` (`TC-05`, `E13`). A consumer never
   reads a Dockerfile to work out how to run something; that is the first step toward
   forking it (R18).

---

## Task fields

| Field | Meaning |
|---|---|
| **Milestone** | Which milestone it belongs to; the step is in this document. |
| **Depends on** | Hard dependencies. Nothing else blocks it. |
| **Team** | `solo` · `pair` (two rounds or a reviewer) · `team` (dispatch a small team; subtasks listed). |
| **Context** | The files to read, and the budget for reading them. It does not price the work. |
| **Effort** | Present only where the deliverable is a computation rather than a change — a build, a synthesis run, a spike, a bulk emission. |
| **Owns** | The surface this task creates or changes. One task, one surface. |
| **Definition** | What the deliverable *is*. Design-level, not implementation. |
| **Acceptance** | Verifiable conditions. Green/red, no judgement calls. |

## Standing rules for every task

- Standard library only in framework source; test-only dependencies excepted.
- Tests are part of the task (R12), never a follow-up.
- No source module over 400 lines, no test module over 600, or the exception is justified in
  the docstring (R11).
- The search path is `git grep`, `grep -rn` and `sed -n`.
- A gate is reported GREEN or RED with its exit code.
- ⛔ **No acceptance condition is satisfied by an untracked artifact alone.** If what a task
  produces is git-ignored, the task ships the check, because the check travels on the branch
  and the artifact does not.
- R7 (no personal data) and R10 (byte-for-byte reproducible) apply everywhere and are not
  restated per task.
- Every task implicitly depends on `M0`.

**Repository shorthand**, all relative to the **workspace root** — the parent directory
holding every component as a sibling (R18). Never write an absolute path into a file: it
carries a home directory, which is personal data (R7). ⚠️ `CS/` and `CSD/` appear only in
framework-side tasks (R20).

`SF/` = `studyforge/` (this repo) · `CS/` = `CodeSignal/.pipeline/` · `CSD/` =
`CodeSignal/` (docker, compose) · `JS/` = `Claude-senior-java-engineer/` ·
`ISO/` = `ISO-8583-jPOS-tutorial/` · `SPARQL/` = `Claude-SPARQL-tutorial/` ·
`TC/` = `code-server-toolchain` · `NS/` = `narrate-service`.
