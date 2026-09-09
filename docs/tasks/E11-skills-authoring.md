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

### SK-07 — Corpus onboarding ⛔ THE SECOND SOURCE'S WHOLE EXPERIENCE
**Milestone** **M2** · **Depends on** SK-02, SF-03, TC-05, SF-02 · **Team** team
**Owns** the onboarding skill
**Context** ~55k — spec R19, §5's placement dry-run, §9; TC-05 and NS consuming contracts

**Definition.** R19's realisation, and the reader-facing answer to *"what does it
cost to point this at a new repository?"* It takes a repository from nothing to
a serving study site, and ⭐ **the one manual step is: add the framework as a
submodule, run this skill.**

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
3. **Ignore rules** — new ignore files written *inside* generated directories. ⛔ Never an edit to the repository's root one (R3, and E07 already rules this for Java).
4. **The compose file** — rendered from `TC/consuming.json` and the narration service's equivalent. ⛔ Never from reading a Dockerfile.
5. **The toolchain selection and the prime project** — which languages, which pinned tag, one *real* minimal source and test per language. ⚠️ An empty prime primes nothing while appearing to succeed.
6. **The build entry point** — corpus configuration over SF-28's CLI.
7. **The non-destructive assertion** — generated with the corpus's declared `permitted_edits` baked in, so it is not a hand-written per-corpus test.
8. **Reader documentation** — from the corpus's *actual* state: how many units have narration, how many have exercises, what needs a container and what does not.
9. **The framework pin and the skill stubs** (spec §9) — thin pointers carrying the pinned version, with a check that fails when a stub drifts from its pin.
10. **An uninstall** — the reverse of every edit it made.

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
submodule added and one command run. Afterwards `git status` shows only
additions plus the declared `permitted_edits`. **Re-running changes nothing.**
The uninstall returns the repository to its prior state, asserted by diff.
`OPS-01`, `OPS-03`, `OPS-04`, `OPS-05` and `OPS-06` are **produced by this
skill** for the Java corpus, not hand-written — asserted by regenerating them
and diffing. Every artifact it produces is regenerable, and a hand-edit to one
is reported as a finding rather than silently kept or silently lost.

---

### SK-03 — Build and serve
**Milestone** M7 · **Depends on** OPS-04 · **Team** solo
**Owns** the build-and-serve skill
**Context** ~30k — OPS-04 entry points, OPS-03

**Definition.** One invocation from raw material to a running site: ingest,
validate, unit documents, pages, narration, contents, index, serve. A thin
wrapper over OPS-04's entry points — and if it cannot be thin, OPS-04 drew its
surface wrong and that is the finding.

Handles the honest partial states rather than failing on them: no narration
service, no toolchain container, no exercises. Each is a **known state with a
stated consequence**, not an error (R6, R8).

**Acceptance.** Produces and serves the Java corpus end to end. Produces a
valid site for a corpus with zero exercises and no narration. Each partial
state is reported with what is missing and what still works.

---

### SK-04 — Exercise derivation
**Milestone** M7 · **Depends on** EX-04 · **Team** pair
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
**Milestone** M7 · **Depends on** SK-03, SF-21 · **Team** pair
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
