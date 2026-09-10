# studyforge — task index

**86 tasks · 13 epics · 9 milestones.** ⭐ **Live status is
`BOARD.md`**, not this file: this one orders the work, that one says where it is.
Companion to
`../specs/2026-09-08-studyforge-v1-design.md`, whose rulings **R1–R21** every
task cites.

⚠️ **Revised 2026-09-09.** Two revisions the same day; the second is the one that
moved the furniture.

**The plan is no longer built around the Java corpus.** The first consumer is a
**small** source, so the framework reaches a complete, useful state early and the
166-unit Java tutorial becomes a consumer like any other. Concretely:
**M0–M4 are the reading floor** — a narrated, navigable, offline site, which is
the *whole product* for prose material — and **M5 onward is the execution
track**, which a corpus enters only if its material is runnable (spec §11.0).
Narration now comes **before** serving, because R8's floor is `file://` and a
reader needs no server. `EX-00` and all of E12 left M0; no milestone is named
after a corpus any more.

**Seven tasks added** — `TC-00` (a pinned build image, so EX-00 can run at all),
`SF-31` (the placement dry-run), `SF-30` (reader state on the `file://` floor),
`SF-32` (the media footprint policy), `SK-07` (corpus onboarding), `SK-08`
(delivery planning — the **product owner** for an integration), `SK-09`
(execution onboarding). One milestone added (**M8**). The skills resequenced out
of M7, because a skill written after the thing it produces is a retrospective
(spec §9). `OPS-05` moved into the framework; `SK-03` now wraps the framework CLI
rather than a consumer's pipeline. ⭐ **Generated media is committed by default**
(SF-17), with SF-32 refusing loudly at the ceiling. **R20** makes the extraction
one-way: this framework mines CodeSignal, and no client application sees it. See
`handoffs/DOC-2026-09-09-codesignal-drift.md`.

## Ordering principle

Tasks are ordered into **milestones, not layers.** Each milestone ends in
something that demonstrably works, so the project is usable early and stays
usable — rather than accumulating nine layers that only become a product at the
end.

The cost of this is real and worth naming: M1 does a lot of contract work for
one page. The alternative — build every contract, then every renderer, then
every service — hides all integration risk until the end, and integration risk
is the kind that reorders plans.

| | Milestone | What works when it lands | Tasks |
|---|---|---|---|
| **M0** | Foundations | An agent can start work without inventing anything | 6 |
| **M1** | One page renders | A unit page from a fixture opens in a browser | 17 |
| **M2** | **A corpus is readable** | Any corpus, offline, with contents, navigation and read marks — **and the skills that built it** | 12 |
| **M3** | It speaks | Narration with highlight sync, and an honest media footprint | 10 |
| **M4** | It is served | An origin, an API, and a record of practice passes | 7 |

⭐ **A prose corpus is finished at M4.** Everything below is the **execution
track**, entered only by material that is actually runnable (spec §11.0). A
corpus with no graders that stops here is complete, not short.

| | Milestone | What works when it lands | Tasks |
|---|---|---|---|
| **M5** | It runs code | Run and Submit against a pinned toolchain | 12 |
| **M6** | The Java corpus reads | 166 units, narrated and navigable | 9 |
| **M7** | The Java corpus has practices | Real exercises with proven graders | 12 |
| **M8** | **It is a framework** | A further, unnamed source converted by the skills alone | 1 |

**M2 is the biggest single jump in value** — it is the first state you would
actually use, and for a prose corpus it is most of the way to done. **M1 is the
riskiest** — it is where every contract meets every other one for the first
time, which is exactly why it comes first rather than last.

---

## Milestones in detail

Within a milestone, each **step** runs in parallel; steps are sequential.

⭐ **The spine is the reading floor** (spec §11.0). M0–M4 build a framework that
turns material into a narrated, navigable, offline study site, and that is a
**complete product** for any corpus whose material is prose. Everything from M5
on is the **execution track** — workspaces, containers, graded practices — which
a corpus earns by having runnable material, and which most corpora will not.

⛔ **No milestone is named after a corpus.** An earlier plan called M2 *"the Java
material is readable"*, which welded the framework's definition of done to one
source's shape. The framework's milestones are proved against the `FND-04`
fixtures — one depth-1, one depth-2 — and any corpus rides them.

### M0 — Foundations
> **Done when:** an agent can pick up any task without inventing a layout,
> hunting for a graph, or building its own fixtures.

- **0.1** — FND-01, FND-02, FND-04 *(parallel)*
- **0.2** — FND-03, FND-06, FND-05a *(parallel)*

⚠️ **M0 is two steps, not one, and the earlier "all parallel" was wrong.**
`FND-03`'s acceptance is that the suite runs, and there is no suite until
`FND-01` lands; `FND-06` extends the same quality floor `FND-01` establishes.
`FND-05a` is in 0.2 only because it is the least urgent — nothing in M1 imports
the parent workspace.

⚠️ **`FND-05` split on 2026-09-09, then `FND-05b` cancelled the same day**
(CTO rulings 2 and round 3). The split was right: left whole, the task made M0
permanently unachievable, and M0 gates the entire plan. ⛔ **The cancellation
followed from a standing decision that nothing is ever pushed to any remote**, so
git submodules have no legal form here (R18, amended) — an absolute local path in
`.gitmodules` is an R7 violation, a relative URL resolves against a parent remote
that does not exist, and a real remote names a commit nobody pushed. ⭐ `FND-05a`
keeps the parent, the workflow and **a tracked pin file that is verified against
the local checkouts** — the pin was always the valuable half of a submodule, and
only the fetch depended on pushing. Every component is recorded there, including
`studyforge`, `TC/` and `NS/` as E12 and E13 create them.

⭐ **`FND-06` is new**: R7 enforced by the build instead of by a reviewer's grep.
It is not `SF-08` — that gates strings entering the *archive*, this gates strings
entering the *repository*.

### M1 — One page renders
> **Done when:** a unit page from the depth-1 fixture opens in a browser, with
> styles and highlighting, over `file://`.

- **1.1** — SF-01, SF-02, SF-07, SF-08, SF-11, **SF-33** · ⚠️ **plus `FND-04`'s
  follow-up, which gates SF-07** (`BOARD.md`)

⭐ **Ordering inside this step matters, and `BOARD.md` carries it.** `SF-01` is
the **exemplar** — the first framework contract, whose conventions the next
fourteen tasks copy — so it merges before anything else in M1. `SF-07` is gated
by `FND-04`'s follow-up steps 1–4: the `disclosure` fixture is its acceptance
input, and a task cannot demonstrate a ruling against a fixture that does not
carry it.
- **1.2** — SF-03, SF-05, SF-06
- **1.3** — SF-09, SF-23, SF-25, SK-01 · **FND-07**
- **1.4** — SF-10
- **1.5** — SF-12, QA-03

*Why SF-23 is here:* SF-10 must know the workspace shape to be built once rather
than revisited — the contract is cheap and it keeps the archive right even for a
corpus that will never have an exercise. *Why SF-04 is not:* one page needs no
discovery.

### M2 — A corpus is readable
> **Done when:** a whole corpus opens offline with a working index, deep links,
> prev/next and read marks — **and the skills that produced it exist.**
> **This is the first genuinely useful state.**

- **2.1** — SF-04, SF-31, SK-02
- **2.2** — SK-07, SK-05, SK-08, SF-13
- **2.3** — SF-14, SF-27
- **2.4** — SF-15, SF-26, SF-30

⚠️ **The skills come with this milestone, not after it.** `SK-02` scaffolds an
adapter and `SK-07` onboards a repository; a corpus built before they exist is a
corpus they can only claim retrospectively (spec §9).

### M3 — It speaks
> **Done when:** narration is generated and the highlight tracks playback.

⭐ **Narration comes before serving, and the order matters.** R8 puts the floor at
`file://` — a reader opens a page by double-clicking it. So a narrated, navigable
corpus is a **finished product with no server at all**, and putting the API
first would have delayed the last piece of the reading floor behind something no
reader needs.

⭐ **The synthesis RUN is decoupled from the milestone gate.** A large corpus is
plausibly a multi-day run on a CPU-default engine. Start it in the background
once SF-16 lands and let the next milestone begin without waiting for it.

- **3.1** — NS-01, SF-16
- **3.2** — NS-02, NS-03
- **3.3** — NS-04, NS-05, NS-06
- **3.4** — SF-17, SF-32
- **3.5** — SF-18

### M4 — It is served
> **Done when:** the site has an origin, an API, and records practice passes.

- **4.1** — SF-21, OPS-05
- **4.2** — SF-19a
- **4.3** — SF-19b, SF-28
- **4.4** — SK-03, SK-06

⚠️ **M4 is a serial bottleneck wearing a milestone's name.** SF-19a is one task
carrying a very large share of the port surface, it cannot be split further, and
a second agent does not help. Plan around it rather than discovering it.

---

⛔ **Everything below is the execution track, and a corpus enters it only if its
material is runnable** (spec §11.0, §7's three states). A corpus with no graders
that stops after M4 is **complete**, not short.

### M5 — It runs code
> **Done when:** a reader edits a workspace and gets real output from Run and a
> real verdict from Submit.

- **5.1** — TC-00, TC-01, SF-20
- **5.2** — TC-02, TC-03, TC-04, SF-29
- **5.3** — TC-05, TC-06
- **5.4** — SK-09, SF-22
- **5.5** — SF-24

### M6 — The Java corpus reads
> **Done when:** the 166-unit Java tutorial is a working, narrated study site.

- **6.1** — JS-01, JS-02
- **6.2** — JS-03, JS-04
- **6.3** — JS-05, JS-06
- **6.4** — OPS-01, OPS-02
- **6.5** — OPS-03

⚠️ **This is a consumer, not the framework.** It is the largest and most
demanding source available, which makes it a good proving ground and a bad
starting point — everything it needs, it needs *because of what it is*, and a
framework shaped around it would be a Java tutorial generator.

⭐ **By the time this milestone starts, the framework is finished and proven.**
These tasks are the source-specific reading plus whatever `SK-07` could not
generate — and every one of the latter is a **finding** (R19), not work to be
quietly absorbed.

### M7 — The Java corpus has practices
> **Done when:** gate-clearing exercises ship with authoritative graders, and
> the coverage report says honestly how many.

- **7.1** — EX-00  *(needs TC-00's pinned image)*
- **7.2** — EX-01
- **7.3** — EX-02, EX-03
- **7.4** — EX-04
- **7.5** — EX-05, SK-04, OPS-04
- **7.6** — OPS-06, OPS-07
- **7.7** — QA-01, QA-02

⛔ **EX-00 still gates all of E08**, and it is still a one-agent-day spike whose
negative result is a success. It moved out of M0 because the exercise strategy is
no longer on the first delivery's path — but it remains the **first thing** done
whenever E08 starts, for the original reason: it moves the largest unknown to the
front rather than discovering it at the end.

⚠️ **E08 is Java-specific and depends on the Java adapter** — `EX-01` on `JS-04`'s
pairings, `EX-02` on `OPS-01`'s image. It cannot precede M6, which is why
practices are a milestone of *this consumer* rather than of the framework.

### M8 — It is a framework
> **Done when:** a further, unnamed repository has been converted **by the skills
> alone**, and the findings that produced are written down.

- **8.1** — QA-04

⭐ **The deliverable is the findings log, not the site** (spec §12). ⛔ Whoever
integrates does not modify `studyforge` — findings, not patches.

**Critical path.** FND-01 → SF-01 → SF-03 → SF-31 → SK-02 → SK-07 → SF-10 →
SF-12 → SF-04 → SF-13 → SF-16 → SF-17 → SF-19a → SF-28 → SF-22 → EX-04 →
OPS-04 → QA-01 → QA-04.

---

## Epics

| Epic | Document | Tasks | Owns |
|---|---|---|---|
| E00 | [Foundations](E00-foundations.md) | FND-01…04, 05a, 06, 07 | scaffolding, graphify, dev container, fixtures, the workspace pin file, the R7 check, the index tripwire |
| E01 | [Core contracts](E01-core-contracts.md) | SF-01…05, SF-31, SF-33 | address, manifest, placement, dry-run, discovery, container map, version guard |
| E02 | [Content pipeline](E02-content-pipeline.md) | SF-06…10 | archive, Markdown, gate, overlay, unit document |
| E03 | [Rendering](E03-rendering.md) | SF-11…15, SF-27 | assets, page, contents, index, navigation |
| E04 | [Narration](E04-narration.md) | SF-16…18, SF-32 | speakable, synthesis, player sync, media footprint |
| E05 | [Serving & execution](E05-serving-execution.md) | SF-19a/b, SF-20…22, SF-29, SF-30 | API, runner, progress, reader state, Run/Submit |
| E06 | [Exercise contract](E06-exercise-contract.md) | SF-23…24 | workspace, trust, practice panel |
| E07 | [Java adapter](E07-java-adapter.md) | JS-01…06 | curriculum, lessons, pairing, emission, audit |
| E08 | [Java exercises](E08-java-exercises.md) | **EX-00**, EX-01…05 | blanking, the two gates, emission, coverage |
| E09 | [Delivery](E09-delivery.md) | OPS-01…07, SF-28 | compose, build pipeline, guarantees, docs — **mostly SK-07's output** |
| E10 | [Validation & QA](E10-validation-qa.md) | SF-25, SF-26, QA-01…04 | validate CLI, harness, acceptance, **the second source** |
| E11 | [Skills & authoring](E11-skills-authoring.md) | SK-01…09 | **the product** (R16, R19) |
| E12 | [Toolchain image](E12-toolchain-image.md) | TC-00…06 | shared code-server repo (§8.1) |
| E13 | [Narration service](E13-narration-service.md) | NS-01…06 | shared synthesis repo (§8.2) |

Future work: [v2-backlog.md](v2-backlog.md).

---

## Working as two agents

The plan is built to be run by **two agents on two sets of repositories**, and
the seams that make that safe already exist — R2 puts the adapter contract on
disk, and `studyforge validate` is a green/red signal that depends on nobody's
judgement.

| | Owns | Epics |
|---|---|---|
| **Framework agent** | `studyforge`, `code-server-toolchain`, `narrate-service` | E00–E06, E10, E11, E12, E13 |
| **Integration agent** | a corpus repository | E07, E08, and what survives of E09 |

⭐ **The skills belong to the framework agent, not the integrator.** That is what
makes the integrator's job small: supply the source-specific reading, and report
what the skills could not do.

**The integration agent plans with `SK-08`** — the delivery-planning skill,
which acts as the **product owner** for that repository: it cuts the work into
tasks that each end in something demonstrable, writes acceptance the framework
can evaluate, and exports to the tracker. ⛔ **Its only channel to the framework
is questions and findings.** It may not patch `studyforge` (§12) and it may not
read the extraction source (R20) — what it would have gone looking for there
lives in the **integration catalogue** in this repository, which it also grows.

**Three seams cross between them, and all three now have a contract:**

1. **The archive** — R2 plus `studyforge validate` (SF-25). This one was always
   right, and it is the best-designed thing in the plan.
2. **Placement** — `studyforge plan` (SF-31). Previously nothing: the integrator
   had to write ignore rules and declare `permitted_edits` with no way to ask
   what the framework would create.
3. **Runtime** — each shared component's `consuming.json` (TC-05, E13).
   Previously prose. ⛔ A consumer never reads a Dockerfile to work out how to
   run something; that is the first step toward forking it (R18).

⛔ **During M8 the integration agent does not modify `studyforge`.** Findings,
not patches. See spec §12.

---

## Before picking up any task

1. `../specs/2026-09-08-studyforge-v1-design.md` — §1–§4 and all of R1–**R20**.
2. Your **epic document** — shared context for your task's neighbours.
3. `../conventions/module-structure.md` — size, packages, tests, templates.
4. `../conventions/graphify.md` — ask the graph before exploring (R14).
5. `../conventions/agent-protocol.md` — how to work and how to hand off.
6. `../conventions/review-rubric.md` — the merge gate your work is judged by.
7. `handoffs/` — notes from the tasks you depend on.

## Task fields

| Field | Meaning |
|---|---|
| **Milestone** | Which milestone it belongs to; the step is in this document. |
| **Depends on** | Hard dependencies. Nothing else blocks it. |
| **Team** | `solo` · `pair` (two rounds or a reviewer) · `team` (dispatch a small team; subtasks listed). |
| **Context** | The files to read, and the budget for **reading them**. Stay under ~200k per session; a task that cannot is already split. ⛔ **It does not price the work.** |
| **Effort** | Present only where the deliverable is a **computation** rather than a change — a graph build, a synthesis run, a spike, a bulk emission. Its absence means the work is proportionate to the reading. |
| **Owns** | The package this task creates. One task, one surface. |
| **Definition** | What the deliverable *is*. Design-level, not implementation. |
| **Acceptance** | Verifiable conditions. Green/red, no judgement calls. |

⛔ **`Context` prices reading and nothing else, and conflating the two was a real
defect.** `FND-02`'s read list was small and correct; the task still ran roughly
an order of magnitude over its ~20k, because building a graph is a 12-chunk
parallel extraction over 217 documents — **work, not reading**. ⭐ Any task whose
deliverable is a computation is mispriced by construction under a single number,
so those tasks carry an **Effort** line and the rest do not. Adding a field is
cheaper than re-estimating eighty-four tasks, and it puts the estimate where the
person who can make it is standing.

## Standing rules for every task

- Standard library only in framework source; test-only dependencies excepted.
- Tests are part of the task (R12), never a follow-up.
- No source module over 400 lines, no test module over 600, or the exception is
  justified in the docstring (R11).
- Ask the graph before exploring (R14).
- Write your handoff before you finish.
- ⛔ **No acceptance condition is satisfied by an untracked artifact alone.** If
  what a task produces is git-ignored, ⭐ **the task ships the check, because the
  check travels on the branch and the artifact does not.** An acceptance nobody
  can re-verify from the repository will be recorded as done and be false
  everywhere but the checkout it ran in.
- R7 (no personal data) and R10 (byte-for-byte reproducible) apply everywhere
  and are not restated per task.
- **Every task implicitly depends on M0.** FND-01's package layout and FND-04's
  fixtures are prerequisites of every framework task; a *Depends on* field lists
  only what is additional to them. `EX-00` blocks all of E08.

**Repository shorthand**, all relative to the **workspace root** — the parent
directory holding every component as a sibling (R18, FND-05a). Never write an
absolute path into a file: it carries a home directory, which is personal data
(R7).

⚠️ **`CS/` and `CSD/` appear only in framework-side tasks (R20).** They are the
extraction source, and a consumer repository's task never cites a path inside
them — what a consumer needs is carried here.

`SF/` = `studyforge/` (this repo) · `CS/` = `CodeSignal/.pipeline/` · `CSD/` =
`CodeSignal/` (docker, compose) · `JS/` = `Claude-senior-java-engineer/` ·
`ISO/` = `ISO-8583-jPOS-tutorial/` · `SPARQL/` = `Claude-SPARQL-tutorial/` ·
`TC/` = `code-server-toolchain` · `NS/` = `narrate-service`.
