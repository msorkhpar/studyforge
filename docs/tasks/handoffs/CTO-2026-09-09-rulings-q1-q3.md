# CTO-2026-09-09-rulings-q1-q3 — handoff

**Kind:** ruling record

**Status:** done. Q1, Q2, Q3, X1 and X2 are ruled and carried into the documents
they touch. ⭐ **SF-07 is unblocked; M1 step 1.1 has no open question left.**

⚠️ **These are decisions, not reviews.** Each is applied to the spec and the task
documents in the same commit, because a ruling that lives only in a handoff is
one the next agent will not find (`delivery-flow.md`).

---

## The pattern first — it generalises much further than Q1 and Q2

The PO asked whether *a contract the spec describes but does not locate* is one
thing worth ruling on rather than three cleanups. ⭐ **It is, and I surveyed the
spec rather than assuming: five more instances are already sitting in it,
unowned.** So it is now **R21**.

> **R21 — A contract is located before it is described.** Every document the
> framework reads or writes states **the file it lives in**, **the key that
> versions it** (R9), and **the one producer that writes it**, before any task
> builds against it. ⛔ A task that meets an unlocated contract **stops and
> asks**; it does not choose.

**Why it has to be a ruling and not advice.** R9 is the reason. Every other kind
of gap gets fixed by the next task that trips on it — but an *invented location*
ships inside a version that refuses to migrate at read time, so by the time two
tasks disagree, the wrong answer is load-bearing. ⭐ **R9 makes this the one
class of gap that gets more expensive rather than less.**

⚠️ **And none of the three that already happened was the tripping task's
fault.** `FND-04` could not fixture §7's exercise declaration because it named
six fields and no file. `SF-05` and §6 disagreed about `container.json` because
neither said which producer owned which case. `SF-07` and `FND-04` ruled
`<details>` oppositely because the vocabulary described `html` without saying
what a disclosure *is*. Each was a gap a task was **obliged to fill and not
equipped to fill**, which is why R21 binds on the spec, not on the builder.

**§2 now carries a register of located contracts.** Eight are closed. ⛔ **Five
are open and each is owed by a named task before that task builds:** the
authored overlay's version, `site.json`'s schema, the narration manifest, the
coverage report's shape, and `consuming.json`.

⚠️ **The overlay's row is the one I would fix next.** It is the only document a
**person** edits, which makes it the likeliest to drift, and R9 does not list it.
`FND-04` followed R9 literally and shipped it unversioned — correctly, on the
information available. Either R9 gains it or R9 says in words why a hand-edited
document needs no version. Silence is the third option and it is the one R21
exists to remove.

---

## Q1 — `<details>` · **due before SF-07, which is now startable**

⭐ **A disclosure is a container block. Narration speaks its summary and stops.**

Two rulings, and the PO was right that one without the other only moves the
defect.

### The archive: `disclosure`, holding blocks exactly as `quote` does

```json
{ "type": "disclosure", "summary": "Show the answer", "open": false,
  "blocks": [ { "type": "para", "text": "…" },
              { "type": "code", "lang": "sparql", "text": "…" } ] }
```

Both existing readings fail, and they fail **oppositely**, which is the tell that
neither is the answer:

- ⛔ **Flattening** (CodeSignal's `markdown.py`: tags dropped, `summary` → a
  `para`) keeps the text and destroys the hiding. All six SPARQL uses hide an
  **exercise answer**, so flattening shows the answer outright. ⚠️ It is right
  *there* — `<details>` is not in `lesson_html.BLOCK_TAGS`, so its DOM reader
  emits nothing and the parser must agree with it. studyforge has no DOM reader
  to agree with, so the reason does not carry.
- ⛔ **One opaque `html` block** (`FND-04`'s) keeps the hiding and makes the body
  invisible to everything else. A fenced query inside an answer would not be a
  `code` block: uncounted, unhighlighted, and unreachable by SF-25's
  *no unit yields fewer blocks than its source implies* gate — which is the check
  that exists precisely to catch content going missing quietly.

⭐ **The resolution is the one C5 already taught this project.** C5's lesson was
that "no exercise" and "graded exercise" are not the only states, and collapsing
the middle one deleted real teaching content. This is the same lesson in the
block vocabulary: **shown** and **absent** are not the only states, and *present
but withheld* is real content. It gets a block.

Four properties that make it the right shape rather than a compromise:

1. **It is a shape the vocabulary already has.** `FND-04` ruled `quote` holds
   blocks rather than text because a quote can hold a list, a fence or a table.
   A withheld section holds the same things, for the same reason. Two container
   blocks, one shape, no new concept to learn.
2. **Nothing is dropped and nothing is opaque.** SF-07's governing rule is
   *never silently drop a line*; a `text`-only container breaks it, and an opaque
   one breaks it invisibly.
3. ⭐ **The archive records semantics; the renderer owns markup.** The document
   says *this is disclosed on demand, and here is its label*. That
   `<details><summary>` is the markup is SF-12's template decision — **R13
   exactly**. `FND-04`'s reading smuggled a presentation choice into the archive,
   where R13 says it must never live.
4. **R1 holds with no manifest data at all.** No source is named; any Markdown
   with a disclosure gets this.

`summary` is content: gated, counted, and rendered. `open` is the author's
default and is honoured, not overridden.

### Narration: the summary is spoken, the body is not

⛔ **The speakable contract does not walk a disclosure's body.**

The author decided the reader should **choose** when to see this. Reading it
aloud overrides that decision silently, on a surface the reader cannot see — the
page still shows the section collapsed while the audio gives the answer away.

⭐ **The decisive argument is §8.5's own, about read marks: a record the reader
cannot trust is worse than none.** Narration that *sometimes* reads out the
answer is narration nobody can leave playing, and that loses the feature for the
whole corpus, not for one lesson.

⚠️ **Withheld is not dropped, and R6 still applies.** The summary gets a speech
id; the body gets **none**, so a clip for it cannot be minted or addressed
(§8.2's structural argument works in our favour here — an unnameable clip is an
unsynthesisable one). The unit's speakable record states how many blocks it
withheld and the coverage report names units with unspoken content, so the
omission reads as a decision rather than as a bug in the walker. ⛔ Do not invent
a spoken sentence announcing the hidden section — that is narration writing prose
the author did not.

⚠️ **No manifest knob, and that is deliberate.** The rule is uniform, so R1 holds
with no per-corpus data; a knob nobody has asked for is the flexibility §4's
YAGNI refuses. A real source wanting its disclosures spoken is a v2 finding with
a source behind it.

### ⭐ The `FND-04` fixture change — a one-line instruction, as asked

In `tests/fixtures/depth1/archive/depth-one/raw/prose/unit-03/lesson-2.json`:

1. **Block 5** (currently `{"type":"html", "text":"<details>\n<summary>This one
   IS raw HTML</summary>…"}`) becomes
   `{"type":"disclosure","summary":"This one IS raw HTML","open":false,
   "blocks":[{"type":"para","text":"…"}]}` — the `<p>` contents become a `para`.
2. ⛔ **Add a new `html` block** carrying markup that is *not* a disclosure, and
   ⚠️ **it must contain a `<p>` tag**, because `test_the_same_tags_appear_fenced_
   and_raw_in_one_corpus` intersects tags found in `code` blocks against tags
   found in `html` blocks, and block 4's fence supplies `<details>`, `<summary>`
   and `<p>`. Losing the intersection turns a green fence-awareness test red for
   the wrong reason. A `<div class="callout"><p>…</p></div>` does it.
3. `counts` gains `"disclosures"`; `html` stays at 1. Recompute
   `content_sha256` with the module's own `content_sha256`, not by hand.
4. In `tests/test_fixture_consistency.py`: add `disclosure` to `BLOCK_FIELDS`
   (`summary`, `open`, `blocks`) and to `COUNT_KEYS`; add it to `depth1`'s
   `REQUIRED_TYPES`.

⚠️ **Everything else in that fixture is untouched and was right.** The three
fenced XML/HTML blocks are the fence-awareness discriminator and they are the
highest-value thing in the set — do not disturb them.

---

## Q2 — the exercise declaration's home · **due before SF-23**

⭐ **An `exercise` object inside the practice archive document**,
`raw/<variant>/unit-NN/practice-M.json`, versioned by that document's existing
`raw_api`, written by the **adapter** (R2). Carried into spec §7 with the worked
example.

⛔ Not a sixth versioned contract, not the authored overlay, not the manifest.

- **No new document, no new version.** R9 enumerates the versioned contracts and
  each costs something forever. ⭐ A contract that rides a version it is already
  inside is strictly cheaper than one that adds a sixth — which is R9's own
  argument, applied to itself.
- **The adapter is the only thing that knows.** `run_command` is a fact about the
  source's build; `provenance` is a fact about where the grader came from. R2
  makes the archive the adapter's entire obligation, and this is archive content.
  ⛔ In the overlay a human would type it, which R19 forbids.
- ⭐ **§7's three states become structural, which is the test the PO set.**
  **none** — no `practice-M.json` exists. **ungraded** — the document exists with
  blocks and **no `exercise` key**. **graded** — the key is present. So ISO
  writes nothing at all for 38 units, SPARQL writes 19 prompts with no workspace,
  and neither declares its own emptiness. ⛔ **A contract that makes the empty
  case do work is a contract fitted to the one source shipping 168 graders**, and
  §11.0 says that source is the exception.
- **R5 gets one place to enforce.** `provenance` and `trust` sit on one document,
  so `validate` refuses `authoritative` + `generated` — one rule, one file,
  exit 1.

⛔ **`trust` is declared but never believed.** An adapter writes its claim; the
framework checks it against `provenance`. `EX-04` writes the same key for a
generated grader that cleared both gates, on the same document, and may only ever
write `advisory`.

---

## Q3 — `container.json`'s two owners · **due before SF-05**

⭐ **`hand-authorable` survives, narrowed to two fields.** The sentence is now in
SF-05:

> ⚠️ **"Hand-authorable" is about two fields, not about the document.** ⛔
> `container.json` is **generated** by the adapter on ingest (§6, `JS-05`) and
> amended only by `EX-04`'s declared practice counts; ⛔ the render pipeline
> never writes it, and neither does a person write it from nothing. What a person
> may amend are the **editorial** fields the generator round-trips rather than
> overwrites — a corrected `title`, a `note` — and a generator that would discard
> one **stops** (§6, R6).

**What legitimately hand-authors it, and why that is not a hole in a skill.**
⭐ Nothing hand-authors the *document*. A person **amends two fields of a
generated document**, and R19's target is precisely what a second source would
have to **retype**. A corrected title or an explanatory note is not retyping — it
is a judgement about one's own material, which is the one thing no skill can
produce. ⛔ Everything that *is* derivable — address, titles, variant, unit list —
is generated, and hand-writing any of it is a finding against the
adapter-authoring skill.

SF-05 gains an acceptance clause: **an edited `note` and `title` survive a
re-read unchanged**, because that round-trip is the entire content of the word.

---

## X1 — `corpus.json` gains `content` · **before SF-02 is assigned**

⭐ **Ruled in, and the timing was the PO's best call on this board.**
`corpus_api: 1` has never been consumed, so the field costs nothing today and
costs a migration R9 makes deliberately expensive tomorrow.

```json
"content": {
  "include": ["src/*.md"],
  "exclude": [ { "path": "src/ISO.md",
                 "why": "whole-series aggregate: a concatenation of 1.md…16.md (C2)" } ] }
```

- ⛔ **C2 is a schema problem, so the countermeasure is a schema field.** ISO
  ships per-unit files *and* aggregates of them; a `src/*.md` glob ingests every
  unit twice and nothing complains, and nothing in the manifest could say
  otherwise.
- ⭐ **The asymmetry is the design.** An inclusion needs no justification; an
  **exclusion is material withheld from the reader** and carries its `why` — the
  same argument `permitted_edits` already makes about an edit. A withholding
  nobody has to explain is one nobody audits.
- ⛔ **Silence is the failure C2 describes, so silence is what this removes.** A
  file under the source root matching neither list is **unclassified**, named,
  exit 1 (R6). ⚠️ It follows that a corpus cannot grow a file without somebody
  deciding what it is — which is the point: the alternative is a second aggregate
  appearing and being read as 38 more units.
- The reconnaissance skill drafts it, and detecting the overlap is exactly what
  C2 asks of it — two files whose digests say one contains the other is a
  reported finding, not something noticed after ingest.

---

## X2 — `assert_clean` and ISO's 96 card-shaped strings · **before SF-06/SF-08**

⭐ **The question dissolves rather than needing an exemption, and I checked the
gate before ruling: it has no card pattern and must not gain one.**

> **R7 governs identifiers that arrive from the environment the build runs in —
> not identifiers that are the material's subject matter.**

A home path, an account id, a name, an email, a bearer token: each reaches a
document because of *whose machine and whose account ran the build*. That is the
leak R7 exists to stop, and the rule's own history is a value taken from session
context. ⛔ **The gate is not a content classifier.** A 16-digit test PAN in an
ISO lesson came from the material, which its owner already wrote and published.

**Verified rather than assumed:** the inherited gate carries exactly three
patterns — a profile URL, an email address, a bearer token. None is a content
shape, and there is no card pattern and no home-path pattern to remove. ⭐ **So
ISO passes today, and the ruling is about what SF-08 must not *add*.** SF-08 is
already adding a home-path pattern, correctly — a home path is environmental.

⚠️ **The residual class is real, and the answer is specified but not built.** A
second source could legitimately carry a shape the gate *does* own. When it does,
the exemption is **manifest data read by the gate**, never a pattern hardcoded
for one corpus — a gate that names a corpus is the framework learning about a
source (R1). Three conditions so it cannot become an off switch:

1. ⛔ **A floor the manifest can never lift.** The declarable shapes are a closed
   list the framework publishes. Home paths, account identifiers and credentials
   are **never** declarable.
2. ⛔ **Scoped and reported, never globally silent.** Every string that passes
   only because of a declaration is counted and named in the build report — *fail
   loud* has a sibling, and it is **pass loud**.
3. ⭐ **The gate still refuses; it refuses less.** A declaration narrows the
   pattern set for one corpus. It never rewrites and never skips silently.

⛔ **v1 builds none of it** — the same move §5 makes for media extraction: build
the awareness, record the shape, let the mechanism plug in behind a decision
already taken. What SF-08 must not do is invent a *different* shape later under
deadline.

---

## Decisions

Things I decided that the questions did not ask.

1. ⭐ **R21 is a new ruling in the spec, and the ruling-range references in four
   documents now say R1–R21.** The PO asked whether the pattern generalises; the
   honest answer was that a note would not hold it, because the five open
   instances have no owner and no deadline until something says they must. This
   is the largest thing in the commit and it is the one I would most want
   overruled explicitly if it is unwelcome, rather than quietly ignored.
2. **I corrected §1's C3 and §4's ISO `levels` row in the spec.** Both were ruled
   in `CTO-2026-09-09-m0-readiness.md` and neither had been applied; C3 is quoted
   verbatim inside SF-07, which Q1 rewrites, so leaving it would have shipped a
   task whose own Definition contradicted its ruling. C3 is now a measured table.
   `v2-backlog.md`'s `V2-06` repeated the same wrong number and is corrected too.
3. **SF-07's vocabulary gained `video` in its list.** It was already a block type
   in the inherited archive and `FND-04` fixtures it, but SF-07's Definition
   omitted it — a task building to that list alone would have produced a reader
   that could not read a fixture that already exists.
4. **I did not add a `state` field to the exercise contract**, though it would
   have been the obvious way to make §7's three states explicit. Structure that
   cannot disagree with itself beats a field somebody has to set correctly.

---

## Surprises

- ⭐ **Q1 and Q2 were not two questions.** Surveying for the pattern the PO named
  turned up five more open instances in the spec, none of them noticed by anyone
  and each waiting for a task to invent an answer. The generalisation was worth
  more than the three answers, exactly as predicted.
- **X2 needed a recount, not a mechanism.** I had drafted the manifest exemption
  before checking whether the gate has a card pattern. It does not, and there was
  no problem to solve — only a mistake to prevent. ⚠️ A ruling that adds
  machinery for a failure nobody has is the thing §5 already warns about, and I
  nearly wrote one.
- **SF-07's task text already contained the opposite ruling to `FND-04`'s
  fixture,** in a merged document, describing `<details>` handling as settled.
  Q1 was not an open question so much as a live contradiction between two things
  already on the release branch.

---

## For dependents

**`SF-07`** — ⭐ **startable now.** `disclosure` is a container block; do not
flatten and do not store raw. Your ISO constraint is **fence-awareness**, not raw
HTML — recount before quoting any number, and note the three places CodeSignal
deliberately does the opposite (`quote`, `rule`, `disclosure`), all three
overruled on purpose.

**`SF-16` (E04)** — narration speaks the summary and stops. The body gets no
speech ids; the withheld count goes in the coverage report; ⛔ do not invent a
spoken announcement.

**`FND-04` follow-up** — the four-step fixture change above. ⚠️ Step 2's `<p>`
requirement is the one that will bite if skipped.

**`SF-23`** — the declaration's home is ruled and in §7. Build to the three
structural states; there is no `state` field and there must not be one.

**`SF-05`** — the sentence is in your task. You build the **reader** and the
round-trip guarantee, and no writer.

**`SF-02`** — `content` is a new manifest field with an acceptance clause. ⛔ Do
this before the schema is consumed; that is the whole reason it was routed to you
rather than to a later task.

**`SF-08`** — do not add a payment-card pattern. Your gate is for what the
*build environment* leaks, not for what the material is about.

**Everyone** — ⛔ **R21.** If the contract you need is described but not located,
**stop and ask**. Five are open and listed in §2's register; if yours is one of
them, that is a question for the CTO before you write the file, not a decision
for you while you write it.
