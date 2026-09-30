"""An editor frame that takes focus as it starts never moves the page or keeps the focus.

⛔ **A reader's page must never scroll to the editor, or lose its focus to it, on
its own.** ⚠️ **The mechanism:** the workbench calls `focus()` on its editor as
it starts, the browser lets a same-site frame take focus from the page with no
user activation, and a focus scrolls every ancestor frame to the element — so
the page would glide to the editor and `document.activeElement` become the
frame. ⭐ `practice-editor.js` gives that focus back and puts the page back where
the reader left it; this module reads the page the way the reader sees it.

⭐ **The frame here is `editor_standin`'s**, on a second loopback origin: a
document whose own script takes focus twice as it starts, the workbench's shape.
⛔ **The precondition is asserted, never assumed:** the frame sits below the
fold, and the stand-in reports its focus calls — a check that ran before the
frame had tried anything would read a still page and prove nothing.

⚠️ **One route of two is read here.** With the page's window focused the steal
raises a `blur` on it, which is the reader's case and this module's. ⛔ The
other route — a steal that raises NO `blur` (an unfocused window, or a frame
taking focus from another frame) — cannot be staged by this harness: every tab
it opens reports `document.hasFocus()` true, and a backgrounded one stops
painting. ⭐ That route's watch is held by `tests/studyforge/render/page/test_practice_editor.py`.

⭐ **And the reader's own hand still works**: a click into the frame focuses it
and what is typed reaches it.

## ⛔ Every wait here is on an EVENT, and none is a sleep

⚠️ The stand-in's reports of four keystrokes are four `fetch`es its server
answers on four threads, so they can arrive in any order; `editor_standin`
numbers each report so the last one TYPED wins, not the last to arrive. ⛔ **And
no wait is a sleep**, because a fixed pause is a guess at how long the machine
takes, and a loaded machine is exactly where the guess is wrong:

- ⭐ the frame's arrival is a `MutationObserver` in the page (`BUILT`);
- ⭐ the stand-in's focus calls and keystrokes are its own reports (`wait_for`);
- ⭐ **"the page has finished answering"** is `AT_REST`: the page's scroll
  position and its `activeElement` unchanged across `REST_FRAMES` consecutive
  painted frames. ⛔ A glide moves the page on every frame it paints, so a page
  that is gliding is never at rest, and a page whose focus is taken back is not
  at rest until it has been — the reading is taken after the behaviour under
  test has had its whole say, however slowly the machine paints.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest

from tests.visual import editor_standin, served, site
from tests.visual.page import OpenPage

#: The unit page whose panel is framed.
CASE = "depth2-unit-01"

#: A viewport short enough that the panel's editor is below the fold at the top.
#: ⛔ Asserted in every check (`_below_the_fold`), because a frame already in
#: view scrolls nothing and a still page would then prove nothing. ⚠️ The
#: editor gives way to the panel's height down to its floor
#: (`practice-panes.css`), so the viewport is short enough that the floor
#: itself runs past the fold.
SHORT = (1280, 280)

#: How many consecutive painted frames the page must hold still to be at rest.
#: ⭐ Frames, not milliseconds: a loaded machine paints fewer of them and the
#: wait grows with it. ⚠️ Enough to span the page's `activeElement` watch
#: (`WATCH_EVERY`, 100 ms) twice at 60 frames a second.
REST_FRAMES = 20

#: The ceiling on any one in-page wait, in ms. ⛔ A ceiling only: a wait that
#: reaches it REJECTS, naming what it waited for, and never lets a check go on.
CEILING_MS = 20000

#: Resolves once the panel has built its editor frame. ⭐ A `MutationObserver`,
#: so it wakes on the frame's insertion rather than on a polling tick.
BUILT = """
new Promise((done, fail) => {
  const wanted = '[data-practice-frame="main"] iframe';
  if (document.querySelector(wanted)) { done(true); return; }
  const watch = new MutationObserver(() => {
    if (document.querySelector(wanted)) { watch.disconnect(); clearTimeout(ceiling); done(true); }
  });
  const ceiling = setTimeout(() => {
    watch.disconnect(); fail(new Error('the panel never built its editor frame'));
  }, __CEILING__);
  watch.observe(document.documentElement, { childList: true, subtree: true });
})
""".replace("__CEILING__", str(CEILING_MS))

#: Resolves once the page's scroll position and `activeElement` have held still
#: for `REST_FRAMES` consecutive animation frames (the module docstring).
AT_REST = """
new Promise((done, fail) => {
  let last = null;
  let still = 0;
  const ceiling = setTimeout(() => fail(new Error(
    'the page never came to rest: it was still moving or changing focus')), __CEILING__);
  function look() {
    const active = document.activeElement;
    const now = [window.scrollX, window.scrollY, active ? active.tagName : ''].join(' ');
    still = now === last ? still + 1 : 0;
    last = now;
    if (still < __FRAMES__) { requestAnimationFrame(look); return; }
    clearTimeout(ceiling);
    done(true);
  }
  requestAnimationFrame(look);
})
""".replace("__CEILING__", str(CEILING_MS)).replace("__FRAMES__", str(REST_FRAMES))

#: The page's own reading: where it is, what holds focus, where the frame is,
#: and how far the open practice's panel — the workspace's right half, which
#: scrolls inside itself — has been scrolled.
STATE = """
(() => {
  const frame = document.querySelector('[data-practice-frame="main"] iframe');
  const panel = document.querySelector('section[data-practice]');
  const active = document.activeElement;
  const box = frame ? frame.getBoundingClientRect() : null;
  const held = panel ? panel.getBoundingClientRect() : null;
  return {
    y: window.scrollY,
    active: active ? active.tagName : '',
    frame: box ? { top: Math.round(box.top), bottom: Math.round(box.bottom),
                   x: box.left + box.width / 2,
                   y: box.top + Math.min(40, box.height / 2) } : null,
    panel: held ? { bottom: Math.round(held.bottom), scrolled: panel.scrollTop } : null,
    height: window.innerHeight
  };
})()
"""


@pytest.fixture
def editor() -> Iterator[editor_standin.StandIn]:
    """The stand-in editor origin, for this check alone."""
    with editor_standin.running() as running:
        yield running


@pytest.fixture
def framing(built_site: site.Site, editor: editor_standin.StandIn) -> Iterator[served.Served]:
    """An origin whose practice-editor route answers the stand-in's two windows."""
    with served.serving(built_site, editor=editor.origin) as running:
        yield running


def _open(page: OpenPage, url: str) -> None:
    """Open `url` in the short viewport, with the page's window focused as a reader's is."""
    page.resize(*SHORT)
    page.browser.call("Emulation.setFocusEmulationEnabled", {"enabled": True}, session=page.session)
    page.open(url)


def _state(page: OpenPage) -> dict:
    return dict(page.evaluate(STATE))  # type: ignore[call-overload]


def _at_rest(page: OpenPage) -> dict:
    """The page's reading once it has held still, so nothing it is doing is still under way."""
    page.evaluate(AT_REST)
    return _state(page)


def _after_the_steals(page: OpenPage, editor: editor_standin.StandIn) -> dict:
    """Wait for the frame, for the stand-in's every focus call, and for the page to come to rest."""
    page.evaluate(BUILT)
    editor.wait_for(lambda s: s.focused >= len(editor_standin.FOCUS_AT_MS))
    return _at_rest(page)


def _below_the_fold(reading: dict) -> None:
    """⛔ The precondition: the frame is not wholly in its panel's view, so a steal would scroll."""
    assert reading["frame"] and reading["frame"]["bottom"] > reading["panel"]["bottom"], (
        f"the editor frame is wholly in view ({reading}), so a still panel proves nothing"
    )


def _scroll_to_the_list(page: OpenPage) -> float:
    """Scroll the page so the *Practice (n)* list is in view, and return where it is."""
    return float(
        page.evaluate(  # type: ignore[arg-type]
            "(() => { const list = document.querySelector('section[data-practices]');"
            " window.scrollTo({top: list.getBoundingClientRect().top + window.scrollY - 40,"
            " behavior: 'instant'}); return window.scrollY; })()"
        )
    )


def test_opening_a_practice_moves_nothing_while_the_editor_takes_focus(
    open_page: OpenPage, framing: served.Served, editor: editor_standin.StandIn
) -> None:
    _open(open_page, framing.url(CASE))
    assert open_page.evaluate("document.hasFocus()"), "the page's window is not focused"
    where = _scroll_to_the_list(open_page)
    open_page.open_practice()
    reading = _after_the_steals(open_page, editor)
    _below_the_fold(reading)
    assert reading["y"] == where, (
        f"the page under the workspace moved from {where} to {reading['y']}"
    )
    assert reading["panel"]["scrolled"] == 0, f"the panel scrolled on its own: {reading}"
    assert reading["active"] != "IFRAME", "the editor frame kept focus the reader never gave it"


def test_closing_the_workspace_returns_the_reader_to_the_card_they_opened(
    open_page: OpenPage, framing: served.Served, editor: editor_standin.StandIn
) -> None:
    # ⛔ Close returns the reader to the same place in the lesson (register
    # ruling), after the editor has had its whole say.
    _open(open_page, framing.url(CASE))
    where = _scroll_to_the_list(open_page)
    open_page.open_practice()
    _after_the_steals(open_page, editor)
    open_page.press("Escape")
    reading = _at_rest(open_page)
    assert reading["y"] == where, f"Close left the page at {reading['y']}, not {where}"
    assert reading["frame"] is None, "the editor frame outlived the practice it was built for"
    focused = open_page.focused()
    assert focused["tag"] == "A" and focused["label"].startswith("#s-"), (
        f"focus went to {focused}, not back to the card that was opened"
    )


def test_a_readers_click_into_the_frame_focuses_it_and_what_they_type_arrives(
    open_page: OpenPage, framing: served.Served, editor: editor_standin.StandIn
) -> None:
    _open(open_page, framing.url(CASE))
    open_page.open_practice()
    _after_the_steals(open_page, editor)
    # ⭐ The reader points at the editor in the workspace, and clicks.
    target = _state(open_page)["frame"]
    call = open_page.browser.call
    for step in range(5):
        call(
            "Input.dispatchMouseEvent",
            {"type": "mouseMoved", "x": target["x"] - 40 + step * 10, "y": target["y"]},
            session=open_page.session,
        )
    for kind in ("mousePressed", "mouseReleased"):
        call(
            "Input.dispatchMouseEvent",
            {"type": kind, "x": target["x"], "y": target["y"], "button": "left", "clickCount": 1},
            session=open_page.session,
        )
    assert _at_rest(open_page)["active"] == "IFRAME", "a reader's click into the editor was refused"
    for letter in "abcd":
        for kind in ("keyDown", "keyUp"):
            message = {"type": kind, "key": letter}
            if kind == "keyDown":
                message["text"] = letter
            call("Input.dispatchKeyEvent", message, session=open_page.session)
    editor.wait_for(lambda s: s.typed == "abcd")
    assert _at_rest(open_page)["active"] == "IFRAME", "focus the reader gave was taken back"
