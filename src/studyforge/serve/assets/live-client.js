/* The page's live-run client: the reader's own API key, and a Live run control where a page has
   an example or a practice that may run live.

   ⭐ **Served by the live namespace at `/api/v1/live/client.js`, and written into no built page.**
   The serving process adds the one script tag to a page it answers, and only when this instance's
   compose started the live runner for a corpus that declares live runs; a built page and a
   read-only preview carry no key field, no script, no style and no route name for it (R8). Every
   control and every style below is drawn BY this script, so a page it never reaches has none.

   ⛔ **Where the key is, and where it is not.** It is typed into one password field. Pressing
   "Use this key" keeps it in `sessionStorage` (gone when the tab closes) and, only when the
   reader ticks the opt-in under a plain warning, in `localStorage` too. Storage that is refused
   leaves it in memory, for this page's life. "Clear" removes it from all three. It is sent in ONE
   request: the body of the live-run `POST` to this page's own origin. It is never in a URL, a
   query string, a cookie, `window.name`, a message to another window, the page's markup outside
   the field, an error line or the console: this file makes no call to `console`. The field is
   emptied the moment the key is taken.

   ⛔ **A run is selected, never composed.** The request names a corpus, a kind (`example` or
   `practice`) and a target the live index listed; the server reads the command from the corpus's
   own records. Output arrives line by line and is written as text, never as markup. */

(function () {
  'use strict';

  var BASE = '/api/v1/live/';
  var STORE = 'studyforge.live.key';
  var SHAPE = /^[A-Za-z0-9_-]{8,256}$/;
  var EXIT = /^--- exit (.+) ---$/;
  var CORPUS = 'data-corpus';

  if (!(location.protocol === 'http:' || location.protocol === 'https:') ||
      typeof fetch !== 'function' || typeof TextDecoder !== 'function') { return; }

  /* The key, in memory, for the life of this page. Everything else is a copy of it. */
  var held = null;
  var index = null;

  function guarded(action) {
    try { return action(); } catch (refused) { return null; }
  }
  function remembered() { return guarded(function () { return localStorage.getItem(STORE); }); }
  function session() { return guarded(function () { return sessionStorage.getItem(STORE); }); }

  function make(tag, attributes, text) {
    var element = document.createElement(tag);
    Object.keys(attributes || {}).forEach(function (name) { element.setAttribute(name, attributes[name]); });
    if (text) { element.textContent = text; }
    return element;
  }

  function targetsOf() {
    var found = [];
    var lists = [].slice.call(document.querySelectorAll('div[data-code-examples][' + CORPUS + ']'));
    lists.forEach(function (list) {
      var corpus = list.getAttribute(CORPUS);
      var declared = index.corpora[corpus];
      if (!declared) { return; }
      [].slice.call(list.querySelectorAll('details[data-code-example]')).forEach(function (details) {
        var paths = [].slice.call(details.querySelectorAll('a[data-code-path]'))
          .map(function (anchor) { return anchor.getAttribute('data-code-path'); });
        var path = paths.filter(function (one) { return declared.examples.indexOf(one) !== -1; })[0];
        if (path) { found.push({ corpus: corpus, kind: 'example', target: path, host: details }); }
      });
    });
    [].slice.call(document.querySelectorAll('section[data-practice][' + CORPUS + ']')).forEach(function (panel) {
      var corpus = panel.getAttribute(CORPUS);
      var declared = index.corpora[corpus];
      var key = panel.getAttribute('data-practice');
      if (declared && declared.practices.indexOf(key) !== -1) {
        found.push({ corpus: corpus, kind: 'practice', target: key, host: panel });
      }
    });
    return found;
  }

  var STYLE =
    '[data-live-panel]{border:1px solid currentColor;border-radius:.4rem;padding:.75rem 1rem;margin:1rem 0;max-width:46rem}' +
    '[data-live-panel] label{display:block;margin:.5rem 0 .25rem}' +
    '[data-live-panel] input[type=password]{width:100%;max-width:30rem;box-sizing:border-box;font:inherit;padding:.4rem}' +
    '[data-live-panel] button,[data-live-run] button{font:inherit;margin:.5rem .5rem 0 0;padding:.35rem .8rem;min-height:2.5rem}' +
    '[data-live-run]{margin:.75rem 0}' +
    '[data-live-run] pre{white-space:pre-wrap;overflow-wrap:anywhere;margin:.5rem 0}';

  function panel(corpusNames) {
    var declared = index.corpora[corpusNames[0]];
    var box = make('section', { 'data-live-panel': '', 'aria-labelledby': 'live-title' });
    box.appendChild(make('h2', { id: 'live-title' }, 'Run live with your own key'));
    box.appendChild(make('p', {},
      'A live run sends real requests to ' + declared.host + ' with the key you type here, and ' +
      'the provider may bill your account for them. It is optional and is never graded.'));
    var risks = make('ul');
    [
      'The key stays in this browser. By default it is kept for this tab only; if you choose to ' +
        'keep it on this device, anyone using this browser profile can read it, and so can browser extensions.',
      'While a run lasts the key is in the environment of the running program, inside the live ' +
        'runner container. Anything running as the same user there, and an administrator of the ' +
        'Docker machine, can read it.',
      'The program you run holds the key. It can send it to ' + declared.host + ' and to the other ' +
        'services on the course\'s internal network. Run only code you have read.'
    ].forEach(function (text) { risks.appendChild(make('li', {}, text)); });
    box.appendChild(risks);
    var status = make('p', { role: 'status', 'aria-live': 'polite', 'data-live-status': '' });
    box.appendChild(status);
    box.appendChild(make('label', { 'for': 'live-key' }, 'API key'));
    var field = make('input', {
      id: 'live-key', type: 'password', autocomplete: 'off', autocapitalize: 'off',
      autocorrect: 'off', spellcheck: 'false', 'data-lpignore': 'true', 'data-1p-ignore': '',
      'data-live-field': ''
    });
    box.appendChild(field);
    var optin = make('input', { id: 'live-remember', type: 'checkbox', 'data-live-remember': '' });
    var remember = make('label', { 'for': 'live-remember' });
    remember.appendChild(optin);
    remember.appendChild(document.createTextNode(
      ' Keep the key on this device after this tab closes (local storage).'));
    box.appendChild(remember);
    var use = make('button', { type: 'button', 'data-live-use': '' }, 'Use this key');
    var clear = make('button', { type: 'button', 'data-live-clear': '' }, 'Clear the key');
    box.appendChild(use);
    box.appendChild(clear);

    function say(text) { status.textContent = text; }
    function describe() {
      if (!index.enabled) {
        say('Live runs are not started. Bring the course up with the live profile (see EXECUTION.md) and reload this page.');
      } else if (held) {
        say('A key is set. It is not shown.');
      } else {
        say('No key is set.');
      }
    }
    optin.checked = !!remembered();
    held = session() || remembered() || null;
    describe();
    use.addEventListener('click', function () {
      var typed = field.value;
      field.value = '';
      if (!SHAPE.test(typed)) {
        say('A key is 8 to 256 letters, digits, hyphens and underscores.');
        typed = null;
        return;
      }
      held = typed;
      typed = null;
      var kept = guarded(function () { sessionStorage.setItem(STORE, held); return true; });
      var local = optin.checked
        ? guarded(function () { localStorage.setItem(STORE, held); return true; }) : true;
      if (!optin.checked) { guarded(function () { localStorage.removeItem(STORE); }); }
      say(kept && local ? 'Key set.'
        : 'This browser refuses storage, so the key is kept in memory until this page closes.');
    });
    clear.addEventListener('click', function () {
      held = null;
      field.value = '';
      optin.checked = false;
      guarded(function () { sessionStorage.removeItem(STORE); });
      guarded(function () { localStorage.removeItem(STORE); });
      say('The key was cleared from this page, this tab and this device.');
    });
    return box;
  }

  function control(found, box) {
    var wrap = make('div', { 'data-live-run': '' });
    var run = make('button', { type: 'button' }, 'Run live');
    var stop = make('button', { type: 'button' }, 'Stop');
    stop.hidden = true;
    var status = make('p', { role: 'status', 'aria-live': 'polite' });
    var output = make('pre', { tabindex: '0' });
    output.hidden = true;
    [run, stop, status, output].forEach(function (one) { wrap.appendChild(one); });
    stop.addEventListener('click', function () {
      var api = window.studyforge && window.studyforge.run;
      if (api && api.stop) { api.stop(); }
    });
    run.addEventListener('click', function () {
      if (!held) { status.textContent = 'Set your key above first.'; return; }
      run.disabled = true;
      stop.hidden = false;
      output.textContent = '';
      output.hidden = false;
      status.textContent = 'Running live…';
      var rest = '';
      fetch(index.run, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', 'X-Studyforge-Live': '1', Accept: 'text/plain' },
        body: JSON.stringify({ corpus: found.corpus, kind: found.kind, target: found.target, key: held }),
        credentials: 'omit', cache: 'no-store', referrerPolicy: 'no-referrer'
      }).then(function (response) {
        if (!response.ok) {
          return response.json().then(function (body) {
            status.textContent = body && typeof body.error === 'string' ? body.error : 'The run was refused.';
          }, function () { status.textContent = 'The run was refused.'; });
        }
        var reader = response.body.getReader();
        var decoder = new TextDecoder();
        var last = '';
        function pump() {
          return reader.read().then(function (step) {
            if (step.done) { return; }
            rest += decoder.decode(step.value, { stream: true });
            var parts = rest.split('\n');
            rest = parts.pop();
            parts.forEach(function (line) { last = line; output.textContent += line + '\n'; });
            return pump();
          });
        }
        return pump().then(function () {
          var verdict = EXIT.exec(last);
          status.textContent = verdict && verdict[1] === '0' ? 'Finished.'
            : verdict && verdict[1] === 'stopped' ? 'Stopped.'
            : verdict && verdict[1] === 'timeout' ? 'Timed out.' : 'The run failed.';
        });
      }).then(null, function () {
        status.textContent = 'The live run could not be started.';
      }).then(function () {
        run.disabled = false;
        stop.hidden = true;
      });
    });
    found.host.appendChild(wrap);
  }

  fetch(BASE, { headers: { Accept: 'application/json' }, cache: 'no-store', credentials: 'omit' })
    .then(function (answer) { return answer.ok ? answer.json() : null; })
    .then(function (document_) {
      if (!document_ || document_.resource !== 'live-index') { return; }
      index = document_;
      var found = targetsOf();
      if (!found.length) { return; }
      var style = make('style', { 'data-live-style': '' }, STYLE);
      document.head.appendChild(style);
      var box = panel([found[0].corpus]);
      var anchor = found[0].host.closest('div[data-code-examples]') || found[0].host;
      anchor.parentNode.insertBefore(box, anchor);
      found.forEach(function (one) { control(one, box); });
    }, function () { return null; });
}());
