# studyforge — task index

**75 tasks · 13 epics · 8 milestones.** Companion to
`../specs/2026-09-08-studyforge-v1-design.md`, whose rulings **R1–R18** every
task cites.

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
| **M0** | Foundations | An agent can start work without inventing anything; **exercise feasibility is known** | 6 |
| **M1** | **One page renders** | A unit page from a fixture opens in a browser | 14 |
| **M2** | **The Java material is readable** | All 166 units, offline, with contents and navigation | 12 |
| **M3** | It is served | The site has an origin, an API, and records progress | 4 |
| **M4** | It speaks | Narration with highlight sync | 10 |
| **M5** | It runs code | Run and Submit against a dockerised toolchain | 12 |
| **M6** | It has practices | Real exercises with proven graders | 5 |
| **M7** | It is a product | Built by skills, documented, accepted | 12 |

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

- **0.1** — FND-01, FND-02, FND-03, FND-04, FND-05, **EX-00** *(all parallel)*

⛔ **EX-00 gates all of E08.** It is a spike: run `mvn test` for a baseline, then
hand-gate ten pairs across the shape spectrum. If the exercise approach does not
yield, we find out in week one rather than at M6.

### M1 — One page renders
> **Done when:** a unit page from the depth-1 fixture opens in a browser, with
> styles and highlighting, over `file://`.

- **1.1** — SF-01, SF-02, SF-07, SF-08, SF-11
- **1.2** — SF-03, SF-05, SF-06
- **1.3** — SF-09, SF-23, SF-25
- **1.4** — SF-10
- **1.5** — SF-12, QA-03

*Why SF-23 is here:* SF-10 must know the workspace shape to be built once
rather than revisited. *Why SF-04 is not:* one page needs no discovery.

### M2 — The Java material is readable
> **Done when:** all 166 units open offline with a working index, deep links
> and prev/next. **This is the first genuinely useful state.**

- **2.1** — SF-04, JS-01
- **2.2** — SF-13, JS-02
- **2.3** — SF-14, JS-03, JS-04
- **2.4** — SF-15, SF-26, SF-27, JS-05
- **2.5** — JS-06

### M3 — It is served
> **Done when:** the site is served, the contents API answers, progress records.

- **3.1** — SF-21
- **3.2** — SF-19a
- **3.3** — SF-19b, SF-28

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

- **5.1** — TC-01, SF-20
- **5.1b** — SF-29
- **5.2** — TC-02, TC-03, TC-04
- **5.3** — TC-05, TC-06
- **5.4** — OPS-01
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
- **7.2** — SK-01, OPS-05, OPS-07
- **7.3** — SK-02, SK-03, SK-04, SK-05, OPS-06
- **7.4** — SK-06
- **7.5** — QA-01, QA-02

**Critical path.** FND-01 → SF-01 → SF-03 → SF-10 → SF-12 → SF-04 → SF-13 →
SF-19a → SF-19b → SF-22 → EX-04 → OPS-04 → QA-01.

---

## Epics

| Epic | Document | Tasks | Owns |
|---|---|---|---|
| E00 | [Foundations](E00-foundations.md) | FND-01…05 | scaffolding, graphify, dev container, fixtures, submodules |
| E01 | [Core contracts](E01-core-contracts.md) | SF-01…05 | address, manifest, placement, discovery, container map |
| E02 | [Content pipeline](E02-content-pipeline.md) | SF-06…10 | archive, Markdown, gate, overlay, unit document |
| E03 | [Rendering](E03-rendering.md) | SF-11…15, SF-27 | assets, page, contents, index, navigation |
| E04 | [Narration](E04-narration.md) | SF-16…18 | speakable, synthesis, player sync |
| E05 | [Serving & execution](E05-serving-execution.md) | SF-19a/b, SF-20…22, SF-29 | API, runner, progress, Run/Submit |
| E06 | [Exercise contract](E06-exercise-contract.md) | SF-23…24 | workspace, trust, practice panel |
| E07 | [Java adapter](E07-java-adapter.md) | JS-01…06 | curriculum, lessons, pairing, emission, audit |
| E08 | [Java exercises](E08-java-exercises.md) | **EX-00**, EX-01…05 | blanking, the two gates, emission, coverage |
| E09 | [Delivery](E09-delivery.md) | OPS-01…07, SF-28 | compose, build pipeline, guarantees, docs |
| E10 | [Validation & QA](E10-validation-qa.md) | SF-25, SF-26, QA-01…03 | validate CLI, harness, acceptance |
| E11 | [Skills & authoring](E11-skills-authoring.md) | SK-01…06 | **the product** (R16) |
| E12 | [Toolchain image](E12-toolchain-image.md) | TC-01…06 | shared code-server repo (§8.1) |
| E13 | [Narration service](E13-narration-service.md) | NS-01…06 | shared synthesis repo (§8.2) |

Future work: [v2-backlog.md](v2-backlog.md).

---

## Before picking up any task

1. `../specs/2026-09-08-studyforge-v1-design.md` — §1–§4 and all of R1–R18.
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
