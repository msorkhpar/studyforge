/* The reading line under the top bar, and the outline's "you are here" (the 2026-11 redesign).

   ⭐ Its width is the share of the page already scrolled past, so a reader
   sees how far through a long unit they are. ⛔ It is decoration for a
   sighted reader only: the element is aria-hidden, and with scripting off it
   stays at no width rather than lying. ⚠️ Measured on scroll and resize, at
   most once a frame.

   ⭐ Scroll-spy: the outline link whose section heading was last scrolled past
   (under the bar) carries `aria-current="location"`, so a reader always sees
   which part of the unit they are in. The outline is a list of links to ids
   on this page; a link whose target is missing is skipped. */
(function () {
  "use strict";
  var line = document.querySelector('body > header > div[data-section="reading-progress"]');
  var spied = [];
  var outline = document.querySelectorAll('nav[aria-label="Outline"] a[href^="#"]');
  for (var i = 0; i < outline.length; i++) {
    var target = document.getElementById(decodeURIComponent(outline[i].getAttribute("href").slice(1)));
    if (target) { spied.push({ link: outline[i], target: target }); }
  }
  if (!line && !spied.length) { return; }
  var current = null;
  function spy() {
    var bar = parseFloat(getComputedStyle(document.documentElement).scrollPaddingTop) || 80;
    var found = null;
    for (var j = 0; j < spied.length; j++) {
      if (spied[j].target.getBoundingClientRect().top - bar <= 1) { found = spied[j].link; } else { break; }
    }
    if (found === current) { return; }
    if (current) { current.removeAttribute("aria-current"); }
    if (found) { found.setAttribute("aria-current", "location"); }
    current = found;
  }
  var queued = false;
  function measure() {
    queued = false;
    var root = document.documentElement;
    var room = root.scrollHeight - root.clientHeight;
    var share = room > 0 ? Math.min(1, Math.max(0, root.scrollTop / room)) : 0;
    if (line) { line.style.width = (share * 100).toFixed(2) + "%"; }
    if (spied.length) { spy(); }
  }
  function queue() {
    if (!queued) { queued = true; window.requestAnimationFrame(measure); }
  }
  window.addEventListener("scroll", queue, { passive: true });
  window.addEventListener("resize", queue);
  measure();
})();
