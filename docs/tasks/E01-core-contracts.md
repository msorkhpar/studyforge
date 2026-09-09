# E01 — Core contracts

The framework's identity layer: what a thing *is* and where it *lives*, kept
strictly apart. Everything else in the project depends on this epic, and its
mistakes are the expensive kind — an address model that leaks a source's
assumptions makes R1 unenforceable everywhere downstream.

**Shared context for this epic.** CodeSignal's `layout.py` is the ancestor of
all five tasks and worth reading once for its reasoning, not its structure. It
was written because eight modules each rebuilt study paths from their own
string pieces, so moving the tree meant finding all eight — and missing one
left half the pipeline looking in the old place *with nothing failing loudly*.
That lesson survives; the single prescribed tree does not (§5).

**The split this epic introduces.** `layout.py` answered two questions at once:
*what is this thing* and *where does it go*. v1 separates them — SF-01 owns
identity, SF-03 owns location, SF-04 recovers identity from artifacts found on
disk. That separation is what makes flexible placement possible (R4).

**Rulings that bite here:** R1 (no source knowledge), R4 (location is data),
R9 (versioned contracts), R10 (reproducible), R11 (packages).

---

### SF-01 — Logical address model
**Milestone** M1 · **Depends on** — · **Team** solo
**Owns** `address/`
**Context** ~30k — spec §4, `CS/tools/study/layout.py` (names, `CourseRef`, `parse_key` only), `CS/tools/study/naming.py`

**Definition.** The identity primitive: an immutable N-segment address plus a
unit ordinal. Widens CodeSignal's two-segment `CourseRef` to exactly
`len(levels)` segments, keeping the property that made it safe — every segment
must already be a slug, and the joined `key` is **one string that cannot be
reassembled two different ways**, so two halves cannot be silently swapped.
Provides the key ⇄ address inverse pair, slugification, identifier derivation
for package and source-tree segments (a leading digit is *prefixed*, never
dropped, so two slugs differing only there cannot collide), and unit ordinal
naming.

**Knows nothing about files** (R1, R4). No paths, no directories, no I/O.

**Acceptance.** Round-trips every address in spec §4's table, at depths 1
through 4. A title passed where a slug is required raises. Two slugs differing
only by a leading digit yield different identifiers. A key of the wrong arity
for a declared depth is rejected. No filesystem import in the package.

---

### SF-02 — Corpus manifest
**Milestone** M1 · **Depends on** — · **Team** solo
**Owns** `corpus/manifest.py`
**Context** ~15k — spec §4

**Definition.** `corpus.json` — the file that makes a directory a source.
Owns `corpus_api`, `source`, `title`, `levels`, `variants`, `exercises`,
`placement`, `permitted_edits`, `media`. Refuses an unknown version rather than migrating
it at read time (R9): a migration that runs when something merely wanted to
render a page rewrites the record of what was ingested.

⭐ **This file is where a corpus's customisation lives** (SK-07). Everything that
differs between two sources and is not the source's own content is a field here
— which is what makes "every artifact is generated" and "every corpus is
different" both true at once. ⛔ If a corpus needs something this file cannot
express, **the manifest is missing a field**, and that is the finding; it is
never a hand-edit to generated output.

`permitted_edits` is R3's declaration: the enumerated set of existing files this
corpus may add to, each with `path`, `kind`, `anchor`, `content` and `why`. ⚠️
**An empty list is the normal case** and the one a purely additive source keeps.
The framework's non-destructive check (`OPS-05`) reads this; it never names a
corpus's exception itself.

`levels` fixes two things at once — the address depth, and the **display
labels** breadcrumbs and the index use, so the Java site reads
"Section › Module › Lesson" and CodeSignal reads "Path › Course › Unit" from
data alone. `variants` replaces CodeSignal's closed `LANGUAGES` tuple, which is
the change that severs the framework's last dependency on `tools/catalog/`
(R1).

⚠️ **`variants` is a filing and presentation key and nothing more** (spec §4). It
says how the archive is partitioned and what a variant selector offers. ⛔ It
never implies anything is buildable, runnable or gradable — that is per exercise
— and it is not a code fence's language, which is a block attribute. CodeSignal
blocked eight courses because one list answered both questions at once.

`media` declares whether generated media is committed — `always`, `never`, or
`auto` with limits (SF-32). ⭐ **The default is `auto`, and `auto` commits**: a
clone that carries its own audio speaks with nothing running, which is what R8
is for. The limits exist so that a corpus which outgrows the default finds out
early and loudly rather than at a rejected push.

**Acceptance.** Accepts manifests for all four shapes in spec §1, including
1-level SPARQL. Rejects empty `levels`, empty `variants`, unknown `corpus_api`,
unknown `placement`, an unknown `media.commit` mode, and a `permitted_edits`
entry that names a forbidden target (R3). Accepts an absent or empty
`permitted_edits`. An absent `media` block means committed-with-default-limits,
and that is asserted rather than assumed. **No framework module
derives runnability from a variant name** — asserted. No framework module
imports anything source-specific — asserted, not assumed.

---

### SF-03 — Placement policy
**Milestone** M1 · **Depends on** SF-01, SF-02 · **Team** pair
**Owns** `corpus/placement/`
**Context** ~40k — spec §5, `CS/tools/study/layout.py` (directories, media filenames)

**Definition.** The pluggable map from a logical address to physical locations,
replacing CodeSignal's single prescribed tree. Two profiles ship:

- **`tree`** — CodeSignal's shape, reproduced byte-identically, so its later
  migration is not also a relocation.
- **`sibling`** — artifacts land beside the source file they were generated
  from. This is what lets the LMS *enhance* a repository instead of
  restructuring it (R3), and it is the Java corpus's profile.

Answers, per profile: where a unit page goes, its audio, its images, its
practice material, the shared assets, and the archive root. Owns artifact
naming — **every generated page gets a real name derived from its numbering and
title, never `index.html`** — because discovery reads names and a reader browses
directories. Media filenames stay deterministic: no clock, no content hash, no
dependence on the order the filesystem enumerates (R10).

⭐ **Also defines the identity block** every generated artifact embeds: address,
unit ordinal, variant, corpus, contract version. It lives here rather than in
SF-04 because **SF-12 writes it in M1, a milestone before SF-04 reads it in
M2** — a definition arriving after its first writer is a definition two tasks
will each guess at differently.

**Acceptance.** One address under both profiles yields two correct, different
location sets. `tree` reproduces CodeSignal's current paths exactly. `sibling`
places a unit page beside its source file. No two units in the Java corpus
produce the same artifact name. A third profile can be added without changing
any consumer.

**Out of scope.** Reading or scanning files — that is SF-04.

---

### SF-31 — Placement dry-run
**Milestone** **M2** · **Depends on** SF-03, SF-02 · **Team** solo
**Owns** `studyforge/cli/plan.py`
**Context** ~20k — spec §5, SF-03 output

**Definition.** `studyforge plan <repo>` — what *will* happen to a repository,
emitted from the manifest alone, before anything is generated: every path that
will be created, every existing file that will be edited, and the declared
reason for each.

⛔ **This task exists because one of the three seams between the framework and a
consumer had no contract at all.** The archive seam has `validate`; the runtime
seam has the components' consuming contracts; **placement had nothing** — a
consumer had to write ignore rules, declare `permitted_edits` (R3) and reason
about what would land in their repository, with no way to ask. SF-03 already
computes every bit of it and nothing exposed it.

Three consumers, all of which need it before a build runs:

- `SK-07` renders the ignore rules and the `permitted_edits` declaration from it.
- It reports the **projected media footprint** (SF-32), so "will this corpus's
  audio fit in git?" is answerable before the gigabytes exist rather than after.
- `OPS-05` asserts against it — what was planned is what happened.
- **A person** reads it before letting a tool loose in a repository they care
  about. ⭐ That is not a secondary use: an onboarding somebody cannot preview is
  one they are right not to run.

⚠️ **It reads the manifest, never the filesystem.** A dry-run that scans first
is reporting what is there, not what is coming, and the two differ precisely in
the case that matters — the first run.

**Acceptance.** Output for both FND-04 fixtures matches what a real build then
creates, path for path — asserted by running both and diffing. Names the
declared edits with their reasons. **Reports the projected media footprint and
whether it fits the corpus's `media` limits** (SF-32). Runs on a repository with
no generated output present. Adding a `permitted_edits` entry changes the plan
and nothing else. Reads no file inside the source material.

---

### SF-04 — Discovery
**Milestone** M2 · **Depends on** SF-03 · **Team** pair
**Owns** `corpus/discovery.py`
**Context** ~30k — spec §5, SF-03 output

**Definition.** R4's mechanism, and the reason the framework can be told
"artifacts go wherever suits the material". Consumes the identity block SF-03
defines, and owns **the scan**: find artifacts under a root and assemble a site
from what each file *says it is*, never from where it sits.

⚠️ Its acceptance tests **identity, not rendering** (R4). A moved page is still
correctly identified; its relative assets legitimately break, because they
resolve relative to the page (R8). Do not write a test requiring a moved page to
render — that would force absolute asset paths and break the `file://` floor.

`site.json` is a **cache of that scan and never the authority.** A stale cache
must be detectable rather than silently wrong — which is the same discipline
`status.json` applies in E03 and the same failure `layout.py` was written to
prevent.

**Acceptance.** A site assembles correctly after artifacts are moved to a
different directory. A renamed artifact is still found and correctly
identified. A stale cache is detected and the scan wins. Two corpora with
different placement profiles are found by one scan. An artifact with no
identity block is **reported by name**, never skipped silently (R6).

---

### SF-05 — Container map
**Milestone** M1 · **Depends on** SF-01, SF-02 · **Team** solo
**Owns** `corpus/container.py`
**Context** ~20k — spec §6, a real `CSD/study/paths/**/course-map.json`

**Definition.** `container.json` — the deepest container's declaration of what
its units are: address, per-level titles, variant, ingestion date, note, and
the unit list with declared practice counts. Generalises CodeSignal's
`course-map.json`. **Hand-authorable, and never written by the render
pipeline** — it is the one place human judgement about a source is recorded, so
a generator that overwrote it would erase the only thing it could not
reproduce.

One variant per container. This preserves the invariant that removed an entire
failure class: a map promising a variant the archive does not hold used to be
an ambiguous half-state, and a single-variant container cannot express it.

⚠️ **"Mechanical renaming" is not sufficient — two fields have no home.** A
real `course-map.json` carries `folder` and, per unit, `url_slug`; the
generalised shape as drafted drops both. V2-03 migrates CodeSignal using its
byte-for-byte tests as the regression harness, so a dropped field is a
migration that cannot pass. Carry them, or record explicitly where they went.

**Acceptance.** Loads a real CodeSignal `course-map.json` after mechanical
field renaming **with no field lost**. Rejects an address whose arity disagrees with `levels`, a
variant absent from `variants`, and non-contiguous unit ordinals. Declared
practice counts are preserved verbatim for SF-25 to check against reality.
