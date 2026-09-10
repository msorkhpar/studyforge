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

⛔ **Two more traps, measured in a real repository 2026-09-09 and carried here
while this task is still unassigned.** ⭐ They are worth more than the first two,
because **neither raises anything and both flatter the person checking.**

- ⛔ **Trap 3 — a filename sort silently reverses the curriculum.** `sorted()`
  puts **35 of 38 units at the wrong index**. ⚠️ The count is right, every page
  renders, every link resolves, **nothing raises** — and ⛔ **it flatters: unit 1
  of each group stays first, so the page anybody spot-checks is correct.** ⭐ It
  is C3's failure class arriving through **ordering** rather than **count**, and
  a count assertion is all the framework has. ⚠️ **The trap inside the trap:**
  the only machine-checkable order oracle is the three aggregate documents —
  **precisely the files a `content.exclude` deletes** — so excluding the
  duplicate destroys the evidence for the ordering. ⛔ **Report both, and never
  propose the exclusion without saying what it costs.**

- ⛔ **Trap 4 — heading level does not identify role.** In the same corpus,
  `README.md` is 675 lines and lines 313–675 carry **361 headings
  digest-identical to the whole heading tree of `TestCases.md`** — **53.7% of the
  curriculum document is a copy of another document's structure**, invisible to
  any whole-file digest. ⛔ **And the file can never be excluded**: it is the only
  record of the corpus's addresses, titles, ordinals and grouping. Consequence:
  `#` means *container* **3** times and *chapter of another document* **17**
  times, so ⚠️ **a parser keyed on heading level emits 21 containers for a
  3-container corpus and raises nothing.**

  ⭐ **This is the sharpest argument in this task's file for R6.** A skill that
  reads structure confidently here is confidently wrong, and the corpus offers no
  signal that it was. ⛔ **The duplicate is a *region*, not a file** — and
  `content.exclude` names files, so ⚠️ **detect and report; do not remedy.** The
  manifest is not going to grow sub-file exclusion and should not.

⛔ **What a *re-run* of this skill is, is undefined and this task does not close
it.** The last reconnaissance of a moving framework happened because a person
asked. ⭐ Recorded as owed to the integration catalogue rather than silently
inherited here.

### ⛔ Carried ruling — the **title-collision** check is this skill's, and only this side can do it

⚠️ **Carried by the PO 2026-09-09 from `handoffs/SF-01.md`'s open `[structural]`
finding, via CTO round 6 and `SF-25`'s definition.** The finding was routed to
"SK-01/SK-02" by its author and ⛔ **had no clause on either side** — the
validate-side half is written into `E10 SF-25` and this half was not.

⛔ **`slugify` is ASCII-lossy and silent about it.** **Measured 2026-09-09:**
`Ströme → 'str-me'`, `Потоки → ''`, `日本語 → ''` — a title with no ASCII letters
produces no address at all. ⭐ **A Russian title is not a corpus defect**: R1 says
the framework knows nothing about a source, *including its alphabet*.

⛔ **And the collision case is punctuation, not alphabet — corrected here the
same day it was written** (round 17, finding 13). ⚠️ **My first draft of this
clause used `café`/`cafe` as the colliding pair. That is wrong**:
`slugify('Café') == 'caf'` and `slugify('Cafe') == 'cafe'` **do not collide**,
because an accent collapses to a separator rather than vanishing. ⭐ **The true
class is wider and far more likely:** `'Streams: an API'` and `'Streams, an API'`
**both** give `streams-an-api`. ⛔ **A skill built to catch the accent case would
miss the case that actually occurs** — ordinary punctuation in ordinary English
titles, which any real corpus has and no reviewer would look twice at.

⭐ **Defence in depth, and the two halves are not substitutes.** `SF-25` sees the
**effect** — two containers at one address — from the archive alone, because by
then the titles are gone and §6 rules an address *recorded, never derived*.
⛔ **Only reconnaissance sees the cause**, because this is the one step that still
holds the titles. So:

- **Acceptance gains a clause:** ⛔ *given material whose titles collide under
  `slugify` — including a title with no ASCII letters — the report names the
  colliding titles and refuses to propose an address for them*, rather than
  proposing a manifest that validates and loses a unit.
- ⚠️ **It is reported, never silently disambiguated.** Appending `-2` would make
  the collision validate and hide it; R6 says uncertainty is reported. ⭐ This is
  the same corpus-scale trap as the duplicate-material one above: the failure is
  **silent** and the archive looks complete.
- ⚠️ **Transliteration is a declared v1 limitation**, not this skill's to solve.
  What is owed here is that a title it cannot address is **named**.

**Acceptance.** Proposes a correct manifest for the Java corpus without being
told the answer. Proposes a correct 1-level manifest for a flat source.
Correctly reports "no runnable code, no graders" for a prose-only source. Every
uncertainty appears in the report rather than as a silent guess. ⛔ **Colliding
and unaddressable titles are named in the report**, per the carried ruling above.

---

### SK-02 — Adapter authoring
**Milestone** **M2** · **Depends on** SK-01, SF-25 · **Team** pair

⚠️ **Was M7, depending on JS-05.** Reversed: **E07's adapter is this skill's
first output.** Its dependency is `validate` — the definition of done it
scaffolds against — not the adapter it was previously copied from.
**Owns** `src/studyforge/skills/adapter/` and its mirror
`tests/studyforge/skills/adapter/` — ⛔ **CORRECTED 2026-09-10 (PO round 26):
this cell read *"the adapter-authoring skill"*, a prose label no command can be
run against.** ⭐ **Verified at `d77cb85`: `skills/adapter/` has **0** files (it
is a CREATE); `skills/reconnaissance/` has **10** — `SKILL.md`, eight modules and
`__init__.py` — and its test mirror has **10**, which is the shape R12 requires.**
⚠️ **The mirror is named because an `Owns` that names no test module is what a
brief is built from** (`W39/3`).
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
   ⛔ **It emits only the keys the corpus needs, and never a key merely because
   the contract has one.** ⚠️ **Carried by the PO 2026-09-09, Q16:** the media
   footprint limits are free to rename **until the first manifest declares
   them** — and the moment an adapter writes one it is a `corpus_api` field whose
   rename is an R9 migration. ⭐ **`SF-02` already asserts that an absent `media`
   block is committed-with-defaults**, so omission is the declared path, not a
   workaround. ⛔ **A generator that emits an unneeded key freezes that key on
   everybody**, and it does so silently, from the one place nobody re-reads. ⚠️ It
   is the failure mode this skill is most exposed to in general: **what a
   generator emits by default becomes the convention.**
   ⛔ **CARRIED BY THE PO 2026-09-10 (round 28), from `SK-02/1`: this skill WRITES
   the `content.not_material` globs into `corpus.json`.** ⭐ **`SF-35` minted the
   vocabulary and `SK-02` GENERATES the globs — `Scaffold.not_material`, two
   entries for eight files — ⚠️ but nothing puts them in the manifest, so today a
   person copies two lines out of a report.** ⛔ **That is R19's *anything a
   second source would have to retype*, which makes it this task's and not a
   board row's.** ⚠️ **Measured by `SK-02` at `corpus_api: 1`: scaffolding into a
   clean corpus and running `studyforge validate` gave `NOT valid: 8 finding(s),
   1 unchecked claim(s)` — one `unclassified` per generated file.** ⭐ **`content.exclude`
   CANNOT say it: it matches by exact path equality, and *exclude* means material
   withheld, which code is not.**
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
carries an R3-safe ignore file for its graph directory** — `graphify-out/.gitignore`
containing a single `*`, written *inside* the generated directory, with the
repository's root ignore file byte-identical to before — asserted, not described.
Afterwards `git status` shows only additions plus the declared
`permitted_edits`. **Re-running changes nothing.** The uninstall returns the
repository to its prior state, asserted by diff. Every artifact it produces is
regenerable, and a hand-edit to one is reported as a finding rather than
silently kept or silently lost.

#### ⛔ RULING 129 (CTO round 37) — this Acceptance was SPLIT, and two halves were RE-HOMED rather than waived

⚠️ **An unmeetable acceptance clause is SPLIT: the met part stays, the residue is
shown unmeetable by a COMMAND, and it is routed to a row the same round.**
⛔ **CHANGES REQUESTED lands on the PLAN, not on the branch — this task's branch
was APPROVED.** ⭐ **Carried here by the PO, round 30. Neither half is deleted.**

| ⛔ **The clause that stood here** | ⭐ **Where it went, and the command that shows it was unmeetable** |
|---|---|
| ⛔ *"`OPS-01`, `OPS-03`, `OPS-04`, `OPS-05` and `OPS-06` are **produced by this skill** for the Java corpus, not hand-written — asserted by regenerating them and diffing."* | ⭐ **RE-HOMED to `SF-28` in `E09`.** ⛔ **`ls src/studyforge/cli/` → `__init__.py`, `plan/` — ONE command, and none of the five `OPS-*` artifacts exists to regenerate.** ⚠️ **It also asserts a diff taken inside a CONSUMER repository, which R20 forbids a framework task to depend on — the second instance after `SK-02/4`.** ⭐ **`artifacts.paths()` and `NOT_MATERIAL` are the two registration points this task already left for it, and `SK-07/1` is the finding** |
| ⛔ *"…a built, bridged graph… with the doc↔code edge census non-zero"* | ⭐ **RE-HOMED to `W54` on the board.** ⛔ **`graphify` is an external binary that is measurably not in the pinned image, and `src/` may not import `tools/` — the same rule that made `SK-02` re-declare `SOURCE_LINE_CEILING`.** ⚠️ **So no framework task could ever close it as written; `W54` places it OUTSIDE `src/`.** ⭐ **The ignore-file half above is MET today and stays here. `SK-07/2` is the finding** |

⛔ **Item 4 above — *the build entry point, corpus configuration over `SF-28`'s
CLI* — is a DEFINITION line, not an acceptance clause, and it stands.** ⚠️ **It
simply cannot be exercised until `SF-28` lands, which is what the re-homing says
out loud.**

---

### SK-08 — Delivery planning ⭐ THE PRODUCT OWNER FOR AN INTEGRATION
**Milestone** **M2** · **Depends on** SK-01, SK-07, SF-31 · **Team** pair
**Owns** the delivery-planning skill, `docs/integration-catalogue.md` in this repo, and ⭐ **the consumer-facing capability index** (see finding **B** below)
**Context** ~45k — spec §9, §12, R19, R20; this repository's own `docs/tasks/` as the worked example

#### ⛔ SIX FINDINGS FROM THE INTEGRATION TRACK, carried 2026-09-10 (PO round 25)

⛔ **The integration track wrote a delivery plan by hand because this skill does
not exist, and then measured the subset a second source would have to invent
AGAIN even after it ships — because this definition does not ask for it.**
⭐ **R19's own test: anything a second source would have to retype is a hole in
the skills.** ⚠️ **They arrive while this skill can still be SHAPED by them, and
that is the whole reason they are carried into the definition rather than into a
board row: five of the six are ONE PARAGRAPH EACH today and a migration after
the skill ships.**

⛔ **These are carried by CLAIM and not by path.** ⭐ **A task in this repository
does not depend on a file in a repository that moves** — ⚠️ **which is R20's
reason applied in the direction it is usually not read.**

| # | ⛔ **The paragraph this definition is missing** |
|---|---|
| **SK08-A** | ⭐ **A corpus milestone DECLARES the framework milestone that gates it, and a task's *Depends on* may name a framework task.** ⛔ Today a corpus milestone is silently gated on framework work and nothing in the plan says so |
| **SK08-B** | ⛔ **The planner reads a CONSUMER-FACING CAPABILITY INDEX, not the epic documents.** ⚠️ **The capability→milestone map was derived by reading thirteen epics, which is exactly what R14's budgets exist to prevent** |
| **SK08-C** | ⭐ **The planner DETERMINES AND STATES the corpus's terminal milestone**, with the evidence, and lists the capabilities it will never use. ⛔ Nothing today asks the planner where the corpus FINISHES — which is `Q18`'s shape one level up |
| **SK08-D** | ⭐ **A task may own NOTHING.** ⛔ Its deliverable is EVIDENCE ABOUT GENERATED OUTPUT, and that is the EXPECTED shape as the skills improve — ⚠️ the current template assumes the integrator writes things |
| **SK08-E** | ⛔ **QUESTIONS are a first-class output beside findings** — numbered, routed at a task, naming what they block, and ⭐ **RE-RUN before they are acted on.** ⚠️ **Named by the filing side as the highest-value item on their branch, and no skill defines it** |
| **SK08-F** | ⭐ **Concentration risk includes risk OUTSIDE the target repository.** ⛔ The current shape cannot express where this integration's risk actually sits |

⭐ **A, C, D, E and F are free: each is one paragraph in this definition, written
before the task is assigned.**

⛔ **B IS NOT FREE, and the PO's call is that it lands INSIDE this task rather
than as a separate framework row.** ⭐ **The reasoning, so it can be re-opened:**
the index is *derived* from the epic documents, and R19 says the consuming half
of a corpus is **generated, not hand-authored** — ⛔ **so a hand-written
capability index would be the very defect this finding reports, one layer up.**
⚠️ **`SK-08` is the one task that already owns a cross-source document in this
repository (`integration-catalogue.md`), so the index sits beside it rather than
inventing a second home.** ⭐ **What it costs is measured on the filing side: 18
rows of a hand-written plan are what it costs when this skill's channel promise —
*"the rulings, the contracts, the authoring reference"* — is met by thirteen
epic documents instead.**

⛔ **Acceptance gains one condition from this block:** ⭐ **the capability index
is GENERATED by this skill and regenerable, and a reviewer can regenerate it and
get identical bytes.** ⚠️ **A hand-edit to it is a FINDING, not a fix (R19).**

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

**Seeded also with one entry that is a *limit* rather than a failure**, because
the catalogue is where limits belong:

> ⭐ **"Never silently drop" is a promise about structure the vocabulary knows.**
> A construct outside it — display maths, a custom directive, an embed — ⛔ **is
> not dropped and is not invented into a block type.** It degrades to prose:
> **visibly, text intact.** ⚠️ The distinction matters when you are planning,
> because a source full of such constructs will *read* correctly and *render*
> plainly, and that is a scoping fact rather than a bug to file.

⚠️ **This entry exists because `math` was proposed as a block type and refused.**
⛔ Inventing a type against **zero sources** is R1's error arriving from the
other direction — the framework learning about material nobody has met — and the
correct output was a written-down limit, not a task. ⭐ **A refused proposal that
leaves no trace gets re-proposed**, which is why the refusal is an entry rather
than a decision somebody remembers.

⭐ **And it grows.** Every integration's findings are distilled back into it, so
the *next* integration starts further along. That is the difference between a
framework and a thing that has been used twice — and it is why the catalogue
lives here rather than in whichever repository happened to learn the lesson.

**Acceptance.** Produces a milestone-ordered backlog for a repository it has not
seen, in which **every task states a demonstrable outcome and an acceptance the
framework can evaluate**. Exports to Jira, and to one other tracker profile
without touching the planner. Flags concentration risk: a plan where a few tasks
carry most of the work says so, because "most tasks are small" is false comfort.
⛔ **Cites no path inside the extraction source** — asserted (R20). Files
findings rather than framework edits, and the catalogue gains an entry for each.
⭐ **The capability index is GENERATED by this skill and regenerable to identical
bytes.**

⛔ **ONE CLAUSE WAS REMOVED FROM THE PARAGRAPH ABOVE, 2026-09-10 (Ruling 151,
PO round 33), and it is recorded here rather than deleted silently.** The clause
read:

> ⭐ *"Pointed at the Java corpus, it produces a backlog recognisably equivalent
> to this repository's own E07–E09"* — the test that it is not vacuous, and it
> costs nothing extra because the answer already exists to compare against.

⚠️ **It is unmeetable from this side, and two commands say so rather than an
argument:** the consumer sibling is absent from a framework checkout
(`ls -d ../Claude-senior-java-engineer` → **`exit=2`**), and the package
**touches no filesystem at all** — asserted by two shipped tests
(`reaches_the_filesystem_nowhere`, `cites_a_path_inside_the_extraction_source`,
**2 passed, 4043 deselected**). ⛔ **So *"pointed at"* names an operation the
subject cannot perform, and producing the comparison means somebody reads a
CONSUMER repository, which R20 puts outside a framework task's reach.**
⚠️ **And *"recognisably equivalent"* names no instrument:
`studyforge.skills.delivery.Acceptance` — shipped by THIS TASK — would refuse
the clause for naming neither a command nor a reviewer.**

⭐ **WHERE IT WENT: `W73`, on the integration side, which is where a reading
taken inside a consumer repository has always belonged.** ⛔ **It does not gate
`SK-08`, it did not gate step 2.2's close, and it is not deleted** —
⚠️ **`SK-02/4` was handled the same way at step 2.1's close and for the same
reason.** ⭐ **This is the THIRD instance of the class, and Ruling 151 closes it:
a framework task's Acceptance may not contain a clause whose subject is a
reading taken inside a consumer repository — such a clause is written on the
integration side from the outset, rather than split there later.**

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
