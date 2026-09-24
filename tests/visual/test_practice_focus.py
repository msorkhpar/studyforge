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
#: view scrolls nothing and a still page would then prove nothing.
SHORT = (1280, 360)

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

#: The page's own reading: where it is, what holds focus, where the frame is.
STATE = """
(() => {
  const frame = document.querySelector('[data-practice-frame="main"] iframe');
  const active = document.activeElement;
  const box = frame ? frame.getBoundingClientRect() : null;
  return {
    y: window.scrollY,
    active: active ? active.tagName : '',
    frame: box ? { top: Math.round(box.top + window.scrollY), x: box.left + box.width / 2,
                   y: box.top + Math.min(40, box.height / 2) } : null,
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
    assert reading["frame"]["top"] > reading["height"], (
        f"the editor frame is in view at the top ({reading}), so a still page proves nothing"
    )


def test_a_page_opened_at_its_top_stays_there_while_the_editor_takes_focus(
    open_page: OpenPage, framing: served.Served, editor: editor_standin.StandIn
) -> None:
    _open(open_page, framing.url(CASE))
    assert open_page.evaluate("document.hasFocus()"), "the page's window is not focused"
    reading = _after_the_steals(open_page, editor)
    _below_the_fold(reading)
    assert reading["y"] == 0, f"the page moved to {reading['y']} on its own"
    assert reading["active"] != "IFRAME", "the editor frame kept focus the reader never gave it"


def test_a_page_opened_at_an_anchor_stays_at_the_anchor(
    open_page: OpenPage, framing: served.Served, editor: editor_standin.StandIn
) -> None:
    _open(open_page, framing.url(CASE))
    # ⛔ An anchor from which the editor is OUT of view, chosen from the layout
    # and never from where the page happens to be: that is the moved quantity.
    anchor = open_page.evaluate(
        "(() => { const panel = document.querySelector('section[data-practice]');"
        " const top = panel.getBoundingClientRect().top + window.scrollY;"
        " const found = Array.from(document.querySelectorAll('main [id]')).find((e) => {"
        "   const t = e.getBoundingClientRect().top + window.scrollY;"
        "   return t > 100 && t + window.innerHeight + 100 < top; });"
        " return found ? found.id : null; })()"
    )
    assert anchor, "the fixture page has no anchor far enough above its practice to open at"
    # ⚠️ Through a blank document: a hash change alone is a same-document
    # navigation, which fires no load and would reuse the frames already there.
    open_page.open("about:blank")
    with editor.lock:
        editor.focused = 0
    _open(open_page, f"{framing.url(CASE)}#{anchor}")
    # ⭐ Where a fragment navigation LEAVES its target: the page's scroll padding
    # and its own scroll margin below the top. ⚠️ Not read at load: the page
    # glides to the anchor, so a reading taken then is a point on the way.
    padding = "parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 0"
    target = f"document.getElementById({anchor!r})"
    margin = f"parseFloat(getComputedStyle({target}).scrollMarginTop) || 0"
    rested = open_page.evaluate(f"({padding}) + ({margin})")
    reading = _after_the_steals(open_page, editor)
    now = open_page.evaluate(f"document.getElementById({anchor!r}).getBoundingClientRect().top")
    moved = abs(float(now) - float(rested))  # type: ignore[arg-type]
    assert moved <= 1, f"the anchor moved from {rested} to {now}"
    assert reading["active"] != "IFRAME", "the editor frame kept focus the reader never gave it"


def test_a_readers_click_into_the_frame_focuses_it_and_what_they_type_arrives(
    open_page: OpenPage, framing: served.Served, editor: editor_standin.StandIn
) -> None:
    _open(open_page, framing.url(CASE))
    reading = _after_the_steals(open_page, editor)
    # ⭐ The reader scrolls to the editor THEMSELVES, and then points and clicks.
    open_page.evaluate(
        f"window.scrollTo({{top: {reading['frame']['top'] - 40}, behavior: 'instant'}})"
    )
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
    for letter in "w449":
        for kind in ("keyDown", "keyUp"):
            message = {"type": kind, "key": letter}
            if kind == "keyDown":
                message["text"] = letter
            call("Input.dispatchKeyEvent", message, session=open_page.session)
    editor.wait_for(lambda s: s.typed == "w449")
    assert _at_rest(open_page)["active"] == "IFRAME", "focus the reader gave was taken back"
