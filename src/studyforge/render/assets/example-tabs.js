/* A two-language example: the tabs of one block, opened by the reading mode.

   ⛔ WRITTEN ONLY FOR A CORPUS THAT DECLARES MODES, composed into `modes.js`
   (`render/example_tabs.py`). The shared script never carries a line of it.

   ⭐ WHAT THE MARKUP ALREADY DID. Every panel is present under a visible label in the
   default mode's order, and `modes.css` hides what the mode does not list. This
   script only upgrades it: it shows the tab bar when a block has two tabs to move
   between, opens the first tab the mode lists, and keeps the keys of the WAI-ARIA
   tabs pattern: Left and Right wrap, Home and End, the selected tab the one in the
   tab order, the panel focusable.

   ⭐ A click changes that block only and is not remembered; the remembered choice is
   the mode. A change of mode re-opens each block on the first tab that mode lists. */

(function () {
  'use strict';

  var MODE_TABS = /*MODE_TABS*/{};
  var ATTRIBUTE = 'data-mode';

  function blocks() {
    return [].slice.call(document.querySelectorAll('div[data-example]'));
  }

  function tabsOf(block) {
    return [].slice.call(block.querySelectorAll('[role="tab"]'));
  }

  function panelOf(tab) {
    return document.getElementById(tab.getAttribute('aria-controls'));
  }

  /* The tabs the mode lists, in the mode's order. */
  function listed(block) {
    var order = MODE_TABS[document.documentElement.getAttribute(ATTRIBUTE)] || [];
    return tabsOf(block)
      .filter(function (tab) { return order.indexOf(tab.getAttribute('data-lang')) !== -1; })
      .sort(function (a, b) {
        return order.indexOf(a.getAttribute('data-lang')) - order.indexOf(b.getAttribute('data-lang'));
      });
  }

  function select(block, tab, focus) {
    tabsOf(block).forEach(function (other) {
      var on = other === tab;
      other.setAttribute('aria-selected', on ? 'true' : 'false');
      other.setAttribute('tabindex', on ? '0' : '-1');
      var panel = panelOf(other);
      if (panel) { panel.hidden = !on; }
    });
    if (focus) { tab.focus(); }
  }

  function upgrade(block) {
    var bar = block.querySelector('[role="tablist"]');
    var shown = listed(block);
    if (!bar) { return; }
    /* Reading order follows the mode: tabs in the bar, panels after it. */
    shown.slice().reverse().forEach(function (tab) {
      bar.insertBefore(tab, bar.firstChild);
    });
    var anchor = bar;
    shown.forEach(function (tab) {
      var panel = panelOf(tab);
      if (panel) { anchor.parentNode.insertBefore(panel, anchor.nextSibling); anchor = panel; }
    });
    block.setAttribute('data-tabs-on', '');
    bar.hidden = shown.length < 2;
    if (shown.length) { select(block, shown[0], false); }
  }

  function key(block, event) {
    var tab = event.target;
    if (tab.getAttribute('role') !== 'tab') { return; }
    var shown = listed(block);
    var at = shown.indexOf(tab);
    var to = null;
    if (event.key === 'ArrowRight') { to = shown[(at + 1) % shown.length]; }
    else if (event.key === 'ArrowLeft') { to = shown[(at - 1 + shown.length) % shown.length]; }
    else if (event.key === 'Home') { to = shown[0]; }
    else if (event.key === 'End') { to = shown[shown.length - 1]; }
    if (to) {
      event.preventDefault();
      select(block, to, true);
    }
  }

  function start() {
    var all = blocks();
    all.forEach(function (block) {
      var bar = block.querySelector('[role="tablist"]');
      if (!bar) { return; }
      bar.addEventListener('click', function (event) {
        var tab = event.target.closest ? event.target.closest('[role="tab"]') : null;
        if (tab) { select(block, tab, false); }
      });
      bar.addEventListener('keydown', function (event) { key(block, event); });
    });
    all.forEach(upgrade);
    new MutationObserver(function () { blocks().forEach(upgrade); })
      .observe(document.documentElement, { attributes: true, attributeFilter: [ATTRIBUTE] });
  }

  if (document.readyState === 'complete') {
    start();
  } else {
    document.addEventListener('DOMContentLoaded', start);
  }
}());
