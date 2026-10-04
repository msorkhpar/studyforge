/* A practice written in several languages: what a card knows of its editions.

   ⭐ **One practice, an edition per language.** A card whose practice is written in several
   languages lists them (`[data-edition]`, each naming its statement section and its panel's key),
   and every edition's statement and panel are on the page like any practice's. This file answers
   the questions `practice-workspace.js` asks of such a card: which editions it has, which one
   opens (the first of the current reading mode's languages that the practice has, else its first),
   which pair is shown, the switch row at the top of each panel, and what the card says of the
   editions that have passed. ⛔ It moves, copies and fetches nothing, and it names no language and
   no mode: the page says them (`data-edition-modes` on the workspace names the attribute that
   holds the mode and each mode's languages).

   ⭐ **A practice of its own is the same card with no editions**: `of` answers `[]`, and `pairs`
   answers its one section and panel, so the workspace has one way to show either. */

(function () {
  'use strict';

  var EDITION = '[data-edition][data-edition-section]';
  var SWITCH = 'button[data-edition-switch]';
  var SWITCH_ROW = '[data-practice-part="editions"]';
  var MODES = 'data-edition-modes';
  var STATE = '[data-practices-part="state"]';
  var STATE_WORD = 'data-practice-state';

  /* A card's language editions, each with its section and panel; `[]` below two. */
  function of(card, panelOf) {
    var found = [].slice.call(card.querySelectorAll(EDITION)).map(function (span) {
      var key = span.getAttribute('data-edition-key') || '';
      return {
        lang: span.getAttribute('data-edition'),
        span: span,
        key: key,
        section: document.getElementById(span.getAttribute('data-edition-section')),
        panel: panelOf(key)
      };
    }).filter(function (one) { return one.section; });
    return found.length > 1 ? found : [];
  }

  /* Every (section, panel) pair a card has. Only the pair `one` is showing is ever visible. */
  function pairs(one) {
    return one.editions.length ? one.editions : [{ section: one.section, panel: one.panel }];
  }

  function byLang(one, lang) {
    return one.editions.filter(function (edition) { return edition.lang === lang; })[0] || null;
  }

  /* The edition a practice opens in: the first of the current mode's languages it has. */
  function preferred(one, shell) {
    var said = {};
    try { said = JSON.parse(shell.getAttribute(MODES) || '{}'); } catch (ignored) { said = {}; }
    var chosen = said.attribute ? document.documentElement.getAttribute(said.attribute) : null;
    var order = (said.modes && said.modes[chosen]) || [];
    for (var at = 0; at < order.length; at += 1) {
      var found = byLang(one, order[at]);
      if (found) { return found; }
    }
    return one.editions[0];
  }

  /* The pair `one` shows from now on. */
  function use(one, edition) {
    one.lang = edition.lang;
    one.section = edition.section;
    one.panel = edition.panel;
  }

  /* The switch row of every edition's panel: shown for the open practice, pressed on the open
     language. ⛔ Shipped `hidden`: with no script there is nothing for it to do. */
  function rows(one, shown) {
    one.editions.forEach(function (edition) {
      var row = edition.panel && edition.panel.querySelector(SWITCH_ROW);
      if (!row) { return; }
      row.hidden = !shown;
      [].slice.call(row.querySelectorAll(SWITCH)).forEach(function (button) {
        var mine = button.getAttribute('data-edition-switch') === one.lang;
        button.setAttribute('aria-pressed', mine ? 'true' : 'false');
      });
    });
  }

  /* The card's status from the reader's record (`held`: practice key's last part -> passed):
     each edition says whether it passed, and the card says none, some of them, or every one.
     ⛔ Each edition's pass is its own record, kept under its own key; nothing is merged. */
  function paint(one, held) {
    var slot = one.card.querySelector(STATE);
    var passed = 0;
    one.editions.forEach(function (edition) {
      var done = held[edition.key.slice(edition.key.lastIndexOf('/') + 1)] === true;
      var mark = edition.span.querySelector('[data-edition-mark]');
      if (mark) { mark.hidden = !done; }
      edition.span.setAttribute('data-edition-state', done ? 'passed' : 'not-started');
      if (done) { passed += 1; }
    });
    var state = passed === 0 ? 'not-started' : passed === one.editions.length ? 'passed' : 'partial';
    [].slice.call(slot.querySelectorAll('[' + STATE_WORD + ']')).forEach(function (word) {
      word.hidden = word.getAttribute(STATE_WORD) !== state;
    });
    var count = slot.querySelector('[data-edition-count]');
    if (count) { count.textContent = String(passed); }
    one.card.setAttribute(STATE_WORD, state);
    slot.hidden = false;
  }

  window.studyforge = window.studyforge || {};
  window.studyforge.editions = {
    of: of,
    pairs: pairs,
    byLang: byLang,
    preferred: preferred,
    use: use,
    rows: rows,
    paint: paint
  };
}());
