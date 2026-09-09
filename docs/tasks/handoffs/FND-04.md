# FND-04 — handoff

**Status:** done · **follow-up landed 2026-09-09** — Q1's `disclosure` block
(`CTO-2026-09-09-rulings-q1-q3.md`). Read *The Q1 follow-up* below before the
sections it changed; the rest of this handoff is the original task.

---

## The Q1 follow-up — `disclosure` is a container block

⭐ **The contract moved, and the fixtures moved with it.** FND-04 originally
encoded a `<details>` as one opaque `html` block. The CTO ruled that reading
out: a disclosure is a **container block**, `disclosure`, holding blocks
exactly as `quote` does.

```json
{ "type": "disclosure", "summary": "Show the answer", "open": false,
  "blocks": [ {"type": "para", "text": "…"},
              {"type": "code", "lang": "sparql", "text": "…"} ] }
```

Both earlier readings fail, and they fail **oppositely** — flattening keeps the
text and destroys the hiding (all six SPARQL uses hide an exercise answer);
one opaque `html` block keeps the hiding and makes the body invisible to
SF-25's block-count gate. ⭐ *Present but withheld* is a third state, which is
**C5's lesson landing in the block vocabulary**. The archive records the
semantics and the label; that the markup is `<details><summary>` is SF-12's
decision (**R13**), and narration speaks the `summary` and stops.

**What changed:** `disclosure` in `BLOCK_FIELDS` (`type`, `summary`, `open`,
`blocks`) and `COUNT_KEYS` (`disclosures`); a new `CONTAINER_BLOCKS` tuple that
every walker recurses on, so the *next* container is not forgotten the way this
one was; three fixture documents; and `counts` rewritten on all 15 archive
documents, because a count key that exists must exist everywhere including the
zeroes. ⛔ `content_sha256` was **not** recomputed for the fifteen — no block
changed, and recomputing would have quietly repaired
`invalid/digest-mismatch/`, which exists to be broken.

⚠️ **Step 5 of the CTO's instruction — the module split — is NOT in this
change.** It was re-routed to another agent so it does not sit on M1's critical
path; nothing for it was started here. The formatter exclusion and its
one-entry assertion are still in place and must be deleted in the same commit
as that split.

---

## What landed

`tests/fixtures/` — two valid synthetic corpora, five deliberately invalid
ones, and a README that is the human-readable index of all seven.
`tests/test_fixture_consistency.py` — 553 lines against R11's 600-line test
ceiling, stdlib + `pytest`, imports no
`studyforge` module (there is none yet, and a fixture check that needed the
framework could not run until the framework did).

```
tests/
  fixtures/README.md
  fixtures/depth1/     1 level  · 1 container · 3 units (4 documents) · 0 exercises
  fixtures/depth2/     2 levels · 2 containers · 5 units · 2 practices
  fixtures/invalid/    bad-corpus-api · address-directory-mismatch
                       digest-mismatch · ordinal-gap · personal-data
  test_fixture_consistency.py
```

⭐ **`depth1` is the common case, and is built as one.** Two of the four
designed source shapes are depth 1 — SPARQL (`["course"]`) and ISO-8583
(`["group"]`; spec §1 is right and §4's table row is stale). It is not a
reduced `depth2`: it exercises two things `depth2` does not — a unit carrying
**two** archive documents, and real media on disk with real digests and byte
counts. ⛔ If a task makes `depth1` look degraded, the task is wrong.

⛔ **The fence-awareness fixture is the highest-value thing in the set.**
`depth1` unit 3 `lesson-2.json` carries three fenced blocks of XML and HTML
(Maven POM, Spring beans, an HTML fragment) **beside a raw `html` block using
the same `<details>`/`<summary>` tags**, in one document; `depth2`'s closing
unit carries a fenced POM too. A parser that scans for `<` without tracking
fences now fails against a fixture that names the defect rather than against
real material — and it fails silently everywhere else, which is why this is
worth a dedicated test rather than a comment.

`violations(root)` in the test module is the reusable surface: it returns
`[(rule_id, message)]` for a corpus and is empty for a valid one. The invalid
corpora are asserted to break **exactly one** rule each — that is what makes
them usable as SF-25's acceptance inputs, because a fixture breaking two rules
cannot tell you which check you were exercising.

**Verified, not asserted.**

- `22 passed`.
- Block-type coverage, counted rather than believed: `depth1` 9 of 10 (no
  `video`, which neither depth-1 shape has); `depth2` **10 of 10**. The module
  prints the table when run directly:
  `python3 tests/test_fixture_consistency.py`.
- Fence awareness is **asserted, not documented**: one test requires each
  corpus to carry markup-shaped text inside a `code` block, and a second
  requires at least one tag to appear both fenced and raw *in the same
  corpus*, so the discriminator cannot be edited away by accident.
- Every check was proved to bite by mutating a **copy** of a valid corpus —
  deleting a declared unit, editing a block, moving a container, opening an
  ordinal gap, mis-declaring a practice count, injecting a home path, using an
  unknown block type, re-sorting the keys on disk, removing declared media,
  writing `workspace` into an overlay, and renaming a variant. All eleven were
  caught, each naming the rule.

## Decisions

Everything below the spec did not settle. Each is a **stated assumption**, and
each is cheap to reverse — the fixtures are generated-shaped data, not code.

1. **The archive document's key order** is CodeSignal's, widened as SF-06
   describes: `raw_api source address variant unit kind ordinal ingested title
   blocks video assets attachments counts content_sha256`, then
   `assets_sha256 starting_code media_skipped` only when they have something to
   say and always after the digest. `path`+`course` became one `address`;
   `language` became `variant`; `captured` became **`ingested`**, matching
   §6's `container.json` and §6's exemption of it from R10.
2. **`source` is the corpus identifier, not a URL.** CodeSignal's `source` was
   the page address it fetched. §6 rules that provenance is called `origin`
   *because* `source` is already the manifest's own identifier, so the fixtures
   use `source` for the corpus id.
3. **`origin` lives in `container.json` and not in the archive document.** §6
   shows it there literally, per container and per unit. Two records carrying
   it would be two records that can disagree, and §6 makes a disagreement about
   an *address* a refusal without saying what a disagreement about provenance
   is. ⚠️ If SF-06 wants provenance in the archive document too, add the key —
   but rule on which record wins at the same time.
4. **`attachments` is a required key holding `[]`**, exactly like `assets`,
   rather than an optional key that is absent when empty. "Absent" and "empty"
   are then not two states a reader has to distinguish. Its entries reuse the
   asset-manifest entry shape (`remote local sha256 bytes content_type kind`)
   with `remote: null`, so there is one entry vocabulary rather than two.
5. **`counts` grew with the vocabulary** — ten keys now, one per block type,
   always all of them including the zeroes.
6. **The container blocks hold blocks, not text** —
   `{"type":"quote","blocks":[…]}`, and since the Q1 follow-up
   `{"type":"disclosure","summary":…,"open":…,"blocks":[…]}`.
   CodeSignal's `_quote` parses a blockquote's content back through `parse`
   because a quote can hold a list, a fence or a table; a `text`-only quote
   would lose exactly what SF-07's *never silently drop* rule exists to keep.
   `rule` is `{"type":"rule"}` and `html` is `{"type":"html","text":...}`.
7. **`video` is a block type as well as a document record.** SF-07 names nine
   types because it describes what the *Markdown reader* produces;
   CodeSignal's archive vocabulary also carries `video`, and
   `rawdoc.declared_media` walks blocks of that type. `depth2` exercises it,
   `depth1` does not. If SF-06 rules it out, deleting one block is the whole
   change.
8. **`media` in the manifest** is `{"commit": "auto", "max_total_bytes":
   5000000000, "max_file_bytes": 104857600}` — the mode names are SF-02's, the
   two limit names are mine, and the values are §5's measured numbers (~5 GB
   soft, 100 MiB hard). SF-32 owns the real names. `depth1` omits `media`
   entirely, which is SF-02's "absent means committed-with-default-limits" case
   and needs a fixture as much as the declared one does.
9. **The authored overlay is `<container>/units/unit-NN/content.json`**,
   mirroring CodeSignal, carrying `address unit title sections`. It has **no
   version key**: R9 enumerates the versioned contracts and the overlay is not
   among them. Sections are `kind lang heading blocks` plus an optional `key`
   (exercised once). It carries **no `workspace` and no `video`** — both are
   derived from the archive and are "not the author's to write" (SF-10b), and
   the fixture check refuses an overlay that writes either.
10. **`folder` and `url_slug` — SF-05's two homeless fields — are answered.**
    `folder` is a real `course-map.json`'s slug path, which is exactly what
    `address` already is, so it is **subsumed, not dropped**. `url_slug` has no
    equivalent and is carried as an optional per-unit key; `depth2`'s second
    container carries it so SF-05 has an input.
11. **`archive/` is a stand-in for `<archive-root>`.** §6 writes the root as a
    variable and §5 shows `.studyforge/archive/` under `sibling`. A plain
    directory keeps the fixtures browsable; consumers must take the root as a
    parameter. An asset's `local` path resolves against
    `<container>/units/unit-NN/`, which is where CodeSignal resolves it
    (`run_capture_audit` uses the *unit* directory, not the raw one).
12. **The invalid fixtures name their rule in `VIOLATION.md` inside the
    fixture directory**, because JSON has no comments and a `_comment` key
    would itself be a second violation of the key-order contract. Each names
    the rule, the file, and what SF-25 is expected to say.
13. **No binary is committed.** `depth1`'s image and attachment are real small
    text files (SVG and Turtle) with real digests and byte counts, so the
    media-presence and media-digest paths are genuinely exercised.
    `depth2`'s video is declared and **not** fetched, carrying `media_skipped:
    true` with an empty manifest — which is what that marker is for.

14. **`depth2` gained a disclosure too, which the instruction did not ask
    for.** Step 4 said to add `disclosure` to `depth1`'s `REQUIRED_TYPES` —
    but both corpora's required sets are *derived* from `BLOCK_FIELDS`
    (`depth1` filters out `video`; `depth2` takes all of it), so adding the
    type required one in **both**. The alternative was excluding `disclosure`
    from `depth2`'s set, which is weakening a test to fit a change. It went
    into `depth2`'s practice as a withheld **hint inside a Problem statement**
    — the ruling's own use case, and it exercises a container block inside the
    practice layout that `blocks.py` parses. The overlay quotes those blocks
    verbatim, so it was updated in step.
15. ⛔ **A second `<details>` was converted, beyond the four literal steps.**
    `depth1` unit 3 `lesson-1.json` also stored a disclosure as a raw `html`
    block. Leaving it would have shipped a corpus where two **adjacent
    documents encode the same construct two different ways** — the exact
    contradiction R21 exists to remove, in the one fixture set twelve epics
    build against. ⚠️ It is flagged here rather than buried because it is
    outside the instruction: overrule it and the change is a two-line revert.

## Surprises

- **The context budget (~35k) was roughly right but pointed at the wrong
  place.** §4–§6 do not define the archive document's key set, the block
  shapes, `counts`, the overlay, or the asset-entry shape. All of it had to
  come from CodeSignal's `rawdoc.py`, `blocks.py`, `content.py`, `unitdoc.py`
  and a real `course-map.json` (R20 permits this and it was essential). A task
  reading only "spec §4–§6, `CS/tests/fixtures/`" would have had to invent all
  five. ⚠️ **`CS/tests/fixtures/` itself was almost no help** — it holds
  CodeSignal's *browser payloads* and anonymised HTML pages, not archive
  documents. The useful material is `CS/tools/study/` and the live `study/`
  tree.
- **The documented placeholder address cannot be used as a personal-data
  fixture.** CodeSignal's `assert_clean` skips a match equal to its own
  replacement value, so a fixture built out of the placeholder every one of
  these documents recommends is refused by *nothing*. The fixture uses a
  fabricated address under the RFC 2606 reserved `.invalid` TLD instead, and a
  test asserts the fixture really is refused — otherwise SF-08 and SF-25 would
  both be accepted against an input that quietly passes.

## Golden files — what is here, and what is deferred to whom

⭐ **The fixtures are the golden files for everything the spec pins down.**
The manifest, the container map and each archive document are written in their
canonical form, so "does the writer reproduce this?" is a byte comparison
against the fixture file itself. `test_fixture_consistency.py` asserts each
archive document re-renders byte-for-byte from its own parsed content, which is
SF-06's byte-for-byte acceptance already available as an input.

⛔ **Nothing else has a golden file, deliberately.** SF-10, SF-11 and SF-12 are
unwritten. A golden file for output nobody has designed is a fixture that will
be wrong and will be trusted, and every task after it would inherit the mistake
as a requirement.

| Deferred golden | Owed by | Why FND-04 could not write it |
|---|---|---|
| `unit.json` for each of the 8 units | **SF-10** | §6 does not state the served document's keys, its `api` value, its section array or how a derived section keys. SF-09 has not defined section keys either. |
| The rendered unit page, section page and root index | **SF-12** (+SF-11) | No renderer, no templates, no asset names, no identity-block spelling. SF-03 owns the identity block and has not drawn it. |
| `toc.json` and `status.json` | **SF-13/SF-14** (E03) | R9 names a "TOC schema version" and nothing else about the shape. |
| `site.json` discovery cache | **SF-04** | It is a cache of a scan that does not exist. |
| `studyforge plan` output for both corpora | **SF-31** | SF-31's own acceptance is "matches what a real build then creates". §5 pins the *kinds* of path but not artifact naming — the worked example derives a page name from the **source filename**, not from the address, and SF-03 owns that derivation. A golden written now would pin the wrong rule. |
| Narration clip manifest and speakable text | **SF-17/SF-18** (E04) | §8.2's clip-name digest is defined; what it is taken over is not. |
| The exercise workspace / provenance / trust record | **SF-09, SF-23** (E06) | §7 says an exercise *declares* `main_path`, `test_path`, `run_command`, `test_command`, `provenance` and `trust` — but no file in §4 or §6 has a place to put the declaration. See Findings. |

⭐ **When SF-31 lands, its acceptance is the cheapest way to close the largest
of these:** run `plan` against both fixtures, commit the output as the golden,
and the placement contract stops being folklore.

## Findings

Defects and gaps seen outside FND-04's scope. **Not fixed, not in the diff.**

⭐ **Triaged, not merely filed** — each carries `[local]` or `[structural]`, and
every `[structural]` one is ruled, scheduled, or explicitly open. The test is
one question: *would this happen again to somebody else?* ⚠️ Finding 10 is why
that rule exists: it was filed correctly, in the right place, and came true
twice more because nothing obliged anyone to act on it.

1. `[structural]` ✅ **RULED (Q3).** *Original finding:* `container.json` had two owners in two documents. Spec §6 rules it is
   *generator-owned with preserved judgement* — "an adapter **generates**
   `container.json` on ingest (JS-05)". `docs/tasks/E01-core-contracts.md`
   SF-05 says it is "**Hand-authorable, and never written by the render
   pipeline**". These are reconcilable (a generator writes it; the render
   pipeline never does) but they read as a contradiction to anyone picking up
   SF-05, and R19 leans hard on nothing being hand-authored. Worth one
   sentence in SF-05.
2. `[structural]` ✅ **RULED (Q2)** — an `exercise` object inside `practice-M.json`, on the existing `raw_api`, written by the adapter. *Original finding:* §7's exercise declaration had no file. Every other contract in §4–§6
   names the document it lives in. `main_path`/`test_path`/`run_command`/
   `test_command`/`provenance`/`trust` name none, so FND-04 could not ship a
   fixture for the thing R5 exists to enforce. E06 will need one, and it will
   need an FND-04-style fixture the day it starts. Candidates: a `practice`
   section of the overlay, a per-practice key in the archive document, or a
   third document. This is a real hole on E06's critical path.
3. `[structural]` ⚠️ **OPEN** — now row 1 of §2's register of located contracts, owed before the overlay is built. R9 enumerates the versioned contracts and the authored overlay is not
   among them** (`corpus_api`, `container_api`, `raw_api`, `unit.json` `api`,
   TOC schema). The overlay is hand-edited, which is the *most* likely thing to
   drift. The fixtures follow R9 literally and ship an unversioned overlay; if
   that is wrong, it is R9 that needs the edit, not SF-09.
4. `[structural]` ✅ **RULED and APPLIED** to the spec by the CTO. *Original finding:* spec §1's C3 was wrong on its numbers and §4's ISO row was stale.
   *(Both confirmed by the CTO's recount; recorded here because the fixtures
   are built on the corrected reading.)* C3 says "18 of ISO's files contain
   raw HTML"; with code fences stripped it is **0 of 38** — all 26
   `<tag>`-shaped matches are XML inside fenced blocks. And §4's table gives
   ISO `levels` as `["section","subsection"]` where §1 says it is 1 level:
   `["group"]` is correct. ⚠️ Neither correction weakens the vocabulary: raw
   HTML is a **SPARQL** requirement (6 of 19 lessons carry `<details>`), and
   `rule` and `quote` are the **Java corpus's**, so SF-07 needs all three at
   M1 regardless. What changes is *which* constraint is real — fence
   awareness, not tag counting.
5. `[structural]` ✅ **RULED (Q1b) — narration speaks a disclosure's summary and stops.**
   *Original finding:* nothing ruled on whether the speakable contract walks an
   `html` block.
   ⛔ If it does, and the block is a `<details>` disclosure, **narration reads
   aloud an answer the page is deliberately hiding** — which is exactly what
   `depth1` unit 3 carries, in both fenced and raw form. Not FND-04's to
   decide and not attempted here; it lands on SF-17/SF-18 (E04) and the
   fixture is ready for whichever way it is ruled.
6. `[local]` — carried into SF-07's own task text, and now **three** places, not two: `disclosure` joins them. CodeSignal handles `rule` and `quote` in the opposite direction to
   SF-07**, and the divergence should be recorded rather than discovered.
   CodeSignal HEAD emits **no block at all** for a thematic break and emits a
   quote's *inner* blocks transparently — both to agree with its DOM reader,
   for which `<hr>` and `<blockquote>` are not block tags. SF-07 correctly
   makes them block types for studyforge (a repository-shaped source has no DOM
   reader to agree with), but a task told to "port `markdown.py` with its
   governing rule intact" will find the current source doing the opposite and
   should know that is intended.
7. `[structural]` ⚠️ **OPEN** — every port task inherits it. §8's snapshot warning is already live for E02. CodeSignal's
   `markdown.py` is 678 lines against R11's 400 and `unitdoc.py` is 827 — both
   arrive as packages, and SF-07 owns one file today.
8. `[structural]` ◐ **PARTLY RULED (X2)** — R7 governs what the *build environment* leaks, not what the material is about; what is still open is whether the sweep reads `docs/` at all. A repository-wide R7 sweep is not clean today, and one hit is a
   *correct* refusal to teach a scrubber about.** Sweeping this repository with
   the email shape matches `docs/tasks/E02-content-pipeline.md`, which quotes
   `n@router` + `.get` as the escaping artefact that refused three clean OAuth
   lessons. ⚠️ That is E02's own worked example of a false positive, so it is
   evidence the sweep works, not a leak — but SF-08's "no generated file, log
   or report contains personal data, asserted by a repository-wide check" needs
   to say whether it sweeps `docs/` at all, and if so what it does with a
   document whose subject *is* the pattern. FND-04 left it alone (finding, not
   patch).
9. `[structural]` ✅ **SCHEDULED** — the module split is routed to another agent and lands before M1 closes; it deletes the formatter exclusion in the same commit. The 400-line ceiling and the `graphify-out/` index are FND-01's and
   FND-02's**; neither exists on this branch, so nothing here was checked
   against them. `test_fixture_consistency.py` is 553 lines against the
   **600-line test ceiling**, which is inside it but no longer comfortably: a
   sixth invalid fixture would want the module split along the same seam the
   checks already have (shape · digests · addresses · media · personal data).
10. `[structural]` ✅ **RULED — and it came true twice more before it was.** The CTO took both mitigations and refused the do-nothing option (*a cost paid fifteen times is not a known cost, it is a policy of paying it*), then found the deeper cause: the rubric diffed and tested each branch's own changes, answering *is this change good?* where a merge gate asks *is the result good?* — and those come apart precisely when two parallel tasks are each correct alone. A trial-merge step is now in the review procedure. ⛔ **The quality floor cannot be enforced on a branch authored in parallel
    with the task that introduces it — and this is structural to M0's plan,
    not incidental.** Finding 9 predicted the shape; the merge gate then
    produced it. FND-04 was reviewed green and merged; FND-01's checker, seen
    for the first time on the combined tree, found one line of
    `test_fixture_consistency.py` at 110 characters against a 100 limit, and
    the trial merge went red. ⚠️ **Neither branch could have seen it alone**:
    FND-04 had no style checker and FND-01's checker had never seen FND-04's
    module. Fixed on `fix/FND-04-line-length`, off `release/m0-foundations`.

    ⭐ The general case: **any parallel task that authors Python before FND-01
    merges will hit this**, and the cost lands at the gate rather than in the
    task. M0 staffs FND-01…FND-05 as parallel, so E00 is where it is cheapest
    and every later wave inherits a floor that already exists. Three options
    for the PO, cheapest first: land FND-01's checker config *alone* as a
    wave-0 prerequisite ahead of the parallel work; or have the gate run the
    incoming checker over every branch before approving rather than after; or
    accept a style-fix round trip per parallel Python-authoring task as a
    known cost. FND-04's own experience says the first is nearly free — the
    fix was one wrapped line, found in seconds once a checker existed.

    ⚠️ **Scope note for whoever configures the checker.** It reported a
    Python file. `tests/fixtures/README.md` and this handoff both carry
    Markdown **table rows** well over 100 characters, which cannot be wrapped
    without destroying the table. If the floor is ever extended to Markdown,
    it needs a table-row exemption, or those two documents become
    unmaintainable.

## For dependents

**Read `tests/fixtures/README.md` first.** It carries the per-unit table — what
each unit exists to exercise — which is the part you actually need.

**How to consume them.** Take the corpus root as a parameter and derive
everything from `corpus.json`. ⛔ Do not hardcode `archive/`: that name is a
stand-in for `<archive-root>`, which SF-03 owns.

**What each fixture is *for*.**

| You are working on | Use | Because |
|---|---|---|
| SF-01 address model | both | `["depth-one"]` is depth 1, `["basics","01-getting-started"]` is depth 2. Segments include a leading-digit slug (`01-getting-started`, `02-going-further`) — SF-01's identifier rule prefixes rather than drops it. |
| SF-02 manifest | both | `depth1` is `tree`/no-exercises/**no `media` key**/empty `permitted_edits`; `depth2` is `sibling`/exercises/declared `media`/one `permitted_edits` entry. Between them every field is exercised in both states. |
| SF-03 placement, SF-31 plan | both | Two profiles, two depths, two containers, media both present and skipped. ⚠️ You owe the golden nobody could write yet — see the deferred table. |
| SF-05 container map | `depth2` | Two containers, `url_slug` on the second, per-unit `origin` and `note`, declared practice counts of 1 and 0. |
| SF-06 archive document | both | Every optional key is exercised: `assets_sha256` (`depth1` u2), `starting_code` (both practices), `media_skipped` (`depth2` A/u3). Each file **is** its own canonical rendering — round-trip is a byte comparison. |
| **SF-07** Markdown reader | both | ⭐ **`disclosure` is a container block** — do not flatten (it shows an answer the author withheld) and do not store raw (its body goes invisible to the block-count gate). `depth1` u3 carries two, one of them beside a fence *about* a `<details>`. |
| SF-07 Markdown reader, cont. | both | All nine reader types. ⛔ **Start with `depth1` u3 `lesson-2`** — fence awareness is the constraint that actually bites, and a `<`-scanning parser passes every other fixture here. `depth1` u2's `quote` nests a `para` **and** a `list`, which is the case a text-only quote loses. |
| SF-08 personal-data gate | `invalid/personal-data/` | Carries a home path **and** an email, both fabricated. ⛔ Your repo-wide sweep must exclude that directory **and only that one**. |
| SF-09 overlay, SF-10 builder | `depth2` | One unit **with** an overlay and two **without** — the authored and derived shapes are different code paths. The overlay carries an explicit `key` on its practice section (SF-09's escape hatch) and writes neither `workspace` nor `video`. |
| SF-25 `studyforge validate` | `invalid/*` | Five inputs, one rule each, the rule named in the fixture's own `VIOLATION.md` with the message you are expected to produce. Both valid corpora must exit 0. |
| E03/E04 contents & narration | `depth1` | Three units, one variant, zero exercises: the smallest corpus that still has a table of contents and something to speak. ⚠️ It also carries the unresolved `<details>` question — see Findings 5. |
| E07/E08 the Java adapter | `depth2` | It is the Java shape at 1/30th the size. Get it green here before pointing anything at 166 files. |

⭐ **`depth1` is not a reduced `depth2`.** It is the reading floor (spec §11.0)
in its complete form — narrated, navigable, offline, with no exercises and no
server. ⛔ **A corpus with no graders is complete at M4, not short** (§7, C5).
If your task makes `depth1` look degraded, the task is wrong, not the fixture.


⭐ **New consumers of the Q1 follow-up.**

| You are working on | What the fixtures now give you |
|---|---|
| **SF-07** | Two `disclosure` blocks in `depth1` and one in `depth2`, each holding real blocks — and, in `depth1` u3 `lesson-2`, a fenced code block whose text *is* a `<details>`, so a reader that cannot tell a fence from markup fails here rather than on real material. |
| **SF-12** (render) | The archive gives you `summary`, `open` and `blocks`. The `<details><summary>` markup is **yours** to choose (R13) — the fixture deliberately does not prescribe it. `open` is the author's default and is honoured, not overridden. |
| **SF-16 / E04** (narration) | ⛔ Speak the `summary`; **do not walk the body**. The body gets no speech ids, so a clip for it cannot be minted or addressed. The withheld count belongs in the coverage report. ⛔ Do not invent a spoken sentence announcing the hidden section. |
| **SF-25** (validate) | `counts` now has eleven keys and `disclosures` is one of them. Nested blocks are **not** counted — same as a quote's — so your completeness gate counts top-level blocks and recurses separately if it wants the total. |

**Changing a fixture.** Change it and run
`python3 -m pytest tests/test_fixture_consistency.py`. Every digest, count and
key order is recomputed and checked there; nothing is maintained by hand. If
you need a shape these fixtures do not carry, **add a fixture rather than
bending one** — a downstream epic is already testing against the one you were
about to edit.
