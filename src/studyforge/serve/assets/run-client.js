/* The page's execution client: Run and Submit, over the served run namespace.

   ⭐ **Served by the run namespace itself, at `/api/v1/run/client.js`, and never
   written into a built site.** A built page opens over `file://` naming no server
   (R8, and the floor `tests/studyforge/cli/serving.py` reads); this file names
   the API on every line that matters, so it exists exactly where the API does —
   an origin that can answer it.

   ⭐ **A client and nothing else.** It publishes `studyforge.run` — `available`,
   `start`, `stop` — and draws nothing: the practice panel that puts Run and
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

  function stop() {
    if (!available()) { return refused('no-origin'); }
    return fetch(BASE + STOP, { method: 'POST', cache: 'no-store', credentials: 'same-origin' })
      .then(function (response) { return response.ok ? response.json() : refused(response.status); })
      .then(function (answer) { return answer.stopped === true; });
  }

  window.studyforge = window.studyforge || {};
  window.studyforge.run = { available: available, start: start, stop: stop, modes: MODES.slice() };
})();
