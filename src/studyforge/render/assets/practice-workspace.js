/* A lesson's practices: the list of cards, and the one workspace a card opens in.

   ⭐ **The user's ruling, whole.** A lesson's practices are one *Practice (n)*
   list of titled cards; opening a card gives a full-screen workspace — the
   problem statement on the left, always visible and scrollable, the editor, Run
   and Submit on the right, Previous and Next between the lesson's practices, and
   Close, which returns the reader to the same place in the lesson.

   ⛔ **Nothing is moved, copied or re-rendered.** Each practice's own section and
   panel are already on the page, under the list; this file HIDES them, and shows
   the chosen pair in the workspace's geometry (`practice-workspace.css`) by one
   attribute on each. ⭐ That is the whole reason the editor can live here: an
   `iframe` MOVED TO ANOTHER PARENT RELOADS, and nothing below appends, removes or
   replaces a node. ⚠️ With no script, nothing is hidden: the practices stay
   readable under the list, which is the `file://` floor (R8).

   ⛔ **No editor loads until a practice is opened, and one at most.** Opening a
   practice raises `studyforge:practice-opened` on its panel, and closing it —
   or opening another — raises `studyforge:practice-closed` first;
   `practice-editor.js` builds the one frame on the first and drops it on the
   second. This file never touches a frame.

   ⛔ **The status is the reader's own record, never the page's.** A card's
   status words are markup, hidden; they are shown only where the SERVED client
   answers what the reader's progress record holds (`studyforge.run.practices`),
   and read again when a run in the workspace settles. ⭐ Over `file://` there is
   no record to ask, and a card says nothing rather than something wrong.

   ⛔ **Close returns the reader to where they were**: the scroll position read
   when the workspace opened is put back `instant` — `reset.css` makes every
   scroll smooth, and a glide is a page still moving when the reader looks — and
   focus goes back to the card that was opened, with `preventScroll`, so exactly
   one thing decides where the page is. Escape closes too, read on the
   DOCUMENT: inside the editor frame, Escape is the editor's.

   ⭐ **An open practice is named in the address**, as its section's own
   fragment, put there with `replaceState` so Back leaves the page as it always
   did. ⚠️ That is what survives the ONE reload a cold editor needs
   (`practice-editor.js`): the page comes back with the practice open, rather
   than closed on a reader who had just opened it. */

(function () {
  'use strict';

  /* The list, its cards, the workspace and its parts. ⚠️ Spelled here and in
     `render/page/practices.py`, which is the single source for what is EMITTED. */
  var REGION = 'section[data-practices]';
  var CARD = 'li[data-practice-card]';
  var CARD_SECTION = 'data-practice-card';
  var CARD_KEY = 'data-practice-key';
  var CARD_CORPUS = 'data-corpus';
  var OPEN_LINK = 'a[data-practices-part="open"]';
  var STATE = '[data-practices-part="state"]';
  var STATE_WORD = 'data-practice-state';
  var WORKSPACE = 'div[data-workspace]';
  var PART = 'data-workspace-part';
  var ACT = 'data-workspace-act';

  /* The mark an open section and panel carry, and the one the document carries
     while the workspace is up. ⛔ Also read by `practice-editor.js`. */
  var OPEN = 'data-workspace-open';
  var LIVE = 'data-practices-live';

  /* What the workspace says to the editor, and what a run says back. */
  var OPENED = 'studyforge:practice-opened';
  var CLOSED = 'studyforge:practice-closed';
  var SETTLED = 'studyforge:practice-settled';
  var ESCAPE = 'Escape';

  var region = document.querySelector(REGION);
  var shell = document.querySelector(WORKSPACE);
  if (!region || !shell) { return; }

  function part(name) {
    return shell.querySelector('[' + PART + '="' + name + '"]');
  }

  function act(name) {
    return shell.querySelector('[' + ACT + '="' + name + '"]');
  }

  /* The panel a practice is worked in: the code panel or the quiz, named by the
     practice's key, which both carry verbatim. */
  function panelOf(key) {
    var found = null;
    [].slice.call(document.querySelectorAll('section[data-practice], section[data-practice-quiz]'))
      .forEach(function (one) {
        var said = one.getAttribute('data-practice') || one.getAttribute('data-practice-quiz');
        if (said === key) { found = one; }
      });
    return found;
  }

  var practices = [].slice.call(region.querySelectorAll(CARD)).map(function (card) {
    return {
      card: card,
      link: card.querySelector(OPEN_LINK),
      section: document.getElementById(card.getAttribute(CARD_SECTION)),
      panel: panelOf(card.getAttribute(CARD_KEY))
    };
  }).filter(function (one) { return one.link && one.section; });
  if (!practices.length) { return; }

  var current = -1;
  var was = 0;

  /* The address with no fragment, and with an open practice's own. */
  function address(hash) {
    try {
      history.replaceState(history.state, '', location.pathname + location.search + hash);
    } catch (ignored) { return; }
  }

  function each(one, visible) {
    [one.section, one.panel].forEach(function (element) {
      if (!element) { return; }
      element.hidden = !visible;
      if (visible) { element.setAttribute(OPEN, ''); } else { element.removeAttribute(OPEN); }
    });
  }

  /* ⭐ **The page under the workspace is `inert`** while it is up, so Tab
     moves through the bar, the statement and the panel and never under the
     cover — the dialog's own focus ring, taken without moving a node. Every
     sibling on the way up to `body` that holds none of the three is marked,
     and exactly those are unmarked again. */
  var stilled = [];

  function still(one) {
    var kept = [shell, one.section, one.panel].filter(Boolean);
    for (var at = shell.parentElement; at && at !== document.documentElement; at = at.parentElement) {
      [].slice.call(at.children).forEach(function (child) {
        if (child.inert || kept.some(function (part) { return child.contains(part); })) { return; }
        child.inert = true;
        stilled.push(child);
      });
    }
  }

  function wake() {
    stilled.forEach(function (child) { child.inert = false; });
    stilled = [];
  }

  function say(name, one) {
    if (one.panel) { one.panel.dispatchEvent(new CustomEvent(name, { bubbles: true })); }
  }

  function leave() {
    if (current < 0) { return; }
    var one = practices[current];
    say(CLOSED, one);
    each(one, false);
    wake();
  }

  function open(index) {
    if (index < 0 || index >= practices.length) { return; }
    if (current < 0) { was = window.pageYOffset || 0; }
    leave();
    current = index;
    var one = practices[index];
    each(one, true);
    part('title').textContent = one.link.textContent;
    act('previous').hidden = index === 0;
    act('next').hidden = index === practices.length - 1;
    shell.hidden = false;
    document.documentElement.setAttribute(OPEN, '');
    still(one);
    one.section.scrollTop = 0;
    part('title').focus({ preventScroll: true });
    address('#' + one.section.id);
    say(OPENED, one);
  }

  function close() {
    if (current < 0) { return; }
    var one = practices[current];
    leave();
    current = -1;
    shell.hidden = true;
    document.documentElement.removeAttribute(OPEN);
    address('');
    /* ⛔ `'instant'`: the argument is at the top of this file. */
    window.scrollTo({ top: was, left: 0, behavior: 'instant' });
    one.link.focus({ preventScroll: true });
  }

  /* --- the list: every practice hidden under it, each card opening its own */
  practices.forEach(function (one, index) {
    each(one, false);
    one.link.addEventListener('click', function (event) {
      event.preventDefault();
      open(index);
    });
  });
  region.setAttribute(LIVE, '');
  part('title').tabIndex = -1;

  act('previous').addEventListener('click', function () { open(current - 1); });
  act('next').addEventListener('click', function () { open(current + 1); });
  act('close').addEventListener('click', close);
  document.addEventListener('keydown', function (event) {
    if (current >= 0 && event.key === ESCAPE) { close(); }
  });

  /* ⭐ A practice named in the address opens at once, and Close then returns
     the reader to its card, which is where they would have chosen it. */
  practices.forEach(function (one, index) {
    if (location.hash !== '#' + one.section.id) { return; }
    open(index);
    var box = one.card.getBoundingClientRect();
    was = Math.max(0, box.top + (window.pageYOffset || 0) - window.innerHeight / 3);
  });

  /* --- the status: the reader's own record, asked of the served origin ---- */
  var run = window.studyforge && window.studyforge.run;
  var asks = run && run.available() && run.practices;

  function paint(card, passed) {
    var slot = card.querySelector(STATE);
    if (!slot) { return; }
    [].slice.call(slot.querySelectorAll('[' + STATE_WORD + ']')).forEach(function (word) {
      var mine = word.getAttribute(STATE_WORD) === (passed ? 'passed' : 'not-started');
      word.hidden = !mine;
    });
    card.setAttribute(STATE_WORD, passed ? 'passed' : 'not-started');
    slot.hidden = false;
  }

  /* ⭐ One question per page: the cards share a unit, so its record is read once
     and each card is painted from the answer. ⛔ An answer that is not one — no
     record, no such unit, a server that could not say — paints nothing. */
  function refresh() {
    if (!asks) { return; }
    var first = practices[0].card;
    var key = first.getAttribute(CARD_KEY) || '';
    var unit = key.slice(0, key.lastIndexOf('/'));
    run.practices(first.getAttribute(CARD_CORPUS), unit).then(function (held) {
      if (!held) { return; }
      practices.forEach(function (one) {
        var own = one.card.getAttribute(CARD_KEY) || '';
        if (one.card.querySelector(STATE)) {
          paint(one.card, held[own.slice(own.lastIndexOf('/') + 1)] === true);
        }
      });
    }, function () { return null; });
  }

  refresh();
  document.addEventListener(SETTLED, refresh);
}());
