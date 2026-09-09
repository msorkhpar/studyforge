# studyforge — task index

**80 tasks · 13 epics · 9 milestones.** Companion to
`../specs/2026-09-08-studyforge-v1-design.md`, whose rulings **R1–R19** every
task cites.

⚠️ **Revised 2026-09-09.** Four tasks added — `TC-00` (a pinned build image, so
EX-00 can run at all), `SF-31` (the placement dry-run), `SF-30` (reader state on
the `file://` floor), `SK-07` (corpus onboarding) — one milestone added (**M8**,
the second source), and the skills resequenced: **SK-01, SK-02, SK-05 and SK-07
move from M7 to M1–M2**, because a skill written after the thing it produces is
a retrospective (spec §9). `OPS-05` moved out of the Java corpus into the
framework. See `handoffs/DOC-2026-09-09-codesignal-drift.md` for the reasoning.

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
| **M0** | Foundations | An agent can start work without inventing anything; **exercise feasibility is known** | 8 |
| **M1** | **One page renders** | A unit page from a fixture opens in a browser | 18 |
| **M2** | **The Java material is readable** | All 166 units, offline, with contents, navigation and read marks | 19 |
| **M3** | It is served | The site has an origin, an API, and records passes | 5 |
| **M4** | It speaks | Narration with highlight sync | 10 |
| **M5** | It runs code | Run and Submit against a dockerised toolchain | 6 |
| **M6** | It has practices | Real exercises with proven graders | 5 |
| **M7** | It is a product | Built by skills, documented, accepted | 8 |
| **M8** | **It is a framework** | A second, unnamed source converted by the skills alone | 1 |

**M2 is the biggest single jump in value** — it is the first state you would
actually use. **M1 is the riskiest** — it is where every contract meets every
other one for the first time, which is exactly why it comes first rather than
last.

---

## Milestones in detail

Within a milestone, each **step** runs in parallel; steps are sequential.

### M0 — Foundations
> **Done when:** an agent can pick up any task without inventing a layout,
> hunting for a graph, or building its own fixtures.

- **0.1** — FND-01, FND-02, FND-03, FND-04, FND-05, **TC-00**, TC-01 *(all parallel)*
- **0.2** — **EX-00**  *(needs TC-00's image)*

⛔ **EX-00 gates all of E08.** It is a spike: run `mvn test` for a baseline, then
hand-gate ten pairs across the shape spectrum. If the exercise approach does not
yield, we find out in week one rather than at M6.

⚠️ **EX-00 was scheduled with no dependencies and could not have run.** It must
build, the toolchain image was M5, and R15 forbids taking a JDK from whoever's
host it lands on — while EX-00's headline output is a *wall-clock measurement*
that decides the shape of all of E08. `TC-00` is a minimal pinned JDK+Maven
image that exists only to unblock it.

⭐ **E12 now starts here, and E13 can too.** Neither depends on anything in the
framework, and both were scheduled at M4/M5 behind milestones they do not need.
Under a two-agent split they are the only work available to the framework agent
while its own critical path is blocked — and ⛔ **`SK-07` at M2 cannot render a
compose file until `TC-05` has published its consuming contract**, which is what
actually forced E12 earlier rather than merely permitted it.

### M1 — One page renders
> **Done when:** a unit page from the depth-1 fixture opens in a browser, with
> styles and highlighting, over `file://`.

- **1.1** — SF-01, SF-02, SF-07, SF-08, SF-11
- **1.2** — SF-03, SF-05, SF-06, TC-02, TC-03, TC-04
- **1.3** — SF-09, SF-23, SF-25, **SK-01**
- **1.4** — SF-10
- **1.5** — SF-12, QA-03

*Why SF-23 is here:* SF-10 must know the workspace shape to be built once
rather than revisited. *Why SF-04 is not:* one page needs no discovery.

### M2 — The Java material is readable
> **Done when:** all 166 units open offline with a working index, deep links
> and prev/next. **This is the first genuinely useful state.**

- **2.1** — SF-04, **SF-31**, **SK-02**, TC-05, TC-06
- **2.2** — **SK-07**, **SK-05**, SF-13
- **2.3** — JS-01, JS-02, SF-14
- **2.4** — JS-03, JS-04, SF-15, SF-26, SF-27, **SF-30**
- **2.5** — JS-05, JS-06

⚠️ **The adapter now comes after the skills that scaffold it**, which is the
single largest reordering in this revision. `SK-02` produces E07's package
structure and `SK-07` produces E09's deployment artifacts; E07 and E09 fill in
what is genuinely source-specific. Reversing this is how the skills become a
retrospective.

### M3 — It is served
> **Done when:** the site is served, the contents API answers, progress records.

- **3.1** — SF-21, **OPS-05**
- **3.2** — SF-19a
- **3.3** — SF-19b, SF-28

⚠️ **M3 is a serial bottleneck wearing a milestone's name.** SF-19a is one task
carrying a very large share of the port surface, it cannot be split further, and
a second agent does not help. Plan around it rather than discovering it.

### M4 — It speaks
> **Done when:** the narration pipeline works end to end and the highlight
> tracks playback on generated units.

⭐ **The synthesis RUN is decoupled from the milestone gate.** 365,158 words is
roughly 40 hours of audio and ~20–25k clips on a CPU-default engine — plausibly
a multi-day run. Start it in the background once SF-16 lands and **let M5 begin
without waiting for it.** Narration arrives when it arrives; nothing on the
critical path queues behind a TTS job.

- **4.1** — NS-01, SF-16
- **4.2** — NS-02, NS-03
- **4.3** — NS-04, NS-05, NS-06
- **4.4** — SF-17, OPS-02
- **4.5** — SF-18

### M5 — It runs code
> **Done when:** a reader edits a workspace and gets real output from Run and a
> real verdict from Submit.

- **5.1** — SF-20
- **5.1b** — SF-29
- **5.4** — OPS-01  *(E12 landed at M0–M2)*
- **5.5** — SF-22, OPS-03
- **5.6** — SF-24

### M6 — It has practices
> **Done when:** gate-clearing exercises ship with authoritative graders, and
> the coverage report says honestly how many.

- **6.1** — EX-01  *(EX-00 landed in M0)*
- **6.2** — EX-02, EX-03
- **6.3** — EX-04
- **6.4** — EX-05

### M7 — It is a product
> **Done when:** the Java corpus is rebuilt end to end **by the skills**, and
> spec §11's acceptance passes.

- **7.1** — OPS-04
- **7.2** — OPS-07
- **7.3** — SK-03, SK-04, OPS-06
- **7.4** — SK-06
- **7.5** — QA-01, QA-02

### M8 — It is a framework
> **Done when:** a second, unnamed repository has been converted **by the skills
> alone**, and the findings that produced are written down.

- **8.1** — QA-04

⭐ **The deliverable is the findings log, not the site** (spec §12). An exercise
that produces a working study site and reports no findings has not been
conducted honestly: these skills will have seen exactly one source. ⛔ **Whoever
integrates the second source does not modify `studyforge`** — the framework pin
does not move, and anything the framework cannot do is filed as a finding rather
than patched. A test of extensibility run by somebody who can edit the thing
being tested measures nothing.

**Critical path.** FND-01 → SF-01 → SF-03 → SF-31 → SK-02 → SK-07 → SF-10 →
SF-12 → SF-04 → SF-13 → SF-19a → SF-19b → SF-22 → EX-04 → OPS-04 → QA-01 → QA-04.

---

## Epics

| Epic | Document | Tasks | Owns |
|---|---|---|---|
| E00 | [Foundations](E00-foundations.md) | FND-01…05 | scaffolding, graphify, dev container, fixtures, submodules |
| E01 | [Core contracts](E01-core-contracts.md) | SF-01…05, SF-31 | address, manifest, placement, dry-run, discovery, container map |
| E02 | [Content pipeline](E02-content-pipeline.md) | SF-06…10 | archive, Markdown, gate, overlay, unit document |
| E03 | [Rendering](E03-rendering.md) | SF-11…15, SF-27 | assets, page, contents, index, navigation |
| E04 | [Narration](E04-narration.md) | SF-16…18 | speakable, synthesis, player sync |
| E05 | [Serving & execution](E05-serving-execution.md) | SF-19a/b, SF-20…22, SF-29, SF-30 | API, runner, progress, reader state, Run/Submit |
| E06 | [Exercise contract](E06-exercise-contract.md) | SF-23…24 | workspace, trust, practice panel |
| E07 | [Java adapter](E07-java-adapter.md) | JS-01…06 | curriculum, lessons, pairing, emission, audit |
| E08 | [Java exercises](E08-java-exercises.md) | **EX-00**, EX-01…05 | blanking, the two gates, emission, coverage |
| E09 | [Delivery](E09-delivery.md) | OPS-01…07, SF-28 | compose, build pipeline, guarantees, docs — **mostly SK-07's output** |
| E10 | [Validation & QA](E10-validation-qa.md) | SF-25, SF-26, QA-01…04 | validate CLI, harness, acceptance, **the second source** |
| E11 | [Skills & authoring](E11-skills-authoring.md) | SK-01…07 | **the product** (R16, R19) |
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

1. `../specs/2026-09-08-studyforge-v1-design.md` — §1–§4 and all of R1–R19.
2. Your **epic document** — shared context for your task's neighbours.
3. `../conventions/module-structure.md` — size, packages, tests, templates.
4. `../conventions/graphify.md` — ask the graph before exploring (R14).
5. `../conventions/agent-protocol.md` — how to work and how to hand off.
6. `handoffs/` — notes from the tasks you depend on.

## Task fields

| Field | Meaning |
|---|---|
| **Milestone** | Which milestone it belongs to; the step is in this document. |
| **Depends on** | Hard dependencies. Nothing else blocks it. |
| **Team** | `solo` · `pair` (two rounds or a reviewer) · `team` (dispatch a small team; subtasks listed). |
| **Context** | The files to read, and a rough budget. Stay under ~200k per session; a task that cannot is already split. |
| **Owns** | The package this task creates. One task, one surface. |
| **Definition** | What the deliverable *is*. Design-level, not implementation. |
| **Acceptance** | Verifiable conditions. Green/red, no judgement calls. |

## Standing rules for every task

- Standard library only in framework source; test-only dependencies excepted.
- Tests are part of the task (R12), never a follow-up.
- No source module over 400 lines, no test module over 600, or the exception is
  justified in the docstring (R11).
- Ask the graph before exploring (R14).
- Write your handoff before you finish.
- R7 (no personal data) and R10 (byte-for-byte reproducible) apply everywhere
  and are not restated per task.
- **Every task implicitly depends on M0.** FND-01's package layout and FND-04's
  fixtures are prerequisites of every framework task; a *Depends on* field lists
  only what is additional to them. `EX-00` blocks all of E08.

**Repository shorthand**, all relative to the **workspace root** — the parent
directory holding every component as a sibling (R18, FND-05). Never write an
absolute path into a file: it carries a home directory, which is personal data
(R7).

`SF/` = `studyforge/` (this repo) · `CS/` = `CodeSignal/.pipeline/` · `CSD/` =
`CodeSignal/` (docker, compose) · `JS/` = `Claude-senior-java-engineer/` ·
`ISO/` = `ISO-8583-jPOS-tutorial/` · `SPARQL/` = `Claude-SPARQL-tutorial/` ·
`TC/` = `code-server-toolchain` · `NS/` = `narrate-service`.
