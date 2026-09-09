# E02 — Content pipeline

From raw material to the one document every consumer reads. This epic owns the
**archive** — the verbatim record of what a source said — and the **unit
document** generated from it.

**Shared context for this epic.** The archive is the project's memory. Pages,
narration, contents and exercises are all regenerable from it, so it must be
trustworthy in a way generated output need not: it is versioned, digest-covered,
and gated against personal data on the way in. CodeSignal learned this the
expensive way — its archive was Markdown with a hand-maintained
render/parse pair that was **lossy by construction** (bold vanished, images were
dropped, fences came back mislabelled), and it would have had to grow bold,
images and video and then be *proved* lossless again. Blocks are simply stored
now: one writer, one reader, no encode/decode pair to keep in step.

**The rule that governs SF-06 and SF-08 together:** the gate **refuses**, it
never rewrites. A match at the archive boundary means something upstream
failed, and silently cleaning it would corrupt the record of what the source
actually said *and* break its own digest.

**Rulings that bite here:** R6 (fail loud), R7 (personal data), R9 (versions),
R10 (reproducible), R11 (packages), R12 (tests).

---

### SF-06 — Archive document
**Milestone** M1 · **Depends on** SF-01 · **Team** pair
**Owns** `archive/document.py`, `archive/blocks.py`
**Context** ~45k — `CS/tools/study/rawdoc.py`, `CS/tools/study/blocks.py`

**Definition.** What an ingested unit *is* on disk (spec §6). Ports
CodeSignal's archive document, widening its `path`/`course`/`unit` keys into one
address and its language into a variant. Every property that makes it
trustworthy carries over, and each has a reason worth keeping:

- **Fixed key order, serialised unsorted**, so an unchanged document
  re-renders to identical bytes (R10).
- **`content_sha256` covers the blocks and nothing else.** It answers exactly
  one question — did the source edit this since we read it? Folding in the
  ingestion date would make every re-ingest differ regardless of content;
  folding in media would make re-downloading a 6 MB video look like a source
  edit. Either would make the one signal it exists for worthless.
- **An unknown `raw_api` is refused, never migrated in place** (R9).
- **Every string is gated on the way out, and the gate refuses** (R7).

Also owns the block-layout reader that distinguishes a lesson from a practice
and exposes a practice's parts — statement, embedded lesson, starting code —
without re-parsing anything.

⚠️ **Round-tripping a real document means handling its optional keys**, none
of which the summary above names: the asset manifest digest, recorded starting
code, the skipped-media marker, the video record's fields and the block counts.
They are written only when they have something to say and always after the
digest, so appending them cannot disturb it. Budget for them.

Attachments (spec §6, C4) are archived here too — files a unit references that
the page links rather than renders.

**Acceptance.** Round-trips a real CodeSignal archive document byte-for-byte
after field renaming, **including every optional key**. A document containing a personal-data-shaped string is
refused, not cleaned. Editing one block changes the digest; changing the
ingestion date does not. An unknown version raises.

---

### SF-07 — Block vocabulary and Markdown reader
**Milestone** M1 · **Depends on** — · **Team** solo
**Owns** `archive/markdown.py`
**Context** ~35k — `CS/tools/study/markdown.py`, `CS/tests/test_markdown.py`

**Definition.** The block vocabulary — `heading`, `para`, `code`, `list`,
`table`, `image`, `video`, plus **`rule`** (thematic break), **`quote`**
(blockquote), **`html`** (raw block-level HTML) and **`disclosure`** (a
`<details>`/`<summary>` withheld section) — and the strict reader that produces
it.

⚠️ **The additions are measured, not speculative — but recount before you quote
a number.** As of 2026-09-09: **10 of 166** Java lessons use `---` and **1** uses
a blockquote; **6 of 19** SPARQL lessons use `<details>`/`<summary>`; and ISO
carries raw HTML in **0 of 38** files, its 26 `<tag>`-shaped files being XML
*inside fenced blocks*. An earlier draft of this task said "18 ISO files contain
raw HTML" and that was a count of angle brackets (spec §1 C3, corrected).

⛔ **So the ISO constraint is fence-awareness, and it is the one that actually
bites.** A `<`-scanning parser passes every other fixture in the set and fails
here. `FND-04`'s `depth1` unit 3 `lesson-2` is built for exactly this: three
fenced blocks of XML and HTML beside a raw block using the same tags.

⛔ **`disclosure` is a container block, and this is a ruling — the two obvious
readings both fail** (CTO, `handoffs/CTO-2026-09-09-rulings-q1-q3.md`).

```json
{ "type": "disclosure", "summary": "Show the answer", "open": false,
  "blocks": [ { "type": "para", "text": "…" },
              { "type": "code", "lang": "sparql", "text": "…" } ] }
```

- ⛔ **Do not flatten it** — dropping the tags and keeping the summary as a
  paragraph is what CodeSignal's `markdown.py` does, and it is right for a DOM
  reader and wrong here: all six SPARQL uses hide an **exercise answer**, and
  flattening shows it outright.
- ⛔ **Do not store it as one raw `html` block** — that keeps the hiding and makes
  the body opaque. A fenced query inside the answer would not be a `code` block:
  uncounted, unhighlighted, invisible to SF-25's block-count gate.
- ⭐ **It is the same shape `quote` already has**, for the same reason FND-04
  ruled `quote` holds blocks rather than text: a withheld section can hold a
  list, a fence or a table, and a `text`-only container loses exactly what
  *never silently drop* exists to keep. Two container blocks, one shape, no new
  concept.
- ⭐ **The archive records the semantics; the renderer owns the markup.** The
  document says *this content is disclosed on demand and here is its label*;
  `<details><summary>` is SF-12's template decision (R13). `summary` is content
  and is gated, translated and counted like any other text. `open` is the
  author's default and is honoured, not overridden.
- **`html` survives for genuinely unstructured markup** — an unknown tag on its
  own line stays prose, because a lesson teaching HTML must keep it. Raw HTML is
  stored verbatim, rendered as-is, not parsed, and gated like any other string.
- ⚠️ `counts` gains one key per new type, so a disclosure is countable without
  being opened.

**This module already exists and is proven; port it with its governing rule
intact: *never silently drop a line*.** An unrecognised construct raises rather
than being swallowed; an unclosed fence raises rather than absorbing the rest
of the document as code. It is a line-oriented parser over exactly the
constructs real material emits — not a general Markdown engine — and emphasis,
inline code and links are left untouched inside `text`, because stripping them
is exactly the loss it exists to prevent.

This is the single most important dependency of the Java adapter (E07): it is
why ingestion there is wiring rather than parser work.

⭐ **Port from HEAD, not from the snapshot this project was planned against**
(spec §8). A dozen parser defects were fixed upstream after the freeze —
indented fences, lazy continuations, nested list items, borderless tables, `1)`
as an ordered marker, display maths as a block — and they are free if you port
current source, re-derived at full cost if you port the version quoted here.

⚠️ **Two places where CodeSignal deliberately does the opposite, and you are
diverging on purpose — record it rather than rediscover it.** Its `_quote`
returns the quote's *inner* blocks transparently and its parser emits **no
block at all** for a thematic break, both to agree with `lesson_html.BLOCK_TAGS`,
its DOM reader, for which `<blockquote>` and `<hr>` are not block tags. ⭐ A
repository-shaped source has no DOM reader to agree with, so studyforge makes
them block types. Its `disclosure` handling — tags dropped, `summary` kept as a
paragraph — is the same reasoning reaching the same wrong answer for us, and is
overruled above. A task told to "port `markdown.py` with its governing rule
intact" will find the current source doing three things differently and should
know all three are intended.

**Acceptance.** CodeSignal's existing Markdown tests pass unchanged. Parses all
166 Java sub-READMEs with zero errors — **or** names every file and construct
that fails, which becomes JS-03's input rather than a silent loss (R6). **And no
unit yields fewer blocks than the source's independently-counted structure
implies** — a raise is not the only way this parser can lose material, and SF-25
turns that count into a gate.

---

### SF-08 — Personal-data gate
**Milestone** M1 · **Depends on** — · **Team** solo
**Owns** `archive/scrub.py`
**Context** ~20k — `CS/tools/study/scrub.py`, `CS/tests/test_scrub.py`

**Definition.** R7's enforcement: `scrub` on the way in, `assert_clean` as the
refusing gate at every disk and wire boundary. Home paths, account
identifiers, names, email addresses.

⛔ **What belongs in the pattern set is ruled, because the obvious answer is
wrong** (CTO on X2, `handoffs/CTO-2026-09-09-rulings-q1-q3.md`).

⭐ **R7 governs identifiers that arrive from the environment the build runs in —
not identifiers that are the material's subject matter.** A home path, an account
id, a name, an email, a bearer token: every one of these reaches a document
because of *whose machine and whose account* ran the build. That is the leak R7
exists to stop, and it is why the rule's own history is about a value taken from
session context. ⛔ **The gate is not a content classifier**, and a pattern that
cannot have come from the build environment does not belong in it.

⚠️ **The case that forced this** (`X2`): ISO-8583 teaches card messaging and its
material carries **96 card-shaped digit strings** — a 16-digit test PAN is the
subject of the lesson. A gate that refuses rather than rewrites (R7) and matched
that shape would refuse the entire corpus, with no escape hatch and a diagnosis
that looks exactly like a leak. ⭐ **Under the ruling the question dissolves: the
framework ships no payment-card pattern**, because a PAN in an ISO lesson came
from the material, which its owner already wrote and published. Verified: the
inherited gate has exactly three patterns — a profile URL, an email address and a
bearer token — and none of them is a content shape. ⛔ **Do not add one.**

⚠️ **The residual class is real and the answer to it is specified, not built.**
A second source could legitimately carry a shape the gate *does* own — a lesson
about HTTP quoting a real support address, say. When that happens the exemption
is **manifest data read by the gate**, never a pattern hardcoded for one corpus,
because a gate that names a corpus is the framework learning about a source (R1).
Three conditions on any such field, so it cannot become an off switch:

1. ⛔ **A floor the manifest can never lift.** The declarable shapes are a closed
   list the framework publishes; a corpus cannot invent one. Home paths, account
   identifiers and credentials are **not** declarable at any time.
2. ⛔ **Scoped and reported, never globally silent.** Every string that passes
   only because of a declaration is counted and named in the build report — *fail
   loud* has a sibling, and it is *pass loud* (R6).
3. ⭐ **The gate still refuses; it refuses less.** A declaration narrows the
   pattern set for one corpus. It never rewrites, and it never skips silently.

⛔ **v1 builds none of it.** No source in scope needs it, and this is the same
move §5 makes for media extraction — build the awareness, record the shape, and
let the mechanism plug in behind a decision that has already been taken. What
this task must not do is invent a *different* shape later under deadline.

The belt-and-braces discipline is deliberate and must survive the port: scrub
first, then assert, **at more than one layer**. The inner gate is not
redundancy — a match there means an upstream stage failed, and that is
information worth surfacing rather than quietly absorbing.

⛔ **But both layers ride the same walker and read the same decoded strings.** A
gate that reads a *serialised* form is not a second check on the first — it is a
check on a different document, and it invents matches the escaping created.
CodeSignal scrubbed decoded strings and then gated the rendered JSON, where a
newline is the two characters `\` and `n`, so a Python decorator on its own line
serialised as `...\n@router.get(...)` — and `n@router.get` is email-shaped.
**Three clean lessons were refused.** ⚠️ Teaching the scrubber that shape would
be far worse: scrubbing a rendered payload rewrites the material's own source
into a placeholder.

⚠️ **A false positive is a failure of the same class as a leak.** The gate
refuses rather than rewrites (R7), so a shape it wrongly matches does not
degrade the output — it stops the corpus, and the diagnosis is expensive because
the refused string looks exactly like a leak. For an unknown second source, whose
material may legitimately contain anything, this is the more likely direction of
failure.

Build output is a live hazard: paths contain home directories, so every line a
process emits passes the gate before it reaches a stream (E05).

**Acceptance.** An absolute home path is refused at the archive boundary.
Build output containing one is scrubbed before it reaches a stream. No
generated file, log or report in the entire v1 output contains personal data —
asserted by a repository-wide check, not by inspection. **Real material
containing a construct that only resembles personal data after escaping is not
refused** — with the measured case as a fixture. **Every gate in the framework
reads the decoded strings, never a rendered form** — asserted. **A document
carrying 16-digit card-shaped strings passes** — asserted, because that is the
ISO corpus's subject matter and the gate is not a content classifier.

---

### SF-09 — Authored overlay and section keys
**Milestone** M1 · **Depends on** SF-06 · **Team** solo
**Owns** `unit/content.py`, `unit/sections.py`
**Context** ~25k — `CS/tools/study/content.py`

**Definition.** The optional human judgement layer beside a unit, and the
section-key vocabulary every downstream consumer keys off — `shared`,
`<variant>`, `practice-<variant>`.

**Keys derive from kind and variant, never from a heading.** A retitled section
must not renumber every speech id beneath it, because those ids name audio
files on disk; content-derived keys would make a copy-edit silently orphan a
unit's narration. An explicit key is the escape hatch, and must still be a legal
slug because a filename is minted from it.

Also owns the exercise provenance (`bundled` | `generated` | `user`) and trust
(`authoritative` | `advisory`) vocabulary that SF-23 consumes and R5 enforces.

**Acceptance.** A retitled section keeps its key and therefore its audio
filenames. A `generated` grader cannot be recorded as `authoritative`. Section
keys are unique within a unit for a multi-variant corpus.

---

### SF-10 — Unit document builder
**Milestone** M1 · **Depends on** SF-05, SF-06, SF-09 · **Team** team
**Owns** `unit/builder.py` and its package
**Context** ~70k — `CS/tools/study/unitdoc.py`, plus SF-05/06/09 outputs

**Subtasks.**
(a) **Derived shape** — no overlay: one section per archive file, lessons
before practices, so a unit is readable the day it is ingested. This is the
common case and the one that makes ingestion worth running before any judgement
is made.
(b) **Authored shape** — an overlay's `sections` array used **verbatim**, order
never re-derived, with only the workspace a practice needs and the video a
lesson has added by the builder, since neither is the author's to write.
(c) Address and media validation.
(d) The **no-material** outcome as a first-class result, not an empty document.

**Definition.** The one document every consumer reads: the page renders it, the
server serves it, the run route takes its commands from it. Generated, never
hand-edited, byte-for-byte reproducible.

**The archive is its only source of text.** Nothing may reach it from a
pre-scrub payload — a document built that way would display text the narration
does not speak, and put ungated strings in a file a browser opens.

Order is never re-derived because two consumers ordering differently would mint
different speech ids for the same unit and desynchronise the page from its
audio.

**Acceptance.** A unit with no overlay is readable. An authored overlay's
section order is preserved exactly. A unit with no archive yields the explicit
no-material outcome. Regenerating produces identical bytes. Both FND-04
fixtures build.
