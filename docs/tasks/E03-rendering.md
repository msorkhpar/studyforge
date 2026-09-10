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
**Owns** `render/assets/`, `render/pageassets/`
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

#### ⛔ First act, before any renderer code: **review the markup-contract names** (`W9`)

⭐ **`render/pageassets/surface.py` is one half of a two-sided contract and only
one side has been written.** `SF-11` published the class names the stylesheet
targets; ⛔ **it had to guess what a renderer would call them, because the
renderer did not exist yet.** ⚠️ **`SF-12` is the other side arriving**, and this
is the one moment the guess is free to correct.

⛔ **So the review is this task's first commit, not a later tidy-up.** ⭐ **The
failure it prevents is silent and the module says so itself:** a stylesheet and a
template that disagree about a class name produce a page that renders, carries
every word, and is **unstyled — with no error anywhere.**

**The rule `surface.py` already states, and it binds this task:** ⭐ **`SF-12` may
rename any of these**, and a rename is a change to that file **and** the
stylesheet, *together*. ⛔ **What it may not do is invent a second name for
something already here** — `test_surface` asserts that every class the shared
stylesheet targets appears in the mapping, so a rename touching one side fails.

⛔ **These are hooks, not semantics.** Nothing this task writes may read a class
name back as a block type. ⭐ That is R4's argument about paths, applied to markup.

⚠️ **`W9` had been a board row reading *"not in E03 yet"*, and the board's own
note said the sequencing instruction *"only works if it reaches the task before
the task starts."*** ⛔ **It is here now because a board row is the destination
that has already evaporated twice, measured.**

#### ⚠️ `W11` — if this task mints an `api` field, it is the one that collides

⭐ **Recorded as an accepted finding with its remedy already stated**, so the
remedy is not re-derived under time pressure: `api` is a generic field name and
the tree guard would flag a module reading an *unrelated* one. ⛔ **Zero instances
today**, and the fix is to **narrow the rule to the module, never to drop the
field.** ⚠️ `SF-12` and E03's TOC task are the two realistic minters — ⭐ **so this
task answers it in one line rather than inheriting it.**

**Acceptance.** Byte-for-byte stable across runs. A page opens from `file://`
with working styles, highlighting and navigation, and issues no network
request. An unfilled placeholder raises. The identity block is present and
correct on every page. Both FND-04 fixtures render against golden files.

⛔ **And: a `para` whose text is tag-shaped renders as visible text, not as an
element.** ⭐ **This clause exists because `SF-07` declined CommonMark's type-7
raw-HTML rule on the promise that such a line stays prose** — an unknown tag on
its own line is kept as a paragraph rather than swallowed as markup, because a
lesson *teaching* HTML must keep it. ⚠️ **`SF-12` is the half that keeps that
promise**: the reader can only preserve the text, and whether the reader's
restraint survives to the page is decided here. ⛔ Without this clause the promise
has an author and no enforcer, and the failure is silent — the text does not
vanish from the archive, it vanishes from the page.

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

⛔ **Added by the PO, 2026-09-10 (round 22).** This task is the first thing in the
project that computes a **reading order**, and therefore the first that can
populate the unit page's between-units bar: `render/page/navigation.py`'s
`between_units(links)` returns `''` for `links=None`, and **no caller anywhere in
`src/` has ever passed anything else**. So one clause: a corpus built through this
task yields `Links` for a unit that has a neighbour, and the rendered page carries
`<nav aria-label="Between units">`. ⭐ **This matters beyond plumbing:** M1's close
condition 8 named the bar in its legibility bar and had to **void** the symptom as
unfalsifiable, because no ref populated it. The bar's rules are `SF-34`'s; its
*content* is this task's, and until it lands nobody can judge either.

#### ⛔ `W32` RE-ROUTED HERE, 2026-09-10 (PO round 25) — the mixed-form contents fixture

⛔ **`W32` was a queue row for four rounds and it could never win one, because
its exposure is `0` BY CONSTRUCTION: there is no parser for it to catch out.**
⭐ **Measured at `ce58a36`: `src/studyforge/contents/` is `__init__.py` and 20
lines, and a `grep` for any list-or-heading parse in it returns nothing.**
⚠️ **A fixture whose acceptance reads *"the fixture fails if a parser reads only
the list form"* is unfalsifiable while no parser exists** — ⛔ **which is
`CTO-29/3`'s family arriving in a queue instead of an acceptance document.**

⭐ **So it becomes an acceptance condition on the task that first needs it, and
this is that task.** ⛔ **The donation is real material, from check 6's `F8`
contribution:** a contents document listing **36 of 38** units as list items and
**2** as headings. ⚠️ **A parser written against the list form reads 36, emits
36, and raises nothing** — a plausible SHORT PARSE with no symptom.

⭐ **The clause:** ⛔ **a contents document whose entries are MIXED list items and
headings parses to the FULL count, and the fixture FAILS if a reader sees only
the list form.** ⚠️ **The fixture is built by this task, not before it.**

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

Renders an arbitrarily deep hierarchy — the Java corpus's is 10 → 45 → 166 —
and must render a 1-level corpus equally well.

**Acceptance.** Renders **both `FND-04` fixtures**, at both depths, with working
deep links into collapsed sections. Works with JavaScript disabled. **Reads no
file other than the two contents documents — asserted, not assumed.** **Issues
no runtime fetch — asserted.**

#### ⛔ Acceptance SPLIT by the PO, 2026-09-10 (round 34) — **Ruling 151**, in the same edit as `SF-27`'s

⛔ **The first clause used to read:**

> ~~Renders **166 units** with working deep links into collapsed sections.~~

⚠️ **`166` is a count of the Java corpus, readable only inside a consumer
repository — the same defect `SF-27/5` reported one row over, and Ruling 151
closed this class after three instances.** ⛔ **Not waived: R20 means a framework
close cannot rest on a measurement only the integration agent can take.**

⭐ **The framework half — both fixtures, both depths — is what actually
discriminates**: a renderer that handles depth-1 and depth-2 handles 166 units or
fails for a reason the fixtures expose. ⛔ **The scale half joins `SF-27`'s in
`W77` on the integration side.**

⚠️ **The `Definition`'s *"Renders the Java corpus's 10 → 45 → 166 hierarchy"* is
kept as an ILLUSTRATION and re-worded to say so** — ⭐ **Ruling 151 forbids the
clause in an ACCEPTANCE, not the corpus in a description; R20's line is between
what a close is gated on and what a task is explained with.**

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

**Acceptance.** Prev/next traverses **every unit of both `FND-04` fixtures** in
curriculum order, including across module and section boundaries. Breadcrumbs
read "Section › Module › Lesson" from data. Works over `file://`. No dangling
links anywhere in the generated output — asserted by a link check.

#### ⛔ Acceptance SPLIT by the PO, 2026-09-10 (round 34) — **Ruling 151**, and this one NOBODY REPORTED

⛔ **The first clause used to read:**

> ~~Prev/next traverses **all 166 units** in curriculum order.~~

⚠️ **Same defect as `SF-27/5` and `SF-14`'s, and it was found by SWEEPING for the
class rather than by fixing the two instances that were handed to me** — ⛔ **`166`
is a count readable only inside a consumer repository.** ⭐ **The framework half —
every unit of both fixtures, across module and section boundaries — is what
actually exercises the boundary-crossing this row exists for.** ⛔ **The scale
half joins `SF-14`'s and `SF-27`'s in `W77`.**

⚠️ **`SF-15` is step 2.4 and would have been dispatched carrying it** —
⭐ **which is the argument for sweeping a ruled class instead of discharging its
reported instances: two were reported, four were framework-side, and the fourth
is in a CLOSED row (`PO-34/9`).**

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

**Acceptance.** Every container of **both `FND-04` fixtures**, under **both
placement profiles**, renders with correct unit lists and working links in both
directions. SF-04 discovers them by identity. Works over `file://`.
Byte-for-byte stable. A depth-1 fixture renders one container page.

#### ⛔ Acceptance SPLIT by the PO, 2026-09-10 (round 34) — **Ruling 151**

⛔ **The first clause used to read, and the text is preserved because a removal
that hides what it removed is not a split:**

> ~~All **45 Java module pages** render with correct unit lists and working links
> in both directions.~~

⚠️ **That is a COUNT INSIDE A CONSUMER REPOSITORY, and Ruling 151 forbids a
framework task's Acceptance from resting on one.** ⛔ **R20 is why it cannot be
waived instead: a framework close may not be gated on a measurement only the
integration agent can take, and `45` is readable in exactly one place this side
does not own.** ⭐ **Reported by the developer as `SF-27/5`, NOT rewritten by
them — which is the reporting half of Ruling 151 working as designed.**

⭐ **The framework half is the clause above and it is strictly stronger in the
dimension that matters**: *both fixtures × both profiles* exercises depth-1 and
depth-2 and each placement, where *45 Java pages* exercises one corpus at one
depth under one profile. ⛔ **The scale half is re-homed to `W77` on the
integration side, exactly as `SK-08/2`'s went to `W73`.**

⚠️ **`SF-14` carried the identical shape and is split in the same commit** — ⭐ **the
developer measured that and said splitting both once is cheaper than twice, which
is right and is why they are one edit.**

---

### SF-34 — Page chrome styles
**Milestone** M2 · **Depends on** SF-11, SF-12 · **Team** solo
**Owns** `render/assets/chrome.css`
**Context** ~25k — `render/assets/reading.css`, `render/pageassets/{bundle,surface}.py`,
`render/page/{section,navigation}.py`, SF-11's and SF-12's handoffs

⛔ **This task exists because the reading surface and the page chrome met at a
boundary neither owner had drawn.** `SF-11`'s finding 3 assigned *"masthead and
layout grid and the navigation rail"* to `SF-12`; `SF-12/5` answered that
`reading.css` declares chrome out of its own scope and that `test_surface`
asserts the published class set and the stylesheet's set are **equal in both
directions** — so a single new chrome class costs three files in two packages
`SF-12` does not own. ⭐ **Both were right. The markup shipped; the rules did
not.** Ruled 2026-09-10: the markup is `SF-12`'s and is done; the rules belong
with `reading.css`, because **a class name with no rule is not styling**.

**Definition.** Rules for the chrome regions the **pages** already emit, as a new
stylesheet part, plus its entry in `STYLE_PARTS` and its hooks in
`SURFACE_HOOKS`.

⛔ **SCOPE CORRECTED BY THE PO, 2026-09-10 (round 34) — `SF-27/2`. This line said
*"the three chrome regions the unit page already emits"* and it was stale in two
directions at once.** ⚠️ **Note (a) below had already made the practice panel a
FOURTH; `SF-27`'s container page now emits a FIFTH, and it is a page this line
did not contemplate at all — the line says *the unit page*, and there are now
two page kinds.** ⛔ **A `solo` row that READS AS COMPLETE while its scope is
short is the worst shape a row can have: nothing about it signals the gap.**

| # | region | ⭐ **whose markup, and where it is** |
|---|---|---|
| 1 | masthead | `SF-12`, shipped |
| 2 | outline | `SF-12`, shipped |
| 3 | between-units bar | `SF-12`, shipped — ⚠️ **and now emitted by the CONTAINER page too** |
| 4 | practice panel | `SF-12`, shipped — added by note (a) |
| 5 | ⛔ **the container's unit listing** | ⛔ **`SF-27`** — `<nav aria-label="Units">` with `<ol>`, and **TWO NEW HOOKS**: `data-readable` on each `<li>` and `data-kind="numbering"` on the ordinal `<span>`. ⭐ **Measured on `feat/SF-27` @ `6c39d5f` against `tests/fixtures/pages/getting-started.section.html`, not taken from the report** — ⚠️ **and `SURFACE_HOOKS` on that branch still holds only `table_scroll`, `copy_button`, `code_caption`, so there is NO RULE ANYWHERE for either hook** |

⭐ **The property this task was scheduled late to preserve still holds and is
re-checked rather than assumed:** the container page addresses its chrome by
element and `aria-label` and `data-*` only — ⛔ **the `<nav>`, `<ol>` and `<li>`
carry no class** — so this row still costs no re-render. ⚠️ **`SF-14`'s root
index will add a SIXTH, and it is now placed: whoever takes `SF-34` re-measures
the region list against the tree rather than against this table.**

⭐ **The page needs no change and no re-render.** `SF-12` addressed all three
regions by element, `aria-label` and `data-*` only — measured: every class the
goldens carry is in `SURFACE_CLASSES | SURFACE_HOOKS | {language-java}`, and the
`<header>`, `<nav>` and `<ol>` carry none. **That is the whole reason this task
could be scheduled late without cost, and it is the property to preserve.**

⚠️ **Two edits land outside `Owns`, and both are additive**: one entry in
`render/pageassets/bundle.py`'s `STYLE_PARTS` and one in
`render/pageassets/surface.py`'s `SURFACE_HOOKS`. **They are named here so the
next author does not stall on the boundary that produced this task.**

⛔ **In the same change:** the two `<nav>` regions move out of Python f-strings
into `render/templates/`. They carry a **product string** (`Contents`) in code
while the rest of the page uses the template mechanism; E03's one-line-container
exception covers them, but this is the place that exception does the most work.

**Why M2 and not M1.** Two of the three regions get their content from SF-13,
SF-14 and SF-15, and SF-15 is step 2.4. **Styling a region before its content
exists is SF-11's own finding-3 warning one layer up** — *the palette defines
tokens nothing paints with* — and this task is where the unit page's share of
that leniency is claimed rather than extended.

**Acceptance.** The three regions carry rules in both themes, every token used
is a palette token, and `test_surface` passes in both directions with no class
added to any page. Contrast clears its threshold in both themes (QA-03's
instrument, not a new one). The two `<nav>` regions render from templates and no
product string is typed in Python. The goldens change once, deliberately, and
the change is stated as a product change rather than absorbed.

---

#### ⭐ Four clauses added by the PO, 2026-09-10 (round 22), from `QA-03`'s captures

⛔ **Each is here because the instrument that opened the page found something no
test can see. The argument for each is in [`BOARD.md`](BOARD.md); this is the
carrier.**

**(a) The practice panel is this task's fourth region.** `reading.css`'s own
scope note disowns five regions by name — *"Masthead, navigation rail, narration
player, progress controls and **practice panels** are NOT here: they belong to
the tasks that render them"* — and the practice panel's markup is `SF-12`'s, which
is done. ⛔ **That is this task's founding defect, one region further along.** So
`SF-34`'s scope is the chrome list `reading.css` disowns, **minus** the regions
whose markup does not exist yet: the narration player and the progress controls
stay `SF-18`'s at M3.

**(b) `QA-03/2` — four ownerless colour tokens, and the ledger is the check.**
`--surface-2`, `--accent-soft`, `--practice` and `--practice-soft` are defined in
`palette.css` and painted by no stylesheet, and they had no owner at any
milestone. They are this task's: paint them, or delete them from the palette and
say so. ⭐ `tests/visual/palette.py`'s `UNPAINTED` rows are **derived from the
stylesheets and asserted equal in both directions**, so painting one fails the
ledger test until somebody states which ground its contrast is taken against.
**That failure is the feature — reclassify the row, never delete it.**

**(c) The between-units bar's legibility bar, re-homed here.** M1's close
condition 8 named three symptoms and one of them — *"the between-units bar
indistinguishable from body text"* — was **unfalsifiable at M1**, because nothing
computes a reading order before `SF-13` and no golden emits the bar. ⛔ **It was
voided at M1 and re-homed rather than dropped**, so it is discharged here: once
the bar is populated, it must be distinguishable from body text without reference
to colour alone. **A bar nobody can see is not a bar that passed.**

**(d) `PO-22/6` — nothing defines *the column*.** `reading.css:38–41` states a
deliberate decision: *"A figure, a table or a code block is scanned rather than
read and takes the full column."* That decision is correct. But `body` carries
`margin: 0; padding: 0 var(--gutter)` and **no `max-width`**, so at a 1280px
viewport *"the full column"* is the full viewport and the page reads as a narrow
measure with full-bleed islands. ⛔ **Bounding the page's column is the layout
grid — `SF-11`'s finding 3 named it and this task inherited it** — so it lands
here. ⚠️ This is not a licence to re-open the measure decision; it is the missing
half of it.
