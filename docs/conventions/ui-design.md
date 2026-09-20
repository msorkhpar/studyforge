# UI design — the brief every page this framework renders is designed against

⭐ **CARRIED, NOT CITED (R20).** This brief was written in the extraction source's pipeline documents and
is carried here whole, on the user's direction of 2026-09-18, so that no task in this repository ever has
to reach into a sibling for it. ⛔ **When this copy and any other disagree, this copy is the one a task
obeys.**

⭐ **How it lands in this repository — two rows, in order (the user's ruling, [round 118](../tasks/BOARD-ARCHIVE.md#po-round-118)):**

1. ⭐ `W362` — the **framework's own identity**: one look for every studyforge site, drawn from the
   subject every such site shares, with every tell in §2 removed and the interaction rules in §3 met.
2. ⭐ `W363` — a **per-corpus theme**, declared as manifest data (R19) and chosen by a skill from that
   corpus's own subject (§1.2), which the framework's identity is the default of. ⛔ **After `W362`.**

⚠️ **Three readings of the brief for this framework, so a taker does not re-derive them:**

- ⛔ **§4's *single portable file* is the reading floor, not a literal:** a generated page opens from
  `file://` with no network (R8), so a face is a vendored font file loaded by a relative `@font-face`,
  ⛔ **never a CDN**. ⭐ The files are fetched once, **pinned by sha256 with their licence beside them**,
  under the user's ruling at round 118 — ⛔ **SIL OFL faces only**.
- ⛔ **§3's *every colour a role-named token* is already this repository's rule** (`palette.css`,
  `test_palette`). ⭐ Keep the token NAMES a stylesheet already paints with — rename a role only in the
  row that also moves every reader of it.
- ⭐ **§1.5 and §6 are acceptance, not advice:** a screenshot of a REAL generated page, light and dark and
  at phone width, read and critiqued, and the contrast figures computed.

---

<ui_design_brief>

You are the design lead at a small studio known for giving every client a visual identity that could not
be mistaken for anyone else's. The client has already rejected work that looked templated. Make
deliberate, opinionated choices about palette, typography and layout that come from THIS subject, and
be able to say why each one belongs to it.

## 1. Process — follow in order

1. **Pin the subject.** One concrete subject, its audience, and the page's single job. If the brief does
   not say, propose them before designing.
2. **Find the subject's own world.** Its materials, instruments, signage, vocabulary. Distinctive choices
   come from there, not from "modern" or "clean". Example: a page tracking progress through an ordered
   course list became a *road route*: lane markings, stops, junctions, an exit sign, highway-sign type.
3. **Write a design plan before any code:**
   - Colour: 4–6 named hex values, each with a role (ground, surface, ink, muted ink, rule, accent,
     semantic states).
   - Type: the typefaces and their roles, and why they fit the subject.
   - Layout: one or two sentences, plus a rough ASCII wireframe; say what is left-aligned and why.
   - The one bold element: which single thing carries the identity.
4. **Review the plan against the tells in §2.** For every part that reads like a default you would
   produce for any similar page, revise it and state what changed and why. Only then build.
5. **Build, then look.** Screenshot the real rendered page (light and dark if both exist, and phone
   width ~400px), critique it, fix what it shows. One or two passes; stop there.
6. **Verify behaviour, not just looks.** Click the controls, reload, and check state persists. Report
   what you actually observed; never claim a thing works because the code looks right.

## 2. The tells — never use these unless the user explicitly asks

Each of these has been rejected, or is a recognised mark of generated design:

- **Palettes:** warm cream + serif display + terracotta accent; near-black + one acid-green or vermilion
  accent; purple-to-blue gradients; **cool slate/blue-grey + teal-green + amber** (the user's own
  rejection: "very generic and repetitive between the designs you always generate").
- **A saturated brand colour as the whole page ground.** A full guide-sign-green background was rejected
  outright. Saturated colour belongs on ONE element, never the page ground.
- **The SaaS card kit:** content chopped into identical rounded bordered cards, one radius on everything,
  the same soft grey shadow under each, cards inside cards.
- **Pill-shaped tags in several accent colours.** Show metadata as quiet text; a colour dot is enough to
  key a category.
- **Template chrome:** ALL-CAPS tracked eyebrow labels above headings; meta strings joined with middle
  dots (`A · B · C`); `WORD — fragment` labels; `→` appended to buttons and links; a monospace face for
  small data labels; a coloured stripe down the left edge of a card.
- **Typefaces:** Inter, Roboto, Open Sans, Lato, Arial, or a bare system stack as the chosen face.
- **Decoration without meaning:** gradient washes, numbered markers (01/02/03) on content that is not a
  sequence, badges and labels that tell the user nothing they need.
- **Labels that stop being true.** A "New" tag was removed because "everything is new for the user". A
  label must stay meaningful from the reader's side, not from the builder's history.

## 3. What to do instead

**Colour**
- Define every colour as a CSS custom property named by role (`--ground`, `--raised`, `--ink`,
  `--ink-soft`, `--ink-faint`, `--rule`, `--accent`/`--next`, semantic states), and use only tokens.
- One dominant ground, one sharp accent. Semantic colour (done, warning, error) is separate from the accent.
- Give neutrals a slight hue so they read as chosen. Avoid tinted near-black (`#0B0B0B`, `#111`) standing
  in for a dark ground; pick a real mid-dark with character (e.g. asphalt `#2b2e31`).
- **Compute contrast; do not eyeball it.** Body text ≥ 4.5:1 against its actual background, large text
  ≥ 3:1, non-text marks (dots, rings) ≥ 3:1. Report the numbers.
- Either design both light and dark themes properly (tokens redefined under
  `prefers-color-scheme: dark`, guarded by `:root:not([data-theme="light"])`, and again under
  `[data-theme="dark"]`), or commit to ONE look on purpose and set `color-scheme` to match. Never a
  half-done second theme.

**Typography**
- A typeface with a reason to be there (the route page used Overpass, modelled on US highway signage).
  One family is fine; two only if clearly distinct.
- Clear scale with real jumps; weight contrast (800 headings vs 400 body), not 400 vs 600.
- Running text ≤ ~65–70 characters; `text-wrap: balance` on headings; `tabular-nums` wherever digits
  line up. Sentence case everywhere.

**Layout and structure**
- Structure must encode information. Numbering only where order is real; borders and dividers only
  where they separate things that are actually separate.
- Spend boldness in one place (the route page: an "exit sign" naming the next course, with a tab on its
  top edge like "Exit 12"). Keep everything around it quiet.
- Hierarchy follows the user's priority: what they need first is biggest and highest.
- Use width when there is room (let the page grow; put secondary facts on the same line, right-aligned),
  but keep prose at a readable measure. Stack cleanly at phone width with a ≥16px gutter and no
  horizontal scroll.
- Tokens for radius (e.g. tight / control / sign) and motion (durations + one easing), not ad-hoc values.
- Check that shapes cannot be misread. A hollow square with a line through it read as a missing-font
  glyph; drawn markers must look intentional (solid, and layered above connecting lines).

**Motion**
- One orchestrated load moment at most (the route page's progress strip "lays itself out" left to
  right), plus motion that answers an action (a stop pops when marked done). No scattered fade-ups.
- Animate `transform`/`opacity` only. Honour `prefers-reduced-motion`. Never let an element's resting
  state depend on an animation having run: remove the animation afterwards so a stalled animation
  cannot leave content invisible.

**Interaction and UX**
- Show the page at rest in a realistic state; open the section the user is in, keep the rest collapsed
  if the list is long.
- Expand and collapse are TWO controls, each doing one thing, never one toggle whose label flips.
- After a user completes a section, move them on (close it, open the next, scroll to the next item).
- Search filters as you type; say how many results match; Esc clears it and restores the prior view.
- Destructive or bulk actions (restore, replace, delete) get an undo, not silence.
- Buttons say exactly what they do ("Back up progress", "Restore from backup", "Undo restore").

**Accessibility and web-interface rules**
- Visible `:focus-visible` everywhere; never remove an outline without a replacement.
- `<button>` for actions, `<a>` for navigation; icon-only buttons need `aria-label`; decorative glyphs
  get `aria-hidden="true"`; live messages (search results, notices) get `role="status"`.
- A skip link to the main content. Heading levels in order.
- Sticky headers must not cover what the user jumps or tabs to: `scroll-padding-top` on `html`.
- Inputs: `name`, `autocomplete="off"` for non-auth fields, `spellcheck="false"` where it misfires,
  placeholders ending in `…`.
- `<meta name="theme-color">`, `touch-action: manipulation` on buttons, no zoom blocking.

**Copy**
- Write from the user's side: what the page is, where its data came from, why it is arranged this way,
  how to use it, in plain short sentences. Credit the source and link to it.
- Active voice, sentence case, no filler, no selling. Errors say what happened and how to fix it.
  Empty states say what to do next.

## 4. Engineering rules that shaped the design

- **If asked for a single portable file, deliver exactly that.** All CSS, JS and data inline; fonts
  embedded as base64 `@font-face` (check the licence, e.g. SIL OFL, and note it in a comment) rather than
  loaded from a CDN; no network requests except the user's own outbound links.
- **Test the way the user will open it.** A file meant to be double-clicked must be tested from
  `file://`, not only through a local server. If you use a server for tooling, say so, stop it
  afterwards, and close any test tab so the user does not mistake a stale test copy for the real file.
- **Persisted state is verified, not assumed.** Read a `localStorage` write back; if it fails, show a
  visible warning. Offer export/import so state can survive a browser change. Say plainly where state
  lives and what erases it.
- **Keep generated output reproducible.** If a script builds the page, re-run it and confirm the output
  is byte-identical before calling a change done.
- **Never put the user's personal data anywhere**: no names, emails, account ids, hostnames or home
  paths in files, requests or published output. Use placeholders.

## 5. Third-party skills, plugins and scripts

Before adding any: read every file in a scratch folder; check `allowed-tools`; reject anything that runs
unpinned remote code (`npx -y …@latest`, `curl | sh`) or fetches its instructions live from a URL on
every run. Install only a pinned local copy with its source commit and sha256 recorded beside it, and
ask before changing the user's global configuration.

## 6. Pre-flight — answer each before you say "done"

1. Would a designer wince at contrast, alignment or hierarchy? (Check with numbers and a screenshot.)
2. If the logo were swapped, could this be any other product's page? If yes, the subject is not in it.
3. Does the most important thing for the user look most important?
4. What would you cut? Remove about 30%: explanatory text the UI already makes obvious, redundant
   labels, decoration without meaning.
5. Did you check it in the real rendered result, in the way the user will open it, and report what you
   saw rather than what you expected?

</ui_design_brief>

---

## ⛔ The rejected palettes, as a table an instrument reads

⛔ **§2's list of rejected palettes was right, was written before the work that broke it, and was
read by NOTHING.** ⚠️ **Measured, `W388/4`:** a repaint's first stage shipped the first half of
*warm cream + serif display + terracotta* and the user rejected it for exactly that reason. ⭐ **So
the tells that can be read off a colour are written below as DATA, and `tools/quality/palettes.py`
reads this table over the stylesheets this framework ships** — a rejected identity that returns is
a finding at the floor, by name, instead of a paragraph somebody was supposed to remember.

⚠️ **What a green floor here does NOT say.** The check reads COLOUR and nothing else: a serif
display face, the SaaS card kit, pill tags, an eyebrow label and a "New" badge are §2 tells that no
hue can see, and they stay the reader's judgement at §6. ⛔ **Green here means *no rejected PALETTE
is shipped*, never *§2 is met*.**

### How a row is read

⭐ **Every colour is read as three measures**, and every bound below is written in them: **hue** in
degrees, **chroma** as `max − min` of its channels over 255 in percent, and **light** as
`(max + min) / 2` over 255 in percent. ⛔ **Chroma and not HSL saturation, deliberately:** a
near-white paper with a one-step tint reports a saturation near 40% and a chroma near 3%, so a
bound written in saturation refuses the paper the user accepted.

⭐ **A row's parts are joined by `+`, and every part must hold IN ONE THEME** — light and dark are
read apart, each over the tokens it defines — with the parts on one role met by that theme's
colours for it. ⛔ **The conjunction is the whole instrument:** cool slate alone is what the user
ACCEPTED below, and it is the TRIPLE that was rejected. A row that fired on one part would refuse
the accepted identity on its first run.

| Role | Read from |
|---|---|
| `ground` | `--bg` |
| `raised` | `--surface`, `--surface-2`, `--panel` |
| `ink` | `--fg`, `--fg-soft`, `--muted` |
| `rule` | `--rule`, `--rule-strong` |
| `accent` | `--accent`, `--sign`, `--focus` |
| `gradient stop` | ⛔ no token — every colour inside ONE `linear-gradient(` or `radial-gradient(`, its `var()` resolved in that theme; a row's stop parts must meet in the SAME gradient |

| Rejected identity | Every part must be present | Why |
|---|---|---|
| Warm cream and terracotta | `ground: hue 20-70, light >= 85, chroma >= 3` + `accent: hue 5-32, chroma >= 25, light 25-65` | §2's first tell, and the one a repaint's first stage shipped |
| Near-black ground, acid-green accent | `ground: light <= 12` + `accent: hue 75-165, chroma >= 45` | §2's second tell; §3 asks for a real mid-dark with character instead of a tinted near-black |
| Near-black ground, vermilion accent | `ground: light <= 12` + `accent: hue 0-20, chroma >= 45` | the same tell's other accent |
| Cool slate with teal-green and amber | `ground: hue 190-250, chroma <= 20` + `accent: hue 150-190, chroma >= 20` + `accent: hue 35-60, chroma >= 30` | the user's own rejection — *"very generic and repetitive between the designs you always generate"*. ⛔ It is the TRIPLE: the slate is accepted below |
| A saturated brand colour as the page ground | `ground: chroma >= 30` | §2's third tell; a full guide-sign-green ground was rejected outright |
| A purple-to-blue gradient | `gradient stop: hue 258-300, chroma >= 20` + `gradient stop: hue 200-255, chroma >= 20` | §2's tell, read where a gradient actually is |

### ⭐ What the user ACCEPTED, 2026-09-19

⛔ **The rejected table is half of what a taker needs, and the other half is what the user said YES
to.** ⚠️ Without it the next repaint re-derives an identity from six refusals.

| Part | What was accepted |
|---|---|
| neutrals | a cool slate scale, ground through rule, in both themes |
| the accent | ONE loud accent, live where it means *next* or *you are here*, and nowhere else |
| green | ⛔ **none in the identity** — *"I am not a fan of green"* |
| themes | both, each designed, with the reader able to choose between them and the system |
| ink | the quieter inks in separate contrast bands — one band for all three is what *"too dim"* named |

⭐ **Two reference pages of the user's OWN were named as the standard**: their documentation
reference, for the slate scale and the ink bands, and their route planner, for the one loud accent
and the contrast it holds. ⛔ **Named in words and nothing else** — neither page's path, bytes,
palette nor screenshot enters this repository, so nothing here can go stale against them and a
taker who needs one asks the user for it.

⚠️ **The green bound is recorded here and is NOT read by the check above**, deliberately: it is a
per-token rule over the shipped palette, it belongs to the row that repaints the site (`W388`), and
a floor finding for a palette that is already being replaced on another branch would redden every
office's gate for a defect none of them could clear from its own.

---

## Worked example: the decisions behind the study-route page

For reference when judging a new UI. Each row is a decision and the reason it held.

| Decision | Why |
|---|---|
| Subject framed as a road route: courses are stops on a line, paths are junctions, the next course is an exit sign | The content really is an ordered journey; the metaphor encodes order, progress and "you are here" |
| Overpass typeface, embedded | Modelled on highway-sign lettering; embedded so the single file works offline |
| Asphalt ground `#2b2e31`, lane-paint white `#f1f2ee`, warning yellow `#ffc933` for the next course | Road materials. A slate/teal/amber palette was rejected as generic; a full sign-green ground was rejected as awful |
| Sign green `#0b5a3a` only on the exit sign | Saturated colour on the one element that matters, nowhere else |
| Dashed white line ahead, solid white behind | Road marking semantics make progress readable without a legend |
| Phase strip sized by course count, clickable | Progress bar and navigation in one, proportional to real work |
| Language shown as a coloured dot + word, level as plain text | Replaced pill tags, a recognised generated-design tell |
| Phases collapsed except the current one; expand all / collapse all as two buttons | A 353-row list is a wall; the user asked for the current phase to open by itself |
| Finishing a phase closes it and opens the next | The user expected to be moved on |
| Short "where it comes from / why this order / how to use it" block at the top | The user asked for provenance and purpose; kept to three short columns |
| "New" tag and one whole language path dropped | Labels and content that did not serve the reader were removed on request |

