/* A lesson's links to its own code: opened in the course's editor, beside the test.

   ⭐ **A link the build marked** (`data-code-path`, `render/page/code.py`)
   names a code file of the corpus, and its href is the file's plain view
   (`unit.mentions`). Served, with the corpus's editor up, a click opens the file in the
   page's code panel instead: the source and its test in two windows of ONE
   editor, and a Run that runs the test. ⛔ **Anything short of that follows the
   link**: no server, no editor, a file the server will not open — the plain
   view is never broken, and the panel's built sentence says why.

   ⛔ **This file draws; it never talks to the API.** Everything it asks goes
   through `window.studyforge.run` — `editor`, `code`, `codeTest`, `stop` —
   which the SERVING PROCESS adds to the page it answers, so a built text names
   no API, no origin and no client file (R8).

   ⭐ **The same frames as a practice.** Each window is built by
   `window.studyforge.frames.frame`, which `practice-editor.js` publishes — the
   same focus guard, so a workbench never takes the reader's focus or moves
   the page — and the same one reload when a cold instance's frame policy
   blocked the frame. ⛔ Neither is copied here.

   ⭐ **The copy is said, not hidden**: the panel's second sentence, shown only
   once the editor answered, tells the reader the editor opens a COPY of the
   code, where their changes and a run's output stay. */

(function () {
  'use strict';

  /* ⚠️ Spelled here and in `render/page/code.py` and `code-panel.html` — the
     two-sided spelling every hook on this page has. The panel reuses the
     practice panel's part names so `practice.css` draws both. */
  var REGION = 'section[data-code]';
  var CORPUS = 'data-corpus';
  var PATH = 'data-code-path';
  var PART = 'data-practice-part';
  var TAB = 'data-practice-tab';
  var FRAME = 'data-practice-frame';
  var ACT = 'data-code-act';
  var WINDOWS = ['main', 'test'];
  var TITLES = { main: 'Source', test: 'Test' };

  var region = document.querySelector(REGION);
  if (!region) { return; }
  var run = window.studyforge && window.studyforge.run;
  var frames = window.studyforge && window.studyforge.frames;
  if (!run || !run.available() || !run.code || !run.editor || !frames) { return; }
  var corpus = region.getAttribute(CORPUS);

  function part(name) { return region.querySelector('[' + PART + '="' + name + '"]'); }
  function show(element, visible) { if (element) { element.hidden = !visible; } }

  var buttons = [].slice.call(region.querySelectorAll('[' + TAB + ']'));
  var slots = {};
  WINDOWS.forEach(function (name) {
    slots[name] = region.querySelector('[' + FRAME + '="' + name + '"]');
  });
  var act = region.querySelector('[' + ACT + '="test"]');
  var stop = region.querySelector('[' + ACT + '="stop"]');
  var status = part('status');
  var output = part('output');
  var current = null;
  var built = {};

  function select(name) {
    buttons.forEach(function (button) {
      var mine = button.getAttribute(TAB) === name;
      button.setAttribute('aria-selected', mine ? 'true' : 'false');
      button.tabIndex = mine ? 0 : -1;
    });
    WINDOWS.forEach(function (one) { show(slots[one], one === name); });
    if (!built[name] && current[name] && current[name].url) {
      built[name] = true;
      frames.frame(slots[name], current[name].url, TITLES[name]);
    }
  }

  /* ⭐ One pair at a time: a new click empties both windows and opens the new
     pair, the file clicked in front. */
  function draw(where) {
    current = where;
    built = {};
    WINDOWS.forEach(function (name) { slots[name].textContent = ''; });
    var both = !!(where.test && where.test.url);
    buttons.forEach(function (button) { show(button, !!where[button.getAttribute(TAB)]); });
    show(part('tabs'), both);
    frames.reloadWhenBlocked(where.main.url);
    show(part('editor'), true);
    show(part('controls'), !!where.runs);
    status.textContent = '';
    show(output, false);
    select(where.opened === 'test' && both ? 'test' : 'main');
    setTimeout(function () { remember(null); }, 5000);
    region.focus({ preventScroll: true });
    region.scrollIntoView({ block: 'start' });
  }

  /* ⚠️ A COLD instance's page is reloaded once, by `frames.reloadWhenBlocked`,
     when its frame policy blocked the first frame — and a reload forgets the
     click. ⭐ So the file asked for rides on this history entry's own state,
     which a reload keeps and nothing else reads, until it is drawn; a page that
     was just reloaded opens it again. ⛔ Not the browser's store: that is
     `study-progress.js`'s alone. ⛔ Only a reload reopens it, and a history
     that cannot carry it is no history: the reader clicks again. */
  var REOPEN = 'studyforgeCode';

  function remember(path) {
    try {
      var state = {};
      state[REOPEN] = path || null;
      history.replaceState(state, '');
    } catch (ignored) { return; }
  }

  function reopened() {
    try {
      var timing = performance.getEntriesByType('navigation');
      var path = history.state && history.state[REOPEN];
      remember(null);
      return timing.length && timing[0].type === 'reload' ? path : null;
    } catch (ignored) { return null; }
  }

  function open(path, href) {
    var fallback = function () { remember(null); if (href) { location.href = href; } };
    remember(path);
    run.code(corpus, path).then(function (where) {
      if (where) { draw(where); } else { fallback(); }
    }, fallback);
  }

  buttons.forEach(function (button) {
    button.addEventListener('click', function () {
      if (current) { select(button.getAttribute(TAB)); }
    });
  });

  act.addEventListener('click', function () {
    if (!current || !current.runs) { return; }
    act.disabled = true;
    show(stop, true);
    output.textContent = '';
    show(output, true);
    status.textContent = 'Running the test…';
    run.codeTest(corpus, current.runs, function (line) {
      output.textContent += line + '\n';
    }).then(function (verdict) {
      status.textContent = verdict === 0 ? 'Passed.' : verdict === 'stopped' ? 'Stopped.'
        : verdict === 'timeout' ? 'Timed out.' : 'Failed.';
    }, function () {
      status.textContent = 'The test could not be run.';
    }).then(function () {
      act.disabled = false;
      show(stop, false);
    });
  });

  stop.addEventListener('click', function () { run.stop(); });

  /* ⭐ Only an editor that is UP turns the links into the panel; until then
     every link is the plain view and the built sentence stands. */
  run.editor(corpus).then(function (found) {
    if (!found) { return; }
    show(part('plain'), false);
    show(part('copy'), true);
    document.addEventListener('click', function (event) {
      if (event.defaultPrevented || event.button !== 0) { return; }
      if (event.metaKey || event.ctrlKey || event.shiftKey || event.altKey) { return; }
      var anchor = event.target.closest ? event.target.closest('a[' + PATH + ']') : null;
      if (!anchor) { return; }
      event.preventDefault();
      open(anchor.getAttribute(PATH), anchor.href);
    });
    var again = reopened();
    if (again) { open(again, null); }
  }, function () { return null; });
}());
