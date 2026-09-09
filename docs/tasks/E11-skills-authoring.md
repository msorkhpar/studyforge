# E11 — Skills and authoring kit

**This epic is the product** (R16). Everything before it is the means.

**Shared context for this epic — read spec §9 first.**

The end state is not "the Java repository has a study site". It is that
somebody points a skill at material they care about — a course site, a book, a
paper collection, a repository of exercises, their own notes — and gets this
format back: pages, narration, contents, navigation, practices, examples, and
their own progress. And then **keeps it**, as a durable personal record they
can review, re-run and extend.

**The Java corpus is the proving ground, not the destination.** Acceptance item
11 requires that the corpus was produced *by these skills*, not by bespoke
scripts, which is why OPS-04's entry points must be clean: a skill that has to
reach past a public entry point into internals is a skill that will not work
for anybody else's material.

**The division of labour mirrors R2.** Exactly one skill reasons about
unfamiliar material (SK-01). Every other skill is source-agnostic and operates
on contracts. If a second skill starts needing to understand a source, the seam
has been drawn wrong.

**⚠️ These do not all come late, and the original plan was wrong to say so.**
Every skill was scheduled at M7 — after the Java corpus had been built by hand
across M2–M6 — which made acceptance item 11 (*"the corpus was produced by the
skills"*) not merely unsatisfiable but **unfalsifiable**: a claim about history
that nothing recorded, about a corpus built before any skill existed.

⛔ **A skill precedes the artifact it produces, or it is a retrospective**
(spec §9). A skill written afterwards has been validated against exactly one
source — the one it was reverse-engineered from — and its first genuine test is
the second source, which is precisely where it must not fail.

So the epic splits in two:

| | Skills | Milestone | Why |
|---|---|---|---|
| **Producing** | SK-01, SK-02, SK-07, SK-05 | **M1–M2** | E07 and E09 are their **first output**, not their input |
| **Wrapping** | SK-03, SK-04, SK-06 | M7 | genuinely thin wrappers over entry points that must exist first |

⚠️ **The cost of the front half is real and is accepted.** SK-02 at M2 is
written before anybody knows what a second adapter looks like. The answer is
that it starts deliberately minimal and grows — scaffolding a package layout, a
test tree and an audit command, leaving the source-specific reading to be filled
in, is buildable at M2 and is already exactly what its definition asks for. The
alternative is worse: a corpus built by hand and skills written afterwards to
claim they produced it.

⚠️ **The back half's original reasoning still stands** for SK-03, SK-04 and
SK-06: they are thin wrappers over entry points that already work, which is only
possible because the pipeline was built with those entry points in mind.

---

### SK-01 — Source reconnaissance
**Milestone** **M1** · **Depends on** SF-02 · **Team** pair

⚠️ **Was M7, depending on JS-02 — that dependency was the circularity.** This
skill's job is to propose a manifest for material nobody has read; taking the
Java curriculum parser as an input meant it could only ever propose the answer
somebody had already written. It now needs the manifest contract and nothing
else.
**Owns** the reconnaissance skill
**Context** ~45k — spec §4, §9; SF-25 output; E07 as the worked example

**Definition.** Given arbitrary material, work out its shape and propose a
corpus manifest: how deep the hierarchy is, what the units are, whether there
are variants, whether anything is runnable, and whether any grader ships with
it. Produces a draft `corpus.json`, a proposed level vocabulary, and **an
honest report of what it could not determine**.

**This is the only skill that reasons about unfamiliar material**, and its
hardest requirement is knowing when it does not know. A confident wrong answer
about a hierarchy costs an entire ingestion; "these 19 files look flat, but
files 12–19 reference a grouping I cannot see — please confirm" costs a
question. Uncertainty is reported, never smoothed over (R6).

Must produce sensible proposals for all four shapes in spec §1, and handle the
two traps real material actually set (C1, C2):

- ⭐ **A hierarchy can live in filenames, not directories.** ISO's three groups
  share one flat `src/`, separated only by prefix (`1.md` / `s1.md` / `c1.md`).
  A skill that reads directory structure sees one flat list and proposes the
  wrong model.
- ⭐ **A corpus can carry the same material twice.** ISO ships per-unit files
  *and* whole-series aggregates (`ISO.md`, 3,858 lines). Globbing `*.md`
  ingests everything twice with nothing complaining. Detect the overlap and
  propose which set is canonical.

**Acceptance.** Proposes a correct manifest for the Java corpus without being
told the answer. Proposes a correct 1-level manifest for a flat source.
Correctly reports "no runnable code, no graders" for a prose-only source. Every
uncertainty appears in the report rather than as a silent guess.

---

### SK-02 — Adapter authoring
**Milestone** **M2** · **Depends on** SK-01, SF-25 · **Team** pair

⚠️ **Was M7, depending on JS-05.** Reversed: **E07's adapter is this skill's
first output.** Its dependency is `validate` — the definition of done it
scaffolds against — not the adapter it was previously copied from.
**Owns** the adapter-authoring skill
**Context** ~40k — spec §6; E07 as the reference adapter; SF-25 output

**Definition.** Scaffolds an adapter for a shape SK-01 identified, **against
`studyforge validate` as the definition of done** — so the skill's output is
checkable by machine rather than by opinion, and a person with no knowledge of
the framework's internals can tell whether it worked.

Produces the adapter's structure, its tests, and its audit command (the JS-06
equivalent), leaving the source-specific reading to be filled in — because that
part is genuinely material-specific and pretending otherwise would produce
plausible code that reads the wrong thing.

**Acceptance.** A scaffolded adapter's tests run and fail informatively before
any source reading is written. **E07's adapter package was produced by this
skill** — the scaffolding commit precedes the source-reading commits, which git
can check. Following the skill on a source it has never seen reaches a
`validate`-clean archive. The generated structure honours R11's size ceiling.

---

### SK-07 — Corpus onboarding ⛔ A NEW SOURCE'S WHOLE EXPERIENCE
**Milestone** **M2** · **Depends on** SK-02, SF-03, SF-02, SF-31 · **Team** team
**Owns** the onboarding skill
**Context** ~55k — spec R19, §5's placement dry-run, §9; TC-05 and NS consuming contracts

**Definition.** R19's realisation, and the reader-facing answer to *"what does it
cost to point this at a new repository?"* It takes a repository from nothing to
a serving study site, and ⭐ **the one manual step is: check the framework out
beside the corpus, run this skill.**

⛔ **Not a submodule — R18 was amended and this task must not be written against
`git submodule add`.** Nothing in this project is pushed to any remote, so a
submodule URL has no legal form (spec R18, `handoffs/CTO-2026-09-09-round3.md`).
⭐ **The framework is a sibling checkout at a recorded commit**, and the commit is
recorded in the workspace pin file (`FND-05a`). *Never vendored, never copied,
never forked* is unchanged — what changes is only how the pin is written down.

⛔ **This task exists because the plan had the same hole `SF-28` already found
once and did not finish closing.** SF-28's own note says orchestration living in
the consumer repository *"breaks R1, R2 and R16 simultaneously"* — and then
`OPS-01` (the toolchain build), `OPS-03` (the compose file), `OPS-05` (the
guarantee test) and `OPS-06` (the reader documentation) were all left
hand-authored, per corpus. For a second source, every one of them is retyped,
which would make the extensibility exercise largely a test of typing speed.

**What it generates in a target repository.**

1. `corpus.json` — promoted from SK-01's draft, including `permitted_edits` (R3).
2. The adapter package, its test tree and its audit command — SK-02's scaffold, wired in.
3. **Ignore rules** — new ignore files written *inside* generated directories. ⛔ Never an edit to the repository's root one (R3, and E07 already rules this for Java). ⭐ **What they ignore is `SF-32`'s verdict, not this skill's opinion**: generated media is committed by default, so the ignore rules must *not* exclude it — and when a corpus crosses the footprint ceiling, this skill is what tells the reader, in the onboarding report, that their media no longer fits in git and what the two ways forward are. ⛔ It never silently flips the policy; the manifest says what happens and a person changes the manifest.
4. **The build entry point** — corpus configuration over SF-28's CLI.
5. **The non-destructive assertion** — generated with the corpus's declared `permitted_edits` baked in, so it is not a hand-written per-corpus test.
6. **Reader documentation** — from the corpus's *actual* state: how many units have narration, how many are reading-only, what needs a container and what does not.
7. **The framework pin and the skill stubs** (spec §9) — thin pointers carrying the pinned version, with a check that fails when a stub drifts from its pin.
8. **An uninstall** — the reverse of every edit it made.
9. ⭐ **The knowledge graph, built and bridged, with its R3-safe ignore file.**
   `FND-02` proved every part of this and it is three commands; ⛔ **without it a
   newly onboarded corpus has no index at all**, and R14 then binds on a
   repository nothing built one for. The ignore file is `graphify-out/.gitignore`
   containing a single `*`, written *inside* the generated directory — ⛔ never a
   line in the repository's root ignore file, which R3 forbids **however
   declared**.

   ⚠️ **Building it is not enough, and this is the part that would be missed.**
   A graph built by running the tool alone has **zero doc↔code edges** — measured
   on the Java corpus at 13,583 code↔code, 767 doc↔doc, **0 doc↔code** — because
   code is extracted by AST and prose by LLM, and no extractor ever sees a lesson
   and its class together. ⭐ **The budget saving R14 promises is a property of a
   graph somebody bridged, not of the tool**, so this step bridges the layers and
   runs the census `graphify.md` documents. A skill that emits an unbridged graph
   has emitted an index that answers the one question the corpus exists for with
   silence.

⭐ **This is the reading floor's onboarding, and for most corpora it is the whole
of it** (spec §11.0). A source with runnable material also needs a compose file
and a pinned toolchain; that is `SK-09`, and it lands with the execution track
rather than making every prose corpus wait for a container it will never
start.

### Customisation is declared, never hand-edited

⚠️ **This is the ruling that decides whether the framework is usable by many
repositories or merely survivable by one.** "Everything is generated" and
"every corpus is different" have to both be true, and there is exactly one way
to get both:

- ⛔ **A hand-edit to a generated artifact is a finding against this skill**, not
  a fix. It is silently reverted by the next run, and a tool that eats your
  changes is a tool nobody runs twice.
- ⭐ **Customisation enters as data in the manifest** — placement profile, level
  labels, variants, voice, toolchains, permitted edits, which units are in and
  out. If a corpus needs something the manifest cannot say, **the manifest is
  missing a field** and that is the finding.
- ⭐ **And there is one declared escape hatch, because there always has to be
  one:** a corpus may keep hand-authored files that this skill **never
  generates and never overwrites**, composed with the generated ones rather than
  replacing them — the compose-override shape. They are named in the manifest,
  so what is hand-held is *visible* rather than discovered when a regeneration
  destroys it. ⛔ An override that shadows a generated file entirely is a
  finding: it means the generator could not express something, and hiding that
  behind an override is how a framework acquires a consumer it cannot serve.

**Acceptance.** A repository goes from nothing to a serving site with the
framework checked out beside it and one command run. ⛔ **No `.gitmodules` and no
`git submodule add` anywhere in what this skill emits** — asserted. **The corpus
carries a built, bridged graph and an R3-safe ignore file**, with the doc↔code
edge census non-zero and the repository's root ignore file byte-identical to
before — both asserted, not described. Afterwards `git status` shows only
additions plus the declared `permitted_edits`. **Re-running changes nothing.**
The uninstall returns the repository to its prior state, asserted by diff.
`OPS-01`, `OPS-03`, `OPS-04`, `OPS-05` and `OPS-06` are **produced by this
skill** for the Java corpus, not hand-written — asserted by regenerating them
and diffing. Every artifact it produces is regenerable, and a hand-edit to one
is reported as a finding rather than silently kept or silently lost.

---

### SK-08 — Delivery planning ⭐ THE PRODUCT OWNER FOR AN INTEGRATION
**Milestone** **M2** · **Depends on** SK-01, SK-07, SF-31 · **Team** pair
**Owns** the delivery-planning skill, and `docs/integration-catalogue.md` in this repo
**Context** ~45k — spec §9, §12, R19, R20; this repository's own `docs/tasks/` as the worked example

**Definition.** The role every integration needs and no other skill covers:
somebody who turns *"convert this repository"* into **an ordered backlog of
tasks that each end in something a person can be shown.** It is the product
owner for an integration — it plans, it sequences, it writes acceptance
somebody else can check, and it reports progress against a plan rather than
against a feeling.

It runs **in the target repository**, and its authority is `studyforge`.

### What it produces

1. **A backlog document in the target repo** — the durable artifact, in the same
   shape this repository's own `docs/tasks/` uses: milestones, waves within a
   milestone that run in parallel, a critical path, and per task an *owns*, a
   *depends on*, a definition and an acceptance.
2. **An export in the tracker's format.** ⭐ **Jira first, and the format is a
   profile rather than a hard-coding** — the next repository may not use Jira,
   and a planner that can only speak one tracker is a planner one team can use.
   The backlog document is the source; the export is a rendering of it.
3. **The findings** that the integration produces (§12, QA-04).

### ⛔ Each task ends in something demonstrable, never in a layer

This is inherited from this repository's own ordering principle and it has
already been paid for once: *build every contract, then every renderer, then
every service* hides all integration risk until the end, and integration risk is
the kind that reorders plans. ⛔ **A task whose deliverable is "the parser is
written" is not a task**; a task whose deliverable is "one unit of this
repository's material opens in a browser" is. The reader must be able to *see*
each step land.

### ⛔ Acceptance the framework can check, never acceptance by opinion

`studyforge validate`, `studyforge plan` and the non-destructive check exist so
that an integrator's work has a green/red signal depending on nobody's judgement
(R2). ⛔ **The planner never writes an acceptance criterion the framework cannot
evaluate** — "the pages look right" is a task nobody can close and everybody can
argue about. Where a genuinely visual judgement is needed, the task says who
looks and at what, and that is stated rather than smuggled in.

### The channel to the framework — this is the interesting part

The planner is allowed to interrogate `studyforge`, and ⛔ **that channel is the
only one it has**: R20 forbids it reading the extraction source, and §12 forbids
it patching the framework. Three kinds of request, each with a defined answer:

| It asks | Because | It gets |
|---|---|---|
| **A question** — *"what does the framework do about X?"* | it is planning around a capability | the rulings, the contracts, the authoring reference (SK-05), and the knowledge graph (R14) |
| **An improvement** — *"the framework cannot do X"* | it hit a wall | a **finding**, which becomes a framework task. ⛔ Never a patch (§12) |
| **Task-writing help** — *"how should this be cut?"* | somebody has been here before | the **integration catalogue**, below |

⭐ **The finding is the lever, and that is deliberate.** An integrator who can
edit the framework fixes their own problem and nobody learns anything; an
integrator who can only file a finding produces a record of what the framework
could not do. That record is the entire yield of §12.

### The integration catalogue — how this repository stays the brain

⛔ **The planner never reads CodeSignal** (R20). What it draws on instead is a
document **in this repository**, which it also maintains: what has gone wrong
when material meets this framework, in a form somebody planning work can use.
Seeded from what has already been paid for — a plausible short parse that raises
nothing (C3, SF-25); a corpus that carries the same material twice (C2); a
hierarchy encoded in filenames rather than directories (C1); an exercise with no
grader, which is not "no exercise" (C5); media that outgrows a git remote
(SF-32); a derived address that sends one link in eight nowhere (§6).

⭐ **And it grows.** Every integration's findings are distilled back into it, so
the *next* integration starts further along. That is the difference between a
framework and a thing that has been used twice — and it is why the catalogue
lives here rather than in whichever repository happened to learn the lesson.

**Acceptance.** Produces a milestone-ordered backlog for a repository it has not
seen, in which **every task states a demonstrable outcome and an acceptance the
framework can evaluate**. Exports to Jira, and to one other tracker profile
without touching the planner. ⭐ **Pointed at the Java corpus, it produces a
backlog recognisably equivalent to this repository's own E07–E09** — the test
that it is not vacuous, and it costs nothing extra because the answer already
exists to compare against. Flags concentration risk: a plan where a few tasks
carry most of the work says so, because "most tasks are small" is false comfort.
⛔ **Cites no path inside the extraction source** — asserted (R20). Files
findings rather than framework edits, and the catalogue gains an entry for each.

---

### SK-09 — Execution onboarding
**Milestone** **M5** · **Depends on** SK-07, TC-05 · **Team** solo
**Owns** the execution half of onboarding
**Context** ~30k — `TC/consuming.json`, the narration service's equivalent, SK-07's output

**Definition.** What `SK-07` generates *additionally* for a corpus whose material
is runnable: the compose file, the toolchain selection, and the prime project.

⛔ **Separated because most corpora will never need it** (spec §11.0). The
reading floor is what every corpus gets; a container is what a corpus with
runnable code earns. Folding this into `SK-07` would put a Docker dependency in
front of somebody converting a book.

- **The compose file** — rendered from `TC/consuming.json` and the narration
  service's equivalent. ⛔ Never from reading a Dockerfile (R18): a consumer that
  reads one is a fork waiting to happen.
- **The toolchain selection** — which languages, which pinned tag, from manifest
  data.
- **The prime project** — one *real* minimal source and test per language. ⚠️ An
  empty prime primes nothing while appearing to succeed: a `NO-SOURCE` compile
  task never resolves the compiler classpath.

**Acceptance.** A runnable corpus gets a working compose file and a primed image
from manifest data alone. ⛔ **A corpus whose manifest says it is not runnable
gets nothing from this skill and no error** — asserted. Re-running changes
nothing. The compose file honours §8.1's four rulings, each asserted rather than
remembered.

---

### SK-03 — Build and serve
**Milestone** **M4** · **Depends on** SF-28 · **Team** solo
**Owns** the build-and-serve skill
**Context** ~30k — SF-28's entry points

**Definition.** One invocation from raw material to a running site: ingest,
validate, unit documents, pages, narration, contents, index, serve. A thin
wrapper over **SF-28's** entry points — and if it cannot be thin, SF-28 drew its
surface wrong and that is the finding.

⚠️ **It wraps the framework CLI, not a consumer's pipeline.** This task used to
depend on `OPS-04` — a file in the Java repository — which is the exact hole
`SF-28` was created to close: a source-agnostic skill wrapping one consumer's
script means the second consumer rewrites the skill.

Handles the honest partial states rather than failing on them: no narration
service, no toolchain container, no exercises. Each is a **known state with a
stated consequence**, not an error (R6, R8).

**Acceptance.** Produces and serves the Java corpus end to end. Produces a
valid site for a corpus with zero exercises and no narration. Each partial
state is reported with what is missing and what still works.

---

### SK-04 — Exercise derivation
**Milestone** **M7** · **Depends on** EX-04 · **Team** pair
**Owns** the exercise-derivation skill
**Context** ~35k — spec §7, E08 in full

**Definition.** Generalises E08's approach to any source that **ships its own
graders**: pair implementation with grader, create the hole, run both gates,
ship only what clears them.

⛔ **It refuses sources that ship no grader.** For those, the honest answer is
zero exercises (spec §7) — and inventing assertions is precisely the theatre R5
forbids. That refusal is a feature of this skill and must be stated plainly to
the user, with the reason, not presented as a failure.

Language-specific pieces — how to blank a body, how to invoke a build — are
pluggable; the two gates are not.

**Acceptance.** Reproduces E08's result on the Java corpus. Refuses a
grader-less source with a clear explanation. The gates cannot be disabled or
bypassed by configuration.

---

### SK-05 — Authoring reference
**Milestone** **M2** · **Depends on** SK-02 · **Team** solo

⚠️ **Was M7.** Moved with the skills that point at it: writing the reference
last means writing it *from* the code rather than the code from it.
**Owns** `docs/authoring/`
**Context** ~35k — spec §4–§7, E07 as the worked example

**Definition.** The document the skills point at: what a corpus is, what an
adapter must produce, what `validate` checks and why, what the placement
profiles do, and when a source should have zero exercises. Written for somebody
converting **their own** material who has never read this spec and does not
intend to.

Uses the Java corpus as a fully worked example, and the 1-level flat shape as
the counter-example — because a reference that only demonstrates the complex
case teaches people that the simple case is unsupported.

**Acceptance.** Somebody following it converts a small new source without
reading the spec or the framework source. Both worked examples are complete and
current. Every claim in it is true of the shipped code — checked, not assumed.

---

### SK-06 — Personal archive
**Milestone** **M4** · **Depends on** SK-03, SF-21 · **Team** pair
**Owns** the export/import skill
**Context** ~35k — SF-21 output, spec §9

**Definition.** The half of R16 that makes this a *record* rather than a
one-time build: export a corpus **with its progress** — material, code,
practices, examples and what the reader has completed — and re-import it on
another machine.

⛔ **Progress and content separate cleanly, and the export must respect that.**
A corpus handed to somebody else carries its material and **not** its owner's
progress; an export meant for the owner's other machine carries both. That is
a choice the exporter makes explicitly, never a default that leaks (R7). SF-21
already keeps progress in one file outside served content, which is what makes
this a clean split rather than a filtering exercise.

**Acceptance.** A corpus exported and re-imported on another machine restores
material and progress intact. An export marked for sharing contains no progress
and no personal data — asserted, not inspected. Re-import into an existing
corpus merges rather than clobbering, and says what it merged.
