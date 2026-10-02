/* The reader's reading mode: the first-visit question, the switch, and the choice kept.

   ⛔ WRITTEN ONLY FOR A CORPUS THAT DECLARES MODES, as its own file. The shared
   script never carries a line of it.

   ⚠️ IT IS LINKED IN THE HEAD, NOT AT THE FOOT OF THE BODY: a `<script>` at body
   level is a row of the page's grid, and the rail spans a fixed count of them.
   So this part waits for `DOMContentLoaded`, which comes after every deferred
   script, `page.js` among them, and reads the store's published name with no
   existence guard: a wrong order would fail loudly, as the theme's does.

   ⭐ WHAT THE MARKUP ALREADY DID. The page ships `data-mode="<default mode>"` on
   the root element and `modes.css` hides the sections of the other languages by
   it, so with this script off the page is the default mode. This script only
   changes the attribute; it shows and hides nothing itself.

   ⛔ THE STORE IS `study-progress.js`'s DISPLAY RECORD, as the theme's is. Every
   read and write goes through its published name, guarded by that store's own
   try/catch, and a refused store costs the page nothing it was showing. The
   head's boot reads a `sessionStorage` cache of the choice, kept by the store,
   so a later page of the same tab does not flash the default for a frame.

   ⭐ WHEN THE QUESTION IS ASKED. Once, on a first visit: when nothing usable is
   stored. Where the page is opened from a file the stored answer is not read at
   all and the question is asked on every load, because a file page has no
   origin to keep it for. Where the browser refuses to keep anything the question
   is not asked (an answer that cannot be remembered would be asked of the reader
   on every page), and the switch still changes the page being read.

   ⭐ The words are in `page.html`'s templates (R13): this file toggles `hidden`
   and `aria-pressed` and types nothing. */

(function () {
  'use strict';

  function start() {
    var PREFERENCE = 'mode';
    var ATTRIBUTE = 'data-mode';
    var SWITCH = '[data-section="mode"]';
    var QUESTION = '[data-section="mode-question"]';
    var CHOICE = 'data-mode-choice';

    var store = window.studyforge.progress;
    var root = document.documentElement;

    var control = document.querySelector(SWITCH);
    var question = document.querySelector(QUESTION);
    if (!control || !question) { return; }

    var fallback = control.getAttribute('data-mode-default');
    var chosen = [].slice.call(control.querySelectorAll('[' + CHOICE + ']'));
    var offered = [].slice.call(question.querySelectorAll('[' + CHOICE + ']'));
    var known = chosen.map(function (button) { return button.getAttribute(CHOICE); });
    if (!known.length || known.indexOf(fallback) === -1) { return; }

    var fromFile = window.location.protocol === 'file:';

    /* A stored value this does not know is no answer at all. */
    function stored() {
      if (fromFile) { return null; }
      var held = store.preference(PREFERENCE);
      return known.indexOf(held) === -1 ? null : held;
    }

    function show(mode) {
      root.setAttribute(ATTRIBUTE, mode);
      chosen.forEach(function (button) {
        button.setAttribute('aria-pressed', button.getAttribute(CHOICE) === mode ? 'true' : 'false');
      });
    }

    function close() {
      var open = !question.hidden;
      question.hidden = true;
      return open;
    }

    function choose(mode) {
      var kept = store.prefer(PREFERENCE, mode);
      /* The cache follows what the store kept, and holds nothing when it kept nothing. */
      store.cache(PREFERENCE, kept && !fromFile ? mode : null);
      show(mode);
      if (close()) {
        var pressed = control.querySelector('[aria-pressed="true"]');
        if (pressed) { pressed.focus(); }
      }
    }

    var held = stored();
    show(held === null ? fallback : held);
    control.hidden = false;

    chosen.concat(offered).forEach(function (button) {
      button.addEventListener('click', function () { choose(button.getAttribute(CHOICE)); });
    });

    question.addEventListener('keydown', function (event) {
      if (event.key === 'Escape') { close(); }
    });

    if (held === null && (fromFile || store.supported())) {
      question.hidden = false;
      if (offered.length) { offered[0].focus(); }
    }
  }

  /* ⚠️ Not `readyState === 'loading'`: while a deferred script runs the state is
     already `interactive`, and `DOMContentLoaded` has not fired yet. */
  if (document.readyState === 'complete') {
    start();
  } else {
    document.addEventListener('DOMContentLoaded', start);
  }
}());
