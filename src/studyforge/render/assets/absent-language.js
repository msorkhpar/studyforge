/* A language a block or a practice lacks, greyed: what a stylesheet cannot do.

   ⛔ WRITTEN ONLY FOR A CORPUS THAT DECLARES `absent_language: grey`, appended to
   `modes.js` after the tabs' script (`render/absent_language.py`), so the shared script and
   every other corpus's `modes.js` keep their bytes.

   ⭐ WHAT THE MARKUP AND THE STYLESHEET ALREADY DID. A tab for a language the block lacks is
   there, `aria-disabled`, and the sentence that names the carriers is shown by the mode's
   rules; a practice card that is outside the mode shows its own sentence. This file makes the
   disabled tab behave as one: a click does nothing, the arrow keys, Home and End still reach it
   (it stays focusable, so its reason can be read), a block opens on the first tab the mode
   lists that exists, and the bar is shown when the mode's one tab is a missing one.

   ⭐ A greyed practice does not open: its link says `aria-disabled` and ignores a click, and
   Previous and Next in the workspace pass over it. Whether a card is greyed is read from the
   page itself, as whether its sentence is shown, so this file holds no list of languages. */

(function () {
  'use strict';

  var ATTRIBUTE = 'data-mode';

  function shown(node) {
    return window.getComputedStyle(node).display !== 'none';
  }

  function enabled(tab) {
    return tab.getAttribute('aria-disabled') !== 'true';
  }

  function visibleTabs(block) {
    return [].slice.call(block.querySelectorAll('[role="tab"]')).filter(shown);
  }

  /* ⭐ Every example block with a tab it lacks is read again after each change of mode, once
     the tabs' own script has put its tabs in the mode's order. */
  function upgrade(block) {
    var bar = block.querySelector('[role="tablist"]');
    if (!bar) { return; }
    var tabs = visibleTabs(block);
    if (!tabs.length) { return; }
    var open = tabs.filter(enabled);
    tabs.forEach(function (tab) {
      if (!enabled(tab)) { tab.setAttribute('aria-selected', 'false'); }
    });
    if (open.length && !open.some(function (tab) { return tab.getAttribute('aria-selected') === 'true'; })) {
      open[0].click();
    }
    bar.hidden = tabs.length < 2 && enabled(tabs[0]);
    var on = tabs.filter(function (tab) { return tab.getAttribute('aria-selected') === 'true' && enabled(tab); })[0];
    tabs.forEach(function (tab) {
      tab.setAttribute('tabindex', (on ? tab === on : tab === tabs[0]) ? '0' : '-1');
    });
  }

  function blocks() {
    return [].slice.call(document.querySelectorAll('div[data-example][data-missing]'));
  }

  function key(event) {
    var tab = event.target;
    if (!tab.closest || tab.getAttribute('role') !== 'tab') { return; }
    var block = tab.closest('div[data-example][data-missing]');
    if (!block) { return; }
    var tabs = visibleTabs(block);
    var at = tabs.indexOf(tab);
    var to = null;
    if (event.key === 'ArrowRight') { to = tabs[(at + 1) % tabs.length]; }
    else if (event.key === 'ArrowLeft') { to = tabs[(at - 1 + tabs.length) % tabs.length]; }
    else if (event.key === 'Home') { to = tabs[0]; }
    else if (event.key === 'End') { to = tabs[tabs.length - 1]; }
    if (!to) { return; }
    event.preventDefault();
    event.stopImmediatePropagation();
    if (enabled(to)) { to.click(); }
    tabs.forEach(function (one) { one.setAttribute('tabindex', one === to ? '0' : '-1'); });
    to.focus();
  }

  function click(event) {
    var tab = event.target.closest ? event.target.closest('[role="tab"][aria-disabled="true"]') : null;
    if (!tab) { return; }
    event.preventDefault();
    event.stopImmediatePropagation();
    tab.focus();
  }

  /* --- practices ---------------------------------------------------------- */
  var LINK = 'a[data-practices-part="open"]';
  var CARD = 'li[data-practice-card]';

  function greyed(card) {
    var note = card.querySelector('[data-practice-carriers]');
    return !!note && shown(note);
  }

  function cards() {
    return [].slice.call(document.querySelectorAll(CARD));
  }

  function mark() {
    cards().forEach(function (card) {
      var link = card.querySelector(LINK);
      if (!link) { return; }
      if (greyed(card)) { link.setAttribute('aria-disabled', 'true'); }
      else { link.removeAttribute('aria-disabled'); }
    });
  }

  function declined(event) {
    var link = event.target.closest ? event.target.closest(LINK) : null;
    if (!link || link.getAttribute('aria-disabled') !== 'true') { return; }
    event.preventDefault();
    event.stopImmediatePropagation();
  }

  /* The card whose section the address names, which is the practice that is open. */
  function openCard() {
    var id = window.location.hash.slice(1);
    return cards().filter(function (card) { return card.getAttribute('data-practice-card') === id; })[0] || null;
  }

  function readable(from, step) {
    var list = cards();
    for (var at = list.indexOf(from) + step; at >= 0 && at < list.length; at += step) {
      if (!greyed(list[at])) { return list[at]; }
    }
    return null;
  }

  /* Previous and Next show only where a practice the mode lists lies that way. */
  function ends() {
    var here = openCard();
    [['previous', -1], ['next', 1]].forEach(function (side) {
      var button = document.querySelector('[data-workspace-act="' + side[0] + '"]');
      if (button && here) { button.hidden = readable(here, side[1]) === null; }
    });
  }

  function step(event) {
    var button = event.target.closest ? event.target.closest('[data-workspace-act]') : null;
    var way = button && button.getAttribute('data-workspace-act');
    if (way !== 'previous' && way !== 'next') { return; }
    var here = openCard();
    if (!here) { return; }
    event.preventDefault();
    event.stopImmediatePropagation();
    var to = readable(here, way === 'next' ? 1 : -1);
    var link = to && to.querySelector(LINK);
    if (link) { link.click(); }
  }

  function start() {
    document.addEventListener('click', click, true);
    document.addEventListener('click', declined, true);
    document.addEventListener('click', step, true);
    document.addEventListener('keydown', key, true);
    cards().forEach(function (card) {
      var link = card.querySelector(LINK);
      if (link) { link.addEventListener('click', function () { window.setTimeout(ends, 0); }); }
    });
    function all() {
      blocks().forEach(upgrade);
      mark();
      ends();
    }
    all();
    new MutationObserver(all)
      .observe(document.documentElement, { attributes: true, attributeFilter: [ATTRIBUTE] });
  }

  if (document.readyState === 'complete') {
    start();
  } else {
    document.addEventListener('DOMContentLoaded', start);
  }
}());
