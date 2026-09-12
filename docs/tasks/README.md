# studyforge — task index

⛔ **HOW MANY TASKS THERE ARE IS NOT WRITTEN HERE, and that is Ruling 150
(CTO round 40).** ⭐ **The authority is the DERIVATION, and it is generated:
[`../capability-index.md`](../capability-index.md) prints the live count, the
per-milestone decomposition and every row, and a hand-edit to it fails
`test_the_shipped_index_is_exactly_what_the_generator_produces_today`.**

⛔ **AND IT IS GENERATED FROM THE `E*.md` FILES IN THIS DIRECTORY, SO EDITING A
TASK'S `Depends on` MAKES IT STALE IN THE SAME COMMIT.** ⭐ **The regeneration
command lives ONCE, in
[`../../src/studyforge/skills/delivery/SKILL.md`](../../src/studyforge/skills/delivery/SKILL.md),
and is not copied here.** ⚠️ **The TRIGGER is named here because this is the
directory whose edits fire it, and the office that edits an epic most often is
the one the command was hardest to find from** (`PO-53/9`). ⛔ **The suite is
the gate and it bites; what was missing was the sentence, not the instrument.**

⚠️ **This line used to open with a bare count — **89** — while `CLAUDE.md` cited
this document and quoted **87**.** ⛔ **The measured answer at `ce80120` was
neither: **91** live capabilities, **1** cancelled row, **92** rows across
**14** epic documents.** ⭐ **A reader who followed the citation was
corrected by two and a reader who did not was wrong by four** — ⚠️ **and
correcting `87` and `89` to `91` was REFUSED, because it buys exactly one round.
This is the class `W38`'s literal `8` was struck for: a number that counts a
growing population, written in prose, in two documents.**

⭐ **Live status is `BOARD.md`**, not this file: this one orders the work, that
one says where it is.
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

⛔ **THE PER-MILESTONE COUNT COLUMN IS STRUCK TOO (Ruling 150, PO round 33), and
it is struck on a MEASUREMENT rather than on the principle.** ⭐ **The column
disagreed with THIS DOCUMENT'S OWN STEP LISTS, three screens below it, in two of
nine rows** — measured at `ce80120` by summing the step lines: ⚠️ **M1 said
**17** and its own steps enumerate **19**; M2 said **14** and its own steps
enumerate **15**.** ⭐ **In both, [`../capability-index.md`](../capability-index.md)
sides with the step lists.** ⛔ **A document that disagrees with itself about a
number it wrote twice is Ruling 150's mechanism one table down.**

| | Milestone | What works when it lands |
|---|---|---|
| **M0** | Foundations | An agent can start work without inventing anything |
| **M1** | One page renders | A unit page from a fixture opens in a browser |
| **M2** | **A corpus is readable** | Any corpus, offline, with contents, navigation and read marks — **and the skills that built it** |
| **M3** | It speaks | Narration with highlight sync, and an honest media footprint |
| **M4** | It is served | An origin, an API, and a record of practice passes |

⭐ **A prose corpus is finished at M4.** Everything below is the **execution
track**, entered only by material that is actually runnable (spec §11.0). A
corpus with no graders that stops here is complete, not short.

| | Milestone | What works when it lands |
|---|---|---|
| **M5** | It runs code | Run and Submit against a pinned toolchain |
| **M6** | The Java corpus reads | 166 units, narrated and navigable |
| **M7** | The Java corpus has practices | Real exercises with proven graders |
| **M8** | **It is a framework** | A further, unnamed source converted by the skills alone |

**M2 is the biggest single jump in value** — it is the first state you would
actually use, and for a prose corpus it is most of the way to done. **M1 is the
riskiest** — it is where every contract meets every other one for the first
time, which is exactly why it comes first rather than last.

---

## Milestones in detail

⚠️ **~~Within a milestone, each step runs in parallel~~; steps are sequential.**

⛔ **CORRECTED 2026-09-10 (PO round 29, Ruling 127's round; CTO round 36 item
5). A STEP IS A BATCH BOUNDARY, NOT A PARALLELISM GUARANTEE.** ⭐ **A step says
*nothing outside this step may start* — which is a real and useful constraint —
and it says **nothing at all** about edges INSIDE it.** ⛔ **In-step edges are
read off the epic document, never inferred from step membership.**

⚠️ **The sentence that stood here was stated as a guarantee a dispatcher may act
on, and it is not one: it is a heuristic that happens to hold in most steps.**
⛔ **Step 2.2 is the counter-example and it is live — `SK-08` *Depends on*
`SK-07` and both are in it (`E11-skills-authoring.md`, `SK-08`'s header line).
A dispatcher reading the old sentence puts two developers on `SK-07` and `SK-08`
at once.** ⭐ **`PO-28/2` found it; the CTO's ruling is narrower than either
option weighed there: the SENTENCE is the defect and the PLAN is fine.**

⛔ **AND THE FIX THAT WAS REFUSED, recorded so it is not re-proposed: moving
`SK-08` into a step 2.3.** ⚠️ **That is renumbering the plan to protect a
sentence, and the next in-step edge would move it again.** ⭐ **Membership stays
here; state stays in `BOARD.md`; the ordering inside a step is the epic's.**

### ⛔ WIDENED 2026-09-12 (user ruling; drafted PO round 58) — A STEP BOUNDARY BINDS WHAT MAY **CLOSE**, AND NO LONGER BINDS WHAT MAY **START**

⭐ **THE SENTENCE, and it is the whole rule:**

> ⛔ **A wave MAY dispatch a capability row from a LATER step of the SAME
> milestone once every earlier step in that milestone is CLOSED or SATURATED —
> provided every dependency the epic declares for that row has MERGED.**
>
> ⭐ **A step is SATURATED when no row in it is dispatchable: every row in it is
> merged, in flight, or blocked on a dependency that has not merged.**

⛔ **THE SHAPE PROPOSED WAS *once the current step's rows are ALL IN FLIGHT*, AND
IT CANNOT HOLD — refuted at this document's own step 3.4, which is the step it
was written for.** ⭐ **`3.4` is `SF-17, SF-32`, and `SF-32` *Depends on* `SF-02,
SF-17` (`E04-narration.md`, `SF-32`'s header line).** ⛔ **So `SF-32` cannot be in
flight while `SF-17` is, *all in flight* is UNSATISFIABLE there, and the widening
would have widened nothing in the wave that asked for it.** ⭐ **`SATURATED` is
the same intent with the blocked case admitted: it is TRUE for `3.4` the moment
`SF-17` is dispatched.**

⛔ **FOUR THINGS THIS DOES NOT DO, and each is load-bearing:**

1. ⛔ **IT DOES NOT WIDEN *CLOSE*.** ⭐ **A step closes only when ITS OWN rows have
   all merged; a later-step row merging closes nothing and moves no milestone
   gate.** ⚠️ **So `3.5` may merge while `3.4` is still open, and both stay open.**
   ⛔ **AND THE ORDERING HOLDS: a step does not close ahead of an earlier step of
   its own milestone.**
2. ⛔ **IT DOES NOT CROSS A MILESTONE.** ⭐ **A milestone boundary is a GATE with a
   close run behind it (Ruling 97), and this clause stops at it.** ⚠️ **The
   earliest dispatchable row outside the open milestone is still not dispatchable.**
3. ⛔ **IT DOES NOT LICENSE A ROW WHOSE DECLARED DEPENDENCIES ARE UNMERGED.** ⭐ **The
   corrected sentence above says a step guarantees nothing about edges INSIDE it;
   this one says it guarantees nothing about edges ACROSS it either.** ⛔ **The
   edge is read off the EPIC at dispatch, or the row is not dispatched.**
4. ⛔ **IT DOES NOT RETIRE THE DISPATCH BOUND** in `BOARD.md`'s Standing decisions.
   ⭐ **That bound is PRIORITY, not exclusivity; this clause only ENLARGES the
   population it ranges over — from *the open step* to *every unsaturated step of
   the open milestone*.** ⚠️ **A `W` row still takes only a slot no capability row
   can fill.**

### ⭐ CLAUSE — PO round 59: THE ORDERING PRICE IS PAYABLE, AND THE CELL PAYS IT

⛔ **THE COST NAMED HONESTLY WHEN THE RULE WAS DRAFTED: clause 1 leaves a step OPEN with
NOTHING IN IT.** ⭐ **`M3 step 3.5`'s only row merged and the step could not close, because
`3.4` is open.** ⚠️ **The question this clause answers is whether to narrow clause 1.**

⛔ **IT IS NOT NARROWED.** ⭐ **Two grounds, and neither is inertia:**

1. ⭐ **A NON-MONOTONE CLOSED COLUMN CANNOT BE READ.** ⛔ **If `3.5` may close while `3.4`
   is open, a reader looking at the milestone table can no longer tell a step that was
   DEFERRED from a step that was SKIPPED** — ⚠️ **and the step column is the one place a
   milestone's frontier is legible at all.**
2. ⭐ **NARROWING BUYS NO DISPATCH.** ⛔ **The widened rule already decoupled dispatch from
   closure: the population is *every unsaturated step of the open milestone*, and clause 4
   left the dispatch bound standing as PRIORITY rather than exclusivity.** ⚠️ **So closing
   `3.5` early unblocks nothing; it converts one deferred close run into two, and the
   deferred one is strictly better evidence — it is re-taken at a ref where `3.4`'s rows
   are true as well.**

⛔ **WHAT WAS ACTUALLY WRONG IS THE CELL, NOT THE RULE.** ⭐ **`OPEN` was answering two
different questions with one word: *work remains here* and *nothing remains here but an
earlier step's close*.** ⚠️ **That is the empty-population failure this project keeps
meeting — a state indistinguishable from a different state reads as the one you expect.**

⭐ **THE CLAUSE, and it is the whole of it:**

> ⛔ **A step whose OWN rows have all merged, and which is held open only by an earlier
> step of its milestone, declares `AWAITING CLOSE` in its state cell — never `OPEN`.**
> ⭐ **`OPEN` then means what it says: a row in this step is still dispatchable or in
> flight.**

⚠️ **It is a CLAUSE and not a ruling: the mint freeze is in force, and the milestone table
is the board's own cell vocabulary rather than a new authority.**

⛔ **THE GROUND IS A MEASUREMENT, NOT A PREFERENCE: three waves delivered 15
merges and 2–3 capabilities**, because an open step admits one or two capability
rows and the spare slots flow to the `W` register by construction. ⭐ **A boundary
that costs developer-waves per step and buys nothing the epic's own `Depends on`
lines do not already buy is a boundary priced wrong** — ⚠️ **and the epic's lines
are the ones that were doing the work the whole time.**

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
- ⭐ **alongside 1.4/1.5, on the tooling surface** — **FND-08** (the repository-wide
  document walk) and **FND-09** (the fixture-access seam). ⛔ **Both are Ruling
  43's, scoped 2026-09-10 after measurement; neither gates the renderer**, and
  `BOARD.md` carries why the four walks became two tasks and one refusal.

*Why SF-23 is here:* SF-10 must know the workspace shape to be built once rather
than revisited — the contract is cheap and it keeps the archive right even for a
corpus that will never have an exercise. *Why SF-04 is not:* one page needs no
discovery.

### M2 — A corpus is readable
> **Done when:** a whole corpus opens offline with a working index, deep links,
> prev/next and read marks — **and the skills that produced it exist.**
> **This is the first genuinely useful state.**

- **2.1** — SF-04, SF-31, **SF-35**, **SF-36**, SK-02
- **2.2** — SK-07, SK-05, SK-08, SF-13
- **2.3** — SF-14, SF-27
- **2.4** — SF-15, SF-26, SF-30, **SF-34**

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
- **3.6** — **SF-42**

⛔ **`3.6` IS A NEW STEP, NOT A SIXTH MEMBER OF `3.5` (PO round 64, `W206`).** ⭐ **`3.5` closed at
`abee048` with `SF-18` as its whole membership, and a close is a set of measurements at ONE
ref (Ruling 97): admitting a task into a closed step would make that record describe a step
that never existed.** ⚠️ **`SF-42` is the act `M3`'s *Done when* is waiting on — see
[`E09`](E09-delivery.md) § *3*.**

### M4 — It is served
> **Done when:** the site has an origin, an API, and records practice passes.

- **4.1** — SF-21, OPS-05
- **4.2** — SF-19a
- **4.3** — SF-19b, SF-28, **SF-37**, **SF-38**, **SF-39**, **SF-40**, **SF-43**

⭐ **`SF-37`–`SF-40` and `SF-43` join `SF-28`'s step because they ARE `SF-28`, split
([`W197`](rows/W197.md)); the in-step edges are the epic's, as above.** ⛔ **`SF-41` is
NOT here — it is `M7`, step `7.6`, after `OPS-06`.**
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
- **7.6** — OPS-06, OPS-07, **SF-41**
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

**Critical path.** ⛔ **DERIVED, NOT TYPED (PO round 64, `W206`): the longest chain of
*waits on* edges in the generated [`../capability-index.md`](../capability-index.md).**
⚠️ **The line that stood here was a SPINE and not a path — `SF-28` does not wait on
`SF-19a`, and `SF-22` does not wait on `SF-28`.** ⭐ **The longest chain to `QA-04` is TIED, so one
representative is shown; the ties differ only in their first two links and at `EX-02`/`EX-03`:**

SF-01 → SF-05 → SF-25 → SK-02 → SK-07 → JS-01 → JS-02 → JS-04 → EX-01 → EX-02 →
EX-04 → OPS-04 → QA-01 → QA-04.

⭐ **`M3`'s own gate chain, the one live now:** SF-01 → SF-03 → SF-04 → SF-13 → SF-14 →
SF-28 → SF-40 → **SF-42**. ⚠️ **An `M3` task waits on two `M4` tasks, both merged.**

---

## Epics

| Epic | Document | Tasks | Owns |
|---|---|---|---|
| E00 | [Foundations](E00-foundations.md) | FND-01…04, 05a, 06, 07 | scaffolding, dev container, fixtures, the workspace pin file, the R7 check |
| E01 | [Core contracts](E01-core-contracts.md) | SF-01…05, SF-31, SF-33, **SF-35**, **SF-36** | address, manifest, placement, dry-run, discovery, container map, version guard, **the third content state**, **sub-file origins** |
| E02 | [Content pipeline](E02-content-pipeline.md) | SF-06…10 | archive, Markdown, gate, overlay, unit document |
| E03 | [Rendering](E03-rendering.md) | SF-11…15, SF-27, SF-34 | assets, page, contents, index, navigation, page chrome |
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
4. ⭐ **The search path is `git grep`, `grep -rn` and `sed -n`.** ⛔ **There is no
   code-graph or index tool here and no document may name one** (R14, withdrawn
   in place 2026-09-12).
5. `../conventions/agent-protocol.md` — how to work and how to hand off.
6. `../conventions/review-rubric.md` — the standard your work is held to.
   ⛔ **THERE IS NO REVIEWING OFFICE AND NO VERDICT: a row is SELF-CERTIFIED by
   its own office on floor + suite GREEN at the ref that merges** (a user
   decision; the rubric carries it).
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
- ⛔ **Do not budget on the graph** — it is untracked and absent from linked
  worktrees. ⭐ **Use it where it exists (R14); otherwise `git grep` / `grep -rn`.**
- ⛔ **RUN EVERY GATE; DO NOT TRANSCRIBE ITS READING.** ⭐ **Report a gate as
  GREEN or RED with its exit code; quote a figure only where the figure IS the
  subject** — ⚠️ **and a RED gate's breached bound always is: say WHICH bound and
  BY HOW MUCH.** ⛔ **The clause lives ONCE, in `../conventions/review-rubric.md`
  under `#run-every-gate-stop-transcribing-readings-into-prose-a-user-decision`,
  NAMED rather than linked because that anchor lands with `W34`.**
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
