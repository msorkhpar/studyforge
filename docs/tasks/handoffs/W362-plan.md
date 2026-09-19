# W362 — the design plan (stage 1 of 2)

**Kind:** survey

**Document kind: `survey`.** ⛔ **Not the task handoff.** It is stage 1 of [`W362`](../rows/W362.md): the
design plan the row's clause 1 requires **before any code**, written for the register to read before the
build is dispatched. Nothing under `src/` changed. The build's own handoff is `W362.md`, written in stage 2.

⭐ **The authority is [the UI design brief](../../conventions/ui-design.md)**. Every section below
answers one of its clauses, and §8 reads the plan against every tell in its §2.

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
| **The margin rule**, a red line down every page. Left of it is yours (numbers, ticks, notes); right of it is the work. | The page divides the same way: the reader's course, their ticks and where the narration is, left of the line; the unit's material, right of it. |
| **Feint ruling**, pale blue lines that separate without shouting. | Every hairline divider: list rows, the table grid, the between-pages rule. |
| **Blue-black ink** for the writing. | The text colour. The neutrals take its blue, so they read as chosen. |
| **Washable royal-blue ink**, the pen you write with. | Links and the next thing to do: the accent. |
| **The marker's tick in red pen.** | The read mark. |
| **The highlighter** swiped over the line you are on. | The narration highlight, and only while it is speaking. |
| **Pencil.** | Muted and secondary text. |
| **Exercise numbers in the margin.** | Unit ordinals in a fixed column, as plain numerals and never chips. |

**The dark theme is the same classroom's other surface, the blackboard.** It has a green-black board,
chalk writing, chalk dust for the quiet text, blue chalk for links, red chalk for the margin and the
ticks, and yellow chalk for the highlight. This is a real mid-dark with a character, not a tinted
near-black.

---

## 4. Colour (§1.3), both themes, by role

⭐ **Both themes are designed, not one of them plus an inversion.** The reason is that this page is read
for hours, often in the evening. Dropping the dark theme would take away something readers of this site
already have. Each theme is a real surface from the same room.

⛔ **Every existing token NAME is kept** (`SF-22` paints with them in parallel). Only values change, and
new tokens are added. The roles below map onto the existing names.

| Role | Existing token | Light: exercise book | Dark: blackboard |
|---|---|---|---|
| Ground, paper / board | `--bg` | `#f1f5f2` exercise paper (a cool green-white, not cream) | `#26322c` blackboard |
| Raised sheet (disclosure, caption, panel) | `--surface`, `--panel` | `#fbfcf9` | `#2e3b34` |
| Chrome ground (row hover, current row) | `--surface-2` | `#e4ebe7` | `#34433b` |
| Ink | `--fg` | `#1b2236` blue-black | `#eef0e8` chalk |
| Soft ink | `--fg-soft` | `#3a4257` | `#d3d8cd` |
| Pencil (muted) | `--muted` | `#586070` graphite | `#aab4a9` chalk dust |
| Feint ruling | `--rule` | `#c6d3de` | `#43534a` |
| Ruling, strong (control borders) | `--rule-strong` | `#72889d` | `#788c7f` |
| Accent, the pen (links, next, focus) | `--accent`, `--focus` | `#23449a` washable blue | `#a9c8ff` blue chalk |
| Accent ground | `--accent-soft` | `#e2e8f4` | `#34433b` |
| Practices, now written in pencil and no longer teal | `--practice` / `--practice-soft` | `#3a4257` / `#e4ebe7` | `#d3d8cd` / `#34433b` |
| Code ground / code ink | `--code-bg` / `--code-fg` | `#e8eee9` / `#1b2236` | `#1f2a25` / `#e6e9e1` |
| Highlighter (spoken passage) | `--hl-bg` / `--hl-fg` | `#fbef7a` / `#1b2236` | `#4f4b1f` / `#fffbe3` |
| Narration progress | `--hl-bar` | `#23449a` | `#a9c8ff` |
| **New: the margin rule** | `--margin` | `#c42d43` margin red | `#f08a8f` red chalk |
| **New: done (the tick)** | `--done` | `#c42d43` | `#f08a8f` |

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
| `--practice` on `--practice-soft` | 8.27 | 7.19 | 4.5 |
| `--code-fg` on `--code-bg` | 13.43 | 12.08 | 4.5 |
| the seven tokens on `--code-bg`, lowest of the seven | 4.99 (comment) | 5.81 (comment) | 4.5 |
| `--hl-fg` on `--hl-bg` | 13.34 | 8.55 | 4.5 |
| `--fg` / `--muted` on `--panel` | 15.35 / 6.14 | 10.20 / 5.48 | 4.5 |
| `--margin` and `--done` on `--bg` (marks) | 5.02 | 5.55 | 3 |
| `--rule-strong` on `--bg` (control borders) | 3.33 | 3.72 | 3 |
| `--hl-bar` on `--surface-2` (the progress fill) | 7.33 | 6.16 | 3 |
| `--focus` on `--bg` (the ring) | 8.07 | 7.87 | 3 |

⚠️ **The link colour against body ink is 1.78:1 in light**, so a link in running text **keeps its
underline**. Colour alone does not mark it.

---

## 5. Type (§1.3), three faces, all SIL OFL, from the world of learning to read

⭐ **Two of the three come from SIL's literacy work: faces drawn for people learning to read.** The
subject every studyforge site shares is learning, and neither face is on any "modern and clean" list.

| Role | Face | Why this one |
|---|---|---|
| Prose | **Charis** (SIL), 400, italic, 700, bold italic | Drawn for long-form reading and literacy publishing, on the Bitstream Charter design the current stack already reaches for. It has sturdy serifs and clear letterforms, and it holds up at body size on an ordinary screen. |
| Headings, rail, trail, controls, captions | **Andika** (SIL), 400 and 700 | A sans drawn **for beginning readers**: `I`, `l` and `1` cannot be confused, and the letterforms are plain. It is the wayfinding voice of the page. It is clearly distinct from Charis, so two families is justified. |
| Code | **JetBrains Mono**, 400, italic, 700 | Code is the material's own instrument, and in these corpora its content is things like `"4111111111111111"`, `"0200"` and field numbers, where 0/O and 1/l/I must not be mistaken. It is used for code only. ⛔ **It is never used for small data labels** (a tell). |

**The scale has real jumps and weight contrast across families.** h1 is Andika 700 at 2.5rem, h2 Andika
700 at 1.6rem, and h3 Andika 700 at 1.2rem. Body is Charis 400 at 1.1875rem/1.65. UI text is Andika 400 at
0.95rem. `text-wrap: balance` goes on headings, `tabular-nums` on every ordinal and counter, and sentence
case everywhere.

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
   `Andika-6.200/web/Andika-Regular.woff2`, `Andika-Bold.woff2`, and `Andika-6.200/OFL.txt`.
3. **JetBrains Mono 2.304**:
   `https://github.com/JetBrains/JetBrainsMono/releases/download/v2.304/JetBrainsMono-2.304.zip`. Files:
   `fonts/webfonts/JetBrainsMono-Regular.woff2`, `JetBrainsMono-Italic.woff2`,
   `JetBrainsMono-Bold.woff2`, and `OFL.txt`.

⚠️ **Size is unknown until the files are fetched.** The SIL faces cover Latin, Greek and Cyrillic and may
be large. See decision D3.

**Fallbacks** follow each vendored family with no banned face in them: `"Charis", Georgia, serif`;
`"Andika", Verdana, sans-serif`; `"JetBrains Mono", "DejaVu Sans Mono", monospace`.

---

## 6. Layout (§1.3)

The reading column is **left-aligned against the margin rule**, because in an exercise book the work
starts at the margin. Prose keeps a **68ch** measure (down from 80). Code, tables and figures use the
full column, up to `--page-max`. Secondary facts share a line with the thing they describe and are
right-aligned. On a wide screen the rail keeps the left edge, as `W325` put it, and the margin rule runs
down the whole page between the rail and the work.

**A unit page, wide (72rem and up):**

```
┌────────────────────┬┃───────────────────────────────────────────────────────────┐
│ ISO-8583 for Visa… │┃  Client implementation                                     │  trail: quiet, above the title
│                    │┃  ISO-8583 message creation                                 │  h1, Andika 700
│ Fundamentals       │┃  Unit 2 of 11                                  jpos-client │  meta, quiet, facts on one line
│ Client impl.       │┃                                                            │
│   1 Basic setup  ✓ │┃  On this page                                              │  outline: plain list, no card
│ ▸ 2 Message crea…  │┃    2.1 ISOMsg  2.2 Message factory  2.3 …                  │
│   3 Channel man…   │┃                                                            │
│   …                │┃▌ 2. ISO-8583 message creation                              │  ▌ narration cue at rest: a
│ Server impl.       │┃  Prose at 68ch in Charis …                                 │    highlighter mark left of the rule
│                    │┃  ┌ java ─────────────────────────────────── Copy code ┐    │  code: squared corners, no border
│  (sticky, scrolls  │┃  │ public class ISOMessageCreator {                    │    │
│   itself)          │┃  └─────────────────────────────────────────────────────┘    │
│                    │┃  Practices still to come                                   │  a pencilled note, no panel
│                  ✓ │┃  [ Mark as read ]   Your ticks stay in this browser.       │  the tick lands left of the rule
│                    │┃  ───────────────────────────────────────── feint rule ──   │
│                    │┃  Previous                             Next                 │
│                    │┃  Basic setup                  Channel management  (large)  │
└────────────────────┴┃───────────────────────────────────────────────────────────┘
                      ┃ [▶ Play narration] ‹ ›  1×   2.1 ISOMsg        Passage 3 of 21   one row, sticky, column width
```

**A unit page at phone width (about 400px):** the rail folds into one closed disclosure. The rule sits in
the gutter and the text starts 1.5rem in.

```
┃ Client implementation
┃ ISO-8583 message
┃ creation                  ← balanced
┃ Unit 2 of 11
┃ ▸ Units in this course    ← one closed line (JS closes it; with no script it stays open, as today)
┃ On this page …
┃ Prose …
┃──────────────────────────
┃[▶ Play] ‹ › 1×   3 of 21   ← about 3.5rem, no keyboard sentence on touch screens
```

**The root index:** a short "what this is and how to use it" block, then one line of progress with the
next unread unit named, then the course. Only the group that holds the next unread unit is open, and two
buttons, **Expand all** and **Collapse all**, do one thing each.

```
┃ ISO-8583 for Visa and Mastercard transactions
┃ Read the units in order; tick each one when you finish it. Ticks stay in this browser.
┃ 5 of 38 units ticked. Next: Transaction flow                         [Expand all] [Collapse all]
┃ ▾ Fundamentals
┃   1 ┃ Introduction to ISO-8583                                   ✓   ← ordinals in a fixed column,
┃   2 ┃ ISO-8583 message structure                                 ✓     ticks right-aligned
┃ ▸ Client implementation
┃ ▸ jPOS server implementation
```

---

## 7. The one bold element (§1.3)

⭐ **The margin rule.** One 2px line in margin red runs the full height of every page, drawn once by a
single pseudo-element on `body`, with no markup. Everything that belongs to the reader sits left of it:
the course rail, their ticks, and the highlighter mark showing where the narration is paused. Everything
that belongs to the material sits right of it. It is the only saturated colour on a resting page.
The tick uses the same red pen, because in an exercise book the marker's tick and the margin are the same
ink. The highlighter yellow appears only while narration is speaking.

It encodes information rather than decorating the page. It tells the reader, without a legend, which
marks are theirs and which words are the author's. That is the distinction `read-mark.js` already keeps
in storage: the mark is the reader's and never in the repository.

**Radius and motion tokens (new):** `--radius-tight: 2px` (code, inline code), `--radius-control: 4px`
(buttons, select), `--dur-quick: 120ms`, `--dur-settle: 220ms`, `--ease: cubic-bezier(.2,.7,.2,1)`.
⭐ **No load animation at all.** The one motion answers an action: the tick "inks in" (scale and
opacity) when a unit is marked read. The animation is removed when it finishes, so the resting state never
depends on it, and it is off under `prefers-reduced-motion`.

---

## 8. The plan read against every tell in §2, and what each one changed

| Tell | Where the plan stood before review | Revision, and why |
|---|---|---|
| Warm cream + serif display + terracotta | The first idea was "paper", which slides toward cream | Paper is **`#f1f5f2`, a cool green-white** (hue about 135°, not the 30–45° of cream). Headings are **sans** (Andika), not serif display. The accent is **blue ink**, not terracotta. The red is a crimson margin line, used as one mark and never as the accent. |
| Near-black + one acid accent | The current dark theme (C6) | Dark is a **mid-dark blackboard `#26322c`** with a chalk palette, and it has no single hot accent. |
| Purple-to-blue gradients | none | No gradients anywhere, and none are possible: every colour is a flat token. |
| **Cool slate / blue-grey + teal + amber** | ⚠️ The first blackboard draft was a blue-grey "slate". The pending panel was teal and the progress fill amber (P3, N6). | The board was pushed to a **green** hue so it cannot read as slate. **Teal is removed** (practices are written in pencil). **Amber is removed** (progress is ink blue, the highlighter is a yellow that appears only while speaking). The ink neutrals carry some blue, but with no teal and no amber the rejected triple is not present. |
| A saturated colour as the page ground | none | Saturated colour is on **one element** (the margin rule) plus the ticks in the same ink. |
| SaaS card kit | Rail, outline, code, disclosure, read mark and practices were all cards (R1, O1, K2, C4, RM1, P1) | **No cards.** The rail and outline are plain lists on the ground. Code keeps a ground of its own (it is a different kind of text) with squared corners and no border. Practices and the read mark become notes in the column. Radii are tokens and differ by job. |
| Pill tags in several accent colours | Level chips and ordinal chips (R3, R4) | Level words are **not shown** in the rail or the trail, where indentation already says the depth. Ordinals are **plain tabular numerals in a fixed column**. |
| ALL-CAPS tracked eyebrows | Masthead meta (M1), `CONTENTS` (O2) | Sentence case, no tracking. The outline's label is "On this page". |
| Meta joined with middle dots | Masthead (M2), player (N4), practices (P2) | The player's dot is removed (layout gap, not a glyph). The masthead and practices dots are built in Python **outside the surface**: decision D2. |
| `WORD — fragment` labels | none in the plan | The between-pages labels are two lines ("Next" over the title), not a dash construction. |
| `→` on buttons and links | B1, N2 | Removed. The player's previous and next are icon buttons with `aria-label` and `aria-hidden` glyphs, and the bar says "Previous" and "Next" in words. |
| Monospace for small data labels | none today (the caption is in the UI face) | Kept that way: the mono face is for code only. |
| Coloured stripe down a card's left edge | Practices (P1), narration gap (N7) | Both removed. ⚠️ **The margin rule is not this tell**: it is page-length, not on a card, and it separates the reader's side from the material's. A blockquote keeps a grey rule, which is the quote convention and is not coloured. |
| Inter, Roboto, Open Sans, Lato, Arial, a bare system stack | The current stacks name Roboto and Arial (M4) | Three vendored OFL faces, each with a subject reason. The fallbacks name none of the banned faces. |
| Decoration without meaning; numbered markers on a non-sequence | Ordinal chips | Ordinals stay **only where order is real** (units in a container). The outline's numbers are the corpus's own text. |
| Labels that stop being true | `prose`, `archived`, `group` (M3, P2, R3) | Removed from what the surface controls. The rest is D2. "More to come" becomes "Practices still to come". |

**Pre-flight §6, answered for the plan:** (2) If the name were swapped, this could still only be a place
where somebody works through a course on their own: the margin, the ticks and the literacy faces all say
so. (3) The unit title and the next unit are the largest things on the page. (4) The cut includes the
chips, the cards, three of the four storage sentences, the keyboard sentence on touch screens, the level
words, and the meta's builder words where the surface allows. That is well past 30% of the chrome.

---

## 9. UX and accessibility fixes from §3 that the build will make, each tied to a flaw

| Fix | Flaws |
|---|---|
| `pre` carries the code font-size and line-height, so code is single-spaced | K1 |
| Trail moves above the title inside `<header>`, and the long root crumb is truncated with an ellipsis and a `title` | M5, M6 |
| Heading scale 2.5 / 1.6 / 1.2rem, Andika 700 over Charis 400, `text-wrap: balance` | M7, I6 |
| Rail: plain list, inline disclosure marker, no chips, ordinals in a column, **ticks shown**, current row on `--surface-2` in bold | R1–R4, R6 |
| Phone: the rail is wrapped in one `<details>` that the page script closes below 72rem; with no script it stays open | R5, M7 |
| Outline: plain list headed "On this page", links not underlined until hover or focus (they are nav, not prose) | O1–O4 |
| No lit passage at rest: at rest the cue is a highlighter mark left of the rule, and the wash appears only while playing (`body:has(#play [data-state=playing]:not([hidden]))`, no script change) | C3 |
| Measure 68ch | C2 |
| Player: one row, column width, Play is the primary button, icon previous/next with `aria-label`, `Passage 3 of 21` in tabular numerals, keyboard sentence hidden on `(hover: none)`, track 3px in ink blue, `--player-height` 3.5rem | N1–N6 |
| Narration gap: a note with no stripe, one sentence | N7 |
| Between pages: "Previous" and "Next" as small sentence-case labels over the titles, next larger and right-aligned; up link "Course contents" | B1–B4 |
| Practices: a pencilled note headed "Practices still to come" | P1, P3, P4 |
| Read mark: two controls, "Mark as read" and, once marked, "Unmark" with the line "You marked this read." One line about storage. The tick inks in once. | RM1, RM2 |
| After marking read, the next-unit link is scrolled into view (focus is not moved) | §3 "move them on" |
| Index: short framing block, a `role="status"` progress line naming the next unread unit, only that group open, Expand all and Collapse all as two buttons | I1–I4 |
| Skip link `Skip to the unit` as the first focusable element (`body > a[href="#content"]`, no new class or hook) | G1 |
| `<meta name="theme-color">` for each scheme, and a test asserting it equals `--bg` | G2 |
| `html { scroll-padding-top: 1.5rem; scroll-padding-bottom: calc(var(--player-height) + 1rem) }` | G3 |
| Tokens redefined under `@media (prefers-color-scheme: dark) { :root:not([data-theme="light"]) }` and under `:root[data-theme="dark"]`, with no toggle UI in this row | G4, C6 |
| `touch-action: manipulation` on buttons; `:focus-visible` kept and re-coloured | §3 |
| Copy button says "Copy code"; the fallback says "Press Ctrl+C", or "⌘C" only on a Mac | K4 |

⛔ **Acceptance (§1.5, §6, clause 6) is the same survey run again on the build:** the same ISO pages and
fixtures, light, dark, 1280 and 400, critiqued, and the critique's fixes made. **Clause 7** is asserted
both ways in stage 2: a planted banned face, a planted raw colour, a planted sub-4.5 pair, a planted
ALL-CAPS tracked rule and a planted middle-dot `content` each go RED by name.

---

## 10. Decisions the register must make before stage 2

- **D1 (the surface is too narrow for three of the fixes).** ⛔ All three need files outside
  `render/assets/` and `render/templates/`:
  - **(a) Fonts:** `pageassets/source.py` reads parts as UTF-8 text only (`PART_SUFFIXES = (".css",
    ".js", ".svg")`), and `bundle.written_files()` is `str → str`. A `.woff2` cannot reach the site
    without touching `pageassets`.
  - **(b) The R11 split of `chrome.css`** (G5) changes `bundle.STYLE_PARTS`.
  - **(c) The phone rail's script** is either a new part (`bundle.SCRIPT_PARTS`) or has to live in an
    unrelated existing part.

  ⭐ **Asked for:** `src/studyforge/render/pageassets/bundle.py` and `source.py`, and their tests.
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
  confirm the Firefox behaviour. Either way, if the fetched sizes are large, a Latin subset is allowed
  under OFL as long as no Reserved Font Name applies (the register reads each `OFL.txt`). Subsetting
  needs `fontTools`, which is a one-time register-side tool and never framework source.
- **D4 (reopening the measure):** `chrome.css` records `PO-22/6`'s "80 characters … is not reopened". The
  brief (the user's direction, round 118) asks for 65–70. **The plan uses 68ch.** Confirm that the brief
  overrides the older decision.
- **D5 (index framing copy, I1):** a sentence written by the framework appears on every corpus's index.
  The plan's wording ("Read the units in order; tick each one when you finish it. Ticks stay in this
  browser.") is about the **site**, never the material, so R1 holds. It needs the index renderer to emit
  it, which falls under D1 or D2's widening. Confirm or cut.
- **D6 (scope, if the build must be smaller):** the first cuts, in order, would be the index's Expand all
  and Collapse all plus the progress line (I2, I4), then the tick's motion. Everything else answers a
  tell or a §3 rule the row lists as acceptance.
- **D7 (the mono face):** vendor JetBrains Mono, or keep code on a system mono stack. Keeping it would
  leave one "bare system stack as the chosen face". **The recommendation is to vendor it.**

## 11. Findings (outside the plan's surface; not fixed)

- **W362-plan/1:** `FND-01`'s size gate reads `*.py` only (`tools/quality/config.python_files`), so
  `chrome.css` reached 748 lines with no R11 justification and nothing failed.
- **W362-plan/2:** `copy-code.js` tells every non-Mac reader to "Press ⌘C" (K4). It is inside the build's
  surface and is listed here only because it is a defect today.
- **W362-plan/3:** the middle-dot separator and the word `archived` are generated in
  `render/page/document.py` and `render/container/document.py` (D2), so a CSS-only identity row cannot
  meet its own clause 2.
