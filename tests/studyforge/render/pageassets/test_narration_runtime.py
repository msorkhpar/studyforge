"""The real player, run under a real JS runtime, against a stub of the real page.

⛔ **The dev image pins a JS runtime, so in the environment that
certifies a result this file does not skip — it fails.** On a contributor's host
with no runtime it skips, because a host without Docker is not the thing being
certified. ⭐ `test_narration.py` holds everything a text can establish and needs
no runtime at all; this file is what establishes that the thing *runs*.

## ⛔ Why the DOM is a stub and not a browser

⚠️ The pinned image has no browser and the framework takes no
dependency that would bring one, so "does the highlight move" cannot be asked of
a real engine here. ⭐ What CAN be asked is whether the part's own logic is
right, and the stub is deliberately **small and dumb**: it implements the six DOM
calls the part makes and nothing else, so a part that reached for a seventh fails
here loudly rather than being quietly accommodated.

⛔ **The page it is run against is the REAL template.** `templates/player.html` is
read off disk and parsed by the stub, so the ids, the `[data-state]` spans and the
`hidden` attributes under test are the ones a page actually ships — not a fixture
that agrees with the script because the same person wrote both.

## ⚠️ What this cannot say

⛔ It cannot say a clip plays, that autoplay policy behaves as the browser
documents it, or that the highlight is visible. Those are browser readings and
belong in `tests/visual/` with the browser and version they were taken in.
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess

import pytest

from studyforge.render import templates
from studyforge.render.pageassets import text

#: Set by `docker/dev/Dockerfile`. ⭐ Its presence means "this run is the one
#: that certifies a result", which is what turns an absent runtime from a skip
#: into a failure.
DEV_CONTAINER = "STUDYFORGE_DEV_CONTAINER"

#: The part under test and the markup it is the other side of.
PART = "narration.js"
PLAYER = "player.html"

#: The stub DOM, and the harness that drives one scenario through it.
#:
#: ⛔ **It implements only what `narration.js` actually calls.** A stub that
#: answered everything would let the part drift into APIs nobody checked; this one
#: throws on an unknown call, so the failure is here rather than in a browser.
DRIVER = r"""
'use strict';
const fs = require('fs');
const spec = JSON.parse(fs.readFileSync(process.argv[3], 'utf8'));

let nextId = 0;
class El {
  constructor(tag, attrs) {
    this.tagName = (tag || 'div').toUpperCase();
    this.attributes = Object.assign({}, attrs || {});
    this.children = [];
    this.parent = null;
    this.listeners = {};
    this.textContent = '';
    this.hidden = 'hidden' in this.attributes;
    this.disabled = false;
    this.isContentEditable = false;
    this.scrolled = 0;
    this.style = { props: {}, setProperty(k, v) { this.props[k] = v; } };
    this.uid = nextId++;
  }
  get id() { return this.attributes.id || ''; }
  /* ⚠️ A real <select> takes its value from the option marked selected, and the
     part reads `.value` rather than an attribute — so the stub has to do the same
     or the speed control would look wired when it is not. */
  get value() {
    if ('value' in this.attributes) { return this.attributes.value; }
    const chosen = this.querySelectorAll('option').filter(o => o.hasAttribute('selected'))[0];
    return chosen ? chosen.getAttribute('value') : '';
  }
  set value(v) { this.attributes.value = String(v); }
  setAttribute(name, value) { this.attributes[name] = String(value); }
  getAttribute(name) { return name in this.attributes ? this.attributes[name] : null; }
  removeAttribute(name) { delete this.attributes[name]; }
  hasAttribute(name) { return name in this.attributes; }
  append(child) { child.parent = this; this.children.push(child); return child; }
  descendants() {
    let all = [];
    for (const child of this.children) { all.push(child); all = all.concat(child.descendants()); }
    return all;
  }
  matches(selector) {
    if (selector.startsWith('[') && selector.endsWith(']')) {
      return this.hasAttribute(selector.slice(1, -1));
    }
    return selector.split(',').map(s => s.trim().toUpperCase()).indexOf(this.tagName) !== -1;
  }
  querySelectorAll(selector) { return this.descendants().filter(el => el.matches(selector)); }
  querySelector(selector) { return this.querySelectorAll(selector)[0] || null; }
  closest(selector) {
    let node = this;
    while (node) { if (node.matches(selector)) { return node; } node = node.parent; }
    return null;
  }
  addEventListener(name, fn) { (this.listeners[name] = this.listeners[name] || []).push(fn); }
  fire(name, event) {
    (this.listeners[name] || []).forEach(fn => fn(Object.assign({ target: this }, event || {})));
  }
  scrollIntoView() { this.scrolled += 1; }
}

/* The real template, parsed just far enough. ⛔ Attributes and nesting only —
   this is not an HTML parser and must never grow into one. */
function parse(markup) {
  const root = new El('body');
  const stack = [root];
  const token = /<(\/?)([a-z0-9]+)((?:\s+[a-z-]+(?:="[^"]*")?)*)\s*>|([^<]+)/gi;
  let m;
  while ((m = token.exec(markup)) !== null) {
    if (m[4] !== undefined) {
      if (m[4].trim()) { stack[stack.length - 1].textContent += m[4]; }
      continue;
    }
    if (m[1]) { if (stack.length > 1) { stack.pop(); } continue; }
    const attrs = {};
    const attr = /([a-z-]+)(?:="([^"]*)")?/gi;
    let a;
    while ((a = attr.exec(m[3] || '')) !== null) { attrs[a[1]] = a[2] === undefined ? '' : a[2]; }
    const el = stack[stack.length - 1].append(new El(m[2], attrs));
    const void_ = ['audio', 'input', 'br', 'hr', 'img'];
    if (void_.indexOf(m[2].toLowerCase()) === -1) { stack.push(el); }
  }
  return root;
}

const body = parse(spec.player);
const content = body.append(new El('main', { id: 'content' }));
const section = content.append(new El('section'));
section.append(new El('h2')).textContent = spec.heading || '';
const passages = spec.passages.map(source => {
  const attrs = source === null ? {} : { 'data-audio': source };
  const el = section.append(new El('p', attrs));
  el.textContent = 'passage';
  return el;
});

/* ⚠️ `[data-audio]` must be reachable, and so must every id — the part looks
   both up, and a stub that answered only one would prove half the wiring. */
const byId = {};
body.descendants().forEach(el => { if (el.id) { byId[el.id] = el; } });

const audio = byId.narrator;
audio.paused = true;
audio.duration = 10;
audio.currentTime = 0;
audio.playbackRate = 1;
audio.plays = 0;
audio.play = function () {
  this.plays += 1;
  if (spec.blockAutoplay) { return Promise.reject(new Error('blocked')); }
  this.paused = false;
  return Promise.resolve();
};
audio.pause = function () { this.paused = true; };

const documentStub = {
  getElementById(id) { return byId[id] || null; },
  querySelectorAll(sel) { return body.querySelectorAll(sel); },
  addEventListener(name, fn) { body.addEventListener(name, fn); },
  fire(name, event) { body.fire(name, event); },
};

global.window = { matchMedia: () => ({ matches: false }) };
global.document = documentStub;

eval(fs.readFileSync(process.argv[2], 'utf8'));

function keys() {
  return (spec.keys || []).forEach(key => {
    documentStub.fire('keydown', { key, target: { tagName: 'BODY' }, preventDefault() {} });
  });
}

let early = null;
function sayingNow() {
  return byId.status.querySelectorAll('[data-state]')
    .filter(el => !el.hidden).map(el => el.getAttribute('data-state'));
}

const actions = {
  none() {},
  play() { byId.play.fire('click'); },
  playThenPause() { byId.play.fire('click'); byId.play.fire('click'); },
  next() { byId.next.fire('click'); },
  previous() { byId.next.fire('click'); byId.previous.fire('click'); },
  ended() { byId.play.fire('click'); audio.fire('ended'); },
  error() { byId.play.fire('click'); audio.fire('error'); },
  /* ⛔ The two orders a missing clip's `error` and `play()` rejection arrive in.
     The mid-scenario reading proves which one came first. */
  errorThenRejection() {
    byId.play.fire('click');
    audio.fire('error');
    early = sayingNow();
  },
  rejectionThenError() {
    byId.play.fire('click');
    setTimeout(function () { early = sayingNow(); audio.fire('error'); }, 0);
  },
  clickSecond() { passages[1].fire('click', { target: passages[1] }); },
  clickLink() {
    const link = passages[1].append(new El('a'));
    passages[1].fire('click', { target: link });
  },
  speed() { byId.speed.value = '1.5'; byId.speed.fire('change'); },
  progress() { byId.play.fire('click'); audio.currentTime = 5; audio.fire('timeupdate'); },
  keys: keys,
};
actions[spec.action || 'none']();

/* ⚠️ Promise rejections settle on the microtask queue, so the reading is taken
   after it drains — otherwise the autoplay case reports the state before the
   browser's refusal has arrived. */
setTimeout(function () {
  process.stdout.write(JSON.stringify({
    hidden: byId.player.hidden,
    speaking: passages.map(el => el.getAttribute('data-speaking')),
    src: audio.src === undefined ? null : audio.src,
    plays: audio.plays,
    paused: audio.paused,
    rate: audio.playbackRate,
    counter: byId.counter.textContent,
    where: byId.where.textContent,
    progress: byId.fill.style.props['--progress'],
    valuenow: byId.track.getAttribute('aria-valuenow'),
    statusHidden: byId.status.hidden,
    saying: byId.status.querySelectorAll('[data-state]')
      .filter(el => !el.hidden).map(el => el.getAttribute('data-state')),
    face: byId.play.querySelectorAll('[data-state]')
      .filter(el => !el.hidden).map(el => el.getAttribute('data-state')),
    disabled: ['previous', 'play', 'next', 'speed'].map(id => byId[id].disabled),
    scrolled: passages.map(el => el.scrolled),
    early: early,
  }));
}, 0);
"""

#: Three passages, each with a clip, as a narrated page carries them. ⛔ Hrefs,
#: because that is what the renderer writes — this file never composes one from a
#: speech id, for the same reason the player does not.
THREE = [
    "unit-01.audio/a.shared.b1-11111111.mp3",
    "unit-01.audio/a.shared.b2-22222222.mp3",
    "unit-01.audio/a.shared.b3-33333333.mp3",
]


def node():
    """The pinned JS runtime — or a skip on a host, a failure in the image."""
    runtime = shutil.which("node")
    if runtime is not None:
        return runtime
    if os.environ.get(DEV_CONTAINER):
        pytest.fail(
            "no JavaScript runtime on PATH inside the dev image, where "
            "docker/dev/Dockerfile pins one. This is a failure rather than a skip "
            "because the pinned environment is the one that certifies a result "
            "(R15) — rebuild the image rather than reading this run as green."
        )
    pytest.skip(
        "node is not installed on this host, so the narration player cannot be run "
        "here. ⭐ It is NOT skipped in the pinned dev image, which installs a "
        "runtime — run `docker/dev/check python3 -m pytest` for the authoritative "
        "result. The runtime-free half of this check is test_narration.py, which "
        "always runs."
    )
    return None  # pragma: no cover - unreachable; pytest.skip raises


def run(tmp_path, **spec):
    """Drive one scenario through the real part and return what the page ended up as."""
    spec.setdefault("passages", THREE)
    spec.setdefault("player", templates.template(PLAYER).template)
    driver = tmp_path / "drive.js"
    driver.write_text(DRIVER, encoding="utf-8")
    part = tmp_path / PART
    part.write_text(text(PART), encoding="utf-8")
    request = tmp_path / "spec.json"
    request.write_text(json.dumps(spec), encoding="utf-8")
    result = subprocess.run(  # noqa: S603 - fixed argv, no shell
        [node(), str(driver), str(part), str(request)],
        capture_output=True,
        text=True,
        timeout=60,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout)


# --- it comes up ------------------------------------------------------------


def test_the_transport_is_unhidden_once_there_is_something_to_play(tmp_path):
    # ⛔ The other half of "no dead control": the template ships it hidden, so if
    # this never ran the reader would have no transport at all.
    assert run(tmp_path)["hidden"] is False


def test_nothing_is_lit_before_anything_is_pressed(tmp_path):
    # ⛔ A marker beside the first heading before anything played would read
    # as narration already under way. The transport's own line says
    # where it will start; the page lights nothing until the reader starts it.
    assert run(tmp_path)["speaking"] == [None, None, None]


def test_pressing_play_is_what_lights_the_first_passage(tmp_path):
    # ⭐ The other way (R12): the same reading after a press is lit, so the one
    # above is not a highlight that never lights at all.
    assert run(tmp_path, action="play")["speaking"] == ["true", None, None]


def test_it_says_nothing_when_there_is_nothing_to_say(tmp_path):
    reading = run(tmp_path)
    assert reading["saying"] == []
    assert reading["statusHidden"] is True


def test_the_count_is_digits_and_the_place_is_the_page_s_own_heading(tmp_path):
    # ⛔ R13: the only two things written into the page are a count and text
    # copied off the page. Neither is prose this part authored.
    reading = run(tmp_path, heading="Getting started")
    assert reading["counter"] == "1 / 3"
    assert reading["where"] == "Getting started"


# --- playing ----------------------------------------------------------------


def test_pressing_play_loads_the_first_clip_the_page_named(tmp_path):
    # ⛔ The src is the page's own value, character for character: the player
    # composes no path (R4) and this is where that is actually observed.
    reading = run(tmp_path, action="play")
    assert reading["src"] == THREE[0]
    assert reading["plays"] == 1
    assert reading["face"] == ["playing"]


def test_pressing_play_twice_pauses_rather_than_restarting(tmp_path):
    reading = run(tmp_path, action="playThenPause")
    assert reading["paused"] is True
    assert reading["face"] == ["paused"]


def test_a_clip_ending_advances_to_the_next_and_the_highlight_goes_with_it(tmp_path):
    # ⭐ THE ROW'S FIRST ACCEPTANCE CLAUSE: the highlight tracks playback across a
    # unit, at speech-unit granularity and with no timing data anywhere.
    reading = run(tmp_path, action="ended")
    assert reading["src"] == THREE[1]
    assert reading["speaking"] == [None, "true", None]


def test_next_and_previous_move_one_passage_and_scroll_it_into_view(tmp_path):
    forward = run(tmp_path, action="next")
    assert forward["speaking"] == [None, "true", None]
    assert forward["scrolled"][1] == 1
    back = run(tmp_path, action="previous")
    assert back["speaking"] == ["true", None, None]


def test_clicking_a_passage_starts_reading_from_there(tmp_path):
    # The template promises this in so many words, so it is a contract.
    reading = run(tmp_path, action="clickSecond")
    assert reading["src"] == THREE[1]
    assert reading["speaking"] == [None, "true", None]


def test_clicking_a_link_inside_a_passage_is_the_link_s_and_not_the_narrator_s(tmp_path):
    # ⚠️ A reader following a footnote must not also start audio.
    reading = run(tmp_path, action="clickLink")
    assert reading["plays"] == 0
    assert reading["speaking"] == [None, None, None]


def test_the_speed_control_reaches_the_audio(tmp_path):
    assert run(tmp_path, action="speed")["rate"] == 1.5


def test_progress_is_through_the_unit_and_not_through_one_clip(tmp_path):
    # ⛔ `#track` says "Progress through this unit" in its own aria-label. Half of
    # the first clip of three is one sixth of the unit, not one half of it.
    reading = run(tmp_path, action="progress")
    assert reading["progress"] == "16.7%"
    assert reading["valuenow"] == "16.7"


# --- it degrades honestly (R6) ----------------------------------------------


def test_a_clip_that_is_not_on_disk_says_so_instead_of_pretending(tmp_path):
    # ⛔ The row's third acceptance clause, at one passage.
    reading = run(tmp_path, action="error")
    assert reading["saying"] == ["missing"]
    assert reading["statusHidden"] is False
    assert reading["face"] == ["paused"]


def test_a_unit_with_no_audio_at_all_states_it_and_leaves_no_dead_control(tmp_path):
    # ⛔ The same clause at the whole unit: the renderer wrote the attribute and
    # synthesis produced nothing. ⚠️ The controls are DISABLED and the reason is
    # SHOWN — hiding the transport would be honest about the control and silent
    # about the cause.
    reading = run(tmp_path, passages=["", "", ""])
    assert reading["saying"] == ["none"]
    assert reading["disabled"] == [True, True, True, True]
    assert reading["hidden"] is False


def test_a_browser_that_refuses_to_start_audio_is_a_stated_state_and_not_an_error(tmp_path):
    # ⛔ The row's second honest state: known, with a stated remedy — press play
    # once — and neither hidden nor treated as a failure.
    reading = run(tmp_path, action="play", blockAutoplay=True)
    assert reading["saying"] == ["blocked"]
    assert reading["face"] == ["paused"]


def test_W276_an_ERROR_before_the_REJECTION_keeps_missing_and_play_stays_enabled(tmp_path):
    # ⛔ Clause 1 and 3, first order: the clip is not on disk, `error` arrives, and the
    # rejection that follows must not replace *missing* with *press play once*.
    reading = run(tmp_path, action="errorThenRejection", blockAutoplay=True)
    assert reading["early"] == ["missing"], "⛔ born vacuous: the error must arrive first"
    assert reading["saying"] == ["missing"]
    assert reading["face"] == ["paused"]
    assert reading["disabled"] == [False, False, False, False], "two passages still play"


def test_W276_the_SAME_order_with_NO_passage_left_reads_none_and_disables_play(tmp_path):
    # ⛔ Clause 1: play is disabled once no passage is playable, whichever event came last.
    reading = run(tmp_path, action="errorThenRejection", blockAutoplay=True, passages=THREE[:1])
    assert reading["early"] == ["none"]
    assert reading["saying"] == ["none"]
    assert reading["disabled"] == [True, True, True, True]


def test_W276_a_REJECTION_before_the_ERROR_reads_blocked_then_missing(tmp_path):
    # ⛔ Clause 3, the other order: the refusal is stated first, and the error that
    # proves the clip is absent then replaces it.
    reading = run(tmp_path, action="rejectionThenError", blockAutoplay=True)
    assert reading["early"] == ["blocked"], "⛔ born vacuous: the rejection must arrive first"
    assert reading["saying"] == ["missing"]
    assert reading["face"] == ["paused"]


def test_a_page_with_no_narrated_passage_at_all_leaves_the_transport_hidden(tmp_path):
    # ⚠️ The gate in `page.document` means this markup should not be on such a
    # page at all — but if it ever is, the part must not unhide a transport with
    # nothing behind it.
    assert run(tmp_path, passages=[])["hidden"] is True


# --- the keyboard -----------------------------------------------------------


def test_space_plays_and_the_arrows_move(tmp_path):
    # ⭐ The row's fourth acceptance clause, and the template's own sentence.
    assert run(tmp_path, action="keys", keys=[" "])["plays"] == 1
    assert run(tmp_path, action="keys", keys=["ArrowRight"])["speaking"] == [None, "true", None]
    right_then_left = run(tmp_path, action="keys", keys=["ArrowRight", "ArrowLeft"])
    assert right_then_left["speaking"] == ["true", None, None]
