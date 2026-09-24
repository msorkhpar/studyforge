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

import json
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

#: The viewport the scroll case pins, so its reading stops depending on which
#: browser ran it. ⛔ **MEASURED, and the two arms really do differ**: the window
#: this harness launches leaves **900px** of viewport in the pinned image and
#: **813px** on this host's own browser — the same page, two different amounts
#: of room, because a browser's own chrome is not part of what `--window-size`
#: promises. ⭐ An explicit height makes the document's spare scroll the same
#: number in both. ⚠️ **1280 wide is deliberately the harness's own wide
#: width**: narrowing it folds the rail and changes the page this row is about.
SCROLL_CASE_VIEWPORT = (1280, 600)

#: How much room the page has, and how much of it the panel is — the three
#: numbers the scroll case's precondition is stated in.
ROOM = """
(() => {
  const panel = document.querySelector('<panel>');
  return {
    viewport: window.innerHeight,
    document: document.documentElement.scrollHeight,
    panel: panel.offsetHeight,
    spare: document.documentElement.scrollHeight - window.innerHeight
  };
})()
""".replace("<panel>", PANEL_SELECTOR)

#: Put the reader at the end of the page — and make sure they ARRIVE.
#:
#: ⛔ **`behavior: 'instant'`, for the very reason this row exists.** `reset.css`
#: sets `scroll-behavior: smooth` on `html`, so a plain `scrollTo` ANIMATES and
#: a reading taken straight after it is a reading of a page still in motion.
#: ⚠️ **MEASURED: this one setup line read `0` on this host's browser while
#: reading the real position in the pinned image** — the same defect this row
#: repairs, living in the check that repairs it, and it is what refused the
#: second merge. ⛔ A check's SETUP is as subject to the mechanism as the code.
TO_THE_END = """
window.scrollTo({ top: document.documentElement.scrollHeight, left: 0, behavior: 'instant' });
"""


#: Where the maximise control sits against the fold, before a single Tab.
BELOW_THE_FOLD = """
(() => {
  const control = document.querySelector('<panel> [data-practice-part="expand"]');
  const box = control.getBoundingClientRect();
  return { top: box.top, bottom: box.bottom, viewport: window.innerHeight };
})()
""".replace("<panel>", PANEL_SELECTOR)

#: Record every time the PAGE comes to rest, and what had focus when it did.
#:
#: ⛔ **The smooth-scroll repair, and this is the whole of it.** Reaching the control by
#: Tab scrolls it into view, and `reset.css`'s `scroll-behavior: smooth` makes
#: that scroll a GLIDE. ⭐ **MEASURED in the pinned image:** from a reader at the
#: top, the glide runs `0, 2, 10, 25, 51, 93 … 1121, 1122` over about 560ms —
#: and the reading of the page the reader left was taken at its first frame.
#: Alone, the Enter lands before a frame is drawn and both readings say `0`;
#: under load a frame or two slips between them, the panel remembers the page
#: where the glide had got to, and the check read `4` against `0`, `4` against
#: `2`, and `2` against `0` — every one a glide frame, never a restore error.
#: ⛔ **So the fix is to read a page AT REST, not to forgive a difference**: the
#: browser's own `scrollend` says when the glide has finished, and it is armed
#: BEFORE the traversal so a glide that ends early is still seen.
#: ⚠️ On the DOCUMENT and not captured, so the output region's own scrolling,
#: which fires at the element and does not bubble, is not mistaken for the page's.
AT_REST = """
(() => {
  window.studyforgeRest = [];
  document.addEventListener('scrollend', () => {
    const active = document.activeElement;
    const box = active.getBoundingClientRect();
    window.studyforgeRest.push({
      label: active.textContent.trim(),
      scrolled: window.scrollY,
      inView: box.top >= 0 && box.bottom <= window.innerHeight
    });
  });
  return true;
})()
"""


#: Resolves with the first rest `AT_REST` recorded with `<label>` focused and in view:
#: at once when that glide has already ended, otherwise on the `scrollend` that ends it.
#: ⚠️ `AT_REST`'s listener was added first, so it has recorded a rest before `seen` reads.
GLIDED_TO = """
new Promise((done, fail) => {
  const label = <label>;
  const found = () => (window.studyforgeRest || []).find((r) => r.label === label && r.inView);
  if (found()) { done(found()); return; }
  const ceiling = setTimeout(() => {
    document.removeEventListener('scrollend', seen);
    fail(new Error('the page never came to rest with ' + JSON.stringify(label)
      + ' in view; it came to rest ' + JSON.stringify(window.studyforgeRest)));
  }, <ceiling>);
  function seen() {
    const rest = found();
    if (!rest) return;
    clearTimeout(ceiling);
    document.removeEventListener('scrollend', seen);
    done(rest);
  }
  document.addEventListener('scrollend', seen);
})
"""


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


def _glided_to(page: OpenPage, label: str) -> dict:
    """Wait until the glide that reaching `label` started has finished, and return where.

    ⛔ An EVENT wait, in the page: `GLIDED_TO` resolves on the browser's own
    `scrollend`, or at once when the glide has already ended, and rejects at a
    ceiling naming what it waited for. A fixed sleep is a check that is slow alone
    and still wrong under load, and a polling tick is a sleep by another name.
    """
    wait = GLIDED_TO.replace("<label>", json.dumps(label))
    wait = wait.replace("<ceiling>", str(int(SETTLE * 1000)))
    return dict(page.evaluate(wait))  # type: ignore[call-overload]


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

    # ⛔ **The precondition of the wait below, stated rather than assumed**: the
    # control starts below the fold, so reaching it MUST scroll the page, and
    # there is a glide to wait for. A control already in view would scroll
    # nothing, send no `scrollend`, and leave the wait with nothing to see.
    fold = dict(open_page.evaluate(BELOW_THE_FOLD))  # type: ignore[call-overload]
    assert fold["bottom"] > fold["viewport"], (
        f"the control is already in view at rest ({fold}), so reaching it scrolls nothing "
        "and this check has no glide to wait out"
    )
    assert open_page.evaluate(AT_REST), "the end-of-scroll recorder could not be armed"
    _tab_to(open_page, at_rest["maximise"]["label"])
    # ⛔ **The page the reader LEFT is read here, after the traversal that
    # reaches the control, AFTER the glide that traversal starts has finished,
    # and before the press — never at the top of the document and never in
    # motion.** ⚠️ The first version compared against `at_rest`, taken before a
    # single Tab; the second read straight after the traversal, at the glide's
    # first frame, and failed under load by whatever frames slipped in before
    # the press (measured at `AT_REST`). ⛔ It is still EXACT equality
    # and not a tolerance — what changed is that both readings are of a page
    # that has stopped.
    rest = _glided_to(open_page, at_rest["maximise"]["label"])
    left = _state(open_page)
    assert left["viewport"]["scrolled"] == rest["scrolled"], (
        f"the page moved again after the glide ended at {rest['scrolled']}: {left['viewport']}"
    )
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
    assert back["viewport"]["scrolled"] == left["viewport"]["scrolled"]


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


def test_restoring_gives_back_the_place_in_the_page_the_reader_left(
    open_page: OpenPage, origin: served.Served
) -> None:
    """⛔ **Clause 1's scroll half, taken at the ONE place it can fail.**

    ⚠️ **This is a repair, and the defect was real** (`W431/1`). The expansion
    is `position: fixed`, which takes the panel OUT OF FLOW — so the document
    loses exactly the panel's own height, the furthest a reader can scroll drops
    with it, and the browser CLAMPS a scroll that no longer fits. ⛔ Restoring
    the height does not undo a clamp.

    ⭐ **MEASURED before the repair, on this fixture page:** a reader at the foot
    of the page came back **306px** from where they left; a reader at the top
    came back exactly where they were. ⛔ **So a reading taken at the top of the
    page asserts nothing about this**, and the first one was — which is how it
    reached a merge gate.

    ⛔ **This case pins its own viewport and states its precondition in numbers**.
    ⚠️ Its first version depended on whatever room the browser
    happened to give the page, and on a `scrollTo` that — like everything else
    on these pages — ANIMATES: it read `0` on this host's browser and the real
    position in the pinned image, and a guard refusing a meaningless reading is
    the only reason that was ever seen.
    """
    # ⛔ **The viewport is PINNED for this case**, so what it reads is the same
    # in both arms of the harness rather than a property of whichever browser
    # ran it — and it is set before `open`, which is the only order that works.
    open_page.resize(*SCROLL_CASE_VIEWPORT)
    open_page.open(origin.url(_case()))

    # ⛔ **The precondition, stated in numbers rather than assumed.** This case
    # needs a document taller than the viewport by MORE than the panel's own
    # height: that surplus is the whole of what the clamp can take away, and
    # without it there is no clamp to read.
    room = open_page.evaluate(ROOM)
    assert room["spare"] > room["panel"], (
        f"this page is {room['document']}px tall in a {room['viewport']}px viewport, so it "
        f"has {room['spare']}px of spare scroll — and the panel is {room['panel']}px of it. "
        "Taking the panel out of flow cannot leave a scroll that no longer fits, so this "
        "check would read nothing"
    )

    label = _state(open_page)["maximise"]["label"]
    _tab_to(open_page, label)
    # ⭐ The reader is put at the END of the page, which is where the document
    # losing the panel's height leaves a scroll that no longer fits.
    open_page.evaluate(TO_THE_END)
    left = _state(open_page)["viewport"]["scrolled"]
    assert left > 0, "the page did not scroll at all, so this reading says nothing"
    # ⛔ **And FAR ENOUGH: past where the shortened document will end.** A reader
    # scrolled less than that is inside what still fits, nothing is clamped, and
    # the check would pass over the defect rather than through it.
    assert left > room["spare"] - room["panel"], (
        f"the reader is at {left} and the shortened document still reaches "
        f"{room['spare'] - room['panel']}, so nothing will be clamped and this check would "
        "pass without ever reaching the defect"
    )

    open_page.press("Enter")
    wide = _until(open_page, lambda reading: reading["expanded"], "expanded")
    # ⚠️ The clamp WHILE EXPANDED is expected and is not the defect: the panel
    # covers the viewport, so nothing of the page behind it is on screen. ⛔ It
    # is asserted so the check is known to be reading the state it is about —
    # without it, a build that never shortened the document would pass here.
    assert wide["viewport"]["scrolled"] < left, (
        f"the document did not shorten under the expansion ({wide['viewport']['scrolled']} "
        f"against {left}), so this check never reaches the clamp it exists for"
    )

    open_page.press("Escape")
    back = _until(open_page, lambda reading: not reading["expanded"], "restored")
    assert back["viewport"]["scrolled"] == left, (
        f"the reader left the page at {left} and came back at "
        f"{back['viewport']['scrolled']} — the restore moved their page by "
        f"{left - back['viewport']['scrolled']}px"
    )
