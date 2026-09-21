/* The practice panel: Run, Submit, and the result, over the served run client.

   ⛔ **This file draws; it never talks to the API.** Everything it sends goes
   through `window.studyforge.run` — `available()`, `start(corpus, practice,
   mode, onLine)`, `stop()` — which the SERVING PROCESS adds to the page it
   answers (`E05` § how a served page loads the run client). ⭐ That is the whole
   reason this part can live in a built site at all: a built text that named the
   API, the serving origin or the client file is a defect R8's floor reads
   (`tests/studyforge/cli/serving.py`), and there is no such name below.

   ⛔ **Over `file://` there is no origin to ask, so the controls stay HIDDEN**
   and the panel shows the sentence that says why. ⚠️ Nothing is disabled: a
   dead button is a promise the page cannot keep, which is this panel's own
   rule about the editor and about Submit.

   ⛔ **The practice key and the two mode words are read off the markup,
   verbatim.** `data-practice` carries the string `progress.practice_key` minted
   in Python and `data-practice-act` carries one of `exercise.COMMANDS`. Nothing
   here composes a key, splits one, encodes one or invents a mode — the client
   refuses a malformed key before any request, and a key spelled twice would
   simply never match anything with nothing failing anywhere.

   ⛔ **The editor is NOT started from here, and that is deliberate.** It is a
   development environment with a shell, and opening a reading page is not
   consent to run one. The slot carries the sentence saying it is not running
   and how to start it, so a reader sees a statement rather than a blank frame
   — ⭐ and when `studyforge.run.practice(corpus, key)` answers where this
   practice's two windows are, the frames replace that sentence (`W416`,
   `W429`). ⛔ **Every URL is the SERVER's answer, never a name in this file**:
   a built page may name no origin and no port (R8), the editor's host port is
   per-project, and the absolute path a window opens is a path inside somebody
   else's container.

   ⛔ **This panel does not make anything read-only and never says it is.** The
   editor enforces that itself, out of the workspace settings the server writes
   — a guard here would be a second, weaker copy of a rule the editor keeps.

   ⛔ **Nothing is written to browser storage.** A run's outcome is the SERVER's
   record (`SF-21`), written where it was established; a page that also
   remembered would be a second answer to *did this pass?*. ⭐ So nothing here
   has to be namespaced against the one storage origin every `file://` page
   shares. ⚠️ **The reload below keeps that rule** — its whole state is the
   browser's own navigation type, which is why it needs nowhere to remember.

   ## ⛔ ONE reload, and only a genuinely COLD instance can ever need it (`W430`)

   ⭐ **What a served page may frame is composed from the editor origins the
   SERVING INSTANCE has discovered**, and a cold instance has discovered none
   until a reader's own client asks — which this panel does, exactly one
   document too late: the policy governing THIS document was sent before the
   ask. ⛔ **The serving process may not ask earlier.** Discovering an editor
   forks `docker`, and putting that on the path of an ordinary page response is
   refused outright (spec §8.3), so the remaining move is the client's.

   ⭐ **The browser is ASKED rather than guessed at.** A
   `securitypolicyviolation` naming `frame-src` and this editor's own host is
   the browser stating that the frame was blocked; the reload then gets a
   document composed from the record that ask has just filled. ⛔ **Nothing is
   reloaded on a hunch** — no violation, no reload.

   ⛔ **Three guards, and each one closes a real loop.** The blocked URI must be
   the editor's host, so an unrelated violation reloads nothing. The editor's
   host must be the host THIS page was reached at, because a server withholds an
   editor from another spelling of the same machine on purpose and no number of
   reloads would change that. And this navigation must not itself be a reload,
   which caps the whole remedy at one. ⚠️ **A browser with no navigation timing
   is not reloaded at all**: failing closed is a frame that does not load, and
   failing open is a page that reloads for ever. */

(function () {
  'use strict';

  /* The panel, and the attributes it carries. ⚠️ Spelled here and in
     `render/page/practice.py`, which is the same two-sided spelling every hook
     on this page has: markup and script cannot import one another, and the
     Python side is the single source for what is EMITTED. */
  var PANEL = 'section[data-practice]';
  var KEY = 'data-practice';
  var CORPUS = 'data-corpus';
  var PART = 'data-practice-part';
  var ACT = 'data-practice-act';
  var TAB = 'data-practice-tab';
  var FRAME = 'data-practice-frame';
  var STOP = 'stop';

  /* What the maximised panel is told apart by, and where the maximise control's
     OTHER word is kept — ⭐ both of its words are the template's, not this file's. */
  var EXPANDED = 'data-practice-expanded';
  var LABEL = 'data-practice-label';
  var ESCAPE = 'Escape';

  /* The two windows, and what each frame is called to a screen reader. ⚠️ These
     are the framework's own words for its own controls, not the material's
     (R1) — the same status the panel's 'Running…' and 'Passed.' already have. */
  var WINDOWS = ['main', 'test'];
  var TITLES = { main: 'Your code', test: 'Tests' };

  /* The directive a blocked editor frame is refused by, in the browser's own
     spelling. ⚠️ Compared as a PREFIX rather than for equality, because the
     older `violatedDirective` reports the whole directive — `frame-src 'none'`
     — where `effectiveDirective` reports only its name. */
  var FRAME_SRC = 'frame-src';

  function part(panel, name) {
    return panel.querySelector('[' + PART + '="' + name + '"]');
  }

  function show(element, visible) {
    if (element) { element.hidden = !visible; }
  }

  /* One line of output, appended as it arrives. ⚠️ `textContent`, never
     `innerHTML`: a program's own output is not markup, and a grader that
     printed a tag would otherwise be parsed as one. */
  function append(output, line) {
    output.appendChild(document.createTextNode(line + '\n'));
    output.scrollTop = output.scrollHeight;
  }

  /* What a finished run is called, from the verdict the client resolves with:
     a status number, 'timeout' or 'stopped'. ⛔ The server decides what a run
     MEANT and records it; this only says what the reader just watched. */
  function verdict(answer, mode) {
    if (answer === 'stopped') { return 'Stopped.'; }
    if (answer === 'timeout') { return 'Timed out.'; }
    if (answer !== 0) { return 'Finished with errors.'; }
    return mode === 'run' ? 'Finished.' : 'Passed.';
  }

  function refusal(answer) {
    if (answer && answer.refused === 409) {
      return 'Something is already running. Stop it first.';
    }
    return 'That could not be started.';
  }

  function frame(slot, url, title) {
    var built = document.createElement('iframe');
    built.src = url;
    built.title = title;
    slot.appendChild(built);
  }

  /* A URL's host, without its port and without its scheme. ⚠️ An IPv6 literal
     keeps its brackets, which is the spelling `location.hostname` uses too. */
  function hostOf(url) {
    var found = /^[a-z]+:\/\/([^/?#]*)/i.exec(String(url || ''));
    return found ? found[1].replace(/:\d+$/, '').toLowerCase() : '';
  }

  /* Reload once if, and only if, the browser says this document's policy
     blocked the editor's frame. ⛔ The three guards are argued at the top of
     this file, and each of them closes a loop rather than tidying one. */
  function reloadWhenBlocked(url) {
    var editor = hostOf(url);
    var timing = window.performance && window.performance.getEntriesByType
      ? window.performance.getEntriesByType('navigation')
      : [];
    if (!editor || editor !== String(location.hostname || '').toLowerCase()) { return; }
    if (!timing.length || timing[0].type === 'reload') { return; }
    var reloaded = false;
    document.addEventListener('securitypolicyviolation', function (event) {
      var directive = event.effectiveDirective || event.violatedDirective || '';
      if (reloaded || directive.indexOf(FRAME_SRC) !== 0) { return; }
      if (hostOf(event.blockedURI) !== editor) { return; }
      reloaded = true;
      location.reload();
    });
  }

  /* ⭐ **Two frames of ONE editor, one visible at a time — never a split pane.**
     The file a reader may type in and the file that judges it are two different
     acts of reading, and standing them side by side halves the width of both.

     ⛔ **Each frame's URL is the SERVER's answer and is never built here**: the
     window's own URL is the only thing that can point two windows of one editor
     at two different files, because an extension cannot read its own window's
     query string and both windows share one workspace settings file.

     ⛔ **The TESTS frame is built LAZILY, on the first click of its tab.** A
     second workbench is a second language server, and a reader who never opens
     the tests should never pay for one.

     ⛔ **This page neither claims nor enforces read-only.** The editor does, out
     of the workspace settings the server wrote; a guard here would be a second,
     weaker copy of a rule the editor already keeps. */
  function windows(panel, where) {
    var slots = {};
    WINDOWS.forEach(function (name) {
      slots[name] = panel.querySelector('[' + FRAME + '="' + name + '"]');
    });
    if (!slots.main) { return; }
    var tested = !!(where.test && where.test.url);
    var buttons = [].slice.call(panel.querySelectorAll('[' + TAB + ']')).filter(
      function (button) {
        var keep = tested || button.getAttribute(TAB) !== 'test';
        if (!keep) { button.hidden = true; }
        return keep;
      }
    );
    var lazy = false;

    function select(name) {
      buttons.forEach(function (button) {
        var mine = button.getAttribute(TAB) === name;
        button.setAttribute('aria-selected', mine ? 'true' : 'false');
        button.tabIndex = mine ? 0 : -1;
      });
      WINDOWS.forEach(function (one) { show(slots[one], one === name && !!slots[one]); });
      if (name === 'test' && !lazy && tested) {
        lazy = true;
        frame(slots.test, where.test.url, TITLES.test);
      }
    }

    /* ⛔ BEFORE the frame is added, because the violation it listens for is
       raised by adding it. */
    reloadWhenBlocked(where.main.url);
    frame(slots.main, where.main.url, TITLES.main);
    buttons.forEach(function (button) {
      button.addEventListener('click', function () { select(button.getAttribute(TAB)); });
      /* ⚠️ Arrow keys move between tabs, which is what a tablist is announced
         as promising. Without them the roles say one thing and the keyboard
         does another. */
      button.addEventListener('keydown', function (event) {
        var step = event.key === 'ArrowRight' ? 1 : event.key === 'ArrowLeft' ? -1 : 0;
        var next = buttons.indexOf(button) + step;
        if (!step || next < 0 || next >= buttons.length) { return; }
        event.preventDefault();
        buttons[next].focus();
        select(buttons[next].getAttribute(TAB));
      });
    });
    select('main');
    /* ⭐ One tab is no choice, so the tablist stays hidden where the material
       names no test — the same honesty as offering no Submit. */
    show(part(panel, 'tabs'), tested);
    show(part(panel, 'no-editor'), false);
  }

  /* ⭐ **MAXIMISE: the PANEL'S OWN GEOMETRY, and never a reparent** (`W431`).
     The reader asked for more room for the code, the tests, Run and Submit —
     and the panel already holds all of them, so the whole move is one attribute
     on the section the stylesheet lays out over the viewport.

     ⛔ **A frame is never moved to another parent.** An `iframe` REPARENTED IN
     THE DOM RELOADS: the unsaved buffer is gone and the code-server session
     restarts. ⚠️ So nothing below appends, removes or replaces a node, and what
     a reader had — both tabs, a live run, its output — survives untouched.

     ⛔ **A full-viewport surface with no keyboard exit is a trap.** The control
     is a real button, focus moves into the expanded practice and back to the
     control on restore, and Escape restores. ⚠️ Escape is read on the DOCUMENT
     because focus may be resting on `<body>`; a key pressed INSIDE the editor
     frame never reaches this document at all, which is right — Escape means
     something of its own in an editor. */
  function maximise(panel) {
    var button = part(panel, 'expand');
    if (!button) { return; }
    var words = [button.textContent, button.getAttribute(LABEL) || button.textContent];
    var wide = false;

    function set(open) {
      wide = open;
      if (open) { panel.setAttribute(EXPANDED, ''); } else { panel.removeAttribute(EXPANDED); }
      button.setAttribute('aria-expanded', open ? 'true' : 'false');
      button.textContent = words[open ? 1 : 0];
      /* ⛔ Into the expanded practice, and back to the control on restore: focus
         left outside a surface that covers the viewport strands a keyboard reader. */
      if (open) { panel.focus(); } else { button.focus(); }
    }

    show(button, true);
    button.addEventListener('click', function () { set(!wide); });
    document.addEventListener('keydown', function (event) {
      if (wide && event.key === ESCAPE) { set(false); }
    });
  }

  function wire(panel, run) {
    var key = panel.getAttribute(KEY);
    var corpus = panel.getAttribute(CORPUS);
    var controls = part(panel, 'controls');
    var status = part(panel, 'status');
    var output = part(panel, 'output');
    var acts = [].slice.call(panel.querySelectorAll('[' + ACT + ']'));
    if (!key || !corpus || !controls || !status || !output || !acts.length) { return; }

    /* ⭐ The editor slot is shown, and what it shows is the sentence saying the
       editor is not running. Hiding it instead would be the blank panel this
       row exists to refuse. */
    show(part(panel, 'offline'), false);
    show(part(panel, 'editor'), true);
    show(controls, true);
    /* ⚠️ Offered where there is something to maximise, and nowhere else: over
       `file://` this panel is one sentence, and a control that makes a sentence
       full-screen is the dead button this file refuses everywhere else. */
    maximise(panel);

    /* ⭐ Fill the editor slot when the server says where THIS PRACTICE's two
       windows are, and leave the sentence standing when it does not. ⛔ Frames
       are added only for an editor that is already up over this corpus's own
       files and that actually holds this practice's file — the server decides
       both, this asks.

       ⚠️ **Asked for, never assumed.** A site BUILT by one version of this
       framework may be SERVED by another, and the client is the serving
       process's; a panel that called a function an older client does not
       publish would take Run and Submit down with it. */
    if (run.practice) {
      run.practice(corpus, key).then(function (where) {
        if (where && where.main && where.main.url) { windows(panel, where); }
      }, function () { return null; });
    }

    var stop = null;
    var starters = [];
    acts.forEach(function (button) {
      if (button.getAttribute(ACT) === STOP) { stop = button; } else { starters.push(button); }
    });

    /* ⛔ **Focus follows the control that goes away, and that is keyboard
       correctness rather than polish.** A button that is disabled or hidden
       while it holds focus drops focus to the document, and a keyboard reader
       is returned to the top of the page mid-run. So the start moves focus to
       Stop and the end gives it back to the button that was pressed — and only
       ever when this panel already had it. */
    var pressed = null;

    /* ⛔ **Set when STOP takes focus away from this panel itself**, which is the
       one hand-back `holdsFocus()` cannot answer for. Pressing Stop disables
       Stop, a disabled element drops focus to the document AT ONCE, and the
       run then settles a moment later with focus already on `<body>` — so the
       question *did the panel have focus?* answers no and the keyboard reader
       is left at the top of the page. ⚠️ **Measured in a browser by `W417`,
       the first reading this panel ever had on a served origin**; the ordinary
       end-of-run path was correct and only this one was not. */
    var handedBack = false;

    /* ⚠️ Asked BEFORE the control is disabled or hidden, never after: a
       disabled element drops focus to the document immediately, so a check
       taken afterwards always answers no and the reader is left at the top of
       the page. */
    function holdsFocus() {
      return panel.contains(document.activeElement);
    }

    function live(running) {
      starters.forEach(function (button) { button.disabled = running; });
      show(stop, running);
    }

    function settle(text) {
      var keyboard = holdsFocus() || handedBack;
      handedBack = false;
      status.textContent = text;
      live(false);
      /* ⛔ AFTER `live(false)`: the button that was pressed is disabled while
         the run is live, and focusing a disabled control does nothing at all. */
      if (keyboard && pressed) { pressed.focus(); }
    }

    starters.forEach(function (button) {
      button.addEventListener('click', function () {
        var mode = button.getAttribute(ACT);
        var keyboard = holdsFocus();
        pressed = button;
        output.textContent = '';
        show(output, true);
        status.textContent = 'Running…';
        live(true);
        if (keyboard && stop) { stop.focus(); }
        run.start(corpus, key, mode, function (line) { append(output, line); }).then(
          function (answer) { settle(verdict(answer, mode)); },
          function (answer) { settle(refusal(answer)); }
        );
      });
    });

    if (stop) {
      stop.addEventListener('click', function () {
        /* ⛔ Asked BEFORE the line below, for the reason `holdsFocus` states:
           this IS the disable that drops focus to the document. */
        handedBack = holdsFocus();
        stop.disabled = true;
        run.stop().then(
          function () { stop.disabled = false; },
          function () { stop.disabled = false; }
        );
      });
    }
  }

  var panels = [].slice.call(document.querySelectorAll(PANEL));
  if (!panels.length) { return; }
  var run = window.studyforge && window.studyforge.run;
  if (!run || !run.available()) { return; }
  panels.forEach(function (panel) { wire(panel, run); });
}());
