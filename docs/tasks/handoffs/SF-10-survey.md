# SF-10 survey (W5) — porting `unitdoc.py` as a package

**Status:** survey only. `feat/SF-10-survey`, branched from
`release/m0-foundations` @ `ac4ed55`.

⛔ **No builder code, and none is proposed as text.** SF-10 is `Team`-sized and
both developers take it together; this is the serial half — W5 — done before the
team convenes rather than retrospectively.

**Base, pinned:** 2274 passed, 8 skipped, floor clean. ⚠️ This branch changes no
code, so the branch reading is the base reading.

**Read:** the module's contract surface — its 101-line docstring, its
signatures, its section banners, and the symbol graph. ⛔ **Its
CodeSignal-specific generation was not read** (that is E08 and works differently
for the Java corpus), and no second large module was opened.

⭐ **The graph answered the structure question before any file was opened**, from
the extraction source's own index — 41 symbol nodes for the module, with the
line-anchored rationale of every one.

---

## 1. Inventory — 827 lines, by responsibility

Spans are the author's own section banners and **sum to 827**.

| Lines | Span | Section | Symbols |
|---:|---|---|---|
| **201** | L1–201 | header | docstring (101), imports (17), 8 constants, `UnitDocError`, `NoMaterial` |
| **30** | L202–231 | gates | `gate` re-export, `render_unit`, `href` |
| **74** | L232–305 | reading the archive | `archive_files`, `read_capture` |
| **189** | L306–494 | derived sections | `_key`, `_workspace_for`, `_keyed_archive`, `_videos_by_key`, `_derived_sections`, `_authored_sections`, `_check_address_against_map` |
| **97** | L495–591 | the build | `build_unit` |
| **134** | L592–725 | `content.json` | `load_content`, `_check_addresses` |
| **102** | L726–827 | `unit.json` | `_check_video`, `load_unit_document`, `check_sources` |

Top-level definition spans sum to **703**; the remaining **124** are the banners
and the blank lines between them.

## 2. ⭐ The headline: about a third of it is already ported

⛔ **W5's premise is true of the file and not of the task.** `src/studyforge/unit/`
already holds three of `unitdoc.py`'s responsibilities, landed by SF-05, SF-06
and SF-09:

| `unitdoc.py` | lines | already in studyforge | lines |
|---|---:|---|---:|
| `load_content` + `_check_addresses` + overlay constants | ~145 | `unit/content.py` — `Overlay`, `Section`, `OVERLAY_KEYS`, `SECTION_FIELDS`, `DERIVED_FIELDS`, `CONTENT_API` | 300 |
| `_key` / `section_key_of` | 12 | `unit/sections.py` | 129 |
| `ContentError` | ~10 | `unit/errors.py` | 42 |
| `AUTHOR_MAY_NOT_WRITE` | 15 | `unit/content.py` → `DERIVED_FIELDS` | — |
| `_check_address_against_map` | 31 | ⚠️ `validate/structure.py` already cross-checks declared vs archived practice counts | — |

⭐ **So SF-10's remaining port is roughly 250 lines of CodeSignal code, not 827** —
`_keyed_archive`, `_videos_by_key`, `_derived_sections`, `_authored_sections`,
`build_unit`, plus the archive-reading and load-side halves.

## 3. It still wants to be a package, and here is the measured reason

⚠️ **Because this house writes ~2× the lines for the same responsibility.**
Measured, n=1: `load_content` + `_check_addresses` + their share of the header is
**~145 CodeSignal lines**; the same contract is **300 lines** in
`unit/content.py`. **≈2.1×.**

⛔ **At that ratio the remaining ~250 lines land at ~500–600 — over R11's 400.**
⚠️ **One data point.** `sections.py` is 129 lines from 12, which looks like 10×
but is not comparable: it added a variant vocabulary CodeSignal did not have. So
the ratio is *weakly grounded* and the conclusion does not rest on it alone —
the seams below are worth having at any size.

## 4. Proposed shape — `src/studyforge/unit/builder/`

⭐ **Each division below is a different question with a different consumer** —
FND-04's criterion, and the reason its split was cheap.

| Module | Question it answers | Consumer | From | Est. |
|---|---|---|---|---:|
| `builder/__init__.py` | the contract, `build`, `NoMaterial` | everyone | `NoMaterial` | ~80 |
| `builder/material.py` | *what did ingestion leave for this unit, and is each file still clean?* | the builder only | `archive_files`, `read_capture`, `_keyed_archive` | ~200 |
| `builder/derived.py` | *what does a unit nobody has curated look like?* | the builder only | `_derived_sections`, `_videos_by_key` | ~110 |
| `builder/authored.py` | *what does the author's order, plus the two fields that are not theirs, look like?* | the builder only | `_authored_sections` | ~150 |
| `builder/document.py` | *what is written, in what order, and out of which files?* | the format (R10) | `build_unit`, `DOCUMENT_KEYS`, `PRACTICES_KEYS`, `SOURCE_KEYS` | ~290 |

### ⛔ The seam that matters most: `derived` and `authored` are two modules

⚠️ **They have opposite rules about the same array.** The derived shape
**computes** order — lessons before practices. The authored shape **must never
re-derive it**: §5.4 fixes that array by construction, because two consumers
ordering differently mint different speech ids and desynchronise the page from
its audio.

⭐ **Split, the authored path cannot reach the ordering code by accident.** In
one module they are two branches of one function and the only thing keeping them
apart is that nobody has edited it carelessly yet. ⛔ **That is a seam, not a
slice at a convenient line number** — and it is the one whose failure is silent.

### ⭐ And one module that is *not* in the package

`load_unit_document`, `_check_video`, `check_sources` (**102 lines**) read a
built `unit.json` back and refuse a stale shape. ⛔ **Nothing about that is the
builder's** — its consumers are the page generator, the server and the run
route, none of which builds anything. Proposed as a **sibling**:
`unit/served.py`, beside `unit/content.py` — the authored document has a reader,
and so should the generated one.

⚠️ **Naming is a team decision, not mine.** `unit/document.py` is the tidier
symmetry with `archive/document.py` (ingested document / served document) and
the more confusable name. Stated rather than chosen.

### ⚠️ `builder/document.py` is the one that could cross 400

At ~290 it has the least headroom. ⭐ **So its next seam is named now, before
anybody needs it** (FND-04's lesson, applied one step earlier): `practices` is
asked by the page — *is there more to come?* — and `sources` is asked by
re-ingest detection — *did the source change under us?* Two questions, two
consumers, already two constants.

## 5. ⛔ What is CodeSignal-specific and does not port (R1)

| In `unitdoc.py` | Why it does not port | What studyforge has instead |
|---|---|---|
| `course-map.json`, `declared_practices`, `_check_address_against_map` | a CodeSignal course page's structure | the corpus manifest + `container.json`; `validate/structure.py` already cross-checks practice counts |
| `href`, `layout.py` paths (`study/paths/<path>/<course>/…`) | one site's tree | placement profiles — `tree`/`sibling`, `Profile.unit()`, `Profile.container()` |
| `parse_capture`, `blocks.py` | HTML capture from one site | `archive.markdown` |
| `scaffold.py` workspace derivation | E08, and it works differently for a Java corpus | the *record* is contracted by `studyforge.exercise` (SF-23); only the derivation is missing |
| `rawdoc.gate` re-export | ⚠️ see finding 53 | `archive.scrub`, placed upstream by Ruling 17 |
| `concept` / `members` | already dead in the source | never existed here |
| `source` = the codesignal.com URL a file was fetched from | the host does not port | ⚠️ see finding 54 |

## 6. ⚠️ What this survey cannot determine

⛔ **R6: reported, never smoothed over.** A survey that proposes a shape it is
not sure of, without saying so, costs the build.

1. **Does the served document get its own `unit_api`?** R9 versions contracts and
   `unitdoc.py` carries `UNIT_API = 3` with refuse-on-load. I found no
   equivalent in studyforge. **Settles it:** the team declares one, or says the
   served document is not a contract — it cannot be both.
2. **Does the loader belong to SF-10 or to SF-25?** `validate` already refuses
   malformed documents. **Settles it:** whether a consumer reading `unit.json`
   at serve time may assume `validate` has run. If it may, `served.py` is much
   smaller than 102 lines.
3. **Does the builder re-gate every archive file it reads?** `unitdoc.py` runs
   `assert_clean` on the way out of the disk *regardless*. ⚠️ Ruling 17 placed
   that boundary upstream and ruled `validate` does not scrub. **Settles it:** a
   ruling on whether "upstream" means *ingest only* or *every read*.
4. **Does `practices` port as two counts and no verdict?** `validate/structure.py`
   compares declared against archived and **does** deliver a verdict.
   **Settles it:** whether the served document repeats a number validation
   already checked, or points at it.
5. **The size estimates rest on one measured ratio.** They are the reason for a
   package, not the proof of one.

## 7. Findings

**52 — W5's number is right about the file and misleading about the task.**
`unitdoc.py` is 827 lines; the part SF-10 has left to port is ~250 of them,
because SF-05, SF-06 and SF-09 already landed the overlay reader, the section-key
vocabulary and the error type. ⭐ Worth carrying because the board's "827 vs 400"
framing invites budgeting for a port three times the real size.

**53 — a live divergence between `unitdoc.py` and Ruling 17.** The source module
re-gates every archive file on every read, *by design*, and says so in its
docstring. Ruling 17 put the gate upstream. ⛔ Both are defensible and they
cannot both be implemented. Named here rather than resolved: it is a ruling.

**54 — `source` means two different things in the two repositories.** In
studyforge an archive document's `source` is the corpus source id
(`"depth2-demo"`). In `unitdoc.py` a `sources` entry's `source` is **the URL the
file was fetched from**. ⚠️ Same word, two levels, two meanings — and SF-10 is
exactly where they meet, because it writes the `sources` array. **Settles it:**
name the second one something else in studyforge before it is written, not after
1,290 documents carry it.

**55 — the load-side validator is in the same file as the builder, and its
consumers are entirely different.** Not a defect in the source — that file
predates R11 — but it is the seam most likely to be ported by habit, because
"it was in unitdoc.py" is the only argument for keeping it there.
