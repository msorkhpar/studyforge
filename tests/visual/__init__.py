"""QA-03 — the visual and browser verification harness.

**What it does.** Opens a page this repository generated in a real browser over
`file://` and reads back what a unit test cannot see: the pixels, the computed
colours in both themes, the order focus moves in, what survives with scripts
off, and every request the page issued.

**How you use it.** The fixtures in `conftest.py` give a test a built site and a
tab. `discovery.require_browser()` is what makes a check skip — loudly, with the
remedy named — on a machine with no browser.

**Depends on.** The standard library, `pytest`, and `studyforge.render` for
building the pages it opens — through the same three fixture builders the
committed golden pages come from, never a second spelling of them (`site.py`).
⛔ **No driver library and no `pip install`** — `browser.py` says why.

## ⛔ What it opens, and why that is a sentence rather than an assumption (`W98`)

⚠️ **Until `W98` this harness wrote the two unit fixtures and nothing else,
rendered with `links=None`** — so of the six chrome regions `SF-34` rules, the
two it judged were the two that were already styled, and the between-units bar,
the practice panel, a container's unit listing and the root index's disclosure
tree were judged by nothing at all. ⛔ **Every check passed over that population
and none of them was skipped**, which is why the repair is a census with its own
negative control (`test_site.py`) rather than a wider list.

⭐ **The tree now carries every page kind the framework renders**, one subtree per
fixture corpus, and the region census is **derived from `SF-34`'s own disposition
table** — so a region added there is a red check here on the day it lands.

## ⛔ Why this exists

⭐ **In the extraction source a highlight-token misclassification italicised
every string in one language, the tests passed, and only a screenshot caught
it.** A project whose reading surface is its product cannot verify that surface
by assertion alone, and four later tasks have acceptance no unit test reaches:
`SF-14` (works with JavaScript disabled), `SF-18` (a highlight tracking
playback), `SF-24` (keyboard-operable), `QA-02` (contrast for every token in two
themes). This lands at M1 rather than M7 so those four use it instead of each
improvising one.

## ⛔ The evidence state, stated here because a reader will look here first

⭐ **These checks are `pinned green` IN THE DEV IMAGE and `unpinned green`
anywhere else**, and which one a run was is **printed** rather than assumed.
⛔ **`QA-03/1` — *the pinned dev image has no browser* — was closed by `W36`**,
which installed one pinned by version and checksum. Until then 57 of these
checks did not run in the one environment Ruling 40 makes authoritative, and
`quality floor: clean` said nothing about any of them.

⚠️ **A host run is still taken against an engine nobody pinned**, so a review of
one states the browser version and does not call it pinned.
`discovery.evidence_state()` decides which state a run may claim, keyed on the
image's own marker; `discovery.report_line()` prints that and the version at the
end of every suite run whether or not a browser was found.

## The acceptance clauses, and where each one runs

⛔ `ACCEPTANCE` is asserted total against this package's own test modules in
`test_init.py`, so a clause cannot be quietly dropped by deleting a file.
"""

from __future__ import annotations

#: `E10`'s acceptance for QA-03, mapped to the module that answers it. ⭐ Each
#: is run twice — against the built site, and against a tree damaged in exactly
#: the way that clause exists to catch (`site.DAMAGE`).
ACCEPTANCE = {
    "renders a generated page in a real browser and captures it": "test_capture",
    "verifies computed contrast for every palette token in both themes": "test_contrast",
    "drives keyboard traversal": "test_keyboard",
    "runs a page with JavaScript disabled": "test_no_script",
    "opens over file:// and issues no network request (R8)": "test_offline",
    #: ⭐ `W324`'s own clause, and it is a SIXTH row rather than a widening of
    #: the keyboard one: *"a link to a unit in another container is present,
    #: resolves, and lands on the right page"* is a claim about a built SITE,
    #: and the four rows above are claims about one page at a time.
    "follows the rail from one container to a unit in another (W324)": "test_rail",
    #: ⭐ `W325`'s clause, and it is a SEVENTH row for the reason the sixth was
    #: one: *"a bar down the LEFT of the reading column, and something usable
    #: where there is no room for one"* is a claim about the page's SHAPE at a
    #: named width, which none of the rows above takes a width to answer.
    "places that rail beside the reading column, and folds it back in when "
    "there is no room (W325)": "test_rail",
    #: ⭐ `W326`'s clause, and it is an EIGHTH row rather than a widening of the
    #: seventh for the reason the seventh was not a widening of the sixth:
    #: *"the rail sizes no row of the reading column"* is a claim about the page
    #: BESIDE the rail, and the placement clause never looks there — it passed,
    #: in a real browser, over a page that opened on the height of the rail in
    #: blank. ⚠️ It runs in a module of its own because it needs a fixture no
    #: other clause here needs: a container with MANY units, which is the only
    #: size of page this defect reads as a defect on rather than as spacing.
    "sizes the masthead's row by the masthead and not by the rail beside it "
    "(W326)": "test_rail_rows",
    #: ⭐ `W328`'s clause, and it is a NINTH row for the reason the eighth was not
    #: a widening of the seventh: *"the rail is flush against the window's left
    #: edge, stays there while the page scrolls, and scrolls itself when it is
    #: taller than the window"* is a claim about the page against the WINDOW, and
    #: not one row above takes a reading after scrolling anything.
    #: ⚠️ It runs in a module of its own because it needs a fixture no other
    #: clause here needs — a rail TALLER than the viewport, which is a bigger
    #: corpus again than `test_rail_rows` widens one container to.
    "pins that rail to the window's left edge, keeps it there while the page "
    "scrolls, and lets a long one scroll itself (W328)": "test_rail_fixed",
    #: ⭐ `W333`'s clause, and it is a TENTH row for a reason none of the nine
    #: above share: every one of them reads ONE page. ⛔ *"A reader crossing
    #: between a page with a rail and a page without one sees no jump in where
    #: the content starts"* is a claim about a PAIR of pages at one viewport, and
    #: each of the two was defensible alone — which is why the nine rows above
    #: were all green over a site whose layout moved when the reader clicked.
    #: ⚠️ It runs in a module of its own because it needs a fixture no other
    #: clause here needs: a site BUILT by `write_site`, because only a real build
    #: decides which page kinds carry a rail at all.
    "starts a page with no rail where it starts a page with one, so the layout "
    "does not move when a reader clicks (W333)": "test_page_start",
    #: ⭐ `W368`'s clause: *"a unit the reader marked read shows marked in the
    #: rail on every page"* is a claim about the page AFTER a reader acts, and not
    #: one row above presses anything. ⚠️ A module of its own because it needs a
    #: store the checks clear before and after, which no other clause touches.
    "shows in that rail which units the reader has marked read, on every page "
    "that carries it (W368)": "test_rail_marks",
    #: ⭐ `W383`'s clause, in the same module because it is the same store and the
    #: same press: the mark is SAID, not only drawn, in the rail and both lists.
    "tells a screen reader which units are read, in the rail and in both lists, "
    "and moves nothing on the screen (W383)": "test_rail_marks",
    #: ⭐ `W388`'s clause, and `W369`'s with it: *"a palette somebody can read
    #: for hours, the rail on the first page too, a transport that spans the
    #: content without growing its buttons, and a reading column with its
    #: secondary block beside it"*. ⛔ It is a row of its own because every one
    #: of the claims is a LIVE reading of a laid-out page under a stated width
    #: and a stated theme — the contrast row above reads a floor and never a
    #: ceiling, and not one row above reads a line of prose in characters.
    "keeps the reading inside a contrast band in both themes, the rail on every "
    "page, the transport the width of the content with its controls unchanged, "
    "and the page's secondary block beside the reading (W388, W369)": "test_reading_room",
    #: ⭐ `W388` stage 2's second clause, the user's own: *"have the both dark
    #: and light themes in studyforge as well"*. ⛔ A module of its own for the
    #: reason `test_rail_marks` is one — it needs a store cleared before and
    #: after every reading — and because what it reads is a page CHANGING under
    #: a press and surviving a reload, which no other row here does.
    "lets the reader choose light, dark or their system's setting on every page "
    "kind, and remembers it across a reload (W388)": "test_theme_choice",
    #: ⭐ `W388`'s width clause, and the user read three shapes before it
    #: settled: *"Still the paragraph texts are not using the full width"* of a
    #: shell pinned left under a ceiling, then *"the width is too wide… maybe if
    #: the display is too big having the menu and content in the middle by
    #: forcing a max width"* of a shell with no ceiling at all. ⛔ A row of its
    #: own rather than a widening of the reading-room row above, for the reason
    #: that module could not have caught either: every clause there is taken at
    #: ONE wide viewport, and both rejected shapes are correct at 1280 and 1440.
    #: ⚠️ What is read here is the shell against the WINDOW at five widths, and
    #: the cap on a line of prose at each of them.
    "fills the window up to its ceiling and centres at it above, with equal "
    "margins, the rail on its left edge and the aside on its right (W388)": "test_reading_width",
    #: ⭐ `W417`'s clause, and it is a row of its own for a reason none of the
    #: rows above share: every one of them opens `file://`. ⛔ *"The panel's tab
    #: order, focus handoff and live region are read in a browser"* cannot be
    #: asked there at all — the controls are unhidden only where
    #: `window.studyforge.run.available()` is true, so the keyboard row above
    #: has always traversed a page whose panel showed the offline note and no
    #: buttons (`SF-24/5`). ⚠️ It needs an origin no other clause here needs,
    #: which `served.py` binds over the same built bytes.
    "reads the practice panel's tab order, focus handoff and live region on a "
    "SERVED origin, where its controls exist (W417)": "test_practice_panel",
    #: ⭐ `W431`'s clause, and it is a row of its own rather than a widening of
    #: the one above, for a reason that module could not have covered: every
    #: clause there reads the panel AT REST, and this one reads it across a
    #: TRANSITION. ⛔ *"A live run must not be interrupted"* and *"an `iframe`
    #: moved to another parent reloads"* are claims about objects that exist
    #: only while a page is running — a text can read the script and cannot read
    #: either. ⚠️ It needs what no other clause here needs: an origin that
    #: answers the practice-editor route, so there is a frame to not move.
    "maximises the practice to the viewport and restores it, keeping every "
    "control, a live run and both editor windows unreloaded (W431)": "test_practice_maximise",
    #: ⭐ `AX-09`'s clause, and it is a row of its own rather than a widening of
    #: either above, because its ORIGIN is the subject: the two panel clauses
    #: need a server, and this one is only a reading if there is none. ⛔ *"A
    #: quiz page shows questions, grades them, and shows no run affordance"* is
    #: a claim about a page that grades with no compiler, no container, no
    #: network and no model (spec §7 §7), so it is read over `file://` — and a
    #: check that needed an origin would have proved the opposite of it.
    "shows a quiz's questions over file://, grades them with no server and no "
    "request, and offers nothing to run (AX-09)": "test_practice_quiz",
    #: ⭐ `AX-09`'s other clause, and it is a row of its own for the reason the
    #: one above is: its origin is the opposite one. ⛔ *"A Submit shows the
    #: breakdown, naming each failed edge case"* is a claim about a page that has
    #: just finished a run, and the verdicts arrive on that run's own stream —
    #: which needs a SERVED origin, and needs the server to say the lines.
    "draws what a Submit reported — main ask, edge cases n/m, each failed case "
    "named — beside a run verdict it never changes (AX-09)": "test_practice_breakdown",
}
