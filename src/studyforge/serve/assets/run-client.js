/* The page's execution client: Run and Submit, over the served run namespace.

   ⭐ **Served by the run namespace itself, at `/api/v1/run/client.js`, and never
   written into a built site.** A built page opens over `file://` naming no server
   (R8, and the floor `tests/studyforge/cli/serving.py` reads); this file names
   the API on every line that matters, so it exists exactly where the API does —
   an origin that can answer it.

   ⭐ **A client and nothing else.** It publishes `studyforge.run` — `available`,
   `start`, `stop`, `editor`, `practice` — and `studyforge.quiz` — `available`,
   `grade` (below) — and draws nothing: the practice panel that puts Run and
   Submit in front of a reader is `SF-24`'s, at `M7`. ⛔ A control this file
   drew before that panel existed would be a dead button, and a dead button is
   a promise the page cannot keep.

   ⛔ **Nothing this sends becomes a command** (spec §8.3, rule 3). A start is
   a `POST` to `/api/v1/run/<corpus>/<mode>/<practice>` with NO body: the path
   SELECTS a practice and one of its two acts, and the server reads the command
   from the unit's generated document. There is no argument here that could
   carry a command, and none is sent.

   ⛔ **The practice is named by its key, verbatim** (`SF-21/4`): the string
   `progress.practice_key` minted in Python, which the page carries. Nothing
   here composes a key, splits one or encodes one; a key that is not segments
   of lowercase letters, digits and hyphens is refused before any request —
   a `.` or `..` segment would otherwise be resolved by the browser into a
   different endpoint.

   ⭐ **The two modes are the data's own words**: `run` (Run: the reader's
   program) and `test` (Submit: the grader). Only a `test` that exits 0 ever
   completes a practice, and that is decided and recorded by the server.

   ⭐ **Output arrives line by line** and each line is handed to `onLine` as it
   arrives; the promise resolves with the verdict the last line spells — a
   status, `timeout` or `stopped`. ⛔ Over `file://` there is no origin to ask
   (R8), so `available()` is false and nothing is sent — should a copy of this
   file ever be loaded there. */

(function () {
  'use strict';

  var BASE = '/api/v1/run/';
  var MODES = ['run', 'test'];
  var STOP = 'stop';
  var EDITOR = 'editor';
  var KEY = /^[a-z0-9]+(?:-[a-z0-9]+)*(?:\/[a-z0-9]+(?:-[a-z0-9]+)*)+$/;
  var CORPUS = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;
  var EXIT = /^--- exit (.+) ---$/;

  function available() {
    return (location.protocol === 'http:' || location.protocol === 'https:') &&
      typeof fetch === 'function' && typeof TextDecoder === 'function';
  }

  function refused(reason) {
    return Promise.reject({ refused: reason });
  }

  /* Split what arrived into whole lines; the remainder waits for the next chunk. */
  function lines(buffer, onLine) {
    var parts = buffer.split('\n');
    var rest = parts.pop();
    parts.forEach(function (line) { onLine(line); });
    return rest;
  }

  function verdictOf(last) {
    var found = EXIT.exec(last || '');
    if (!found) { return null; }
    return /^\d+$/.test(found[1]) ? Number(found[1]) : found[1];
  }

  function start(corpus, practice, mode, onLine) {
    if (!available()) { return refused('no-origin'); }
    if (MODES.indexOf(mode) === -1) { return refused('mode'); }
    if (!CORPUS.test(corpus) || !KEY.test(practice)) { return refused('practice'); }
    var last = null;
    var each = function (line) {
      last = line;
      if (onLine) { onLine(line); }
    };
    return fetch(BASE + corpus + '/' + mode + '/' + practice, {
      method: 'POST',
      cache: 'no-store',
      credentials: 'same-origin'
    }).then(function (response) {
      if (!response.ok) { return refused(response.status); }
      var reader = response.body.getReader();
      var decoder = new TextDecoder();
      var buffer = '';
      function pump() {
        return reader.read().then(function (chunk) {
          if (chunk.done) {
            buffer += decoder.decode();
            if (buffer) { each(buffer); }
            return verdictOf(last);
          }
          buffer = lines(buffer + decoder.decode(chunk.value, { stream: true }), each);
          return pump();
        });
      }
      return pump();
    });
  }

  /* The run index, asked once per page and remembered. ⭐ Where a running
     editor is can only be true at SERVE time: its host port is per-project and
     a built page may name no origin and no port (R8), so the page asks the
     origin it is being read at. ⛔ An index that cannot be read is no editor,
     never an error a reader sees. */
  var index = null;

  function asked() {
    if (!index) {
      index = fetch(BASE, { cache: 'no-store', credentials: 'same-origin' })
        .then(function (response) { return response.ok ? response.json() : {}; })
        .then(null, function () { return {}; });
    }
    return index;
  }

  /* Where this corpus's editor is — { origin, folder } — or null when there is
     not one to say. ⛔ Nothing here starts one, and nothing here builds a URL:
     a caller decides what to do with an origin and a folder. */
  function editor(corpus) {
    if (!available()) { return refused('no-origin'); }
    if (!CORPUS.test(corpus)) { return refused('corpus'); }
    return asked().then(function (answer) {
      var found = answer && answer.editor && answer.editor[corpus];
      return found && found.origin && found.folder ? found : null;
    });
  }

  /* One practice's two editor windows: where each is, and the workspace
     settings they are read under, prepared by the server on the way.

     ⭐ **Two windows of ONE editor, and each is addressed by its own URL** —
     which is the only thing that can tell them apart: an extension cannot read
     its own window's query string, and both windows share one workspace
     settings file, so anything an extension opened it would open in BOTH.

     ⛔ **The URLs are the SERVER's, never built here.** The `vscode-remote`
     authority is the editor's own host and port, which only the origin the
     reader is reading at can say (R8), and a path the editor does not hold is
     answered as nothing rather than as a URL that would open an empty, dirty
     buffer titled with the file's own name.

     ⛔ **`editor` stands where a mode stands and is not one of `MODES`**: it
     starts nothing. ⚠️ Anything but an answer — no editor, no such practice, a
     workspace that could not be prepared — is `null`, never an error a reader
     sees, and the page then shows the sentence it already ships. */
  function practice(corpus, key) {
    if (!available()) { return refused('no-origin'); }
    if (!CORPUS.test(corpus) || !KEY.test(key)) { return refused('practice'); }
    return fetch(BASE + corpus + '/' + EDITOR + '/' + key, {
      method: 'POST',
      cache: 'no-store',
      credentials: 'same-origin'
    }).then(function (response) {
      return response.ok ? response.json() : null;
    }).then(function (answer) {
      return answer && answer.main && answer.main.url ? answer : null;
    }, function () { return null; });
  }

  function stop() {
    if (!available()) { return refused('no-origin'); }
    return fetch(BASE + STOP, { method: 'POST', cache: 'no-store', credentials: 'same-origin' })
      .then(function (response) { return response.ok ? response.json() : refused(response.status); })
      .then(function (answer) { return answer.stopped === true; });
  }

  /* ⭐ A QUIZ IS GRADED HERE TOO, AND IT IS NOT A RUN (the user's ruling
     of 2026-09-23). The key never reaches the page: what the reader chose is
     sent to `/api/v1/quiz/<corpus>/<practice>/<question>=<option>/…` and the
     server answers the verdict — right or wrong per question, the CHOSEN
     option's sentence, the count, and whether the quiz is complete. ⛔ It is
     published as `studyforge.quiz` and not under `run`: it starts nothing,
     records nothing, and produces no run. ⚠️ It lives in this file because
     this is the ONE script a serving process adds to a page (`W370`), and a
     second insertion would be a second place a built page could learn it is
     being served. ⛔ The answers travel in the PATH because a request body is
     discarded by the server, unread — so a question or option id that is not
     `QUIZ_ID`'s shape is refused here, before any request. */
  var QUIZ_BASE = '/api/v1/quiz/';
  var CHOSE = '=';
  var QUIZ_ID = /^[A-Za-z0-9][A-Za-z0-9._-]*$/;

  function grade(corpus, practice, answers) {
    if (!available()) { return refused('no-origin'); }
    if (!CORPUS.test(corpus) || !KEY.test(practice)) { return refused('practice'); }
    var segments = [];
    var ids = Object.keys(answers || {});
    for (var at = 0; at < ids.length; at += 1) {
      var option = answers[ids[at]];
      if (!QUIZ_ID.test(ids[at]) || typeof option !== 'string' || !QUIZ_ID.test(option)) {
        return refused('answer');
      }
      segments.push(ids[at] + CHOSE + option);
    }
    var path = QUIZ_BASE + corpus + '/' + practice + (segments.length ? '/' + segments.join('/') : '');
    return fetch(path, { method: 'POST', cache: 'no-store', credentials: 'same-origin' })
      .then(function (response) { return response.ok ? response.json() : refused(response.status); });
  }

  window.studyforge = window.studyforge || {};
  window.studyforge.quiz = { available: available, grade: grade };
  window.studyforge.run = {
    available: available,
    start: start,
    stop: stop,
    editor: editor,
    practice: practice,
    modes: MODES.slice()
  };
})();
