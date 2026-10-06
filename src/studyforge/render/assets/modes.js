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
   and `aria-pressed` and types nothing.

   ⭐ ENTRIES OF THE OTHER LANGUAGE. An index row, a rail row and a row of a module's list
   that belongs to some languages only carries `data-entry-lang`; the stylesheet greys it
   by the mode, with no script. What a script adds is what a stylesheet cannot do:
   under `data-outside="locked"` it takes the `href` off the link of a row the mode does not
   read (keeping it in `data-href`, `aria-disabled`, out of the tab order) and gives it back
   when a mode that reads it is chosen; it counts only the pages the mode reads (the groups'
   `of N read`, the progress line and strip, the Up next slip and the module's unit count);
   it shows, in the between-units bar, the first neighbour the mode reads; and it keeps a
   section a link points into on the page while that link is the target.

   ⛔ `page.js` is not changed for it: it ran before this file and counted every row. This file
   recounts after it, and after each change of mode. */

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

    var ENTRY = 'data-entry-lang';
    var locked = root.getAttribute('data-outside') === 'locked';
    var prose = {};
    chosen.forEach(function (button) {
      prose[button.getAttribute(CHOICE)] = button.getAttribute('data-mode-prose');
    });

    function tokens(node, name) {
      return (node.getAttribute(name) || '').split(' ');
    }

    /* Whether `node` belongs to languages the chosen mode does not read. */
    function outside(node, mode, name) {
      return node.hasAttribute(name) && tokens(node, name).indexOf(prose[mode]) === -1;
    }

    function own(row) {
      return [].slice.call(row.querySelectorAll('a')).filter(function (link) {
        return link.closest('[' + ENTRY + ']') === row;
      });
    }

    function lock(row, closed) {
      own(row).forEach(function (link) {
        if (closed) {
          if (link.hasAttribute('href')) {
            link.setAttribute('data-href', link.getAttribute('href'));
            link.removeAttribute('href');
          }
          link.setAttribute('aria-disabled', 'true');
          link.setAttribute('tabindex', '-1');
        } else {
          if (link.hasAttribute('data-href')) {
            link.setAttribute('href', link.getAttribute('data-href'));
            link.removeAttribute('data-href');
          }
          link.removeAttribute('aria-disabled');
          link.removeAttribute('tabindex');
        }
      });
      if (!row.hasAttribute('data-readable')) { return; }
      var opens = own(row).some(function (link) { return link.hasAttribute('href'); }) ||
        row.hasAttribute('aria-current');
      row.setAttribute('data-readable', opens ? 'true' : 'false');
    }

    var LISTS = 'nav[aria-label="Contents"] li[id], nav[aria-label="Units"] li[id]';

    /* A row the mode reads, that has a page, and that this mode can open. */
    function counted(row, mode) {
      return row.getAttribute('data-readable') === 'true' && !outside(row, mode, ENTRY);
    }

    function fill(holder, value) {
      var slot = holder && holder.querySelector('b, strong');
      if (slot) { slot.textContent = String(value); }
    }

    /* Writes a number into the text node that already holds one, keeping its words:
       `of 5 read` takes the number alone, `3 units` takes the plural with it. */
    function phrase(holder, total) {
      [].slice.call(holder.childNodes).forEach(function (node) {
        if (node.nodeType !== 3) { return; }
        if (/\d+ units?/.test(node.nodeValue)) {
          node.nodeValue = node.nodeValue.replace(/\d+ (unit)s?/, total + ' $1' + (total === 1 ? '' : 's'));
        } else if (/ of \d+ /.test(node.nodeValue)) {
          node.nodeValue = node.nodeValue.replace(/ of \d+ /, ' of ' + total + ' ');
        }
      });
    }

    function recount(mode) {
      var usable = store.supported();
      var marks = usable ? store.marks() : [];
      var rows = [].slice.call(document.querySelectorAll(LISTS));
      var live = rows.filter(function (row) { return counted(row, mode); });
      function read(row) { return marks.indexOf(row.id) !== -1; }
      function within(group) {
        return live.filter(function (row) { return group.contains(row); });
      }
      function done(list) { return list.filter(read).length; }

      [].slice.call(document.querySelectorAll('nav[aria-label="Contents"] summary > small')).forEach(
        function (tally) {
          var members = within(tally.parentNode.parentNode);
          fill(tally, done(members));
          phrase(tally, members.length);
          tally.hidden = !usable || !members.length;
        }
      );

      var next = live.filter(function (row) { return !read(row); })[0] || null;
      [].slice.call(document.querySelectorAll('[aria-current="step"]')).forEach(function (node) {
        node.removeAttribute('aria-current');
      });
      if (usable && next) { next.setAttribute('aria-current', 'step'); }

      var region = document.querySelector('section[aria-label="Progress"]');
      if (region) {
        var line = region.querySelector('p');
        fill(line, done(live));
        fill(line && line.querySelector('span'), live.length - done(live));
        if (line) { phrase(line, live.length); }
        [].slice.call(region.querySelectorAll('li > a[href^="#"]')).forEach(function (link) {
          var group = document.getElementById(link.getAttribute('href').slice(1));
          var members = group ? within(group) : [];
          var share = members.length ? Math.round((100 * done(members)) / members.length) : 0;
          link.style.setProperty('--read', share + '%');
          if (usable && next && group && group.contains(next)) {
            link.parentNode.setAttribute('aria-current', 'step');
          }
        });
      }

      var slip = document.querySelector('nav[aria-label="Up next"]');
      if (slip && live.length) {
        var lead = slip.querySelector('a');
        var finished = slip.querySelector('p');
        var target = next || (usable ? null : live[0]);
        var source = target && (target.querySelector('a[href]') || target.querySelector('a'));
        var address = source && (source.getAttribute('href') || source.getAttribute('data-href'));
        if (lead && address) {
          var title = source.cloneNode(true);
          [].slice.call(title.querySelectorAll('span, small')).forEach(function (node) {
            node.parentNode.removeChild(node);
          });
          lead.setAttribute('href', address);
          lead.lastChild.textContent = ' ' + title.textContent.trim();
          lead.hidden = false;
          if (finished) { finished.hidden = true; }
        } else if (lead && finished && usable) {
          lead.hidden = true;
          finished.hidden = false;
        }
      }

      /* A module's page says how many units it holds, in its masthead. */
      var meta = [].slice.call(document.querySelectorAll('body > header p')).filter(function (p) {
        return /^\d+ units?/.test(p.textContent);
      })[0];
      if (meta && rows.length) { phrase(meta, live.length); }
    }

    /* The between-units bar shows the first neighbour in each direction the mode can open. */
    function pager(mode) {
      ['previous', 'next'].forEach(function (side) {
        var chain = [].slice.call(document.querySelectorAll('nav[aria-label="Between units"] a[data-pager="' + side + '"]'));
        var shown = null;
        chain.forEach(function (link) {
          var opens = shown === null && !outside(link, mode, 'data-pager-lang');
          if (opens) { shown = link; }
          link.hidden = !opens;
          if (opens) { link.setAttribute('rel', side === 'previous' ? 'prev' : 'next'); }
          else { link.removeAttribute('rel'); }
        });
      });
    }

    /* A link into a section the mode hides shows that section, so it lands on something. */
    function arrive() {
      [].slice.call(document.querySelectorAll('section[data-linked]')).forEach(function (section) {
        section.removeAttribute('data-linked');
      });
      var id = window.location.hash.slice(1);
      var target = id ? document.getElementById(decodeURIComponent(id)) : null;
      var section = target && target.closest('section[data-lang]');
      if (section && window.getComputedStyle(section).display === 'none') {
        section.setAttribute('data-linked', '');
        target.scrollIntoView();
      }
    }

    function apply(mode) {
      [].slice.call(document.querySelectorAll('section[data-linked]')).forEach(function (section) {
        section.removeAttribute('data-linked');
      });
      [].slice.call(document.querySelectorAll('li[' + ENTRY + ']')).forEach(function (row) {
        lock(row, locked && outside(row, mode, ENTRY));
      });
      if (locked) { pager(mode); }
      recount(mode);
    }

    function show(mode) {
      root.setAttribute(ATTRIBUTE, mode);
      chosen.forEach(function (button) {
        button.setAttribute('aria-pressed', button.getAttribute(CHOICE) === mode ? 'true' : 'false');
      });
      apply(mode);
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
    arrive();
    window.addEventListener('hashchange', arrive);

    var noted = [].slice.call(document.querySelectorAll(
      'aside[data-section="mode-outside"] [' + CHOICE + ']'
    ));

    chosen.concat(offered, noted).forEach(function (button) {
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
