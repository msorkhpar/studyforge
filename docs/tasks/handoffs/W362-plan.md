# W362 — the design plan (stage 1 of 2)

**Kind:** survey

**Document kind: `survey`.** ⛔ **Not the task handoff.** It is stage 1 of [`W362`](../rows/W362.md): the
design plan the row's clause 1 requires **before any code**, written for the register to read before the
build is dispatched. Nothing under `src/` changed. The build's own handoff is `W362.md`, written in stage 2.

⭐ **The authority is [the UI design brief](../../conventions/ui-design.md)**. Every section below
answers one of its clauses, and §8 reads the plan against every tell in its §2, and §12 reads it against the reference page the register shared.

**As of:** `release/m0-foundations` at `6c05538`, fast-forwarded onto this branch.
**Looked at:** real generated pages, opened over `file://` in headless Chrome 149 on this host (unpinned:
the dev image's browser was not used for this survey), driven by the existing `tests/visual/` harness
(`browser.py`, `page.py`, `site.build`), with no second harness. Light, dark, 1280px and 400px wide.
Two sources:

- the framework's own fixtures (`depth1`, `depth2`) built by `tests/visual/site.build`;
- ⭐ **the ISO-8583 corpus at its pinned `77535e6`**, built with `studyforge build` into a scratch directory
  (the sibling was only read, and its tree was clean afterwards). Pages read: the root index, the
  `client-implementation` container, and three units with code (`iso-fundamentals` unit 2,
  `jpos-client` unit 2, `jpos-server` unit 2).

The screenshots stay in the office's scratch directory and are not committed (R7).

---

## 1. What exists: the flaws, by region

Every flaw has an id so §9 can tie a fix to it. **Measured** means read from the browser. **Seen** means
read off a screenshot. Where the cause is outside this row's surface, the flaw says so.

### Masthead and trail (M), 7

- **M1**: the meta line is ALL-CAPS and tracked (`JPOS-CLIENT · PROSE`), which is the eyebrow tell
  (`chrome.css` region 1: `text-transform: uppercase; letter-spacing: .06em`).
- **M2**: the meta parts are joined with middle dots. ⚠️ The separator is `META_SEPARATOR = " · "` in
  `render/page/document.py` and `render/container/document.py`, **outside this row's surface**.
- **M3**: the meta line is made of builder words that tell a reader nothing: the variant `prose`, an
  address slug `01-getting-started`, and the level word `group`. The container page shows all three:
  `GROUP · JPOS-CLIENT · PROSE`.
- **M4**: headings use `--font-ui`, a system stack that names `Roboto` and `Arial` (two banned faces) and
  is a bare system stack (banned). The face a reader gets depends on their machine.
- **M5**: the trail sits **under** the title, below a rule. The reader reads the title, then the path to
  it, then the contents card.
- **M6**: in the trail, the first crumb is the whole corpus title (two lines at 400px), the middle crumbs
  carry level chips (`group`, `module`, `section`), and linked and unlinked crumbs are mixed. The `›`
  in front of the current crumb reads as a leading glyph.
- **M7**: the heading scale is flat: h1 30.4px against h2 22.4px, both weight 700 (**measured**). On a unit
  page the first prose line starts at **409px at 1280 wide and 1126px at 400 wide** (**measured**, ISO
  `jpos-client` unit 2), so at phone width a full screen of chrome comes before any of the lesson.

### Rail across containers (R), 6

- **R1**: the rail is a card (a `--surface-2` ground, a 1px border and a 10px radius) that stops where
  the list stops, so a rounded box floats at the top left of a long page. That is the card-kit tell.
- **R2**: each container's disclosure triangle sits alone on a line **above** its title, because the
  summary's link is `display: block`. It reads as a stray glyph (the brief's "shapes that can be
  misread").
- **R3**: every container title has a tinted chip with the level word in it (`group`, `module`). That is
  the pill tell, and the word tells a reader nothing.
- **R4**: unit ordinals are tinted chips of varying width, so titles after 1–9 and titles after 10+ start
  at different x. **Seen** in the rail and on the index.
- **R5**: at phone width the whole rail renders open before the lesson. It is the main cause of M7's 1126px.
- **R6**: the rail shows no read ticks. `chrome.css` paints `data-marked` only on the `Units` and
  `Contents` lists, so the one list that is on every page never says what the reader has finished.

### In-page outline (O), 4

- **O1**: a card, the same kit as R1.
- **O2**: its label is `CONTENTS`, ALL-CAPS and tracked (the eyebrow tell).
- **O3**: a stack of underlined accent links. The first entry repeats the page title (that part is corpus
  data).
- **O4**: about 60px of empty ground between the card and the first heading.

### Reading column (C), 6

- **C1**: the light palette is warm cream `#f6f3ee`, a serif prose face and a terracotta accent
  `#8f3f16`. **That is the first palette the brief names as a tell** (the row's own measurement).
- **C2**: the prose measure is `80ch`, 760px at 19px (**measured**). The brief asks for about 65–70.
- **C3**: when the page opens, the first narrated passage is already lit with the highlight wash
  (`[data-speaking]` count 1 on load, **measured**), before anything has played. The resting page looks
  as if something is selected.
- **C4**: `details.disclosure` ("Show a hint") is a rounded, bordered card.
- **C5**: the prose stack begins with `Iowan Old Style`, which no Linux host has, so the face falls
  through to whatever serif the machine has. The page is not designed in the face it is read in.
- **C6**: the dark theme is a tinted near-black `#141519` with an orange accent `#e79a63`. The brief says
  not to use a tinted near-black as the dark ground, and this is close to the "near-black plus one hot
  accent" tell.

### Code (K), 4

- **K1**: ⛔ **every code block is double-spaced.** `pre` inherits the body's 19px/1.72 strut, so lines
  of 13.44px code sit 32.68px apart (**measured**: `pre` line-height 32.68px, `code` 21.77px). Blocks are
  about 1.5× as tall as they need to be.
- **K2**: the block is a rounded 8px bordered card with a caption bar. Its ground `#f3eee5` is barely
  different from the page ground `#f6f3ee`.
- **K3**: the syntax colours are a generic editor theme (magenta keywords, violet functions) with no
  relation to the page.
- **K4**: the copy button's fallback text is `Press ⌘C` (`copy-code.js:52`), which is wrong on every
  machine that is not a Mac.

### Narration player (N), 7

- **N1**: the player is a full-width white slab with a soft shadow, **140px tall at 1280 wide and 188px at
  400 wide, 21% of a 900px phone screen** (**measured**), sitting over the text for the whole visit.
- **N2**: `← Prev` and `Next →` have arrows added to the labels (the arrow tell). All three buttons have
  the same bordered look, so Play is not the primary control.
- **N3**: the keyboard sentence ("Space plays and pauses…") is always shown, including on touch screens
  where it cannot apply.
- **N4**: the position is joined with a middle dot drawn by `narration.css` (`#counter::before { content:
  " · " }`).
- **N5**: the controls sit flush on the slab's left edge with no inner gutter.
- **N6**: the progress track is 0.3rem of `--surface-2` with an amber fill, which is barely visible.
- **N7**: the narration-gap notice has a coloured stripe down its left edge (`border-left: .2rem solid
  var(--accent)`), which is a tell, and its paragraph is three sentences long.

### Between-pages bar (B), 4

- **B1**: `← Basic Setup` and `Channel Management →` (arrow tell, in `link-previous.html` and
  `link-next.html`).
- **B2**: previous and next have the same weight. The next unit, which is what the reader wants, is not
  the most prominent thing.
- **B3**: the up link in the middle is the whole corpus title and wraps.
- **B4**: at phone width the three links stack left-aligned with no labels. Only the arrow says which one
  is next.

### Pending practices (P), 4

- **P1**: a tinted panel with a 4px coloured stripe down its left edge and an 8px radius. That is the
  stripe tell and the card tell together.
- **P2**: `1 of 2 archived · 1 to come.` has a middle dot and the builder word `archived`. ⚠️ The sentence
  is built in `render/page/document.py`, **outside this row's surface**.
- **P3**: its colour is teal (`--practice`), a second accent family unrelated to the rest, and teal is
  one third of a rejected palette.
- **P4**: the heading "More to come" does not say *what* is to come.

### Read mark (RM), 2

- **RM1**: a panel whose three-line storage disclaimer is longer than the one action it offers.
- **RM2**: one toggle whose label flips between "Mark as read" and "Marked as read ✓". Pressing it again
  unmarks the unit with no notice.

### Root index (I), 6

- **I1**: no framing copy. Nothing says what this site is, where the material came from, or how to use it.
- **I2**: every group is open, so a 38-unit course is about 2,000px of list. The brief says to open the
  section the reader is in.
- **I3**: rows are about 46px apart, with chips (R4's misalignment).
- **I4**: no sense of progress: no count of what is read and no way to continue at the next unread unit.
- **I5**: the first group repeats the page title word for word (corpus data), in bold, with a `group` chip.
- **I6**: at 400px wide the h1 wraps to five lines. It has no `text-wrap: balance`.

### Container page (CP), 2

- **CP1**: meta `GROUP · JPOS-CLIENT · PROSE`: M1, M2 and M3 all at once.
- **CP2**: about 50px of empty band between the masthead and the list.

### Whole page (G), 5

- **G1**: no skip link to the content.
- **G2**: no `<meta name="theme-color">`.
- **G3**: no `scroll-padding`. A tabbed-to control near the bottom can land under the sticky player.
- **G4**: the dark theme is keyed only on `prefers-color-scheme`. There are no `[data-theme]` guards,
  which the brief requires for both themes.
- **G5**: `chrome.css` is **748 lines** and its docstring does not justify going past R11's 400. ⚠️ The
  `FND-01` gate never saw it because `tools/quality/config.python_files` reads `*.py` only. That is a
  finding (§11).

**Total: 57 flaws in 12 regions.** The count by region: M 7, R 6, O 4, C 6, K 4, N 7, B 4, P 4, RM 2,
I 6, CP 2, G 5.

---

## 2. The subject, the reader, the page's job (§1.1)

- **The subject every studyforge site shares:** a body of teaching material that one person works through
  **alone, in order, offline**, reading it and sometimes listening to it, and ticking off what they have
  done. The corpus changes; this does not.
- **The reader:** someone teaching themselves from their own machine. In both corpora on this host that
  is a developer.
- **The single job:** on a unit page, *read (and hear) this unit, then go on to the next one*. On the
  index and a container page, *show me where I am in the course and let me pick up there*.

## 3. The subject's own world (§1.2)

⭐ **The exercise book.** It is the instrument of working through material on your own. Everything in it
has a job, and every studyforge page has the same jobs:

| In the exercise book | On the page |
|---|---|
| **The margin rule**, a thin pink-red line printed down every page. Left of it is yours (numbers, ticks); right of it is the work. | Quiet structure, and not the loud element: one pale line between the reader's column (the course, their ticks, the narration cue) and the material. |
| **Feint ruling**, pale blue lines that separate without shouting. | Every hairline divider: list rows, the table grid, the between-pages rule. |
| **Blue-black ink** for the writing. | The text colour, and ordinary links (underlined), so the page is written in one ink. The neutrals take its blue, so they read as chosen. |
| **Washable royal-blue ink**, the fresh pen you are about to write with. | ⭐ **The accent, and it means one thing only: what is next and where you are.** The next unit, the current unit's marker, the current container's segment, and the focus ring. |
| **The label on the next exercise-book in the pile**, the one you open when this one is full. | ⭐ **The one saturated element: the "Up next" slip** (§7). |
| **Tick boxes** printed in the margin of a workbook. | The per-unit marker: an empty ruled box, a solid ink box with a paper tick once done, and a washable-blue outlined box for the one that is next. |
| **The highlighter** swiped over the line you are on. | The narration highlight, and only while it is speaking. |
| **Pencil.** | Muted and secondary text, and per-item facts, right-aligned. |
| **Exercise numbers in the margin.** | Unit ordinals in a fixed column, as plain numerals and never chips. |

**The dark theme is the same classroom's other surface, the blackboard.** It has a green-black board,
chalk writing, chalk dust for the quiet text, blue chalk for what is next, a faint red-chalk margin, and
yellow chalk for the highlight. This is a real mid-dark with a hue, not a tinted near-black.

---

## 4. Colour (§1.3), both themes, by role

⭐ **Both themes are designed, not one of them plus an inversion.** The reference page commits to one
look, which is right for a page opened for a minute to choose a course. A unit page is read for an hour,
often in the evening, and readers of this site already have a dark theme. Taking it away would be a
regression, so each theme is a real surface from the same room.

⛔ **Every existing token NAME is kept** (`SF-22` paints with them in parallel). Only values change, and
new tokens are added. The roles below use the brief's role vocabulary (ground, raised, ink, ink-soft,
ink-faint, rule, next, sign) and map onto the names this repository already paints with.

| Role (brief's name) | Existing token | Light: exercise book | Dark: blackboard |
|---|---|---|---|
| Ground (`--ground`), paper / board | `--bg` | `#f1f5f2` exercise paper (a cool green-white, not cream) | `#26322c` blackboard |
| Raised (`--raised`): disclosure, caption, player | `--surface`, `--panel` | `#fbfcf9` | `#2e3b34` |
| Chrome ground: current row, track | `--surface-2` | `#e4ebe7` | `#34433b` |
| Ink (`--ink`) | `--fg` | `#1b2236` blue-black | `#eef0e8` chalk |
| Ink, soft (`--ink-soft`) | `--fg-soft` | `#3a4257` | `#d3d8cd` |
| Ink, faint (`--ink-faint`): pencil | `--muted` | `#586070` graphite | `#aab4a9` chalk dust |
| Feint ruling (`--rule`) | `--rule` | `#c6d3de` | `#43534a` |
| Ruling, strong: control borders, empty tick boxes | `--rule-strong` | `#72889d` | `#788c7f` |
| **Next (`--next`): up next, you are here, focus** | `--accent`, `--focus` | `#23449a` washable blue | `#a9c8ff` blue chalk |
| Next, ground (the current row's wash) | `--accent-soft` | `#e2e8f4` | `#34433b` |
| Practices, now in pencil and no longer teal | `--practice` / `--practice-soft` | `#3a4257` / `#e4ebe7` | `#d3d8cd` / `#34433b` |
| Code ground / code ink | `--code-bg` / `--code-fg` | `#e8eee9` / `#1b2236` | `#1f2a25` / `#e6e9e1` |
| Highlighter (the spoken passage) | `--hl-bg` / `--hl-fg` | `#fbef7a` / `#1b2236` | `#4f4b1f` / `#fffbe3` |
| Narration progress | `--hl-bar` | `#23449a` | `#a9c8ff` |
| **New, sign (`--sign`): the Up next slip's ground** | `--sign` | `#23449a` | `#a9c8ff` |
| **New: the slip's ink** | `--sign-ink` | `#fbfcf9` | `#1f2a25` |
| **New: the margin rule (structure, never a signal)** | `--margin` | `#cf8f98` | `#8a5257` |
| **New: done (a solid ink tick box)** | `--done` | `#1b2236` | `#eef0e8` |

⭐ **One hue carries both "next" and the slip, and that is on purpose.** In the reference the next
course's colour (yellow) and the exit sign's (green) differ because road signage has two separate
colour codes. An exercise book has one fresh pen. The distinction is kept by **form, not by hue**: the
accent is only ever a line, a ring or a word, and the slip is the only **filled** area of saturated
colour on any page.

**Syntax, re-tuned as a pen case of inks** (the seven `--tok-*` names are kept). Keywords are blue-black
bold, types are washable blue, functions violet ink, strings green ink, numbers sepia, comments pencil
italic and punctuation graphite. Light: `#1b2236 #23449a #6a3294 #26663a #8a4513 #5e6570 #555c66`. Dark:
`#f2f4ec #a9c8ff #d6b0ff #9bd8a4 #f1b27a #9aa59b #b3bcb2`. `--hl-code` becomes a highlighter wash:
`rgba(251,239,122,.35)` in light and `rgba(242,226,122,.14)` in dark. `--shadow` becomes a single
hairline instead of a soft grey shadow: `0 -1px 0 #c6d3de` in light and `0 -1px 0 #43534a` in dark.

**Contrast, computed with the WCAG 2 formula and not judged by eye.** `test_palette` will recompute every
one of these in stage 2.

| Pair (text on ground, or mark on ground) | Light | Dark | Floor |
|---|---|---|---|
| `--fg` on `--bg` | 14.36 | 11.60 | 4.5 |
| `--fg-soft` on `--bg` | 9.10 | 9.19 | 4.5 |
| `--muted` on `--bg` / `--surface` / `--surface-2` | 5.74 / 6.14 / 5.22 | 6.23 / 5.48 / 4.88 | 4.5 |
| `--accent` on `--bg` / `--surface-2` | 8.07 / 7.33 | 7.87 / 6.16 | 4.5 |
| `--sign-ink` on `--sign` (the slip's words) | 8.62 | 8.75 | 4.5 |
| `--sign` against `--bg` (the slip's edge) | 8.07 | 7.87 | 3 |
| `--practice` on `--practice-soft` | 8.27 | 7.19 | 4.5 |
| `--code-fg` on `--code-bg` | 13.43 | 12.08 | 4.5 |
| the seven tokens on `--code-bg`, lowest of the seven | 4.99 (comment) | 5.81 (comment) | 4.5 |
| `--hl-fg` on `--hl-bg` | 13.34 | 8.55 | 4.5 |
| `--fg` / `--muted` on `--panel` | 15.35 / 6.14 | 10.20 / 5.48 | 4.5 |
| `--done` on `--bg` (the solid tick box) | 14.36 | 11.60 | 3 |
| `--rule-strong` on `--bg` (control borders, empty tick boxes) | 3.33 | 3.72 | 3 |
| `--hl-bar` on `--surface-2` (the progress fill) | 7.33 | 6.16 | 3 |
| `--focus` on `--bg` (the ring) | 8.07 | 7.87 | 3 |
| `--margin` on `--bg` | 2.37 | 2.17 | none: decoration |

⚠️ **The margin rule is deliberately below 3:1.** It carries no information that nothing else carries:
the reader's column is also told apart by position and by its own content. That is why it may be quiet.
⚠️ **Running-text links are ink with an underline** (colour is not what marks them). Navigation lists
(rail, outline, index) are unlined ink and underline on hover and focus, as the reference does.

---

## 5. Type (§1.3), three faces, all SIL OFL, from the world of learning to read

⭐ **Two of the three come from SIL's literacy work: faces drawn for people learning to read.** The
subject every studyforge site shares is learning, and neither face is on any "modern and clean" list.
⛔ **Overpass is not used**, because it is the reference page's own subject choice (highway signage).

| Role | Face | Why this one |
|---|---|---|
| Prose | **Charis** (SIL), 400, italic, 700, bold italic | Drawn for long-form reading and literacy publishing, on the Bitstream Charter design the current stack already reaches for. It has sturdy serifs and clear letterforms, and it holds up at body size on an ordinary screen. |
| Headings, rail, trail, controls, captions, the slip | **Andika** (SIL), 400 and 700 | A sans drawn **for beginning readers**: `I`, `l` and `1` cannot be confused, and the letterforms are plain. It is the wayfinding voice of the page. It is clearly distinct from Charis, so two families is justified. |
| Code | **JetBrains Mono**, 400, italic, 700 | Code is the material's own instrument, and in these corpora its content is things like `"4111111111111111"`, `"0200"` and field numbers, where 0/O and 1/l/I must not be mistaken. It is used for code only. ⛔ **It is never used for small data labels** (a tell). |

**The scale has real jumps and real weight contrast.** h1 is Andika at its heaviest shipped weight,
2.5rem. h2 and h3 are Andika 700 at 1.6rem and 1.2rem. Body is Charis 400 at 1.1875rem/1.65. UI text is
Andika 400 at 0.95rem. ⚠️ The reference sets 800 against 400. If the Andika zip carries an ExtraBold
(the register reads the listing), the h1 and the slip's title use it. If not, 700 Andika against 400
Charis is a contrast of weight **and** of family, which is stronger than 700 against 400 in one family.
`text-wrap: balance` goes on headings, `tabular-nums` on every ordinal and counter, and sentence case
everywhere.

### The files the register must fetch (no network was used here; names are from upstream's release layout)

⚠️ **Read with care: these URLs and paths come from memory of each project's release layout and could
not be checked from this host.** The register confirms each tag exists, lists each zip, and pins each file
it keeps by sha256, with the licence beside it.

1. **Charis 6.200**: `https://github.com/silnrsi/font-charis/releases/download/v6.200/Charis-6.200.zip`
   (SIL's mirror: `https://software.sil.org/downloads/r/charis/Charis-6.200.zip`). Files:
   `Charis-6.200/web/Charis-Regular.woff2`, `Charis-Italic.woff2`, `Charis-Bold.woff2`,
   `Charis-BoldItalic.woff2`, and `Charis-6.200/OFL.txt`.
2. **Andika 6.200**: `https://github.com/silnrsi/font-andika/releases/download/v6.200/Andika-6.200.zip`
   (SIL's mirror: `https://software.sil.org/downloads/r/andika/Andika-6.200.zip`). Files:
   `Andika-6.200/web/Andika-Regular.woff2`, `Andika-Bold.woff2`, any ExtraBold the zip carries, and
   `Andika-6.200/OFL.txt`.
3. **JetBrains Mono 2.304**:
   `https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip`. Files:
   `fonts/webfonts/JetBrainsMono-Regular.woff2`, `JetBrainsMono-Italic.woff2`,
   `JetBrainsMono-Bold.woff2`, and `OFL.txt`.

⚠️ **Size is unknown until the files are fetched.** The SIL faces cover Latin, Greek and Cyrillic and may
be large. The reference embeds a **Latin subset** of its face, which is the same answer D3 proposes.

**Fallbacks** follow each vendored family with no banned face in them: `"Charis", Georgia, serif`;
`"Andika", Verdana, sans-serif`; `"JetBrains Mono", "DejaVu Sans Mono", monospace`.

---

## 6. Layout (§1.3): what the reader needs first

⭐ **Hierarchy follows the reader's priority, page by page, and that decided the layout rather than the
other way round.**

- **Root index: first "what this is", then "where I am", then "what is next".** A heavy title. One
  plain paragraph. Three short columns: *Where it comes from*, *How it is ordered*, *How to use it*. A
  progress line (`5 of 38 units read`, with `33 to go` right-aligned on the same line). A **segmented
  strip** sized by units per container, which is also the containers' navigation. Then the **Up next
  slip**. Then the course.
- **Unit page: first the lesson, then what is next.** The title and one quiet line ("Unit 2 of 11 in
  Client implementation"), then the lesson with nothing heavy in between. The slip comes at the foot,
  where the reader finishes, and names the next unit.
- **Container page: its units, with its own progress.** The same rows as the index, but for one
  container.

**Progress doubles as navigation, in two places:**

1. **The index's strip.** One segment per container, `flex-grow` equal to its unit count. The filled part
   of each segment is its read fraction in ink. The container holding the next unit is **outlined in
   the accent**. Each segment is a link to that container's group, and its accessible name says
   "Client implementation, 1 of 11 read".
2. **The rail and the index rows.** Each container row carries `n of m read` right-aligned, over a thin
   progress rule. The units hang on one vertical feint line with a **tick box** each: empty ruled, solid
   ink once read, and **outlined in the accent** for the next unit. On a unit page the current unit's row
   also has the accent wash (`--accent-soft`) so "you are here" and "next" cannot be confused.

The reading column is left-aligned, because the work starts at the margin. Prose keeps a **68ch**
measure (down from 80). Code, tables and figures use the full column, up to `--page-max`. Per-item facts
(`n of m read`, the practice count) are quiet, right-aligned text on the item's own line.

**A unit page, wide (72rem and up):**

```
┌────────────────────────┬┊──────────────────────────────────────────────────────────┐
│ ISO-8583 for Visa…     │┊  Client implementation                                    │  trail: quiet, above the title
│                        │┊  ISO-8583 message creation                                │  h1, Andika, heaviest
│ Fundamentals   16/16 ▸ │┊  Unit 2 of 11 in Client implementation                    │  one quiet line, no dots
│ ─────────────────────  │┊                                                           │
│ Client impl.    1/11 ▾ │┊  On this page                                             │  outline: plain list, no card
│ ▪ 1 Basic setup        │┊    2.1 ISOMsg   2.2 Message factory   2.3 …               │
│ ▣ 2 Message creation   │┊                                                           │  ▣ = here (accent wash)
│ □ 3 Channel manage…    │┊▌ Prose at 68ch in Charis …                                │  ▌ narration cue at rest
│ □ 4 …                  │┊  ┌ java ──────────────────────────────── Copy code ┐       │  code: squared, no border
│ Server impl.    0/11 ▸ │┊  └──────────────────────────────────────────────────┘       │
│ (sticky, scrolls)      │┊  Practices still to come                                  │  a pencilled note
│                        │┊  [ Mark as read ]  Your ticks stay in this browser.      │
│                        │┊         ┌─ Unit 3 ─┐                                      │  the tab on the slip's top edge
│                        │┊  ┌──────┘          └──────────────────────────────────┐   │
│                        │┊  │ Up next in Client implementation                    │   │  THE ONE SATURATED ELEMENT
│                        │┊  │ Channel management              [ Open unit 3 ]     │   │  --sign ground, --sign-ink
│                        │┊  └─────────────────────────────────────────────────────┘   │
│                        │┊  Previous: Basic setup                  Course contents   │  quiet, one line
└────────────────────────┴┊──────────────────────────────────────────────────────────┘
                          ┊ [▶ Play narration] ‹ ›  1×   2.1 ISOMsg     Passage 3 of 21   one row, sticky
```

(`▪` read, `▣` here, `□` not read, `┊` the pale margin rule.) When the next unit is also read, the slip
names the first unread unit instead, with "Up next" unchanged. When everything is read, the slip says
"You have read every unit" and links to the contents. It never names a unit the reader has finished.

**A unit page at phone width (about 400px):** the rail folds into one closed disclosure. The rule sits in
the gutter and the text starts 1.5rem in.

```
┊ Client implementation
┊ ISO-8583 message
┊ creation                   ← balanced
┊ Unit 2 of 11
┊ ▸ Units in this course 1/11 ← one closed line (the script closes it; with no script it stays open)
┊ On this page …
┊ Prose …
┊ ┌ Unit 3 ┐
┊ │ Up next: Channel management  [Open] │
┊[▶ Play] ‹ › 1×   3 of 21    ← about 3.5rem, no keyboard sentence on touch screens
```

**The root index:**

```
┊ ISO-8583 for Visa and Mastercard transactions                              ← heavy title
┊ This is a study site for the material below: read and hear each unit in order, and tick it off.
┊ ─────────────────────────────────────────────────────────────────────────────────────────────
┊ Where it comes from          How it is ordered             How to use it
┊ (the corpus's source,        (in the order the author      1. Open the unit under Up next.
┊  from manifest data, D5)      arranged it)                  2. Tick it when you finish.
┊                                                             3. Ticks stay in this browser.
┊ 5 of 38 units read                                                              33 to go
┊ [■■■■■□□□□□□□□□□□][▢□□□□□□□□□□][□□□□□□□□□□□]     ← segments sized by unit count;
┊  Fundamentals       Client impl.   Server impl.         next container outlined in the accent
┊         ┌─ Unit 3 ─┐
┊ ┌───────┘          └────────────────────────────────────────────┐
┊ │ Up next in Client implementation                               │
┊ │ Channel management                      [ Open unit ] [ Show in list ] │
┊ └────────────────────────────────────────────────────────────────┘
┊ [ Filter units…                               ] [Expand all] [Collapse all]
┊ 1  Fundamentals                                            16 of 16 read ▸
┊ 2  Client implementation                                    1 of 11 read ▾
┊    □ 1 Basic setup … ▪   (units on one feint line, tick boxes, facts right-aligned)
┊ 3  Server implementation                                    0 of 11 read ▸
```

Containers are numbered **only because their order is the author's order**. Only the container holding
the next unit is open.

---

## 7. The one bold element (§1.3)

⭐ **The "Up next" slip.** It is the label on the next exercise book in the pile: a block of washable-blue
ground with paper-coloured Andika words, a **tab on its top edge** carrying the next unit's number
("Unit 3"), the container it is in, the unit's title, and one primary button, "Open unit 3". It
appears **once per page**: at the foot of a unit page, and under the progress strip on the index and on
a container page. ⛔ **It is the only filled area of saturated colour anywhere on the site.** Everything
around it is ink, pencil and feint ruling.

It holds the page's single most important fact for a returning reader: **where to pick up**. It is
computed at read time from the reader's own ticks (`study-progress.js` already keeps them), so the
generated page is byte-identical whoever opens it (R10). **With no script**, it names the unit the
page's own "next" link names (the build already knows that), and the index shows the course's first unit.
The row's R8 floor holds.

**The margin rule stays, demoted to structure.** It is a pale line and never a signal (§4).

**Radius and motion tokens (new), named by job as the reference names them:** `--radius-tight: 2px`
(code, tick boxes, focus ring), `--radius-control: 4px` (buttons, the filter field),
`--radius-sign: 10px` (the slip and its tab, and nothing else). `--dur-quick: 120ms` (a tick box's
fill), `--dur-pop: 300ms` (a box when you tick it), `--dur-fill: 350ms` (progress rules),
`--ease: cubic-bezier(.2,.7,.2,1)`.
⭐ **No load animation.** The reference spends its one load moment laying its road, which is its subject.
A study site opened ten times a day should not perform. **The one motion answers an action**: the tick
box pops (scale) and fills (opacity) when a unit is marked read, and the progress rules fill to the new
value. The animation is removed when it ends, so the resting state never depends on it, and it is off
entirely under `prefers-reduced-motion` (the reference's rule: `animation: none; transition: none`).

---

## 8. The plan read against every tell in §2, and what each one changed

| Tell | Where the plan stood before review | Revision, and why |
|---|---|---|
| Warm cream + serif display + terracotta | The first idea was "paper", which slides toward cream | Paper is **`#f1f5f2`, a cool green-white** (hue about 135°, not the 30–45° of cream). Headings are **sans** (Andika), not serif display. The accent is **blue ink**, not terracotta. |
| Near-black + one acid accent | The current dark theme (C6) | Dark is a **mid-dark blackboard `#26322c`** with a chalk palette, and it has no hot accent. |
| Purple-to-blue gradients | none | No gradients anywhere, and none are possible: every colour is a flat token. |
| **Cool slate / blue-grey + teal + amber** | ⚠️ The first blackboard draft was a blue-grey "slate". The pending panel was teal and the progress fill amber (P3, N6). | The board was pushed to a **green** hue so it cannot read as slate. **Teal is removed** (practices are written in pencil). **Amber is removed** (progress is ink blue, the highlighter is a yellow that appears only while speaking). The ink neutrals carry some blue, but with no teal and no amber the rejected triple is not present. |
| A saturated colour as the page ground | ⚠️ **The first committed draft of this plan** (`740f13e`) put saturation on a crimson margin rule on every page **and** on every tick, **and** used the accent for every link. That is three saturated uses. | Revised against the reference's judgement: saturation is on **one element, the Up next slip**. The accent means **next and here only**. The margin rule is pale. Ticks are ink. Links are ink. |
| SaaS card kit | Rail, outline, code, disclosure, read mark and practices were all cards (R1, O1, K2, C4, RM1, P1) | **No cards.** The rail and outline are plain lists on the ground. Code keeps a ground of its own (it is a different kind of text) with squared corners and no border. Practices and the read mark become notes in the column. The slip is **one** sign, not a card: it has its own radius token, which nothing else uses, and it never nests. |
| Pill tags in several accent colours | Level chips and ordinal chips (R3, R4) | Level words are **not shown** in the rail or the trail, where indentation already says the depth. Ordinals are **plain tabular numerals in a fixed column**. A category, if one is ever keyed, is a dot plus a word (the reference's rule). |
| ALL-CAPS tracked eyebrows | Masthead meta (M1), `CONTENTS` (O2) | Sentence case, no tracking. The outline's label is "On this page". The slip's "Up next in Client implementation" is a sentence-case lead line, as in the reference. |
| Meta joined with middle dots | Masthead (M2), player (N4), practices (P2) | The player's dot is removed (layout gap, not a glyph). The unit line becomes a sentence. The Python-built dots are D2. |
| `WORD — fragment` labels | none in the plan | The slip and the bar use sentences ("Up next in …", "Previous: Basic setup"), not a dash construction. |
| `→` on buttons and links | B1, N2 | Removed. The player's previous and next are icon buttons with `aria-label` and `aria-hidden` glyphs. The slip's button says what it does: "Open unit 3". |
| Monospace for small data labels | none today (the caption is in the UI face) | Kept that way: the mono face is for code only. Counters are Andika with `tabular-nums`. |
| Coloured stripe down a card's left edge | Practices (P1), narration gap (N7) | Both removed. The pale margin rule is page-length and on no card. A blockquote keeps a grey rule, which is the quote convention and is not coloured. |
| Inter, Roboto, Open Sans, Lato, Arial, a bare system stack | The current stacks name Roboto and Arial (M4) | Three vendored OFL faces, each with a subject reason, and Overpass deliberately not taken from the reference. The fallbacks name none of the banned faces. |
| Decoration without meaning; numbered markers on a non-sequence | Ordinal chips | Numbers only where order is real (containers and units in the author's order). The outline's numbers are the corpus's own text. |
| Labels that stop being true | `prose`, `archived`, `group` (M3, P2, R3) | Removed from what the surface controls, and the rest is D2. "More to come" becomes "Practices still to come". ⭐ **The slip can never name a unit already read.** It is computed from the ticks, which is the reference's "Up next" rule. |

**Pre-flight §6, answered for the plan:** (2) If the name were swapped, this could still only be a place
where somebody works through a course on their own: the tick boxes, the next-exercise slip and the
literacy faces all say so. (3) On the index the resume point is the first thing below the progress
line. On a unit page, the lesson comes first and then the slip. (4) The cut includes the chips, the
cards, three of the four storage sentences, the keyboard sentence on touch screens, the level words, and
the meta's builder words where the surface allows. That is well past 30% of the chrome.

---

## 9. UX and accessibility fixes from §3 that the build will make, each tied to a flaw

| Fix | Flaws |
|---|---|
| `pre` carries the code font-size and line-height, so code is single-spaced | K1 |
| Trail moves above the title inside `<header>`, and the long root crumb is truncated with an ellipsis and a `title` | M5, M6 |
| Heading scale 2.5 / 1.6 / 1.2rem, heavy Andika over Charis 400, `text-wrap: balance` | M7, I6 |
| Rail: plain list, inline disclosure marker, no chips, ordinals in a column, tick boxes on one feint line, `n of m read` per container with a thin rule, current unit in the accent wash, next unit outlined in the accent | R1–R4, R6 |
| Phone: the rail is wrapped in one `<details>` that the page script closes below 72rem; with no script it stays open | R5, M7 |
| Outline: plain list headed "On this page", unlined ink links that underline on hover or focus | O1–O4 |
| No lit passage at rest: at rest the cue is a highlighter mark left of the rule, and the wash appears only while playing (`body:has(#play [data-state=playing]:not([hidden]))`, no script change) | C3 |
| Measure 68ch | C2 |
| Player: one row, column width, Play is the primary button, icon previous/next with `aria-label`, `Passage 3 of 21` in tabular numerals, keyboard sentence hidden on `(hover: none)`, track 3px in the accent, `--player-height` 3.5rem | N1–N6 |
| Narration gap: a note with no stripe, one sentence | N7 |
| **The Up next slip** at the foot of a unit page (it is the between-pages bar's "next", promoted), then a quiet line with "Previous: …" and "Course contents" | B1–B4 |
| Practices: a pencilled note headed "Practices still to come" | P1, P3, P4 |
| Read mark: two controls, "Mark as read" and, once marked, "Unmark" with the line "You marked this read." One line about storage. The tick box pops once. | RM1, RM2 |
| **Moving the reader on:** marking a unit read updates the slip, fills the rail's box, and scrolls the slip into view. Focus is not moved. | §3 "move them on" |
| **Index:** heavy title, one paragraph, three columns, a progress line with the remainder right-aligned, the segmented strip as navigation, the slip, a filter that narrows rows as you type and says how many match (`role="status"`, Esc clears and restores the prior open state, placeholder ending in `…`, `name`, `autocomplete="off"`, `spellcheck="false"`), then Expand all and Collapse all as two buttons, with only the next unit's container open | I1–I4 |
| Container page: the same progress line, strip segment and rows for its own units; the slip when a next unit exists | CP2 |
| Skip link `Skip to the unit` (index: `Skip to the course`) as the first focusable element (`body > a[href="#content"]`, no new class or hook) | G1 |
| `<meta name="theme-color">` for each scheme, and a test asserting it equals `--bg` | G2 |
| `html { scroll-padding-top: 1.5rem; scroll-padding-bottom: calc(var(--player-height) + 1rem) }` | G3 |
| Tokens redefined under `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` and under `:root[data-theme="dark"]`, with no toggle UI in this row | G4, C6 |
| `touch-action: manipulation` on buttons; `:focus-visible` in the accent, 2px, offset 2px, `--radius-tight` | §3 |
| Copy button says "Copy code"; the fallback says "Press Ctrl+C", or "⌘C" only on a Mac | K4 |
| Backing up ticks (export and import) is **not** in this row: it is new state machinery. It is named in D6 as the next row, with the undo a restore needs. | §4 "offer export/import" |

⛔ **Acceptance (§1.5, §6, clause 6) is the same survey run again on the build:** the same ISO pages and
fixtures, light, dark, 1280 and 400, critiqued, and the critique's fixes made. Controls are verified by
behaviour: tick a unit, reload, and see the slip, the box and the strip move (§1.6). **Clause 7** is
asserted both ways in stage 2: a planted banned face, a planted raw colour, a planted sub-4.5 pair, a
planted ALL-CAPS tracked rule, a planted middle-dot `content`, and **a second filled `--sign` area** each
go RED by name.

---

## 10. Decisions the register must make before stage 2

- **D1 (the surface is too narrow for four of the fixes).** ⛔ All four need files outside
  `render/assets/` and `render/templates/`:
  - **(a) Fonts:** `pageassets/source.py` reads parts as UTF-8 text only (`PART_SUFFIXES = (".css",
    ".js", ".svg")`), and `bundle.written_files()` is `str → str`. A `.woff2` cannot reach the site
    without touching `pageassets`.
  - **(b) The R11 split of `chrome.css`** (G5) changes `bundle.STYLE_PARTS`.
  - **(c) The page's new behaviour** (folding the rail on a phone, the Up next slip, the strip, the
    filter, Expand all and Collapse all) is one new part, `progress-view.js`, beside `study-progress.js`
    whose store it reads. It is listed in `bundle.SCRIPT_PARTS`.
  - **(d) The index's and a container page's new markup** (the framing block, the progress line, the
    strip, the slip's no-script default, the filter) is emitted by `render/index/` and
    `render/container/`. The strip's sizes are unit counts the build already knows, so they are written
    into the page and never computed at read time.

  ⭐ **Asked for:** `src/studyforge/render/pageassets/bundle.py` and `source.py`, the index and container
  renderers' document modules, and their tests.
- **D2 (words built in Python):** the middle dot (`META_SEPARATOR`), the meta's builder words
  (`variant`, the address slug) and `archived` are written in `render/page/document.py` and
  `render/container/document.py`. Either widen the surface to those two constants and sentences, or keep
  them as findings for a follow-up row. **The recommendation is to widen**: M2, M3, CP1 and P2 are tells
  the row's clause 2 says are gone "from every generated page", and CSS cannot remove them.
- **D3 (how the faces reach the page).**
  - **(a) Relative files** (the row's wording): copy the `.woff2` beside `page.css` and load them with
    `url("fonts/…")`. Chrome 149 loads a font from a parent directory over `file://` (**measured** here
    with a probe page). ⚠️ **Firefox was not measurable on this host** (its sandboxed package cannot read
    the scratch directory). The recollection, **not a measurement**, is that Firefox 68+ treats each
    `file://` document as its own origin and refuses cross-origin `@font-face` from it, which would break
    R8's floor in Firefox.
  - **(b) Inline:** the bundle composes the pinned `.woff2` bytes into `page.css` as base64 `data:` URIs
    at build time. The brief's own §4 says "fonts embedded as base64", and it works in every engine from
    `file://`. The cost is a `page.css` about a third larger than the fonts.

  **Recommendation: (b), with the vendored `.woff2` as the single pinned source**, *if* the register can
  confirm the Firefox behaviour. The reference page takes the same route: it embeds a Latin subset of its
  OFL face as base64, with the licence named in a comment beside it. Either way, if the fetched sizes are large, a Latin subset is allowed
  under OFL as long as no Reserved Font Name applies (the register reads each `OFL.txt`). Subsetting
  needs `fontTools`, which is a one-time register-side tool and never framework source.
- **D4 (reopening the measure):** `chrome.css` records `PO-22/6`'s "80 characters … is not reopened". The
  brief (the user's direction, round 118) asks for 65–70. **The plan uses 68ch.** Confirm that the brief
  overrides the older decision.
- **D5 (the index's three columns, I1):** *How to use it* and *How it is ordered* are about the **site**,
  never the material, so the framework may write them and R1 holds. ⛔ *Where it comes from* is the
  corpus's own fact (its source, its author, a link). The framework must not invent it. Either it reads a
  manifest field that already exists, or the column is **omitted** until `W363`'s manifest data carries
  one. ⭐ **The recommendation is to omit it in this row and never guess it.** Confirm.
- **D6 (scope, if the build must be smaller):** the plan grew when it was read against the reference (§12).
  The first cuts, in order, would be the filter, then Expand all and Collapse all, then the strip's
  navigation (it stays as a picture), then the tick's motion. ⛔ **The slip, the progress line and the
  tick boxes are not cuttable**: they are the plan's answer to "what the reader needs first". Export and
  import of ticks (brief §4) is proposed as **its own next row**, with the undo a restore needs, and is not
  in this one.
- **D7 (the slip's hue):** the plan uses one hue for "next" and for the slip, and tells them apart by form
  (a line or a ring, against the only filled area). If the register wants the reference's two-colour
  split, the second colour must still come from the exercise book. The only candidate is the margin red,
  and it reads as an error on a "next" sign, so it is **not recommended**.
- **D8 (the mono face):** vendor JetBrains Mono, or keep code on a system mono stack. Keeping it would
  leave one "bare system stack as the chosen face". **The recommendation is to vendor it.**

## 11. Findings (outside the plan's surface; not fixed)

- **W362-plan/1:** `FND-01`'s size gate reads `*.py` only (`tools/quality/config.python_files`), so
  `chrome.css` reached 748 lines with no R11 justification and nothing failed.
- **W362-plan/2:** `copy-code.js` tells every non-Mac reader to "Press ⌘C" (K4). It is inside the build's
  surface and is listed here only because it is a defect today.
- **W362-plan/3:** the middle-dot separator and the word `archived` are generated in
  `render/page/document.py` and `render/container/document.py` (D2), so a CSS-only identity row cannot
  meet its own clause 2.

---

## 12. Read against the reference page (the method, not the look)

The register shared the finished page the brief's worked example describes, as a reference for quality.
Its road imagery belongs to its own subject and **none of it is copied**: not its face, its colours, its
ring markers or its words. What was translated is the judgement:

| The reference's judgement | Its studyforge equivalent in this plan |
|---|---|
| A mid-dark ground with a hue, off-white ink | The blackboard `#26322c` with chalk `#eef0e8` (dark), and the cool exercise paper (light) |
| One accent, used only for "next" and "where you are" | Washable blue: the next unit, the current unit, the current container's segment, focus. Nothing else. |
| Saturation on exactly one element, with a tab on its top edge | The Up next slip, with "Unit 3" on its tab |
| One family with 800 against 400 | Two literacy faces from one foundry, with weight and family contrast (§5) |
| A heavy title, one plain paragraph, three short columns | The same order on the root index; the column headings are the site's questions, not the corpus's |
| A progress line with the remaining work right-aligned | `5 of 38 units read` … `33 to go` |
| A segmented strip sized by real work, doubling as navigation | Segments sized by each container's unit count, each a link to its group |
| Filter, plus Expand all and Collapse all as two buttons | The same on the index |
| Numbered phases only because the order is real, `n of m done` and a thin rule, only the current one open | Containers in the author's order, `n of m read`, only the next unit's container open |
| Items on a line with markers: solid once done, accent for next; quiet facts right-aligned | Tick boxes on one feint line: solid ink once read, accent outline for next; the practice count right-aligned |
| Role-named tokens, radius and motion tokens, one easing, reduced motion removes all motion | §4 and §7, with the existing names kept and the role names mapped |

