"""`W417` — the practice panel read with a keyboard, in a browser, on a SERVED origin.

⛔ **The reading `SF-24` could not take, and said so** (`SF-24/5`). That row
asserted the panel's STRUCTURE — real `<button>`s, `type="button"`, `tabindex`
on the scrolling output, a `role="status"` live region, and a focus handoff
argued in `practice.js` — and could assert nothing about its BEHAVIOUR, because
the controls exist only where `window.studyforge.run.available()` is true and
the whole harness opened `file://`. ⭐ `served.py` is the origin; this module is
the reading.

⚠️ **`QA-02`'s acceptance is what makes this a precondition rather than a
neighbour**: *"full keyboard traversal of a unit page, including the practice
panel"*. A traversal that never sees Run, Submit, Stop or the output region has
not traversed the panel — it has traversed the page the panel is hidden on.

⛔ **Every control is driven by a real key event**, never `element.click()`:
sequential focus navigation and activation are the browser's, and a panel whose
buttons were `<div role=button>` would pass a check that called `click()` on
each in turn.

## ⛔ The controls, both ways round

⭐ Two negative controls, both already declared in `site.DAMAGE` rather than
invented here: `keyboard` — every control given `tabindex="-1"` — must make the
traversal fail, and `contrast` — text on its own ground — must make the panel's
own ratios fail. ⚠️ A third control is the `file://` reading itself, which must
show the offline note and NO buttons: that is the state, not a defect, and a
check that could not tell the two origins apart would prove nothing about
either.
"""

from __future__ import annotations

import time
from collections.abc import Iterator

import pytest

from tests.visual import contrast, served, site, theme
from tests.visual.page import SCHEMES, OpenPage

#: The panel's region, spelled once. ⛔ `data-practice` and never `data-section`:
#: `templates/section.html` carries a CORPUS's own key in `data-section` (R1), so
#: a corpus with a section called `practice` would otherwise be read as the
#: framework's panel (`SF-24`'s decision, and its *For dependents* hands it here).
PANEL_SELECTOR = "section[data-practice]"

#: How many presses a traversal of this page takes before giving up. ⚠️ Larger
#: than `test_keyboard`'s, because a served page carries every stop that one
#: does **plus** the panel's own controls and its output region.
PRESSES = 100

#: Seconds a reading waits for the page to reach a state the script produces.
SETTLE = 15.0

#: What the panel's status says at each stage, in the panel's own words.
#: ⛔ **`FINISHED` and not `Passed.`, and the difference is the subject**: only
#: Submit can pass a practice, so `practice.js` settles a clean *Run* on
#: *Finished.* ⚠️ Asserting the wrong one here would have read as a defect in
#: the panel and been "fixed" by making Run claim a pass.
RUNNING = "Running…"
FINISHED = "Finished."
STOPPED = "Stopped."

#: One reading of the whole panel, taken in the browser in a single evaluation.
#: ⛔ One round trip rather than eight: a panel read field by field is a panel
#: read at eight different moments, and the mid-run state this module is about
#: lasts exactly as long as a check lets it.
PANEL_STATE = """
(() => {
  const panel = document.querySelector('<panel>');
  if (!panel) return null;
  const part = (name) => panel.querySelector('[data-practice-part="' + name + '"]');
  const seen = (el) => !!el && el.checkVisibility();
  const status = part('status');
  const output = part('output');
  const active = document.activeElement;
  return {
    controls: seen(part('controls')),
    offline: seen(part('offline')),
    editor: seen(part('editor')),
    acts: Array.from(panel.querySelectorAll('[data-practice-act]')).map((b) => ({
      act: b.getAttribute('data-practice-act'),
      label: b.textContent.trim(),
      tag: b.tagName,
      type: b.getAttribute('type'),
      visible: b.checkVisibility(),
      disabled: !!b.disabled
    })),
    status: {
      text: status ? status.textContent.trim() : null,
      role: status ? status.getAttribute('role') : null,
      live: status ? status.getAttribute('aria-live') : null
    },
    output: {
      text: output ? output.textContent : null,
      visible: seen(output),
      tabindex: output ? output.getAttribute('tabindex') : null
    },
    focus: {
      tag: active ? active.tagName : '',
      label: active ? active.textContent.trim().slice(0, 40) : '',
      inPanel: !!active && panel.contains(active),
      isStatus: !!active && active === status
    },
    expanded: panel.hasAttribute('data-practice-expanded'),
    box: (() => {
      const box = panel.getBoundingClientRect();
      return { w: box.width, h: box.height, top: box.top, left: box.left };
    })(),
    viewport: { w: window.innerWidth, h: window.innerHeight, scrolled: window.scrollY },
    maximise: (() => {
      const control = part('expand');
      if (!control) return null;
      return {
        label: control.textContent.trim(),
        says: control.getAttribute('aria-expanded'),
        visible: control.checkVisibility()
      };
    })(),
    frames: Array.from(panel.querySelectorAll('iframe')).map((frame) => ({
      slot: frame.parentElement ? frame.parentElement.getAttribute('data-practice-frame') : null,
      ready: !!frame.contentDocument && frame.contentDocument.readyState === 'complete',
      element: frame.dataset.stamp || null,
      inside: (() => {
        try { return frame.contentWindow.studyforgeStamp || null; } catch (e) { return 'gone'; }
      })()
    }))
  };
})()
""".replace("<panel>", PANEL_SELECTOR)


@pytest.fixture
def origin(built_site: site.Site) -> Iterator[served.Served]:
    """One loopback origin over the built tree, bound for this check alone.

    ⛔ **Per check and not per module**, because `ScriptedRuns` holds the state
    of ONE run — started, released, stopped. A shared one would hand the next
    check a run that had already ended, and the mid-run reading every clause
    here depends on would quietly become a post-run reading.
    """
    with served.serving(built_site) as running:
        yield running


def _case() -> str:
    """The unit page the fixture corpora put a practice panel on."""
    return "depth2-unit-01"


def _state(page: OpenPage) -> dict:
    """The whole panel, as the browser holds it now."""
    reading = page.evaluate(PANEL_STATE)
    assert reading is not None, "this page carries no practice panel, so it proves nothing"
    return dict(reading)  # type: ignore[arg-type]


def _until(page: OpenPage, ready, what: str) -> dict:
    """Poll the panel until `ready` says so, or fail naming what was waited for.

    ⛔ Polled and bounded, never slept through: a fixed sleep is either a slow
    check or a flaky one, and the wait here is on a script the page runs.
    """
    deadline = time.monotonic() + SETTLE
    reading = _state(page)
    while time.monotonic() < deadline:
        if ready(reading):
            return reading
        time.sleep(0.05)
        reading = _state(page)
    raise AssertionError(f"the panel never {what}; it reads {reading}")


def _tab_to(page: OpenPage, label: str) -> dict:
    """Tab from the top of the document until focus lands on `label`.

    ⛔ **From the top, with real Tab presses**, so reaching the control is part
    of what is asserted: a check that focused the button directly would pass on
    a panel no keyboard reader can get into.
    """
    page.focus_body()
    for _press in range(PRESSES):
        page.tab()
        here = page.focused()
        if here["label"] == label:
            return here
    raise AssertionError(f"{PRESSES} Tab presses never reached {label!r}")


def _acts(reading: dict, visible: bool = True) -> list[str]:
    """The panel's act buttons, in document order, by the word each carries."""
    return [act["label"] for act in reading["acts"] if act["visible"] == visible]


# --- the precondition: which origin shows what ------------------------------


def test_a_file_shows_the_offline_note_and_a_served_page_shows_the_controls(
    open_page: OpenPage, built_site: site.Site, origin: served.Served
) -> None:
    """⛔ Both origins, in one check, because each is the other's control.

    ⭐ Over `file://` the panel must show the offline note and NO buttons —
    *that is the state, not a defect* (`SF-24/5`), and nothing is disabled
    there either. ⛔ Over a served origin the same bytes must show Run and
    Submit and hide the note, or every clause below would be reading a page
    whose controls were never unhidden and would pass over an empty set.
    """
    open_page.open(built_site.url(_case()))
    as_a_file = _state(open_page)
    assert not as_a_file["controls"], "a page opened from a file offered Run and Submit"
    assert as_a_file["offline"], "a page opened from a file did not say why it cannot run"
    assert _acts(as_a_file) == [], f"a file showed act buttons: {_acts(as_a_file)}"
    assert not any(act["disabled"] for act in as_a_file["acts"]), (
        "a control was emitted DISABLED, and a dead button is a promise the page "
        "cannot keep — the panel's own rule"
    )

    open_page.open(origin.url(_case()))
    as_served = _state(open_page)
    assert as_served["controls"], "a served page did not unhide the panel's controls"
    assert not as_served["offline"], "a served page still says running needs a server"
    assert as_served["editor"], "a served page hid the editor slot instead of explaining it"
    assert _acts(as_served) == ["Run", "Submit"], (
        f"a served page offers {_acts(as_served)}, not Run and Submit"
    )


# --- the traversal ----------------------------------------------------------


def test_every_control_the_panel_offers_is_reached_by_tab_in_document_order(
    open_page: OpenPage, origin: served.Served
) -> None:
    """⭐ `W417` clause 2, the tab order: the panel is part of the page's focus ring."""
    open_page.open(origin.url(_case()))
    offered = _acts(_state(open_page))
    assert offered, "the panel offered nothing, so this traversal asserts nothing"
    reached = [step["label"] for step in open_page.trail(PRESSES)]
    hit = [label for label in reached if label in offered]
    assert hit == offered, f"tab order reached {hit}, the panel offers {offered}"


def test_the_panel_s_controls_are_real_buttons_the_keyboard_can_land_on(
    open_page: OpenPage, origin: served.Served
) -> None:
    """⛔ Read from the element focus LANDED on, never from the markup alone."""
    open_page.open(origin.url(_case()))
    here = _tab_to(open_page, "Run")
    assert here["tag"] == "BUTTON", f"Tab landed on a {here['tag']} where Run should be"
    kinds = {act["label"]: (act["tag"], act["type"]) for act in _state(open_page)["acts"]}
    assert all(kind == ("BUTTON", "button") for kind in kinds.values()), (
        f"a control is not a plain button: {kinds}"
    )


def test_a_page_whose_controls_are_out_of_the_focus_ring_fails_the_traversal(
    open_page: OpenPage, damaged_sites: dict[str, site.Site]
) -> None:
    """⛔ Negative control: `keyboard` damage, served, must make the check above red.

    ⚠️ The panel still UNHIDES — the damage is to the focus ring and not to the
    script — so this control reaches exactly the state the check above passes
    in, minus the one property it asserts.
    """
    with served.serving(damaged_sites["keyboard"]) as broken:
        open_page.open(broken.url(_case()))
        offered = _acts(_state(open_page))
        assert offered, "the control page unhid no controls either, so it proves nothing"
        reached = [step["label"] for step in open_page.trail(PRESSES)]
        assert not [label for label in reached if label in offered], (
            f"a panel whose every control carries tabindex=-1 was traversed: {reached}"
        )


# --- the focus handoff ------------------------------------------------------


def test_pressing_run_with_the_keyboard_hands_focus_to_stop_and_hands_it_back(
    open_page: OpenPage, origin: served.Served
) -> None:
    """⛔ `W417` clause 2, the focus handoff — the reading `practice.js` argued for.

    ⚠️ **The failure this catches is silent and specific.** A button that is
    disabled or hidden while it holds focus drops focus to the document, and a
    keyboard reader is returned to the top of the page mid-run. ⭐ So the start
    moves focus to Stop — the control that has just appeared — and the end gives
    it back to the button that was pressed.
    """
    open_page.open(origin.url(_case()))
    _tab_to(open_page, "Run")
    open_page.press("Enter")

    assert origin.runs.started.wait(SETTLE), "pressing Run with the keyboard started no run"
    live = _until(open_page, lambda r: r["status"]["text"] == RUNNING, "said it was running")
    assert live["focus"]["label"] == "Stop", (
        f"while the run was live focus was on {live['focus']!r}, not the Stop button"
    )
    assert _acts(live) == ["Run", "Submit", "Stop"], (
        f"Stop did not appear while the run was live: {_acts(live)}"
    )
    assert [act["disabled"] for act in live["acts"] if act["label"] != "Stop"] == [True, True], (
        "a starter stayed pressable while a run was already live"
    )

    origin.runs.release.set()
    done = _until(open_page, lambda r: r["status"]["text"] == FINISHED, f"settled on {FINISHED!r}")
    assert done["focus"]["label"] == "Run", (
        f"when the run ended focus was on {done['focus']!r}, not back on the button pressed"
    )
    assert _acts(done) == ["Run", "Submit"], f"Stop outlived its run: {_acts(done)}"
    assert not any(act["disabled"] for act in done["acts"]), "a control stayed disabled at rest"


def test_stop_is_pressable_by_keyboard_and_ends_the_run_it_stops(
    open_page: OpenPage, origin: served.Served
) -> None:
    """⭐ The third act, reached the only way a keyboard reader reaches it: the handoff."""
    open_page.open(origin.url(_case()))
    _tab_to(open_page, "Run")
    open_page.press("Enter")
    assert origin.runs.started.wait(SETTLE), "pressing Run with the keyboard started no run"
    _until(open_page, lambda r: r["focus"]["label"] == "Stop", "handed focus to Stop")

    open_page.press("Enter")
    done = _until(open_page, lambda r: r["status"]["text"] == STOPPED, f"settled on {STOPPED!r}")
    assert origin.runs.stopped, "Stop was pressed and the origin was never asked to stop"
    assert done["focus"]["label"] == "Run", (
        f"after Stop focus was on {done['focus']!r}, not back on the button pressed"
    )


def test_the_control_that_goes_away_takes_focus_with_it_out_of_the_panel(
    open_page: OpenPage, origin: served.Served
) -> None:
    """⛔ The mechanism the two hand-backs above exist for, read rather than believed.

    ⭐ **This is the control under them.** `practice.js`'s own sentence is
    *"focus follows the control that goes away"*, and until this reading that
    was an argument in a comment: if a control that vanished left focus where
    it was, both checks above would pass with no hand-back in the script at all.

    ⛔ **HIDING and not disabling, and the difference was MEASURED rather than
    chosen.** A first draft disabled the focused Stop, which drops focus to the
    document on this host's engine and does NOT on the one the pinned image
    carries — ⚠️ **so the check asserted a property of the BROWSER and read RED
    in the one environment Ruling 40 makes authoritative.** ⭐ Hiding is what
    `live(false)` actually does to Stop when a run ends, and a hidden element is
    out of the focus flow in every engine.
    """
    open_page.open(origin.url(_case()))
    _tab_to(open_page, "Run")
    open_page.press("Enter")
    assert origin.runs.started.wait(SETTLE), "pressing Run with the keyboard started no run"
    _until(open_page, lambda r: r["focus"]["label"] == "Stop", "handed focus to Stop")

    open_page.evaluate("document.querySelector('[data-practice-act=\"stop\"]').hidden = true")
    dropped = _state(open_page)
    assert not dropped["focus"]["inPanel"], (
        "hiding the focused control left focus inside the panel, so neither "
        f"hand-back above is asserting anything: {dropped['focus']}"
    )


# --- the live region and the output -----------------------------------------


def test_the_run_is_announced_in_a_live_region_that_never_takes_focus(
    open_page: OpenPage, origin: served.Served
) -> None:
    """⛔ `W417` clause 2, the live region: what a screen reader is told, and what moves.

    ⭐ **An announcement is not a focus move**, and the two failures are
    opposite: a region that is not live says nothing at all, and a region that
    took focus would drag a reader out of the controls on every state change.
    """
    open_page.open(origin.url(_case()))
    at_rest = _state(open_page)
    assert at_rest["status"]["role"] == "status", "the panel's status is not a status region"
    assert at_rest["status"]["live"] == "polite", "the status region is not announced politely"
    assert at_rest["status"]["text"] == "", "the panel announced something before anything happened"

    said = [at_rest["status"]["text"]]
    _tab_to(open_page, "Run")
    open_page.press("Enter")
    assert origin.runs.started.wait(SETTLE), "pressing Run with the keyboard started no run"
    said.append(
        _until(open_page, lambda r: r["status"]["text"] == RUNNING, "said running")["status"][
            "text"
        ]
    )
    origin.runs.release.set()
    ended = _until(open_page, lambda r: r["status"]["text"] == FINISHED, f"settled on {FINISHED!r}")
    said.append(ended["status"]["text"])

    assert said == ["", RUNNING, FINISHED], f"the live region said {said}"
    assert not ended["focus"]["isStatus"], "the live region took focus when it was written to"
    assert ended["focus"]["inPanel"], "the panel let focus escape while it was announcing"
    reached = [step["label"] for step in open_page.trail(PRESSES)]
    assert FINISHED not in reached, (
        "the live region is a tab stop; a reader has to tab past an announcement"
    )


def test_the_output_region_is_written_to_and_becomes_reachable_by_tab(
    open_page: OpenPage, origin: served.Served
) -> None:
    """⛔ A scrolling region a keyboard reader cannot reach is a region they cannot read.

    ⚠️ It ships `hidden`, so before a run it is correctly NOT in the focus ring
    — a stop on an empty invisible box is noise. ⭐ After a run it carries the
    output and `tabindex="0"` puts it in the ring, which is what this reads.
    """
    open_page.open(origin.url(_case()))
    before = _state(open_page)
    assert not before["output"]["visible"], "the output region was showing before any run"
    assert before["output"]["tabindex"] == "0", "the output region is not focusable at all"
    assert "Output" not in [step["label"] for step in open_page.trail(PRESSES)]

    _tab_to(open_page, "Run")
    open_page.press("Enter")
    assert origin.runs.started.wait(SETTLE), "pressing Run with the keyboard started no run"
    origin.runs.release.set()
    after = _until(open_page, lambda r: r["status"]["text"] == FINISHED, f"settled on {FINISHED!r}")
    assert after["output"]["visible"], "the run wrote output the page never showed"
    for line in served.SCRIPTED:
        assert line in after["output"]["text"], f"the output lost {line!r}"
    # ⚠️ The wire's own last line is in the transcript too, because the client
    # hands EVERY line to `onLine` and reads the verdict off the last of them.
    # ⛔ Asserted as it is rather than as it might be preferred: this module
    # reads the panel, and what the reader sees there is a finding for `QA-02`'s
    # handoff, never a behaviour changed from a test.
    assert served.EXIT_LINE.format(verdict="0") in after["output"]["text"]
    landed = [step["tag"] for step in open_page.trail(PRESSES)]
    assert "PRE" in landed, f"the output region is not in the focus ring after a run: {landed}"


# --- the panel in both themes ------------------------------------------------


@pytest.mark.parametrize("scheme", SCHEMES)
def test_every_control_in_the_panel_shows_a_visible_focus_ring_in_both_themes(
    open_page: OpenPage, origin: served.Served, scheme: str
) -> None:
    """⛔ `QA-02`: a focus ring that is invisible in dark is no ring — now on the panel too."""
    open_page.open(origin.url(_case()), scheme=scheme)
    offered = _acts(_state(open_page))
    invisible = [
        f"{step['label']}: outline {step['outline']}"
        for step in open_page.trail(PRESSES)
        if step["label"] in offered and step["outline"].startswith(("none", "hidden"))
    ]
    assert not invisible, f"{scheme}: a panel control focused with no visible ring: {invisible}"


@pytest.mark.parametrize("scheme", SCHEMES)
def test_every_word_the_panel_paints_clears_aa_in_both_themes(
    open_page: OpenPage, origin: served.Served, scheme: str
) -> None:
    """⛔ `QA-02`'s contrast clause over text no `file://` reading could see.

    ⚠️ **The buttons' own words are the gap this closes.** They ship `hidden`,
    `theme.text_elements` skips what is not painted, and so the panel's controls
    contributed nothing to the element census — for every reading this harness
    had ever taken.
    """
    open_page.open(origin.url(_case()), scheme=scheme)
    failures = []
    for element in theme.text_elements(open_page):
        ratio = contrast.ratio(contrast.parse(element["colour"]), contrast.parse(element["ground"]))
        needed = contrast.threshold(element["size"], element["weight"])
        if ratio + 1e-9 < needed:
            failures.append(
                f"{element['tag']}.{element['cls']} {element['colour']} on "
                f"{element['ground']} = {ratio:.2f} (needs {needed}) — {element['text']!r}"
            )
    assert not failures, f"{scheme}: {len(failures)} element(s) below AA:\n" + "\n".join(failures)


def test_the_panel_s_contrast_check_fails_on_a_stylesheet_whose_text_matches_its_ground(
    open_page: OpenPage, damaged_sites: dict[str, site.Site]
) -> None:
    """⛔ Negative control for the clause above, served, so the controls are painted."""
    with served.serving(damaged_sites["contrast"]) as broken:
        worst = {}
        for scheme in SCHEMES:
            open_page.open(broken.url(_case()), scheme=scheme)
            assert _state(open_page)["controls"], "the control page unhid no controls"
            worst[scheme] = min(
                contrast.ratio(contrast.parse(el["colour"]), contrast.parse(el["ground"]))
                for el in theme.text_elements(open_page)
            )
    assert all(ratio < contrast.AA_NORMAL for ratio in worst.values()), (
        f"a served page whose text colour equals its background measured {worst} — "
        "this reading cannot see a contrast failure"
    )
