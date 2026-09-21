"""`W431` — the practice maximises, restores, and throws nothing away, in a browser.

⛔ **THE USER ASKED FOR THIS DIRECTLY:** *"there should be a button that user
could maximize this window to have more control over the code and tests + run
and summit buttons"*. ⭐ The panel is a region of a reading page sized for prose,
and a reader writing code works through a letterbox: the editor, the test they
must satisfy and a run's output all compete for a few hundred pixels under a
chapter of teaching material.

## ⛔ Why this needs a BROWSER, and why a text could not answer it

⭐ **Two of the row's clauses are runtime identities and nothing else.** *"A live
run must not be interrupted by the transition"* and *"the two windows are
`iframe`s, and an `iframe` MOVED TO ANOTHER PARENT RELOADS"* are claims about
objects that exist only while a page is running. ⛔ A text can establish that the
script reaches for no node-moving call — `tests/studyforge/render/page/test_practice.py`
does, and that reading is real — but it cannot establish that the document a
reader was typing in is still the document that is there afterwards.

⭐ **So the frames are MARKED TWICE, and the two marks fail differently.** The
element carries one and the document inside it carries the other: a reparent
keeps the *element* and replaces the *window*, so an element mark alone would
survive the very move this row forbids. ⚠️ `_survived` reads both.

## ⛔ What is real here and what is a stand-in

⭐ **Real:** the built page's bytes, the serving process, `run-client.js`, the
`frame-src` the framework composes, the panel's own script, and the two
`iframe`s it builds from the server's answer. ⛔ **A stand-in:** what is BEHIND
the API — `ScriptedRuns` answers the practice-editor route with two blank
same-origin documents (`served.WINDOW_URLS`, where the choice is argued), because
this module's subject is whether a frame SURVIVES a transition and never what is
inside one. ⚠️ **No editor container is started here**, and nothing in this
module is a reading of `code-server`.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from tests.visual import served, site
from tests.visual.page import OpenPage
from tests.visual.test_practice_panel import (
    FINISHED,
    PANEL_SELECTOR,
    RUNNING,
    SETTLE,
    _acts,
    _case,
    _state,
    _tab_to,
    _until,
)

#: Mark every editor frame, on the ELEMENT and inside the DOCUMENT it is
#: showing. ⛔ **Two marks, because they fail differently and only both together
#: read the clause.** A frame moved to another parent is the SAME element — so an
#: element mark alone would survive the very reparent this row forbids — but the
#: move reloads it, and the window the document lived in is replaced, so the mark
#: INSIDE is gone. ⚠️ Written only once every frame has finished loading: a mark
#: put on a window that is still committing a document goes with it.
STAMP = """
(() => {
  const frames = Array.from(document.querySelectorAll('<panel> iframe'));
  const loaded = (frame) => !!frame.contentDocument
    && frame.contentDocument.readyState === 'complete';
  if (!frames.length || !frames.every(loaded)) return null;
  frames.forEach((frame, at) => {
    frame.dataset.stamp = 'element-' + at;
    frame.contentWindow.studyforgeStamp = 'inside-' + at;
  });
  return frames.length;
})()
""".replace("<panel>", PANEL_SELECTOR)

#: How many pixels apart two edges may be and still be called the same edge.
TOUCHING = 1.0

#: The word the maximise control ships showing. ⚠️ Spelled here only to TAB to
#: it; every assertion about what the control says reads the page, because the
#: template is the single source for both of its words.
MAXIMISE = "Maximise"


@pytest.fixture
def origin(built_site: site.Site) -> Iterator[served.Served]:
    """One loopback origin over the built tree, bound for this check alone."""
    with served.serving(built_site) as running:
        yield running


@pytest.fixture
def framed(built_site: site.Site) -> Iterator[served.Served]:
    """An origin that also answers the practice-editor route, so the panel has frames.

    ⛔ **Its own fixture and not the default**, because a frame is a focus scope
    of its own and every traversal in `test_practice_panel` counts stops:
    turning it on for all of them would change what those checks read.
    """
    with served.serving(built_site, windows=True) as running:
        yield running


def _frames(reading: dict, field: str) -> list:
    """One field of every editor frame the panel is showing, in document order."""
    return [frame[field] for frame in reading["frames"]]


def _survived(reading: dict, what: str) -> None:
    """Assert both editor frames came through `what` as the same frames."""
    assert _frames(reading, "slot") == ["main", "test"], (
        f"{what} the practice moved a frame out of its slot: {reading['frames']}"
    )
    assert _frames(reading, "element") == ["element-0", "element-1"], (
        f"{what} the practice replaced a frame element: {reading['frames']}"
    )
    assert _frames(reading, "inside") == ["inside-0", "inside-1"], (
        f"{what} the practice RELOADED an editor window: {reading['frames']} — a reader's "
        "unsaved buffer is gone and the code-server session has restarted"
    )


def test_the_practice_maximises_to_the_whole_viewport_and_escape_restores_it(
    open_page: OpenPage, origin: served.Served
) -> None:
    """⛔ Clause 1 and clause 4, driven by real keys from the top of the document.

    ⭐ **Tab to the control, Enter to open, Escape to close** — so *reachable and
    escapable without a mouse* is measured rather than assumed. ⛔ **A
    full-viewport surface with no keyboard exit is a trap**, and the two halves
    of the exit are Escape and the focus that comes back with it.
    """
    open_page.open(origin.url(_case()))
    at_rest = _state(open_page)
    assert at_rest["maximise"] and at_rest["maximise"]["visible"], (
        "a served panel offers no maximise control, so there is nothing to read"
    )
    assert at_rest["maximise"]["says"] == "false"
    assert not at_rest["expanded"]
    assert at_rest["box"]["w"] < at_rest["viewport"]["w"], (
        "the panel already fills the window at rest, so an expansion proves nothing"
    )

    _tab_to(open_page, at_rest["maximise"]["label"])
    open_page.press("Enter")
    wide = _until(open_page, lambda reading: reading["expanded"], "expanded")
    assert wide["box"]["w"] == pytest.approx(wide["viewport"]["w"], abs=TOUCHING)
    assert wide["box"]["h"] == pytest.approx(wide["viewport"]["h"], abs=TOUCHING)
    assert wide["box"]["top"] == pytest.approx(0, abs=TOUCHING)
    assert wide["box"]["left"] == pytest.approx(0, abs=TOUCHING)
    assert wide["focus"]["inPanel"], (
        f"the practice covered the window and focus stayed at {wide['focus']!r}"
    )
    assert wide["maximise"]["says"] == "true"
    assert wide["maximise"]["label"] != at_rest["maximise"]["label"], (
        "the control says the same word expanded as it does at rest"
    )
    # ⛔ Clause 2: expanded, the reader keeps EVERYTHING the panel had.
    assert _acts(wide) == _acts(at_rest), f"maximising dropped a control: {_acts(wide)}"

    open_page.press("Escape")
    back = _until(open_page, lambda reading: not reading["expanded"], "restored")
    assert back["box"]["w"] == pytest.approx(at_rest["box"]["w"], abs=TOUCHING)
    assert back["maximise"]["label"] == at_rest["maximise"]["label"]
    assert back["maximise"]["says"] == "false"
    assert back["focus"]["label"] == at_rest["maximise"]["label"], (
        f"restoring left focus at {back['focus']!r} rather than on the control"
    )
    # ⭐ The place in the page the reader left is the place they come back to.
    assert back["viewport"]["scrolled"] == at_rest["viewport"]["scrolled"]


def test_neither_editor_window_is_reloaded_by_maximising_or_restoring(
    open_page: OpenPage, framed: served.Served
) -> None:
    """⛔ **THE clause this row is measured by, and it is measured ground.**

    ⭐ The two windows are `iframe`s, and an `iframe` MOVED TO ANOTHER PARENT
    RELOADS — so a maximise built by reparenting the frames into a full-screen
    container throws away the reader's unsaved buffer and restarts the
    code-server session, while looking entirely correct. ⛔ Both marks are read:
    the elements are the same elements in the same slots, and the documents
    inside them are the same documents.
    """
    open_page.open(framed.url(_case()))
    _until(
        open_page,
        lambda reading: len(reading["frames"]) == 1 and reading["frames"][0]["ready"],
        "loaded the editor window it was given",
    )
    # ⭐ The second window is built on the first press of its tab (`W429`), and
    # this row must carry BOTH of them across the transition. ⚠️ **Reached with
    # an ARROW and not with Tab**: a tablist uses a roving `tabindex`, so exactly
    # one tab is in the focus ring and the other is an arrow away from it.
    _tab_to(open_page, "Your code")
    open_page.press("ArrowRight")
    ready = _until(
        open_page,
        lambda reading: len(reading["frames"]) == 2 and all(_frames(reading, "ready")),
        "loaded both editor windows",
    )
    assert _frames(ready, "slot") == ["main", "test"]
    assert open_page.evaluate(STAMP) == 2, "the frames could not be marked, so nothing is read"

    _tab_to(open_page, MAXIMISE)
    open_page.press("Enter")
    _survived(_until(open_page, lambda reading: reading["expanded"], "expanded"), "maximising")
    open_page.press("Escape")
    _survived(_until(open_page, lambda reading: not reading["expanded"], "restored"), "restoring")


def test_a_live_run_and_everything_it_has_written_survive_both_transitions(
    open_page: OpenPage, origin: served.Served
) -> None:
    """⛔ Clause 3, on the surface a reader actually watches: a run that is live
    stays live and its output is still there, through the expansion and through
    the restore — and it still settles afterwards.
    """
    open_page.open(origin.url(_case()))
    _tab_to(open_page, "Run")
    open_page.press("Enter")
    assert origin.runs.started.wait(SETTLE), "pressing Run with the keyboard started no run"
    live = _until(
        open_page,
        lambda reading: reading["status"]["text"] == RUNNING and bool(reading["output"]["text"]),
        "said it was running and wrote a line",
    )
    written = live["output"]["text"]

    _tab_to(open_page, MAXIMISE)
    open_page.press("Enter")
    wide = _until(open_page, lambda reading: reading["expanded"], "expanded")
    assert wide["status"]["text"] == RUNNING, f"maximising ended the run: {wide['status']}"
    assert wide["output"]["text"] == written, "maximising lost what the run had written"
    assert _acts(wide) == ["Run", "Submit", "Stop"], f"Stop did not survive: {_acts(wide)}"

    open_page.press("Escape")
    back = _until(open_page, lambda reading: not reading["expanded"], "restored")
    assert back["status"]["text"] == RUNNING, f"restoring ended the run: {back['status']}"
    assert back["output"]["text"] == written, "restoring lost what the run had written"

    origin.runs.release.set()
    done = _until(
        open_page, lambda reading: reading["status"]["text"] == FINISHED, f"settled on {FINISHED!r}"
    )
    assert done["output"]["text"].startswith(written), "the run's own output was rewritten"
