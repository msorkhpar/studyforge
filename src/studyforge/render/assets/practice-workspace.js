/* A lesson's practices: the list of cards, and the one workspace a card opens in.

   ⭐ A lesson's practices are one *Practice (n)*
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
   status words are markup, hidden. A code card's are shown only where the
   SERVED client answers what the reader's progress record holds
   (`studyforge.run.practices`); a quiz card's from the reader's browser store
   (`studyforge.progress`), where the quiz page records a pass — served or over
   `file://`. Both are read again when a run or a quiz settles. ⭐ Where there
   is no record to ask, a card says nothing rather than something wrong.

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
   than closed on a reader who had just opened it.

   ⭐ **A practice written in several languages is one card** (`practice-editions.js`). Opening it
   shows ONE edition's statement and panel — the language of the current reading mode, else the
   first — and the switch at the top of the panel swaps the pair: the panel left is told it is
   closed and the one shown is told it is opened, with the same two events, so the editor, Run and
   Submit follow the edition shown and nothing is moved. */

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

  /* ⭐ A quiz opens as ONE PAGE that scrolls as one: its intro above its
     questions, in the page's own flow, with no editor to set beside it and no
     scroll box of its own. The mark on the document chooses that geometry, and
     everything else on the page is marked `AWAY` while the quiz is up
     (`practice-workspace.css`). */
  var KIND = 'data-practice-kind';
  var QUIZ_OPEN = 'data-workspace-quiz';
  var AWAY = 'data-workspace-away';

  function isQuiz(one) { return one.card.getAttribute(KIND) === 'quiz'; }

  function column(one) {
    var root = document.documentElement;
    if (!one || !isQuiz(one)) {
      root.removeAttribute(QUIZ_OPEN);
      return;
    }
    root.setAttribute(QUIZ_OPEN, '');
  }
  var LIVE = 'data-practices-live';

  /* What the workspace says to the editor, and what a run says back. */
  var OPENED = 'studyforge:practice-opened';
  var CLOSED = 'studyforge:practice-closed';
  var SETTLED = 'studyforge:practice-settled';
  var ESCAPE = 'Escape';
  var EXAMPLE = 'details[data-code-example][open]';

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

  /* ⭐ A card's language editions (`[]` for a practice of its own). `section` and `panel` of a card
     are the pair it shows: its first, until an edition is chosen. */
  var editions = window.studyforge.editions;
  var SWITCH = 'button[data-edition-switch]';

  var practices = [].slice.call(region.querySelectorAll(CARD)).map(function (card) {
    var found = editions.of(card, panelOf);
    return {
      card: card,
      link: card.querySelector(OPEN_LINK),
      editions: found,
      lang: found.length ? found[0].lang : null,
      section: document.getElementById(card.getAttribute(CARD_SECTION)),
      panel: panelOf(card.getAttribute(CARD_KEY))
    };
  }).filter(function (one) { return one.link && one.section; });
  if (!practices.length) { return; }

  var current = -1;
  var was = 0;

  /* The address with no fragment, and with an open practice's own. */
  /* ⭐ Where the reader was rides on this history entry's own state, beside
     whatever else it holds, so the one reload brings Close back to it too. */
  var WAS = 'studyforgeWorkspace';

  function address(hash) {
    try {
      var state = Object.assign({}, history.state || {});
      state[WAS] = hash ? was : null;
      history.replaceState(state, '', location.pathname + location.search + hash);
    } catch (ignored) { return; }
  }

  /* Only the pair a card is showing is ever visible: its editions' others stay hidden. */
  function each(one, visible) {
    editions.pairs(one).forEach(function (pair) {
      var shown = visible && pair.section === one.section;
      [pair.section, pair.panel].forEach(function (element) {
        if (!element) { return; }
        element.hidden = !shown;
        if (shown) { element.setAttribute(OPEN, ''); } else { element.removeAttribute(OPEN); }
      });
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
        /* A quiz is read as a page, so what is not part of it is taken out of the flow. */
        if (document.documentElement.hasAttribute(QUIZ_OPEN)) { child.setAttribute(AWAY, ''); }
        stilled.push(child);
      });
    }
  }

  function wake() {
    stilled.forEach(function (child) { child.inert = false; child.removeAttribute(AWAY); });
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
    editions.rows(one, false);
    column(null);
    wake();
  }

  function open(index, lang) {
    if (index < 0 || index >= practices.length) { return; }
    if (current < 0) { was = window.pageYOffset || 0; }
    leave();
    current = index;
    var one = practices[index];
    if (one.editions.length) {
      editions.use(one, editions.byLang(one, lang) || editions.preferred(one, shell));
    }
    each(one, true);
    editions.rows(one, true);
    part('title').textContent = one.link.textContent;
    act('previous').hidden = index === 0;
    act('next').hidden = index === practices.length - 1;
    shell.hidden = false;
    document.documentElement.setAttribute(OPEN, '');
    column(one);
    still(one);
    one.section.scrollTop = 0;
    if (isQuiz(one)) { window.scrollTo({ top: 0, left: 0, behavior: 'instant' }); }
    part('title').focus({ preventScroll: true });
    address('#' + one.section.id);
    /* ⛔ One editor on the page at most: an expanded code example is closed —
       an attribute, so nothing moves — and `code-links.js` drops its frames. */
    [].slice.call(document.querySelectorAll(EXAMPLE)).forEach(function (entry) { entry.open = false; });
    say(OPENED, one);
  }

  /* ⭐ The switch: another edition of the open practice takes the place of the one shown. */
  function switchTo(lang) {
    if (current < 0) { return; }
    var one = practices[current];
    var to = editions.byLang(one, lang);
    if (!to || to.section === one.section) { return; }
    say(CLOSED, one);
    each(one, false);
    wake();
    editions.use(one, to);
    each(one, true);
    editions.rows(one, true);
    still(one);
    one.section.scrollTop = 0;
    address('#' + one.section.id);
    say(OPENED, one);
    var pressed = one.panel && one.panel.querySelector(SWITCH + '[aria-pressed="true"]');
    if (pressed) { pressed.focus({ preventScroll: true }); }
  }

  document.addEventListener('click', function (event) {
    var button = event.target.closest ? event.target.closest(SWITCH) : null;
    if (button) { switchTo(button.getAttribute('data-edition-switch')); }
  });

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
  window.addEventListener('resize', function () { if (current >= 0) { column(practices[current]); } });

  /* ⭐ A practice named in the address opens at once, and Close then returns
     the reader to where the entry's state says they were — or, with none, to
     the practice's card, which is where they would have chosen it. */
  practices.forEach(function (one, index) {
    var named = editions.pairs(one).filter(function (pair) {
      return location.hash === '#' + pair.section.id;
    })[0];
    if (!named) { return; }
    var kept = history.state && history.state[WAS];
    open(index, named.lang);
    var box = one.card.getBoundingClientRect();
    was = typeof kept === 'number'
      ? kept : Math.max(0, box.top + (window.pageYOffset || 0) - window.innerHeight / 3);
  });

  /* --- the status: the reader's own record ------------------------------ */
  /* ⭐ A code practice's pass is the served origin's (a run established it);
     a quiz's is the reader's browser store, where the quiz page kept it (nothing about a quiz is a server's). */
  var run = window.studyforge && window.studyforge.run;
  var asks = run && run.available() && run.practices;
  var store = window.studyforge && window.studyforge.progress;
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

  /* ⭐ One question per page for the code cards: they share a unit, so its
     record is read once. ⛔ An answer that is not one — no record, no such
     unit, a server that could not say — paints nothing. A quiz card is read
     from the store, served or not; with no store it says nothing. ⛔ A quiz's
     own settling asks the server nothing: answering a quiz makes no request. */
  function refresh(event) {
    practices.forEach(function (one) {
      if (isQuiz(one) && store && store.supported()) {
        paint(one.card, store.passedQuiz(one.card.getAttribute(CARD_KEY) || ''));
      }
    });
    var quizzed = !!event && event.target.hasAttribute('data-practice-quiz');
    if (!asks || quizzed) { return; }
    var first = practices[0].card;
    var key = first.getAttribute(CARD_KEY) || '';
    var unit = key.slice(0, key.lastIndexOf('/'));
    run.practices(first.getAttribute(CARD_CORPUS), unit).then(function (held) {
      if (!held) { return; }
      practices.forEach(function (one) {
        var own = one.card.getAttribute(CARD_KEY) || '';
        if (one.editions.length) {
          if (one.card.querySelector(STATE)) { editions.paint(one, held); }
        } else if (!isQuiz(one) && one.card.querySelector(STATE)) {
          paint(one.card, held[own.slice(own.lastIndexOf('/') + 1)] === true);
        }
      });
    }, function () { return null; });
  }

  refresh();
  document.addEventListener(SETTLED, refresh);
}());
