"""The visual and browser verification harness.

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

## ⛔ What it opens, and why that is a sentence rather than an assumption

⭐ **The tree carries every page kind the framework renders**, one subtree per
fixture corpus, and the region census is **derived from the chrome stylesheet's
own disposition table** — so a region added there is a red check here on the day
it lands. ⛔ A harness that opened only the unit pages would judge two of the
six chrome regions and pass over the rest, which is why the population is a
census with its own negative control (`test_site.py`) rather than a list.

## ⛔ Why this exists

⭐ **A highlight-token misclassification can italicise every string in one
language while every assertion passes, and only a screenshot shows it.** A
project whose reading surface is its product cannot verify that surface by
assertion alone: working with JavaScript disabled, a narration highlight
tracking playback, keyboard operation and contrast for every token in two themes
are all readings of a page in a browser.

## ⛔ The evidence state, stated here because a reader will look here first

⭐ **These checks are `pinned green` IN THE DEV IMAGE and `unpinned green`
anywhere else**, and which one a run was is **printed** rather than assumed. The
dev image carries a browser pinned by version and checksum, and it is the one
environment whose readings are authoritative (R15).

⚠️ **A host run is taken against an engine nobody pinned**, so a review of
one states the browser version and does not call it pinned.
`discovery.evidence_state()` decides which state a run may claim, keyed on the
image's own marker; `discovery.report_line()` prints that and the version at the
end of every suite run whether or not a browser was found.

## The acceptance clauses, and where each one runs

⛔ `ACCEPTANCE` is asserted total against this package's own test modules in
`test_init.py`, so a clause cannot be quietly dropped by deleting a file.
"""

from __future__ import annotations

#: The visual harness's acceptance, clause by clause, mapped to the module that answers it. ⭐ Each
#: is run twice — against the built site, and against a tree damaged in exactly
#: the way that clause exists to catch (`site.DAMAGE`).
ACCEPTANCE = {
    "renders a generated page in a real browser and captures it": "test_capture",
    "verifies computed contrast for every palette token in both themes": "test_contrast",
    "drives keyboard traversal": "test_keyboard",
    "runs a page with JavaScript disabled": "test_no_script",
    "opens over file:// and issues no network request (R8)": "test_offline",
    #: ⭐ A row of its own rather than a widening of the keyboard one: *a link
    #: to a unit in another container is present, resolves, and lands on the
    #: right page* is a claim about a built SITE, and the rows above are claims
    #: about one page at a time.
    "follows the rail from one container to a unit in another": "test_rail",
    #: ⭐ A row of its own for the same reason: *a bar down the LEFT of the
    #: reading column, and something usable where there is no room for one* is a
    #: claim about the page's SHAPE at a named width, which none of the rows
    #: above takes a width to answer.
    "places that rail beside the reading column, and folds it back in when "
    "there is no room": "test_rail",
    #: ⭐ A row of its own: *the rail sizes no row of the reading column* is a
    #: claim about the page BESIDE the rail, where the placement clause never
    #: looks. ⚠️ A module of its own because it needs a fixture no other clause
    #: here needs: a container with MANY units, the only size of page on which a
    #: rail that sizes the masthead's row reads as a defect rather than spacing.
    "sizes the masthead's row by the masthead and not by the rail beside it": "test_rail_rows",
    #: ⭐ A row of its own: *the rail is flush against the window's left edge,
    #: stays there while the page scrolls, and scrolls itself when it is taller
    #: than the window* is a claim about the page against the WINDOW, and no row
    #: above takes a reading after scrolling anything. ⚠️ A module of its own
    #: because it needs a rail TALLER than the viewport, which is a bigger
    #: corpus again than `test_rail_rows` widens one container to.
    "pins that rail to the window's left edge, keeps it there while the page "
    "scrolls, and lets a long one scroll itself": "test_rail_fixed",
    #: ⭐ A row of its own, because every row above reads ONE page. ⛔ *A reader
    #: crossing between a page with a rail and a page without one sees no jump
    #: in where the content starts* is a claim about a PAIR of pages at one
    #: viewport, and each of the two is defensible alone. ⚠️ A module of its own
    #: because it needs a site BUILT by `write_site`: only a real build decides
    #: which page kinds carry a rail at all.
    "starts a page with no rail where it starts a page with one, so the layout "
    "does not move when a reader clicks": "test_page_start",
    #: ⭐ *A unit the reader marked read shows marked in the rail on every page*
    #: is a claim about the page AFTER a reader acts, and no row above presses
    #: anything. ⚠️ A module of its own because it needs a store the checks
    #: clear before and after, which no other clause touches.
    "shows in that rail which units the reader has marked read, on every page "
    "that carries it": "test_rail_marks",
    #: ⭐ In the same module because it is the same store and the same press:
    #: the mark is SAID, not only drawn, in the rail and both lists.
    "tells a screen reader which units are read, in the rail and in both lists, "
    "and moves nothing on the screen": "test_rail_marks",
    #: ⭐ *A palette somebody can read for hours, the rail on the first page
    #: too, a transport that spans the content without growing its buttons, and
    #: a reading column with its secondary block beside it.* ⛔ A row of its own
    #: because every one of the claims is a LIVE reading of a laid-out page under
    #: a stated width and a stated theme — the contrast row above reads a floor
    #: and never a ceiling, and no row above reads a line of prose in characters.
    "keeps the reading inside a contrast band in both themes, the rail on every "
    "page, the transport the width of the content with its controls unchanged, "
    "and the page's secondary block beside the reading": "test_reading_room",
    #: ⭐ *Both a dark and a light theme.* ⛔ A module of its own for the reason
    #: `test_rail_marks` is one — it needs a store cleared before and after
    #: every reading — and because what it reads is a page CHANGING under a press
    #: and surviving a reload, which no other row here does.
    "lets the reader choose light, dark or their system's setting on every page "
    "kind, and remembers it across a reload": "test_theme_choice",
    #: ⭐ The width clause: the shell fills the window up to a ceiling and
    #: centres above it. ⛔ A row of its own rather than a widening of the
    #: reading-room row above: every clause there is taken at ONE wide viewport,
    #: where a shell pinned left under a ceiling and a shell with no ceiling are
    #: both correct at 1280 and 1440. ⚠️ What is read here is the shell against
    #: the WINDOW at five widths, and the cap on a line of prose at each of them.
    "fills the window up to its ceiling and centres at it above, with equal "
    "margins, the rail on its left edge and the aside on its right": "test_reading_width",
    #: ⭐ A row of its own, because every row above opens `file://`. ⛔ *The
    #: panel's tab order, focus handoff and live region are read in a browser*
    #: cannot be asked there at all — the controls are unhidden only where
    #: `window.studyforge.run.available()` is true, so the keyboard row above
    #: traverses a page whose panel shows the offline note and no buttons.
    #: ⚠️ It needs an origin no other clause here needs, which `served.py`
    #: binds over the same built bytes.
    "reads the practice panel's tab order, focus handoff and live region on a "
    "SERVED origin, where its controls exist": "test_practice_panel",
    #: ⭐ A row of its own rather than a widening of the one above: every clause
    #: there reads the panel AT REST, and this one reads it across a
    #: TRANSITION. ⛔ *A live run must not be interrupted* and *an `iframe`
    #: moved to another parent reloads* are claims about objects that exist
    #: only while a page is running — a text can read the script and cannot read
    #: either. ⚠️ It needs what no other clause here needs: an origin that
    #: answers the practice-editor route, so there is a frame to not move.
    "lists a lesson's practices as titled cards and opens each in one full-screen "
    "workspace, at desktop and phone width, with one editor at most": "test_practice_workspace",
    #: ⭐ Two rows of their own: a divider
    #: dragged, over an editor frame, is real input across a frame boundary
    #: that no text can read, and a choice that survives a reload is a claim
    #: about the reader's browser store. ⚠️ One row per side, so each module
    #: stays one module: the description's side, then the report's.
    "resizes a code practice's description by a divider dragged or keyed, and "
    "closes and reopens it, kept per reader": "test_practice_panes",
    "resizes a code practice's report by a divider and collapses it to a bar "
    "that keeps the last verdict, kept per reader": "test_practice_report",
    #: ⭐ A row of its own because its ORIGIN is the subject: the two panel
    #: clauses need a server, and this one is only a reading if there is none.
    #: ⛔ *A quiz page shows questions, grades them, and shows no run
    #: affordance* is a claim about a page that grades with no compiler, no
    #: container, no network and no model (spec §7 §7), so it is read over
    #: `file://` — a check that needed an origin would prove the opposite of it.
    "shows a quiz's questions over file://, grades them with no server and no "
    "request, and offers nothing to run": "test_practice_quiz",
    #: ⭐ A row of its own for the reason the one above is: its origin is the
    #: opposite one. ⛔ *A Submit shows the breakdown, naming each failed edge
    #: case* is a claim about a page that has just finished a run, and the
    #: verdicts arrive on that run's own stream — which needs a SERVED origin,
    #: and needs the server to say the lines.
    "draws what a Submit reported — main ask, edge cases n/m, each failed case "
    "named — beside a run verdict it never changes": "test_practice_breakdown",
    #: ⭐ The served-faces clause, and it is a row of its own because its ORIGIN and its
    #: POLICY are the subject: `file://` carries no policy, so no clause above
    #: can see a policy that blocks the faces on a served page.
    #: ⛔ Read over the real `serve` process, never a header written here.
    "loads every vendored face on a page the serve process answers, under the "
    "policy it sends, and raises no CSP violation": "test_served_faces",
    #: ⭐ The page-start clause: *a reader who opens a page stays where they
    #: opened it.* ⛔ A row of its own, because its frame must be a document of
    #: ANOTHER origin whose own script takes focus: `served.py`'s blank windows
    #: have no script, and what is read is the framed document's behaviour.
    "keeps the page where the reader opened it, top or anchor, while an editor "
    "frame takes focus as it starts, and still lets a click focus it": "test_practice_focus",
    #: ⭐ The clip-presence clause, a row of its own because it reads the CONSOLE,
    #: which no row above reads, and does so over `file://` AND the real `serve`:
    #: a failed load is an error in both, and the page must avoid it in both.
    "hides every narration control on a page whose clips are absent, with a console "
    "free of errors and warnings over file:// and served, and plays them once "
    "restored with no rebuild": "test_narration_clips",
    #: ⭐ The build-without-clips clause: a site built to hold no clip names none, so its
    #: pages ask for nothing and log nothing.
    "asks for no clip and logs nothing on a page of a site built without narration": (
        "test_narration_stripped"
    ),
    #: ⭐ The scale clause, a row of its own because its CORPUS is the subject: a
    #: strip of sixty groups and a rail title longer than the rail are shapes no
    #: committed fixture has, and the operator is read as a picture, which no row
    #: above takes of code.
    "fits the progress strip of a course of sixty groups and a rail title with no "
    "break inside the column, and draws code's operators without ligatures": "test_scale",
    #: ⭐ A row of its own because its ORIGIN is the subject: the preview is a static
    #: page set read from Python's own `http.server`, with no study server behind it.
    #: ⛔ *No request fails, none asks an `/api/` path or a clip, a quiz grades inside
    #: the page* is a claim about the console and the network of that origin alone.
    "opens every page of the read-only preview from a static server with a console free "
    "of errors, no request to the study server, and no Run or Submit to press": "test_preview",
    #: ⭐ A row of its own because its CSP is the subject: a published site that names an
    #: editor in its configuration must let the first page frame it, which only a real
    #: browser logs a violation for, and only over an origin that answers as the editor.
    "frames a cold published site's configured editor from the first response, with "
    "no Content-Security-Policy violation": "test_cold_published_frame",
}
