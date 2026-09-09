# E03 — Rendering

The reader's surface: the unit page, the root index, the contents behind both,
and the navigation between them.

**Shared context for this epic.** The governing constraint is R8 — **the site
works over `file://` with no network and no server.** Every choice here answers
to it: assets are local and linked relatively, content the index needs is baked
in at generation time (a sibling JSON cannot be loaded over `file://` at all),
and anything requiring a server is progressive enhancement gated on protocol,
never a dependency.

⛔ **Say it as a prohibition, because the spec's own wording was a trap.**
Acceptance item 3 used to read *"from `toc.json` alone"*, which invites
`fetch('toc.json')` — code that passes every served test and then dies silently
over `file://`, showing an empty index and no error. ⛔ **A renderer fetches
nothing at runtime.** The two contents documents are its *build-time* inputs;
whatever a page needs at runtime is delivered into it at generation time.

⭐ **The reader's own state is part of this surface too** — SF-30 owns the
mark-as-read control and the browser-side store, for the same reason everything
else here exists: the floor is a double-clicked file.

The second constraint is R10 — pages are compared **byte-for-byte**, which is
what makes reproducibility enforceable rather than aspirational. It is also
why R13's template rules are strict: a template is used exactly, minus one
trailing newline, with no reflow and no re-indentation.

**The layering.** Contents (SF-13) is *data*; the index (SF-14) and the page
(SF-12) are renderers over it. If a renderer needs something the data does not
carry, the data is wrong — not the renderer. SF-14 reads **only** the two
contents documents, and that isolation is asserted rather than trusted,
because it is the proof that the contract carries everything a future client
would need.

**Rulings that bite here:** R8 (`file://`), R10 (byte-for-byte), R11
(packages), R13 (templates and assets are source files).

---

### SF-11 — Page assets
**Milestone** M1 · **Depends on** — · **Team** pair
**Owns** `render/assets/`, `render/pageassets.py`
**Context** ~35k — `CS/tools/study/assets/*.{css,js}`, `CS/tools/study/pageassets.py`, `CS/tests/test_highlight.py`

⭐ **Budget corrected down.** The assets are *already* 22 real `.css`/`.js`
files loaded by `pageassets.py` — R13 was satisfied here before this project
started, so this task is a **copy, not a repair**. The "80 KB of triple-quoted
strings" is history. R13's remaining cost lands in SF-12, not here.

**Definition.** The shared reading surface: palette, reset, focus ring, reading
column, the page stylesheet and script, vendored Prism, vendored Plyr. Ports
CodeSignal's rulings intact, each of which cost something to learn:

- **CSS and JS are source files, never Python literals** (R13). They were 80 KB
  of triple-quoted strings until somebody had to edit Python to change a colour.
- **Assets are shared and linked, never inlined.** They were 79% of each 60 KB
  page and byte-identical across all of them; at 1,290 units that is ~60 MB of
  duplication.
- **Filenames stay plain — no content hash.** A hash means a new filename, and
  a rewrite of every page that links it, every time a colour changes. The cost
  is a browser holding a stale copy until reload, which on a local study site
  is free.
- **Highlighting happens in the browser, never at build time.** Building spans
  into every page inflates all of them, puts a lexer's output permanently on
  disk, and would feed markup to the narration extractor. A language with no
  grammar is left alone rather than dressed up as code.
- **One element carries several highlight token classes**, and selectors of
  equal specificity mean **the last matching group wins** — so the group order
  *is* the mapping. A variant filed under the wrong group italicised every
  string in one language and the tests still passed; only a screenshot caught
  it. The port keeps the test that resolves each emitted combination the way a
  browser would.
- **Every colour token is defined in both themes.** A token defined once is a
  token that is wrong in one of them.

**Acceptance.** The highlight tests pass, including the check that no token
combination takes the comment colour without being a comment. A page opens with
only local requests. Every palette token is defined in both light and dark and
clears its contrast threshold. Vendored bundles carry their licences and are
unedited.

---

### SF-12 — Templates and unit page renderer
**Milestone** M1 · **Depends on** SF-10, SF-11 · **Team** team
**Owns** `render/page/`, `render/templates/`
**Context** ~110k — `CS/tools/study/html.py`, `CS/tools/study/templates/`, `CS/tests/test_html.py`, `CS/tests/test_templates.py`

⚠️ **Budget corrected up, and R13 has live work here.** `html.py:1112` is
`PLAYER = """<footer id="player">` — triple-quoted markup, in this exact
module. R13 is not satisfied in the source; that literal must become a template
during the port, not survive it.

**Subtasks.**
(a) Template loading and strict substitution — **an unfilled placeholder must
fail**, never reach the page as a literal.
(b) Block rendering, one module per group of block types.
(c) The **identity block** SF-04 scans for (R4).
(d) Relative asset, audio and media resolution for the `file://` floor (R8).

**Definition.** The reference renderer over a unit document. Markup lives in
template files (R13); the document skeleton, the figures, the panels and the
section wrapper are files, while loop bodies, inline wrappers and one-line
containers stay in code, because a template file for a closing tag removes no
duplication and adds a hop.

**A template is used exactly, minus one trailing newline.** That forces a split
the tests enforce: markup emitted on one line is *authored* on one line, however
long, while a template whose newlines are real output reads as a page.

⚠️ This is the largest port in the project after SF-19a. It is a **package**
(R11); a task that produces one large module has not done the task.

**Acceptance.** Byte-for-byte stable across runs. A page opens from `file://`
with working styles, highlighting and navigation, and issues no network
request. An unfilled placeholder raises. The identity block is present and
correct on every page. Both FND-04 fixtures render against golden files.

---

### SF-13 — Table of contents
**Milestone** M2 · **Depends on** SF-04, SF-05 · **Team** pair
**Owns** `contents/`
**Context** ~60k — `CS/tools/study/toc.py`

**Definition.** The site's contents **as data** — the primary artifact, of
which HTML is one renderer. Two documents, and the split is the whole point:

- **Stable** — the hierarchy itself, a pure function of committed inputs.
  Check out the repository on another machine and get the same bytes. A
  consumer can cache it against its version.
- **Local** — what is true right now: which pages exist on this machine, what
  the reader has ticked, what is next. It annotates the stable document by id
  and carries no structure of its own.

Keeping them in one blob would mean a consumer could neither cache the stable
half nor diff the volatile one — every regeneration would rewrite everything
and no reader could tell what actually changed. The local document names the
schema and version it annotates, so a stale pair is **detectable** rather than
silently joined on ids that no longer mean the same thing.

Generalised from CodeSignal's fixed nesting to `len(levels)`, and sourced from
discovery (SF-04) rather than a catalog — which is what severs the last tie to
CodeSignal's dedupe engine (R1). Level display labels come from `levels`.

**Acceptance.** Builds correct contents for a depth-1 and a depth-2 corpus from
the same code. Reproducible byte-for-byte. A mismatched pair is detected, not
silently joined. Both FND-04 fixtures produce valid contents.

---

### SF-14 — Root index renderer
**Milestone** M2 · **Depends on** SF-13, SF-11 · **Team** team
**Owns** `render/index/`
**Context** ~80k — `CS/tools/study/index.py`, `CS/tests/test_index.py`

**Subtasks.**
(a) Arbitrary-depth nesting using **real disclosure elements** — they open,
close and take keyboard focus with scripting off entirely, which is the
`file://` floor this page must clear.
(b) Default open/closed policy scaled to corpus size: open what was already
visible before anything could expand; make the layers that would multiply the
page's rendered length opt-in.
(c) Deep-link reveal — walk up from the target opening every ancestor, on load
and on hash change, so a link into a collapsed section lands open rather than
on nothing.
(d) Progressive enhancement gated on protocol, never a dependency.

**Definition.** The single self-contained page that opens by double-clicking,
with no server, no build step and no network. It reads **only** the two
contents documents — never the filesystem, never a catalog. That isolation is
the point: if this page can be built, the contract carries everything a
renderer needs; if it cannot, the contract is missing something. It shares the
unit page's palette and type stack by importing them rather than restating
them, so the two documents are one product.

Renders the Java corpus's 10 → 45 → 166 hierarchy, and must render a 1-level
corpus equally well.

**Acceptance.** Renders 166 units with working deep links into collapsed
sections. Works with JavaScript disabled. **Reads no file other than the two
contents documents — asserted, not assumed.** **Issues no runtime fetch —
asserted.** Renders the depth-1 fixture.

---

### SF-15 — In-page navigation
**Milestone** M2 · **Depends on** SF-12, SF-13 · **Team** solo
**Owns** `render/page/navigation.py`
**Context** ~40k — SF-12 and SF-13 outputs

**Definition.** Moving through the material from inside a unit: previous and
next across container boundaries, a breadcrumb labelled from `levels`, and a
jump list built from the unit's own headings — which for the Java corpus is the
nine uniform `##` sections every lesson carries, obtained for free because
E07 ingests them as heading blocks.

A neighbour with no generated page falls back to the root index anchor for it
rather than dangling, so navigation degrades to something useful instead of a
broken link.

**Acceptance.** Prev/next traverses all 166 units in curriculum order,
including across module and section boundaries. Breadcrumbs read
"Section › Module › Lesson" from data. Works over `file://`. No dangling links
anywhere in the corpus — asserted by a link check over generated output.

---

### SF-27 — Container page renderer
**Milestone** M2 · **Depends on** SF-12, SF-13 · **Team** solo
**Owns** `render/container/`
**Context** ~35k — SF-12 and SF-13 outputs, spec §5

**Definition.** The page for a **container** — `<module>.section.html` in the
Java corpus's placement (spec §5): what this module is, its units in order,
which are readable, and links up to its parent and down to its units.

This task exists because the spec named `*.section.html`, SF-04's discovery
scans for it, and **no task owned it** — 45 missing pages and a failing SF-04
acceptance. It is the one page a reader lands on when navigating downward, so
its absence is not cosmetic.

Renders at any depth: a 1-level corpus has one container page, a 2-level corpus
has one per module. The same renderer serves both — level labels come from
`levels` (SF-02), exactly as the breadcrumb does.

**Acceptance.** All 45 Java module pages render with correct unit lists and
working links in both directions. SF-04 discovers them by identity. Works over
`file://`. Byte-for-byte stable. A depth-1 fixture renders one container page.
