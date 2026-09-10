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
`placement`, `content`, `permitted_edits`, `media`. Refuses an unknown version rather than migrating
it at read time (R9): a migration that runs when something merely wanted to
render a page rewrites the record of what was ingested.

⭐ **`content` is new, and it is here rather than in a later task on purpose**
(CTO on X1, `handoffs/CTO-2026-09-09-rulings-q1-q3.md`; spec §4). `corpus_api: 1`
has never been consumed, so adding a field now costs nothing and adding it after
SF-02 ships costs a migration R9 makes deliberately expensive.

```json
"content": {
  "include": ["src/*.md"],
  "exclude": [
    { "path": "src/ISO.md",
      "why": "whole-series aggregate: a concatenation of 1.md…16.md (C2)" } ] }
```

⛔ **This is C2's countermeasure and C2 is a schema problem.** ISO ships both
per-unit files *and* whole-series aggregates of them, so a `src/*.md` glob
ingests every unit twice and nothing complains — and nothing in the manifest
could say otherwise. ⭐ **The asymmetry is deliberate:** an inclusion needs no
justification, an exclusion is material withheld from the reader and carries its
`why`, exactly as `permitted_edits` does for an edit. ⛔ A file under the source
root matching neither list is **unclassified** and is named and refused (R6) —
silence is the failure C2 describes, so silence is what this removes.

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
**1-level SPARQL and 1-level ISO** (`levels: ["group"]` — spec §1's table is the
correct one; §4's row has been corrected). Rejects empty `levels`, empty
`variants`, unknown `corpus_api`,
unknown `placement`, an unknown `media.commit` mode, and a `permitted_edits`
entry that names a forbidden target (R3). Accepts an absent or empty
`permitted_edits`. **An `exclude` entry with no `why` is refused**, and a file
matching neither `include` nor `exclude` is reported unclassified by name —
asserted against an ISO-shaped fixture carrying an aggregate. An absent `media` block means committed-with-default-limits,
and that is asserted rather than assumed. **No framework module
derives runnability from a variant name** — asserted. No framework module
imports anything source-specific — asserted, not assumed.

---

### SF-33 — Contract version guard
**Milestone** M1 · **Depends on** — · **Team** solo
**Owns** `version.py`
**Context** ~10k — R9, `SF-02`'s merged version check

**Definition.** One place that answers *"is this a version I accept?"*, for every
contract R9 versions. ⭐ **Promoted out of `SF-02` rather than invented**: the
check exists, it is correct for one contract, and R9 names **six** — `corpus_api`,
`container_api`, `raw_api`, `unit.json`'s `api`, the TOC schema version, and
`consuming_api`. ⛔ **Five of the six are unwritten**, which is exactly why this is
cheap now: it is one extraction today and six divergent re-implementations later.

⛔ **The naive membership test is porous, and that is the bug this closes.**
`value in SUPPORTED` accepts a JSON `true` where `1` is supported, because Python
compares them equal — so a malformed document passes the gate that exists to
refuse malformed documents. ⚠️ **The failure is silent and it is on the read
path**: nothing raises, and the document is processed as though it declared a
version it never declared. The guard checks the **type** before the value.

⚠️ **Sequenced into step 1.1, before `SF-06`.** `SF-06` is the second contract to
refuse a version (`raw_api`), and it is where a second copy would be born.

**Acceptance.** A supported version is accepted; an unsupported one is refused
naming the contract and both versions. ⛔ **A JSON `true` is refused where `1` is
supported** — asserted, with the same for `1.0` and `"1"`. Refusal is a raise,
never a migration (R9). `SF-02` imports it rather than keeping its own copy, and
⛔ **a test fails if a second version check appears in the tree.**

⛔ **Follow-up (CTO round 16, Finding 8): two refusals in this module blame the
corpus and one of them leaks.**

1. `slugify` produces an empty slug for a title with no ASCII letters, and the
   refusal reads *"titles are the corpus's, so this is a corpus defect."* ⚠️ **A
   Russian title is not a defect.** R1 says the framework knows nothing about a
   source, including its alphabet; R6 licenses failing loudly, not
   misattributing the fault. ⭐ **Name the framework's limitation instead** — the
   spec now declares it beside R10.
2. `require_slug` and `require_ordinal` format `{value!r}`, and the branch fires
   *because* the value is not a slug — which is exactly when it may be a path.
   ⛔ **7 of the tree's 26 emission sites are these two lines seen through their
   callers**; an identity's `corpus` field leaks a full path today. ⚠️ **Do not
   simply delete the echo:** *"did you pass a title?"* is the most useful
   sentence in the module. ⭐ Ruling 14 — name the type, or the character class
   and position that failed. Lands with Ruling 10's `describe` extraction, this
   pair first.


**Out of scope.** Deciding any contract's supported set — each contract's own
task owns its numbers.

---

### SF-03 — Placement policy
**Milestone** M1 · **Depends on** SF-01, SF-02 · **Team** pair
**Owns** `corpus/placement/`
**Context** ~40k — spec §5, `CS/tools/study/layout.py` (directories, media filenames)

**Definition.** The pluggable map from a logical address to physical locations,
replacing CodeSignal's single prescribed tree. Two profiles ship:

- **`tree`** — the extraction source's shape below the container segment,
  reproduced segment for segment, so its later migration moves a tree rather
  than re-deriving one. ⛔ **The page filename is the one thing it does not
  reproduce, and cannot** — that tree names every unit page `index.html`, and
  the naming rule two paragraphs below rules that out. One file per unit is
  renamed by a migration; every directory and every media href is unchanged.
  See the ruling in `docs/tasks/handoffs/CTO-2026-09-09-round14.md`.
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
location sets. `tree` reproduces the extraction source's directory shape below
the container segment for segment, and its per-unit media hrefs unchanged —
⚠️ **not its page filenames**, which the naming rule above forbids. `sibling`
places a unit page beside its source file. No two units in the Java corpus
produce the same artifact name. A third profile can be added without changing
any consumer.

### ⚠️ Revision — `Profile` grew after this task merged, and here is why

⭐ **Carried by the PO 2026-09-09, from CTO round 17 finding 12, so the next
reader is not left inferring it from a diff.**

⛔ **`SF-25`'s sibling-collision check found that `structure.py:109` branched on a
placement profile *name*** — and `SF-03`'s own `ast` test, **in another
package**, failed because of it. ⚠️ **Only the trial merge could see this**: each
branch was correct alone, which is the only situation that defect occurs in.

⛔ **Branching on a profile name is R1 in miniature** — the framework holding a
source-shaped fact by name instead of asking for a capability — so `Profile`
**gains the capability** rather than the caller gaining a special case.

⛔ **And then it did not grow, which is the part worth keeping.** ⭐ **`Profile`
gained nothing.** SF-25's author measured that the collision check needs **no new
capability** — `test_nothing_downstream_branches_on_a_profile_name` went **1
failed → 1 passed**, with **zero** profile names in `validate/` and **zero**
profiles skipped — and declined to add one, on the same rule that had been used
to schedule it: ⛔ **a capability designed by somebody with no caller is a guess**,
and here it would have had **no caller at all.**

⚠️ **So this contract is unchanged, and the record exists to stop somebody adding
the capability later on the strength of a ruling that was withdrawn.** ⭐ The
defect was real and is fixed **in the caller**, where it was: `validate` no longer
knows any profile by name.

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
creates, path for path — asserted by running both and diffing. ⭐ **That output
is committed for both fixtures as the golden file**, and it is the first golden
the fixture tree gets: `FND-04` could not write one, because §5 pins the *kinds*
of path but not artifact naming, and `SF-03` owns the derivation. This is the
cheapest close on the largest deferred gap, and it puts the golden beside the
contract that produces it rather than three milestones upstream of it. Names the
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

⭐ **R21's row for this contract is CLOSED — Ruling 95, CTO round 27.** ⛔ **The
key is `site_api`**, minted in `src/studyforge/version.py`'s `CONTRACT_FIELDS`
**in the same commit that writes the cache**, per that tuple's own convention;
`SF-09`'s `content_api` is the worked example. ⛔ **`SF-04` is the one writer** —
`placement` names the file and the renderer addresses it, but nothing else
produces it.

⛔ **Two things about `site_api` that a builder will otherwise get wrong, and
both are ruled:**

1. ⛔ **An unsupported or absent `site_api` does not raise.** It means *the cache
   is not read*: the scan runs and the cache is rewritten at the current
   version. ⭐ That IS R9's refusal — nothing in the old document is carried
   forward, so nothing is migrated — and it is the only reading compatible with
   §5's *"the scan wins"*. ⚠️ Use `version.is_supported`, **not**
   `version.check`: that module documents `is_supported` as the predicate *"for
   a caller that reports rather than refuses"*, and this is that caller. ⛔ The
   re-scan is **reported** (R6), naming the path and both versions — never
   silent.
2. ⛔ **`site_api` is NOT the staleness mechanism.** It answers *"is this the
   shape of cache I speak?"* and nothing else. Content staleness — the tree
   moved since the cache was written — is a separate signal and a separate
   test. ⚠️ Bumping `site_api` per scan would make a contract version into
   mutable data and would break R9 for every other reader of that tuple.

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
`course-map.json`.

⚠️ **"Hand-authorable" is about two fields, not about the document, and the two
readings only look contradictory** (CTO ruling on Q3,
`handoffs/CTO-2026-09-09-rulings-q1-q3.md`). ⛔ `container.json` is **generated**
by the adapter on ingest (spec §6, `JS-05`) and amended only by `EX-04`'s
declared practice counts; ⛔ the render pipeline never writes it, and neither
does a person write it from nothing. What a person may amend are the
**editorial** fields the generator round-trips rather than overwrites — a
corrected `title`, a `note` — and a generator that would discard one **stops**
(§6, R6).

⭐ **That is not a hole in a skill.** R19 forbids a second source having to
*retype* what a skill could have produced; a corrected title or an explanatory
note is not retyping, it is a judgement about one's own material, which is the
one thing no skill can produce. ⛔ Anything that *is* derivable — the address,
the titles from the source, the variant, the unit list — is generated, and
hand-writing it is a finding against the adapter-authoring skill.

**This task builds the reader and the round-trip guarantee. It builds no
writer.**

One variant per container. This preserves the invariant that removed an entire
failure class: a map promising a variant the archive does not hold used to be
an ambiguous half-state, and a single-variant container cannot express it.

⚠️ **"Mechanical renaming" is not sufficient — two fields have no home.** A
real `course-map.json` carries `folder` and, per unit, `url_slug`; the
generalised shape as drafted drops both. V2-03 migrates CodeSignal using its
byte-for-byte tests as the regression harness, so a dropped field is a
migration that cannot pass. Carry them, or record explicitly where they went.

⛔ **Three per-unit fields are ruled on before the map freezes**
(`handoffs/CTO-2026-09-09-round14.md`). R9 versions this contract and never
migrates it at read time, so a field added after SF-05 costs a `container_api`
bump and every archive already written — which makes "decide it later" the
expensive option, not the cheap one.

1. **`label`** — *optional* `str`, the corpus's own display numbering for the
   unit, spelled the way the corpus spells it (`4.4.1`, `1`, `04`). ⚠️ Not a
   slug: it is presentation. ⛔ It may not be empty and may not carry a path
   separator or whitespace, because it becomes part of a filename — SF-03's
   `label_of` already enforces exactly that and already has the assertion that
   it reproduces spec §5's worked example. ⭐ **It is not speculative**: §5
   commits to an output that cannot be produced without it, and the seam that
   consumes it is written and tested. Absent, a unit is named by its ordinal.
2. **`origin` on a unit** — a path to the **source file**, relative to the
   source root, never a directory and never absolute. Load-bearing: `sibling`
   places by it and refuses its absence (R6).
3. **`origin` on a container** — ⛔ **also a file**, not the container's
   directory. Placement takes its parent, so a container recording a directory
   silently places its page one level too high, at the repository root. The
   fixtures already record `…/README.md`; that convention becomes contract
   here, and ⚠️ **SF-25 enforces it**, because placement does no I/O and
   cannot tell a file path from a directory path.

**Acceptance.** Loads a real CodeSignal `course-map.json` after mechanical
field renaming **with no field lost**. Rejects an address whose arity disagrees with `levels`, a
variant absent from `variants`, and non-contiguous unit ordinals. Declared
practice counts are preserved verbatim for SF-25 to check against reality.
**An edited `note` and `title` survive a re-read unchanged** — asserted, because
that round-trip is the entire content of "hand-authorable".
