/* The mark-as-read control, and the marks surfaced on the two lists.

   ⛔ **The only consumer of the store, and it touches no storage itself.**
   `study-progress.js` owns every read and every write; this file asks it
   questions. Two implementations would be a mark written under one name and
   read back under another, with no symptom but a badge that never lights.

   ⛔ **The store is read through its published name with NO existence guard,
   and that is the ruling rather than an oversight.** The extraction source
   composed its store AFTER the script that read it, guarded the access, and
   shipped a feature that silently never came back with a green suite behind
   it. ⚠️ Here a bundle composed in the wrong order throws on the first line
   that needs the store — loudly, in the console, on the page — and the
   ordering is asserted against the real composition as well. ⛔ This part is
   LAST in `bundle.SCRIPT_PARTS` so that a throw of its own reaches nothing
   else.

   ⛔ **Progressive enhancement, and the control ships HIDDEN.** The region,
   its button and the sentence about where the mark lives are all markup
   (`templates/read-mark.html`) — so nothing here types a word a reader sees
   (R13) — and the region stays hidden until this file has a working store to
   back it. ⚠️ With scripting off, or with site data blocked, the reader is
   shown nothing rather than a control that cannot do anything: a control that
   does nothing is worse than no control.

   ⛔ **Joined by the address and nothing else**. The control carries
   the unit key `Address.unit_key` minted in Python; a row on the root index or
   on a container page carries that same key as its `id`, which is also its
   deep-link anchor. Nothing here composes a key, derives one from a position,
   or reads one back out of an href. */

(function () {
  'use strict';

  /* The first line that needs the store, deliberately unguarded — see above. */
  if (!window.studyforge.progress.supported()) { return; }
  var store = window.studyforge.progress;

  /* The region the unit page carries, and the attribute holding its key. ⚠️
     Spelled here and in `render/page/mark.py`, which is the same two-sided
     spelling every hook on this page has: markup and script cannot import one
     another, and the Python side is the single source for what is EMITTED. */
  var CONTROL = 'section[data-section="read-mark"]';
  var UNIT = 'data-unit';

  /* Whether the reader has marked this. ⚠️ `data-marked` is published in
     `pageassets.SURFACE_HOOKS` because `chrome.css` reaches it; the two values
     below are this file's own and nothing styles them. */
  var MARKED = 'data-marked';
  var STATE = 'data-state';
  var READ = 'read';
  var UNREAD = 'unread';

  /* A row is an `<li>`, checked rather than assumed. ⚠️ A unit page's own
     sections carry a corpus's keys as ids, and a corpus may name one anything
     at all (R1) — so an id that matches a mark is only treated as a row when
     it actually is one. */
  function surface(keys) {
    keys.forEach(function (key) {
      var row = document.getElementById(key);
      if (row && row.tagName === 'LI') { row.setAttribute(MARKED, 'true'); }
    });
  }

  surface(store.marks());

  var control = document.querySelector(CONTROL);
  if (!control) { return; }
  var key = control.getAttribute(UNIT);
  var button = control.querySelector('button');
  if (!key || !button) { return; }
  var labels = [].slice.call(control.querySelectorAll('[' + STATE + ']'));

  /* ⛔ Shown from the STORE's answer, never from what was just pressed: a
     write the browser refused must not leave the page claiming it happened. */
  function shown(marked) {
    control.setAttribute(MARKED, marked ? 'true' : 'false');
    button.setAttribute('aria-pressed', marked ? 'true' : 'false');
    labels.forEach(function (label) {
      label.hidden = label.getAttribute(STATE) !== (marked ? READ : UNREAD);
    });
  }

  /* ⭐ THE NEXT UNIT MARKS THIS ONE READ AND CONTINUES (the 2026-11 redesign).
     Each next link carries two labels (`link-next.html`): *Up next*, shown, and
     *Mark read & continue*, hidden. While this unit is unmarked the second is
     the one shown, and following the link marks the unit before the browser
     leaves. ⛔ The link is still a plain link: with no script it navigates and
     marks nothing. Every next link of a chain is relabelled, because a reading
     mode may show another one; and, as everywhere here, no word is typed. */
  var NEXT = 'nav[aria-label="Between units"] a[rel="next"], nav[aria-label="Between units"] a[data-pager="next"]';
  var CONTINUE = 'data-continue';
  var nexts = [].slice.call(document.querySelectorAll(NEXT));

  function relabel(marked) {
    nexts.forEach(function (link) {
      var going = link.querySelector('span[' + CONTINUE + ']');
      var plain = link.querySelector('span:not([' + CONTINUE + '])');
      if (going && plain) {
        going.hidden = marked;
        plain.hidden = !marked;
      }
    });
  }

  function show(marked) {
    shown(marked);
    relabel(marked);
  }

  show(store.marked(key));
  control.hidden = false;

  button.addEventListener('click', function () {
    if (store.marked(key)) { store.unmark(key); } else { store.mark(key); }
    show(store.marked(key));
  });

  nexts.forEach(function (link) {
    link.addEventListener('click', function () {
      if (!store.marked(key)) { store.mark(key); }
    });
  });
}());
