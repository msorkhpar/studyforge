/* The rail keeps its scroll position from one page to the next.

   ⭐ **WHAT THIS PART DOES AND WHAT IT DOES NOT.** It SAVES where the rail is scrolled to; it
   never puts the rail back. The putting-back is the small inline script in `page.html` right
   after the rail, which runs as the page is parsed and so before the first paint: a deferred
   part such as this one runs after it, and a rail that painted at the top for a frame and then
   jumped is the defect being removed. That script also brings the current page's row into view
   with the rail's own scroll offset (never `scrollIntoView`, which would move the page
   as well) when the saved position does not show it, and does the same when nothing was saved.

   ⛔ **THE STORE KEEPS THE RECORD, NOT THIS PART.** `window.studyforge.progress.cache` is the one
   place that touches the browser's storage, and it answers `false` when the browser refuses
   it, which costs nothing here: the next page then opens with the current row in view.
   ⚠️ The name is spelled here and in `page.html`, the two-sided spelling every hook has;
   the store files it as `studyforge.boot.rail.v1`.

   ⭐ Saved when the reader scrolls the rail (once per frame) and again when they follow a link
   out of it or leave the page, so the last position always wins. */

(function () {
  'use strict';

  var NAME = 'rail';
  var RAIL = 'nav[aria-label="Containers"]';

  var store = window.studyforge.progress;
  var rail = document.querySelector(RAIL);
  if (!rail) { return; }

  var waiting = false;

  function save() {
    waiting = false;
    store.cache(NAME, String(Math.round(rail.scrollTop)));
  }

  rail.addEventListener('scroll', function () {
    if (!waiting) {
      waiting = true;
      window.requestAnimationFrame(save);
    }
  }, { passive: true });

  rail.addEventListener('click', save, true);
  window.addEventListener('pagehide', save);
}());
