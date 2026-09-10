# SF-12 survey (W9) — porting `html.py` as a package

**Document kind: `survey`.** ⛔ **Not a task handoff, and it does not owe the
six-section handoff contract** in `docs/conventions/agent-protocol.md` — it
produces no code and closes no task. It is the serial half of a `Team`-sized
port, written **before** the team convenes, on the precedent the CTO approved
for `SF-10` at `13b2857`: *only somebody who knows the module's internals can
answer where it divides.* ⚠️ Named here because `W25` is writing a check on this
directory and an undeclared document is what will trip it.

**Branch:** `feat/SF-12-survey`, off `release/m0-foundations` @ `e5bcc85`.

**Base, pinned:** **2490 passed, 8 skipped**, floor clean — a clean worktree of
`release/m0-foundations` @ `e5bcc85`, in the image.
**This branch, pinned:** **2490 passed, 8 skipped**, floor clean — **identical
to base**, which is the right answer for a docs-only branch.

Both measured with `docker/dev/check python3 -m pytest -q -rs` and
`docker/dev/check python3 -m tools.quality`. ⛔ **All 8 skips are named**
(§4b-i): five in `tests/docker/test_dev_image.py` — *"already inside the dev
image; building it again would recurse"* — and three in
`tests/test_knowledge_index.py` for siblings and a corpus index the image does
not mount.

⚠️ **An earlier draft of this document reported 2487 / 11 from an unpinned host
run.** See finding **68**: three tests the image runs did not run on the host,
and the skips were unnamed, so the *lower* number was the *worse* run and looked
like the same one.

**Read:** `html.py`'s contract surface — its 68-line docstring, its section
banners, every top-level span measured with `ast`, and the twelve template files
beside it. ⛔ **Its CodeSignal-specific generation was not read**, and neither
was `index.py` (SF-14) or `toc.py` (SF-13).

⭐ **The graph answered the SF-07 half before any source file was opened** —
`docs_tasks_handoffs_cto_2026_09_09_round9_ruling_commonmark_type6` and its
child `…_escape_tag_shaped_prose` gave the ruling, its rationale and its one
dependent edge for a few hundred tokens. ⚠️ **Node ids throughout, never labels.**
The graph indexes **studyforge**, not the extraction source; every number below
about `html.py` was measured directly, on the commit `workspace.json` pins
(`49c11d5e`).

---

## 0. ⛔ Two corrections before anything is budgeted

**The task's line citation is stale, and its claim is true.** `E03` says
*"`html.py:1112` is `PLAYER = """<footer id="player">`"*. Line 1112 is **blank**.
The literal is at **L1233–1253**. ⭐ The claim survives measurement and only its
address moved — 121 lines, by the two navigation commits since (`716eaa3c`,
`72ce2c30`). ⚠️ Recorded because *"verify it still says what the task claims"*
was the instruction, and half of it did not.

**The file is 1699 lines, not the ~1100 the citation implies.** ⛔ **But the
port surface is 898 of them**, and that is the number to budget — §2.

---

## 1. Inventory — 1699 lines, every one accounted for

Boundaries are each top-level definition together with the comment run
immediately above it, taken with `ast` rather than by eye, and they are
**contiguous**: the column sums to 1699 exactly.

| Lines | n | Section | Disposition |
|---|---:|---|---|
| 1–94 | **94** | module docstring (68) + imports | re-authored |
| 95–263 | **169** | constants, `UnitLink`, `UnitNav`, `Section` | **SF-12** |
| 264–319 | **56** | `escape`, `escape_attribute`, `safe_href`, `external_link` | **SF-12** |
| 320–416 | **97** | speech ids, audio digest, `audio_href` | ⚠️ SF-16 (M3) |
| 417–454 | **38** | `render_inline` — inline markers | **SF-12** |
| 455–649 | **195** | block renderers: code, list, table, image, video, heading | **SF-12** |
| 650–695 | **46** | outline entries + `_render_toc` | ⚠️ SF-13/SF-14 seam |
| 696–765 | **70** | catalog tree + rail | SF-14 |
| 766–816 | **51** | prev/next/up bar | **SF-12** |
| 817–953 | **137** | the workspace: panel, editors, Run and Submit | ⚠️ M5 |
| 954–998 | **45** | the section wrapper | **SF-12** |
| 999–1110 | **112** | language pills | ⚠️ open, §5.4 |
| 1111–1231 | **121** | asset composition — `STYLE`, `SCRIPT`, sprite | ✅ **landed, SF-11** |
| 1232–1253 | **22** | the `PLAYER` literal | **SF-12 → template** |
| 1254–1347 | **94** | asset names, head and tail, nav root | **SF-12** |
| 1348–1431 | **84** | the back-link to the original site | ⛔ R1 — does not port |
| 1432–1471 | **40** | the mark-as-read control | SF-30 (M5) |
| 1472–1518 | **47** | practices still to come | **SF-12** |
| 1519–1699 | **181** | the composer: `render_unit_page`, `render_unit_html` | **SF-12** |
| | **1699** | | |

### ⭐ The headline: SF-12's own port surface is **898 lines**, not 1699

| Disposition | Lines |
|---|---:|
| ⭐ **SF-12** (incl. the 22 that become a template) | **898** |
| M5 execution track — the workspace | 137 |
| ✅ already landed by SF-11 | 121 |
| open, may not port at all — language pills | 112 |
| SF-16 at M3 — speech ids and audio paths | 97 |
| re-authored, not ported — docstring and imports | 94 |
| ⛔ R1 — does not port | 84 |
| SF-14 — the catalog tree and rail | 70 |
| SF-13/SF-14 seam — the outline | 46 |
| SF-30 at M5 — the read control | 40 |
| **Total** | **1699** |

⚠️ **Roughly 47% of the file is somebody else's or nobody's.** ⛔ The 177 lines
of workspace-plus-read-control sit inside `SF-12`'s stated `~110k` context
budget and inside two *other* tasks' definitions — see finding **64**.

### The templates already on disk — 12 files, and one is not SF-12's

Measured in bytes, because `wc -l` reports **0** for the inline ones and that is
the point: a template emitted on one line is *authored* on one line.

| File | bytes | newlines | Asked for by |
|---|---:|---:|---|
| `code.html` | 222 | 0 | `_render_code` |
| `image.html` | 108 | 0 | `_render_image` |
| `inline-video.html` | 117 | 0 | `_render_inline_video` |
| `inline-video-link.html` | 232 | 0 | `_render_inline_video` |
| `practice-panel.html` | 650 | 0 | ⚠️ `_render_workspace` — M5 |
| `lesson-credit.html` | 137 | 1 | ⛔ R1 — does not port |
| `nav-tree.html` | 417 | 1 | ⚠️ `render_nav_tree` — SF-14 |
| `read-control.html` | 204 | 1 | SF-30 |
| `video.html` | 111 | 1 | `_render_video` |
| `section.html` | 125 | 3 | `_render_section` |
| `pending-practices.html` | 229 | 4 | `render_pending_practices` |
| `page.html` | 448 | 17 | the composer |

⭐ **Nine of the twelve are SF-12's; three are not.** Plus `player.html`, which
does not exist yet — §3.

### The tests — 2758 lines, 198 tests, and 911 lines are not SF-12's

`test_html.py` is **2758 lines**. ⛔ **R11 caps a test module at 600**, so it is a
package before the port ratio is applied at all. `test_templates.py` is a further
**101 lines / 9 tests**, and ports nearly intact.

| Lines | Tests | Section | For |
|---:|---:|---|---|
| 428 | 15 | the player, under a fake DOM | ⚠️ SF-18 (M3) |
| 483 | 14 | the run script, under a fake DOM | ⚠️ M5 |
| 305 | 22 | the practice panel | ⚠️ M5 |
| 262 | 18 | the lesson's own media | SF-12 |
| 106 | 9 | the left rail | SF-14 |
| 101 | 9 | the reference back to CodeSignal | ⛔ R1 |
| 1073 | 111 | escaping, inline, emphasis, ids, structure, sections, merged units, anchors and outline, reproducibility, assets, pending practices, inline video, read control, "nothing added here is spoken" | mixed, mostly SF-12 |
| **2758** | **198** | | |

⭐ **The two fake-DOM harnesses are 911 lines and 29 tests, and neither is
SF-12's.** They are browser-script tests for a player SF-18 owns and a run
script that does not exist before M5. ⚠️ Worth carrying because they are 33% of
the test file and the obvious thing to port by habit.

---

## 2. It is a package, and here is the measured reason

⚠️ **Because this house writes more lines for the same responsibility.** Four
data points now, where SF-10's survey had one:

| Contract | source | studyforge | ratio |
|---|---:|---:|---:|
| overlay reader (SF-05/06/09) | ~145 | 300 | ≈2.1× |
| Markdown reader (SF-07) — `markdown.py` + `blocks.py` | 858 | 1229 | **≈1.43×** |
| page assets (SF-11) — `pageassets.py` | 89 | 538 | ≈6.0× |
| page assets, less the two contracts CS never had | 89 | 382 | ≈4.3× |

⭐ **The honest range is 1.4×–2.1×, and SF-07 is the right analogue** — it is a
walk over the same eleven-name block vocabulary, mostly mechanical, and it came
in at **1.43×**. The SF-11 figure is not comparable: `surface.py` and
`vendored.py` are contracts the source did not have, not the same code written
longer.

⛔ **At 1.4×–2.1×, 898 lines land at ~1260–1890** — three to five times R11's
400 ceiling. ⭐ **The conclusion does not rest on the ratio**: at 898 source
lines the file is already 2.2× the ceiling before a single line is rewritten.
The ratio only decides whether the package has six modules or nine.

---

## 3. ⛔ The live R13 work, measured

**R13 forbids markup, CSS or JS in Python strings; the source does not satisfy
it.** Swept with `ast` rather than `grep`, so implicit concatenation is not
mistaken for a template and vice versa.

**Every non-docstring string literal in `html.py`:**

- **72 literals contain a markup tag**, occupying **101 source lines**.
- **20 literals contain a newline in their *value*** — i.e. produce more than
  one output line.
- ⭐ **Exactly one of those 20 is a template rather than a joiner: `PLAYER`,
  L1233–1253, 21 source lines and 20 output lines.** Every other newline-bearing
  literal is `"\n"`, `"</p>\n"`, `"\n<script src="` or similar — a separator, not
  markup with structure.

⭐ **So R13's live work in this module is exactly one file: `render/templates/player.html`.**
That is a *smaller* finding than E03 implies, and it is the finding, because the
alternative reading — *"72 literals carry markup, extract them all"* — would
break E03's own rule that **loop bodies, inline wrappers and one-line containers
stay in code**. The remaining 71 are one-line fragments; a template file for
`'<div class="langs" role="group">'` removes no duplication and adds a hop.

⚠️ **Three near-misses, deliberately left in code, and the reason is one rule.**
L762–764 (`<nav class="toc">`), L893–899 (the editor tab strip) and L1329–1330
(the two `<script src>` tags) each span several *source* lines but produce **one
output line each** — they are implicit concatenation, not multi-line markup. ⛔
**Extracting them would be a byte-for-byte regression under R10**, because
`template()` does not join lines and the committed pages have no newline there.
`test_templates.py::test_an_inline_template_stays_on_one_line` already pins this
for four files and the port must keep it.

⛔ **The literal must become a template *during* the port, not survive it.**
`player.html` is multi-line — its newlines are real output — so it is authored
across lines like `page.html`, and it is the one new template file the port adds.

---

## 4. Proposed shape — `src/studyforge/render/page/`

⭐ **Each division is a different question with a different consumer** — FND-04's
criterion, and the one SF-10's split was approved on.

| Module | Question it answers | Consumer | From | Est. |
|---|---|---|---|---:|
| `page/__init__.py` | the contract: `render(document, placement) -> bytes`, `PageError` | everyone | part of N | ~90 |
| `page/text.py` | *how does a string become safe page text?* | ⭐ every block renderer | 264–319, 417–454 (94) | ~180 |
| `page/blocks/__init__.py` | *which renderer answers for this block type?* | the section renderer | part of C | ~90 |
| `page/blocks/prose.py` | heading, para, list, table, quote — **escaped** | the dispatcher | C | ~150 |
| `page/blocks/figure.py` | *what does the reader look at rather than read?* — code, image, video | the dispatcher | C | ~200 |
| `page/blocks/verbatim.py` | ⛔ *which block types bypass escaping?* — `html`, and nothing else | the dispatcher | C | ~70 |
| `page/section.py` | *what wraps one section, and what does its pill say?* | the composer | F (45) | ~100 |
| `page/navigation.py` | *where does this page point — back, forward, up?* | the composer | D3 (51) | ~110 |
| `page/assets.py` | *where does this page reach, relative to itself?* (R8) | the composer, SF-18 | J (94) | ~170 |
| `page/document.py` | *what is written, in what order, out of which templates?* | ⭐ the format (R10) | N (181) | ~260 |
| `render/templates/` | the markup | — | 9 files ported + `player.html` | 10 files |

Estimate: **~1420 lines**, inside the 1260–1890 the ratio predicts. ⚠️ **Ten
modules for one renderer is a lot**, and the split is argued on the seam below
rather than on that total.

### ⛔ The seam whose failure is silent: `verbatim.py` is its own module

⚠️ **Two block types are byte-identical in shape and have opposite rules about
the same field.**

Measured, in `src/studyforge/archive/markdown/leaf.py`:

- `read_paragraph` returns `{"type": "para", "text": …}`
- `read_html` returns `{"type": "html", "text": …}`

⛔ **Same field name, same Python type, same possible content.** The text of a
tag-shaped `para` — `<blink>hello</blink>` — is byte-identical to the text of an
`html` block carrying the same tag. ⭐ **Nothing but the declared `type`
separates them**, and `surface.py` gives both the same answer (`None` — no
class), so the class name cannot be used to tell them apart either.

⭐ **`html` is the only block type in the whole vocabulary whose text reaches the
page unescaped.** Eleven block types; one bypass.

⛔ **The failure is silent in both directions, and neither raises anything:**

- **Escape too little.** A `para` emitted raw is consumed by the browser as
  markup. The page renders, is well-formed, links correctly, carries every other
  word, and **the sentence is gone**. The archive is unchanged. `validate`
  passes. Nothing logs.
- **Escape too much.** An `html` block escaped shows a lesson's own markup as
  literal text — visible, wrong, and equally silent.

⭐ **The specific way this arrives is by deciding escaping from the text rather
than from the declared type** — `if text.lstrip().startswith("<")` in a generic
`_render_block`, written by somebody reasonably trying to be helpful. ⛔ **That
is exactly the promise SF-07 made and declined type 7 to keep**, and SF-12 is the
only enforcer of it.

⭐ **Split, "which block types bypass escaping" is answered by `ls`, not by
reading branches.** Adding a second raw type becomes a new import into one named
module — a reviewable event in a diff. Adding a second raw *branch* inside a
195-line dispatcher is not. ⛔ **That is a seam, not a slice at a convenient line
number**, and it is the one whose failure nothing else in the pipeline catches.

⚠️ **It is not free.** `verbatim.py` at ~70 lines is the smallest module in the
package and will look like over-engineering to a reviewer who has not read this
section. ⭐ That is the argument for writing the section, not for merging the
module.

### ⚠️ `page/document.py` is the one with the least headroom

At ~260 estimated it is the largest, and it is the one the composer grows into:
every new page region (the player at M3, the read control at M5, a container
page at SF-15) adds a slot to it.

⭐ **So its next seam is named now, before anybody needs it** — FND-04's lesson,
applied one step earlier. The split is between **the skeleton** — which regions
exist, in what order, and the one `page.html` substitution that fills them —
and **the regions themselves**, each of which is *optional and gated on
something*: the player on whether narration exists, the read control on SF-30,
pending practices on §7's three states. Two questions: *what is the shape of a
page?* and *is this region present on this one?* When `document.py` crosses 400,
it divides into `document.py` and `regions.py` along that line, and not
elsewhere.

### ⭐ And one thing that is *not* in the package

The template loader — `TEMPLATE_DIR`, `template()`, `template_names()` — is
**35 lines living in `pageassets.py`** in the source, and SF-11 **did not port
it**: measured, `render/pageassets/` has no template function and
`render/templates/` does not exist.

⛔ It belongs beside its sibling, not inside `page/`. `pageassets` already
serves both halves of R13 in the source and its own test asserts they are not
confused (`test_templates_are_not_confused_with_the_asset_parts`). Proposed:
**`render/pageassets/templates.py`**, ~110 lines, published from
`render.pageassets` alongside `stylesheet()` and `script()`.

⚠️ **This crosses SF-11's `Owns`.** SF-11 owns `render/pageassets.py`; SF-12 owns
`render/page/` and `render/templates/`. ⛔ **Neither owns the loader**, and E03
lists it as SF-12 subtask (a). Stated rather than chosen — see finding **65**.

---

## 5. ⚠️ Open questions — what this survey cannot determine

⛔ **R6: reported, never smoothed over.** Each carries what would settle it.

### 5.1 ⛔ How a test pins the tag-shaped-`para` promise

**This is the one SF-12's Acceptance names, and it is the seam above.** Three
tests, and the third is the one that matters.

1. `test_a_para_whose_text_is_tag_shaped_renders_as_visible_text` — feed
   `<blink>hello</blink>` through **`markdown.parse`**, render, assert
   `&lt;blink&gt;` is in the page and `<blink>` is not.
   ⛔ **Through `parse`, never a hand-built block dict.** The promise spans two
   tasks; a test that builds `{"type": "para", …}` by hand asserts SF-12 against
   SF-12's own belief about what SF-07 emits, and the belief is the thing that
   can be wrong. ⚠️ The tag must be off CommonMark's type-6 list — `blink`,
   `marquee` — or SF-07 correctly returns an `html` block and the test proves
   nothing.
2. `test_an_html_block_reaches_the_page_verbatim` — the converse, so that a fix
   to (1) which escapes everything is caught by (2) rather than by a reader.
3. ⭐ `test_exactly_one_block_type_is_emitted_without_escaping` — derived from
   `BLOCK_TYPES`, asserting the set of types `verbatim.py` answers for is exactly
   `{"html"}`. ⛔ **Tests 1 and 2 are pinned to two fixture strings and a twelfth
   block type would pass both** while quietly acquiring a raw path. Test 3 is the
   one that survives the vocabulary changing, and it is the same shape
   `surface.py` already uses to make a new block type a loud failure.

**Settles it:** nothing — this is an answer, offered so the team does not
re-derive it. ⚠️ **What is *not* settled** is whether test 1 belongs to SF-12 or
to a shared cross-task test, given it exercises SF-07 and SF-12 together.

### 5.2 ⛔ Does the rendered page get its own `api`? — **R21, and it is not the question it looks like**

⛔ **R21: a task that meets an unlocated contract stops and asks. Routing this to
the CTO.**

**Measured.** There is no `PAGE_API` and no `SURFACE_API`. The five that exist
are `CONTENT_API`, `IDENTITY_API`, `CONTAINER_API`, `CORPUS_API`, `RAW_API`.

⭐ **But the page is not unversioned.** `corpus/placement/identity.py` carries
`IDENTITY_API = 1`, and `identity_api` is the **first key** of the identity block
SF-12 embeds in every page.

⭐ **So the real question is: which contract is `identity_api` versioning?** It
versions the JSON object SF-04's scan parses. ⛔ **It does not version the markup
contract**, and the markup contract has out-of-process consumers today:

| Not versioned by anything | Written by | Read by |
|---|---|---|
| the class names in `SURFACE_CLASSES` / `SURFACE_HOOKS` | SF-12's templates | `render/assets/*.css`, `render/assets/copy-code.js` |
| `data-speech-id`, `data-audio` | SF-12 | ⚠️ SF-18's player, at M3 |
| the DOM id derivation (`element_id`, `section_id`) | SF-12 | in-page anchors, and the narration highlight at M3 |

⚠️ **`surface.py`'s own docstring says the failure it exists to prevent is
silent** — *"a stylesheet and a template that disagree about a class name produce
a page that renders, carries every word, and is unstyled, with no error
anywhere."* ⛔ **A contract whose disagreement is silent is precisely the one R9
versions**, and this one is half-written and unversioned.

**The ask, in R21's three-part form, for the CTO to rule rather than for SF-12 to
choose:**

- **File** — `render/pageassets/surface.py`, which already holds half of it.
- **Key** — proposed **`surface_api`**, not `page_api`. ⭐ The page's *bytes* are
  not a contract (R10 pins them by golden file, which is a different mechanism);
  its *hooks* are.
- **Producer** — ⚠️ **this is the part that is genuinely unclear.** SF-11 owns
  the file. SF-12 is the first writer of markup that honours it. SF-18 is the
  second reader. R21 wants *one* producer named.

⭐ **Ruling W9 already puts this on the right desk at the right moment:** *"SF-12
reviews the names in one commit as its first act."* ⛔ **That commit is the
natural home for the answer, which is why the ruling is owed before SF-12 starts
and not during it** — a version key minted in the same commit that renames the
classes is one decision; minted afterwards it is a migration.

### 5.3 ⚠️ SF-12 lands at M1 and the ids it must not invent land at M3

**Measured.** `E04` line 54: `SF-16 — Speakable contract`, **M3**, owns
`narrate/speakable.py`, `Depends on SF-10`. `SF-12` is **M1**.

⛔ **`html.py`'s own docstring states the invariant: *"Ids come from
`speakable.py`, never from here (17.1) … two numbering schemes that agree today
are exactly the coupling that breaks silently tomorrow."*** ⚠️ **At M1 there is
no `speakable.py` to take them from.** SF-12 either mints `data-speech-id` and
`data-audio` itself — creating at M1 exactly the coupling the source warns about,
to be discovered at M3 — or emits neither.

⚠️ **Emitting neither is not free either:** the M1 golden pages then change shape
at M3 when SF-18 adds the attributes, and R10 compares byte-for-byte, so **every
committed golden file churns**. ⭐ That may be entirely acceptable — a reading
floor that gains narration is a real change — but it should be a decision, not a
surprise at M3.

**Settles it:** a ruling on whether the reading floor's golden pages may change
shape at M3; or, if not, landing SF-16's id derivation early as a small contract
module the way `identity.py` landed ahead of SF-04, and for the same stated
reason — *"a definition arriving after its first writer is a definition two tasks
each guess at differently."*

### 5.4 ⚠️ One page per variant, or one page for all of them? — 112 lines turn on it

**Measured, and the two landed modules do not agree.**

- `unit/sections.py`: a unit document holds sections keyed `shared`,
  `<variant>`, `practice-<variant>` — **several variants in one document**.
- `corpus/placement/identity.py`: `Identity.variant` is a single **required**
  slug (`require_slug(self.variant, "identity 'variant'")`), and `variant` is
  singular in `IDENTITY_KEYS` — **one variant per page**.

⛔ **Both are true today and they cannot both be true of a rendered page.** If a
page is one variant, the 112-line language-pill row does not port at all and the
composer reads one variant's sections out of a multi-variant document. If a page
is all variants, `Identity.variant` cannot be a single slug and `identity.py`
needs a change — ⚠️ **a change to a contract that is already versioned at
`IDENTITY_API = 1` and already has a second consumer written (SF-04, M2)**.

**Settles it:** a ruling on whether two variants of one unit are one page or two.
⭐ **It is cheap now and expensive at M2**, and it is the difference between an
898-line port and a 1010-line one — the 112 pill lines are held out of the 898
in §1 precisely because this is unresolved.

### 5.5 The outline is a fifth of a task and has no owner

`_toc_entries` + `_render_toc` (**46 lines**) build the *page's own* outline from
its own sections. ⚠️ SF-13 owns contents **as data** and SF-14 owns the root
index; the rail (70 lines) is SF-14's. ⛔ **The in-page outline is neither** — it
is derived from one unit document, not from `toc.json`.

**Settles it:** whether the unit page's outline is SF-12's (it reads only the
document it is rendering, so E03's layering says yes) or SF-13's (it is
"contents", so the name says no). ⭐ The layering argument looks decisive and it
is stated rather than acted on, because `E03`'s task table assigns it to neither.

---

## 6. ⛔ What is CodeSignal-specific and does not port (R1)

| In `html.py` | Why it does not port | What studyforge has instead |
|---|---|---|
| `lesson_links`, `render_lesson_credit`, `LESSON_LINK_TITLE`, `PRACTICES_ELSEWHERE`, `lesson-credit.html` (84 lines) | a back-link to one specific site, with that site's name in the title text | ⚠️ **nothing** — attribution is corpus data if it exists at all. `tools/quality/source_names.py` makes the name in `src/` a build failure |
| `RUN_ENDPOINT = "/api/v1/run"`, the editor tab strip, Run and Submit (137 lines) | the execution track, and it starts at M5 | `studyforge.execute` (skeleton), E08 |
| `PRACTICE_NOTE`, `STARTER_CAPTION` | one site's wording | corpus manifest strings |
| `LANGUAGE_NAMES`, `pill_entries`, `UNCAPTURED_PILL` (112 lines) | merged multi-language units | ⚠️ variants — **see §5.4** |
| `_unit_number` — `"unit-03" -> 3` for the run endpoint | R4: never infer identity from a path | the identity block carries `unit` as an integer |
| `parse_capture` / payload-block prototype input | HTML capture from one site | `archive.markdown` |
| `render_unit_html` — the single-section convenience wrapper (31 lines) | ⚠️ exists because the source's fixtures are single-section | ⭐ FND-04's two fixtures are real documents; a second entry point that only tests use is a second contract |

---

## 7. Findings

**63 — the R13 debt in this module is one file, not seventy-two.** `[structural]`
⛔ E03's wording — *"triple-quoted markup, in this exact module"* — is true of
exactly one literal, `PLAYER`. 72 string literals in `html.py` contain a markup
tag, but **only one has a newline in its value**; the other 71 are one-line
fragments that E03's own rule keeps in code, and extracting them would be a
byte-for-byte regression under R10 because `template()` does not join lines.
⭐ Worth carrying because *"R13 is not satisfied in the source"* invites a sweep
that would break the rule it is trying to serve.
**Measured** — `python3 -c` over `ast.parse` of `tools/study/html.py` at
`49c11d5e`, counting non-docstring `ast.Constant` string nodes:
`string literals containing markup tags: 72 | source lines they occupy: 101`;
`literals whose VALUE spans multiple OUTPUT lines: 20`, of which one
(`PLAYER`, L1233–1253) is markup and nineteen are separators. 2026-09-10.

**64 — SF-12's context budget names 177 lines that belong to two other tasks.**
`[structural]`
⛔ `_render_workspace` + `_unit_number` (137 lines) is the Run/Submit surface,
which `CLAUDE.md` puts on the **execution track at M5**; `render_read_control`
(40 lines) is **SF-30**'s, by E03's own epic preamble. Both are inside
`CS/tools/study/html.py`, which is the whole of SF-12's stated `~110k` context.
⚠️ `practice-panel.html` — the largest template on disk at 650 bytes — is the
workspace's, not SF-12's. ⭐ The test file makes it worse: **911 lines and 29
tests** are fake-DOM harnesses for the player (SF-18, M3) and the run script
(M5). ⛔ A port that follows the file rather than the task ships the execution
track at M1.
**Measured** — contiguous `ast` spans of `tools/study/html.py`: `817-953 = 137`,
`1432-1471 = 40`; banner spans of `tests/test_html.py`: `879-1306 = 428` (15
tests), `1718-2200 = 483` (14 tests). 2026-09-10.

**65 — the template loader is owned by nobody, and it is SF-12's subtask (a).**
`[local]`
SF-11 ported `pageassets.py`'s asset half and not its template half:
`render/pageassets/` has no `template()` and `render/templates/` does not exist.
E03 gives SF-12 subtask (a) *"template loading and strict substitution"* but
gives it `Owns render/page/`, `render/templates/` — **not**
`render/pageassets.py`, where the function's sibling lives and where the source
kept it. ⛔ SF-12 either writes 35 lines into a file it does not own, or puts the
loader somewhere the source deliberately did not. ⭐ Cheap to settle and
invisible until the diff.
**Measured** — `grep -rni 'template' src/studyforge/render/` returns only
docstring prose and CSS token names, no loader; `find src/studyforge/render -type d`
lists `assets`, `pageassets` and no `templates`. Source: `tools/study/pageassets.py`
L61–89. 2026-09-10.

**66 — `test_templates.py`'s orphan check names a second source that asks for
nothing.** `[local]`
Its `SOURCES = ("tools/study/html.py", "tools/study/index.py")`, and
`index.py` requests **zero** templates today. ⚠️ Not a defect — it is correct and
forward-looking — but the port must keep the *list* rather than the *current
answer*, because SF-14 is the task that makes the second entry true, and a check
narrowed to one renderer at SF-12 is a check that silently stops covering the
index at SF-14. ⭐ The same shape as W7: the catch is right, the case never
arrives.
**Measured** — `grep -on 'pageassets\.template("[^"]*")' tools/study/index.py`
returns nothing; the same command against `html.py` returns 12 call sites.
2026-09-10.

**67 — `html.py` is 1699 lines and E03's citation implies ~1100.** `[local]`
⛔ Line 1112 is **blank**; `PLAYER` is at L1233. The citation drifted 121 lines
across two navigation commits (`716eaa3c`, `72ce2c30`) after E03 was written.
⭐ The *claim* survived measurement and only its address moved — which is the
argument for R11's *"a task counts its own port surface at start rather than
inheriting a number"*, applied to line numbers as well as totals. ⚠️ Filed local
rather than structural because the fix is a re-measurement at task start, which
is already the rule.
**Measured** — `wc -l tools/study/html.py` → `1699`;
`sed -n '1112p'` → empty; `grep -n 'PLAYER' ` → `1233:PLAYER = """<footer id="player">`.
`workspace.json` pins `49c11d5e`, and `git status --short` in that checkout is
clean. 2026-09-10.

**68 — an unpinned run that silently skips is indistinguishable from one that
passed, and the author is the last person able to tell.** `[structural]`
⛔ **This document reported its own base wrongly, and nothing in the number said
so.** The host run printed `2487 passed, 11 skipped` with **no skip reasons**;
the image runs the same tree at `2490 passed, 8 skipped`. ⚠️ **Three tests did
not run at all**, and the failure mode is that the *host* number is lower in
passes and higher in skips — so it does not look like a truncated run, it looks
like a slightly different one. ⭐ Ruling 40 already says unpinned green is
evidence for the test suite proper and never the verdict, and §4b-i already says
every skip is named or the run did not happen. ⛔ **Both rules were written for
the reviewer and both would have caught this at the author**, one round earlier
and for free — which is §4b-i's own argument arriving one step upstream of where
it is currently aimed. ⭐ Cheap remedy, and it is a habit rather than a check:
`-rs` on every run, so an unnamed skip cannot be reported as a base.
**Measured** — same worktree, same commit, minutes apart:
`python3 -m pytest -q` on the host → `2487 passed, 11 skipped`;
`docker/dev/check python3 -m pytest -q -rs` → `2490 passed, 8 skipped`, all 8
named. Base, in a clean worktree of `release/m0-foundations` @ `e5bcc85` in the
image → `2490 passed, 8 skipped`, floor clean. 2026-09-10.

---

⚠️ **One correction with no action attached, recorded because it was reported
verbally and would otherwise not be written down anywhere.** This survey's
author attributed the extra host skips to this worktree having no
`graphify-out/`. ⛔ **That was wrong**: a detached worktree of the base measures
2490 / 8 in the container too, so the missing index was not the cause. ⭐ The
FND-07 behaviour itself is real and unchanged — an absent index reports a notice
and exits 0, which is why this docs-only branch leaves the floor clean here and
will red it only in a checkout that *has* an index. Only the number attributed
to it was wrong, and finding **68** is where that number came from.
