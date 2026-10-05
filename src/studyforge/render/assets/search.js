/* The search: Ctrl or Cmd + K, or `/`, opens a box over the page; results appear as the reader types.

   ⭐ **LOCAL AND OFFLINE.** The ranking library (`minisearch.js`, vendored) and the index
   (`search-index.js`, written by the build from the pages themselves) are two files beside
   `page.js`, loaded from the site on the first time the box is opened, and never from anywhere
   else. ⛔ They are scripts and not fetched JSON so the search also works from a page opened
   as a file. The index is turned into a ranked index in the page, in chunks, so the box stays
   usable while it fills.

   ⭐ **ONE RECORD PER HEADING, GROUPED BY PAGE.** A result names the page (and the module it is
   in) once, and under it the parts of the page that matched, each with the matched words marked
   and a snippet around the first one. Enter opens the chosen part at its heading.

   ⛔ **THE WORDS A READER SEES ARE IN `page.html`** as `data-search-*` attributes of the dialog;
   this part types none. ⛔ Results are built with `textContent` and `<mark>` elements, never
   markup from the index, so nothing in a page can inject into the box.

   ⭐ Keys: Up and Down move, Enter opens, Esc closes, Tab stays inside the box. `/` is left
   alone while the reader is typing in a field or an editor. */

(function () {
  'use strict';

  var OPEN = '[data-section="search-open"]';
  var DIALOG = '[data-section="search"]';
  var LIBRARY = 'minisearch.js';
  var INDEX = 'search-index.js';
  var BUNDLE = /\/page\.js(?:\?|#|$)/;
  var MAX_PAGES = 8;
  var MAX_PARTS = 3;
  var LOOK_BEHIND = 60;
  var LOOK_AHEAD = 150;
  var ELLIPSIS = '…';

  var opener = document.querySelector(OPEN);
  var dialog = document.querySelector(DIALOG);
  if (!opener || !dialog) { return; }
  var field = dialog.querySelector('[data-search-field]');
  var list = dialog.querySelector('[data-search-results]');
  var status = dialog.querySelector('[data-search-status]');
  var hints = dialog.querySelector('[data-search-hints]');
  var close = dialog.querySelector('[data-search-close]');

  var data = null;
  var engine = null;
  var state = 'idle';
  var pending = null;
  var returnTo = null;
  var active = -1;
  var timer = 0;

  function word(name) { return dialog.getAttribute('data-search-' + name) || ''; }

  /* ⭐ The input is made here, with the words the dialog carries: the page has no search box
     to show without this part, so it ships none. */
  var input = document.createElement('input');
  input.type = 'text';
  input.setAttribute('role', 'combobox');
  input.setAttribute('aria-expanded', 'false');
  input.setAttribute('aria-owns', 'search-results');
  input.setAttribute('aria-autocomplete', 'list');
  input.setAttribute('aria-label', word('placeholder'));
  input.setAttribute('placeholder', word('placeholder'));
  input.setAttribute('autocomplete', 'off');
  input.setAttribute('autocapitalize', 'off');
  input.setAttribute('spellcheck', 'false');
  input.setAttribute('enterkeyhint', 'go');
  field.parentNode.replaceChild(input, field);

  /* --- the files ---------------------------------------------------------- */

  function base() {
    var scripts = [].slice.call(document.scripts);
    for (var i = 0; i < scripts.length; i += 1) {
      if (BUNDLE.test(scripts[i].src)) { return scripts[i].src; }
    }
    return '';
  }

  function script(name, done, failed) {
    var tag = document.createElement('script');
    tag.src = new URL(name, base()).href;
    tag.onload = done;
    tag.onerror = failed;
    document.head.appendChild(tag);
  }

  function fail() {
    state = 'failed';
    status.textContent = word('failed');
  }

  function load() {
    if (state !== 'idle') { return; }
    state = 'loading';
    status.textContent = word('loading');
    script(LIBRARY, function () {
      script(INDEX, build, fail);
    }, fail);
  }

  function build() {
    data = window.studyforge && window.studyforge.searchIndex;
    if (!data || !window.MiniSearch) { fail(); return; }
    engine = new window.MiniSearch({
      fields: ['title', 'heading', 'text'],
      searchOptions: { prefix: true, fuzzy: 0.15, boost: { title: 3, heading: 2 }, combineWith: 'AND' }
    });
    var docs = data.records.map(function (record, id) {
      return { id: id, title: data.pages[record[0]][1], heading: record[1], text: record[3] };
    });
    engine.addAllAsync(docs, { chunkSize: 300 }).then(function () {
      state = 'ready';
      status.textContent = '';
      if (input.value.trim()) { run(); }
    }, fail);
  }

  /* --- matching and showing ------------------------------------------------ */

  function tokens(query) {
    return query.toLowerCase().split(/[\s\p{P}]+/u).filter(Boolean);
  }

  function escaped(text) { return text.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); }

  function matcher(terms) {
    var unique = terms.filter(function (term, at) { return terms.indexOf(term) === at; });
    unique.sort(function (a, b) { return b.length - a.length; });
    return unique.length ? new RegExp('(' + unique.map(escaped).join('|') + ')', 'giu') : null;
  }

  function marked(into, text, pattern) {
    var last = 0;
    if (pattern) {
      text.replace(pattern, function (hit, whole, at) {
        if (at > last) { into.appendChild(document.createTextNode(text.slice(last, at))); }
        var mark = document.createElement('mark');
        mark.textContent = hit;
        into.appendChild(mark);
        last = at + hit.length;
        return hit;
      });
    }
    if (last < text.length) { into.appendChild(document.createTextNode(text.slice(last))); }
  }

  function snippet(text, pattern) {
    if (!text) { return ''; }
    var at = 0;
    if (pattern) {
      pattern.lastIndex = 0;
      var found = pattern.exec(text);
      at = found ? found.index : 0;
    }
    var from = Math.max(0, at - LOOK_BEHIND);
    var to = Math.min(text.length, at + LOOK_AHEAD);
    if (from > 0) {
      var space = text.indexOf(' ', from);
      from = space !== -1 && space < at ? space + 1 : from;
    }
    if (to < text.length) {
      var back = text.lastIndexOf(' ', to);
      to = back > at ? back : to;
    }
    return (from > 0 ? ELLIPSIS : '') + text.slice(from, to) + (to < text.length ? ELLIPSIS : '');
  }

  function ranked(query) {
    var found = engine.search(query);
    if (!found.length && tokens(query).length > 1) { found = engine.search(query, { combineWith: 'OR' }); }
    return found;
  }

  function grouped(found) {
    var order = [];
    var by = {};
    found.slice(0, 80).forEach(function (hit) {
      var record = data.records[hit.id];
      var key = record[0];
      if (!by[key]) { by[key] = []; order.push(key); }
      by[key].push({ record: record, hit: hit });
    });
    return order.slice(0, MAX_PAGES).map(function (key) { return { page: data.pages[key], parts: by[key] }; });
  }

  function target(page, record) {
    var url = new URL(page[0], base()).href;
    return record[2] ? url + '#' + record[2] : url;
  }

  function show(groups, query, terms) {
    list.textContent = '';
    var count = 0;
    var pattern = matcher(terms.concat(tokens(query)));
    groups.forEach(function (group, g) {
      var box = document.createElement('div');
      box.setAttribute('role', 'group');
      var title = document.createElement('p');
      title.id = 'search-page-' + g;
      title.setAttribute('data-search-page', '');
      title.textContent = group.page[1];
      if (group.page[2]) {
        var crumb = document.createElement('small');
        crumb.textContent = group.page[2];
        title.appendChild(crumb);
      }
      box.setAttribute('aria-labelledby', title.id);
      box.appendChild(title);
      group.parts.slice(0, MAX_PARTS).forEach(function (part) {
        var row = document.createElement('a');
        row.setAttribute('role', 'option');
        row.setAttribute('aria-selected', 'false');
        row.id = 'search-hit-' + count;
        row.href = target(group.page, part.record);
        var head = document.createElement('strong');
        marked(head, part.record[1] || group.page[1], pattern);
        row.appendChild(head);
        var text = snippet(part.record[3], pattern);
        if (text) {
          var body = document.createElement('span');
          marked(body, text, pattern);
          row.appendChild(body);
        }
        box.appendChild(row);
        count += 1;
      });
      list.appendChild(box);
    });
    input.setAttribute('aria-expanded', count ? 'true' : 'false');
    var rows = options();
    status.textContent = count ? '' : word('none') + ' “' + query + '”';
    activate(rows.length ? 0 : -1);
  }

  function run() {
    var query = input.value.trim();
    if (state !== 'ready') { return; }
    if (!query) {
      list.textContent = '';
      status.textContent = '';
      input.setAttribute('aria-expanded', 'false');
      active = -1;
      return;
    }
    var found = ranked(query);
    var terms = [];
    found.slice(0, 80).forEach(function (hit) { terms = terms.concat(hit.terms || []); });
    show(grouped(found), query, terms);
  }

  /* --- keys, focus and the box itself --------------------------------------- */

  function options() { return [].slice.call(list.querySelectorAll('a[role="option"]')); }

  function activate(at) {
    var rows = options();
    rows.forEach(function (row, i) { row.setAttribute('aria-selected', i === at ? 'true' : 'false'); });
    active = rows.length ? Math.max(0, Math.min(at, rows.length - 1)) : -1;
    if (active === -1) { input.removeAttribute('aria-activedescendant'); return; }
    rows[active].setAttribute('aria-selected', 'true');
    input.setAttribute('aria-activedescendant', rows[active].id);
    rows[active].scrollIntoView({ block: 'nearest' });
  }

  function openBox() {
    if (!dialog.hidden) { return; }
    returnTo = document.activeElement;
    dialog.hidden = false;
    load();
    input.focus();
    input.select();
  }

  function closeBox() {
    if (dialog.hidden) { return; }
    dialog.hidden = true;
    if (returnTo && returnTo.focus) { returnTo.focus(); }
  }

  function typing(node) {
    if (!node || !node.tagName) { return false; }
    var tag = node.tagName.toLowerCase();
    return tag === 'input' || tag === 'textarea' || tag === 'select' || node.isContentEditable
      || !!(node.closest && node.closest('.monaco-editor, [contenteditable="true"]'));
  }

  document.addEventListener('keydown', function (event) {
    var key = event.key;
    if ((event.ctrlKey || event.metaKey) && !event.altKey && (key === 'k' || key === 'K')) {
      event.preventDefault();
      if (dialog.hidden) { openBox(); } else { closeBox(); }
      return;
    }
    if (key === '/' && dialog.hidden && !event.ctrlKey && !event.metaKey && !event.altKey && !typing(event.target)) {
      event.preventDefault();
      openBox();
    }
  });

  dialog.addEventListener('keydown', function (event) {
    var rows = options();
    if (event.key === 'Escape') { event.preventDefault(); closeBox(); }
    else if (event.key === 'ArrowDown') { event.preventDefault(); activate(active + 1 >= rows.length ? 0 : active + 1); }
    else if (event.key === 'ArrowUp') { event.preventDefault(); activate(active - 1 < 0 ? rows.length - 1 : active - 1); }
    else if (event.key === 'Enter' && active !== -1 && event.target === input) {
      event.preventDefault();
      rows[active].click();
    } else if (event.key === 'Tab') {
      event.preventDefault();
      (document.activeElement === input ? close : input).focus();
    }
  });

  dialog.addEventListener('click', function (event) {
    if (event.target === dialog || event.target === close) { closeBox(); }
    else if (event.target.closest && event.target.closest('a[role="option"]')) { closeBox(); }
  });

  dialog.addEventListener('mousemove', function (event) {
    var row = event.target.closest && event.target.closest('a[role="option"]');
    var at = options().indexOf(row);
    if (row && at !== active) { activate(at); }
  });

  input.addEventListener('input', function () {
    window.clearTimeout(timer);
    timer = window.setTimeout(run, 40);
  });

  opener.addEventListener('click', openBox);

  /* ⭐ The label on the opener names the key the reader's platform has. */
  var mac = /Mac|iPhone|iPad/.test(navigator.platform || navigator.userAgent || '');
  var keys = opener.querySelector('kbd');
  if (keys) { keys.textContent = opener.getAttribute(mac ? 'data-keys-mac' : 'data-keys-other') || ''; }

  ['move', 'open', 'close'].forEach(function (name) {
    var hint = document.createElement('span');
    hint.textContent = word('hint-' + name);
    hints.appendChild(hint);
  });

  opener.hidden = false;
}());
