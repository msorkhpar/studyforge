/* The reader's choice of theme: light, dark, or whatever their system says.

   ⛔ **The user asked for BOTH THEMES to be reachable from the page**
   (`W388` stage 2, 2026-09-19: *"have the both dark and light themes in
   studyforge as well"*). `palette.css` has carried both since `W362` and the
   guards `[data-theme="light"]` and `[data-theme="dark"]` since then; until now
   nothing wrote either, so a reader whose system said light could not read the
   dark page at all.

   ⛔ **THREE STATES, AND THE THIRD IS THE DEFAULT.** *System* is not the same
   answer as *light*: a reader whose machine turns dark at sunset wants the page
   to follow, and a two-state control can only record "dark" or "not dark" —
   which freezes the page at whatever it was when they pressed it. So *system*
   is a stored value like the others, and it is also what an absent record
   means, so the two can never disagree.

   ⛔ **The store is `study-progress.js`'s display record, not a second one.**
   That file owns every read and every write; this one asks it questions, the
   way `read-mark.js` does. ⚠️ Its docstring already ruled the display record
   independent of the read marks *"because a preference that fails to parse
   cannot take every mark with it"* — this is that record's first consumer.
   ⛔ Read through the published name with NO existence guard, and this part
   sits after `study-progress.js` in `bundle.SCRIPT_PARTS` for that reason.

   ⛔ **The control is NOT gated on storage working.** `read-mark.js` hides its
   control when nothing can be stored, because a mark that is not kept is a lie.
   A theme that is not kept is still a theme: the reader sees the page they
   asked for, for as long as they are on it. ⚠️ So this shows the control
   whenever scripting is on, and `prefer()` returning false costs the page
   nothing it was showing.

   ⛔ **THE FLASH IS PREVENTED IN THE HEAD, NOT HERE.** This part is deferred,
   so it runs after the first paint — applying the stored theme here would show
   every reader the wrong page for a frame. `page.html` carries a tiny
   synchronous boot in `<head>` that sets `data-theme` before anything is
   painted. ⚠️ That boot spells the store's key, version and field a second
   time, because it must run before any bundle exists; `test_theme` holds the
   two spellings equal, both ways.

   ⭐ **The words a reader sees are in `page.html`** (R13): this file toggles
   `hidden` and `aria-pressed` and types nothing.

   ⛔ **`theme-color` is kept honest.** The page ships two of them, one per
   system scheme. A reader who has CHOSEN a theme has made those media queries
   wrong, so the chosen one is widened to `all` and the other is switched off;
   choosing *system* puts both media queries back exactly as the skeleton wrote
   them. */

(function () {
  'use strict';

  /* The name the choice is filed under inside the display record, and the three
     values it may take. ⚠️ `SYSTEM` is stored like the others and is also what
     an absent record means. */
  var PREFERENCE = 'theme';
  var LIGHT = 'light';
  var DARK = 'dark';
  var SYSTEM = 'system';

  /* The attribute `palette.css` guards on, and the control's own hooks. ⚠️
     Spelled here and in `render/templates/page.html`, the two-sided spelling
     every hook on this page has: markup and script cannot import one another. */
  var THEME = 'data-theme';
  var CONTROL = '[data-section="theme"]';
  var CHOICE = 'data-theme-choice';

  /* The browser-chrome colour, one per system scheme, and what switches one
     off. ⚠️ `not all` rather than removing the element: the skeleton's own two
     media queries are what *system* restores, so nothing is thrown away. */
  var COLOUR = 'meta[name="theme-color"]';
  var EVERY = 'all';
  var NONE = 'not all';

  var store = window.studyforge.progress;
  var root = document.documentElement;

  var control = document.querySelector(CONTROL);
  if (!control) { return; }
  var buttons = [].slice.call(control.querySelectorAll('[' + CHOICE + ']'));
  if (!buttons.length) { return; }

  /* Each theme-colour element with the media query the skeleton gave it, read
     once, before anything here has had a chance to change one. */
  var colours = [].slice.call(document.querySelectorAll(COLOUR)).map(function (meta) {
    return { meta: meta, media: meta.getAttribute('media') || EVERY };
  });

  /* A stored value this cannot apply is treated as no choice at all — the same
     ruling the store itself makes about a record it cannot display. */
  function chosen() {
    var held = store.preference(PREFERENCE);
    return held === LIGHT || held === DARK ? held : SYSTEM;
  }

  function paint(choice) {
    if (choice === SYSTEM) {
      root.removeAttribute(THEME);
    } else {
      root.setAttribute(THEME, choice);
    }
    colours.forEach(function (carried) {
      if (choice === SYSTEM) {
        carried.meta.setAttribute('media', carried.media);
      } else {
        carried.meta.setAttribute(
          'media',
          carried.media.indexOf(choice) === -1 ? NONE : EVERY
        );
      }
    });
    buttons.forEach(function (button) {
      var mine = button.getAttribute(CHOICE) === choice;
      button.setAttribute('aria-pressed', mine ? 'true' : 'false');
    });
  }

  /* ⛔ Shown from the STORE's answer, never from what was just pressed: a write
     the browser refused must not leave the page claiming it was remembered. */
  function choose(choice) {
    store.prefer(PREFERENCE, choice);
    paint(chosen());
  }

  paint(chosen());
  control.hidden = false;

  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      choose(button.getAttribute(CHOICE));
    });
  });
}());
