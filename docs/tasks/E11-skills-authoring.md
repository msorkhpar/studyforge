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

**Why these come late but are not an afterthought.** They are thin wrappers
over entry points that already work — which is only possible because the
pipeline was built with those entry points in mind. Building them earlier would
mean wrapping things that do not exist; building them without this constraint
in mind from wave one would mean discovering the entry points are unusable.

---

### SK-01 — Source reconnaissance
**Milestone** M7 · **Depends on** SF-25, JS-02 · **Team** pair
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
**Milestone** M7 · **Depends on** SK-01, JS-05 · **Team** pair
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
any source reading is written. Following the skill on a new source reaches a
`validate`-clean archive. The generated structure honours R11's size ceiling.

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
**Milestone** M7 · **Depends on** SK-02 · **Team** solo
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
