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
   — ⚠️ and until something publishes where a running editor is, that sentence
   is the only state this part can reach (`SF-24/1`).

   ⛔ **Nothing is written to browser storage.** A run's outcome is the SERVER's
   record (`SF-21`), written where it was established; a page that also
   remembered would be a second answer to *did this pass?*. ⭐ So nothing here
   has to be namespaced against the one storage origin every `file://` page
   shares. */

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
  var STOP = 'stop';

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
      var keyboard = holdsFocus();
      status.textContent = text;
      live(false);
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
