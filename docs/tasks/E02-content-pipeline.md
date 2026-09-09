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
`table`, `image`, plus **`rule`** (thematic break), **`quote`** (blockquote) and
**`html`** (raw block-level HTML) — and the strict reader that produces it.

⚠️ **The last three are additions, and they are not speculative.** Counted in
real material: 10 Java lessons use `---` thematic breaks and one uses a
blockquote; **18 ISO files contain raw HTML**. A parser whose rule is *raise,
never drop* stops dead on all of them. Adding these now costs little; meeting
them during an ingest costs a stalled milestone. Raw HTML is stored verbatim
and rendered as-is — it is not parsed, and it is gated for personal data like
any other string.

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
⚠️ One of them discharges part of C3: `<details>`/`<summary>` is handled as a
**named shape, never a general HTML stripper** — the tags are markup and are
dropped, the summary text is content the reader clicks and is kept as a
paragraph, and an unknown tag on its own line stays prose, because a lesson
teaching HTML must keep it.

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
reads the decoded strings, never a rendered form** — asserted.

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
