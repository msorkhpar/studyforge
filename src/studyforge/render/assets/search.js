/* The search: Ctrl or Cmd + K, or `/`, opens a box over the page; results appear as the reader types.

   ⭐ **LOCAL AND OFFLINE.** The ranking library (`minisearch.js`, vendored) and the index
   (`search-index.js`, written by the build from the pages themselves) are two files beside
   `page.js`, loaded from the site on the first time the box is opened, and never from anywhere
   else. ⛔ They are scripts and not fetched JSON so the search also works from a page opened
   as a file. ⭐ The index was built by the build: this part hands it to `MiniSearch.loadJSON`
   and builds nothing. A large one comes in string pieces (`search-index-0.js` and on), joined in
   order before the one load. ⚠️ A site built without `node` holds the records instead (versions 1
   and 2), and only then a third file, `search-build.js`, that builds them here. A version this
   part does not know fails, and so does a piece that is missing.

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
  var BUILDER = 'search-build.js';
  var KINDS = { 1: 'records', 2: 'records', 3: 'precompiled' };
  var SEARCH = { prefix: true, fuzzy: 0.15, boost: { title: 3, heading: 2 }, combineWith: 'AND' };
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

  var engine = null;
  var entry = null;
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
      script(INDEX, opened, fail);
    }, fail);
  }

  function opened() {
    var found = window.studyforge && window.studyforge.searchIndex;
    var kind = found && Object.prototype.hasOwnProperty.call(KINDS, found.version) && KINDS[found.version];
    if (!kind || !window.MiniSearch) { fail(); return; }
    if (kind === 'precompiled') { pieces(found); return; }
    script(BUILDER, function () { built(found); }, fail);
  }

  /* ⭐ A precompiled index: whole in the manifest, or its pieces loaded one after the other. */
  function pieces(found) {
    if (typeof found.index === 'string') { loaded(found, found.index); return; }
    var names = found.parts;
    if (!names || !names.length) { fail(); return; }
    var joined = [];
    (function next(at) {
      if (at === names.length) { loaded(found, joined.join('')); return; }
      script(names[at], function () {
        var piece = window.studyforge.searchParts && window.studyforge.searchParts[names[at]];
        if (typeof piece !== 'string') { fail(); return; }
        joined.push(piece);
        next(at + 1);
      }, fail);
    }(0));
  }

  function loaded(found, json) {
    try {
      engine = window.MiniSearch.loadJSON(json, {
        fields: found.fields, storeFields: found.storeFields, searchOptions: SEARCH
      });
    } catch (error) { fail(); return; }
    entry = function (hit) {
      var page = Number(String(hit.id).split('.')[0]);
      return { key: page, url: found.pages[page], title: hit.title, trail: hit.trail,
        heading: hit.heading, anchor: hit.anchor, text: hit.snippet };
    };
    ready();
  }

  /* ⚠️ The records of a site built without `node`: `search-build.js` joins and builds them. */
  function built(found) {
    if (!window.studyforge.searchBuild) { fail(); return; }
    window.studyforge.searchBuild(found, SEARCH, script, function (made, named) {
      engine = made;
      entry = named;
      ready();
    }, fail);
  }

  function ready() {
    state = 'ready';
    status.textContent = '';
    if (input.value.trim()) { run(); }
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
      var part = entry(hit);
      if (!by[part.key]) { by[part.key] = []; order.push(part.key); }
      by[part.key].push(part);
    });
    return order.slice(0, MAX_PAGES).map(function (key) { return { page: by[key][0], parts: by[key] }; });
  }

  function target(part) {
    var url = new URL(part.url, base()).href;
    return part.anchor ? url + '#' + part.anchor : url;
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
      title.textContent = group.page.title;
      if (group.page.trail) {
        var crumb = document.createElement('small');
        crumb.textContent = group.page.trail;
        title.appendChild(crumb);
      }
      box.setAttribute('aria-labelledby', title.id);
      box.appendChild(title);
      group.parts.slice(0, MAX_PARTS).forEach(function (part) {
        var row = document.createElement('a');
        row.setAttribute('role', 'option');
        row.setAttribute('aria-selected', 'false');
        row.id = 'search-hit-' + count;
        row.href = target(part);
        var head = document.createElement('strong');
        marked(head, part.heading || part.title, pattern);
        row.appendChild(head);
        var text = snippet(part.text, pattern);
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
