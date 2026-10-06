/* What a run reported about each case beyond pass or fail: the failure message and the text the reader's own code wrote.

   ⭐ **A collector the panel calls, and nothing else.** `practice.js` hands every `--- detail {json} ---` line of a
   run to `window.studyforge.practiceDetail.collect(panel)`'s `add`, and calls `draw` when the run settles. This file
   never talks to the API and never reads storage; the lines arrive on the stream the panel already reads, and only
   because the panel ASKED (`start(..., { detail: true })`). ⛔ **A page whose server sends no such line draws
   nothing here**, so a course built before the lines existed renders exactly as it always did.

   ⛔ **Text is text.** Every line goes in with `textContent`; a program's log is not markup.

   ⭐ **Two kinds of text, kept apart.** *Your log* is what the code wrote through its language's logger, attributed to
   the case that was running. *Printed output* is what it printed; where the test tool records it per case it sits
   under the case, and where it does not it is shown once for the whole run and the page SAYS so. A practice that
   grades printed output is marked `data-practice-graded-output` on its panel, and its printed text is then called
   *Graded output*, so debug logging is never mistaken for what the checks compare. */

(function () {
  'use strict';

  var LINE = /^--- detail (\{.*\}) ---$/;
  var CASE = 'data-practice-case';
  var PART = 'data-practice-part';
  var WORDS = {
    log: 'Your log',
    out: 'Printed output',
    graded: 'Graded output',
    err: 'Printed to the error stream',
    run: 'Whole run',
    runNote: 'This test tool does not record printed text per case, so it is shown once for the whole run.',
    logNote: 'Log lines no case claimed.',
    cut: 'Only the last lines are kept; earlier ones were dropped.'
  };

  function element(tag, part, text) {
    var made = document.createElement(tag);
    if (part) { made.setAttribute(PART, part); }
    if (text !== undefined) { made.textContent = text; }
    return made;
  }

  function fold(title, lines, part) {
    var box = element('details', part);
    box.appendChild(element('summary', null, title + ' (' + lines.length + (lines.length === 1 ? ' line)' : ' lines)')));
    box.appendChild(element('pre', part + '-lines', lines.join('\n')));
    return box;
  }

  function list(value) {
    return Array.isArray(value) ? value.map(String) : [];
  }

  /* One record off the stream, or null when it is not one this file knows. */
  function parse(line) {
    var found = LINE.exec(line);
    if (!found) { return null; }
    try {
      var record = JSON.parse(found[1]);
      return record && record.v === 1 ? record : null;
    } catch (ignored) { return null; }
  }

  function collect(panel) {
    var cases = {};
    var run = null;

    function clear() {
      cases = {};
      run = null;
      [].slice.call(panel.querySelectorAll('[' + PART + '="case-detail"], [' + PART + '="run-detail"]'))
        .forEach(function (node) { node.remove(); });
    }

    /* Takes a stream line; answers the record when it was a detail line, so the panel keeps it off the output. */
    function add(line) {
      var record = parse(line);
      if (!record) { return null; }
      if (record.run) { run = record; } else if (typeof record.case === 'string') { cases[record.case] = record; }
      return record;
    }

    function printed(record) {
      var graded = panel.hasAttribute('data-practice-graded-output');
      var box = element('div', 'case-detail');
      if (record.message) { box.appendChild(element('pre', 'case-message', record.message)); }
      var log = list(record.log);
      if (log.length) {
        var folded = fold(WORDS.log, log, 'case-log');
        /* A case that did not pass opens its log: that is the text a reader came for. */
        folded.open = record.passed !== true;
        box.appendChild(folded);
      }
      var out = list(record.out).concat(list(record.err));
      if (out.length) { box.appendChild(fold(graded ? WORDS.graded : WORDS.out, out, 'case-out')); }
      return box.childNodes.length ? box : null;
    }

    function wholeRun(summary) {
      var log = list(run.log);
      var out = list(run.out);
      var err = list(run.err);
      if (!log.length && !out.length && !err.length && !run.truncated) { return; }
      var box = element('div', 'run-detail');
      if (log.length) {
        box.appendChild(fold(WORDS.log + ': ' + WORDS.logNote.toLowerCase(), log, 'run-log'));
      }
      if (out.length || err.length) {
        box.appendChild(element('p', 'run-note', WORDS.run + ': ' + WORDS.runNote));
        if (out.length) { box.appendChild(fold(WORDS.out, out, 'run-out')); }
        if (err.length) { box.appendChild(fold(WORDS.err, err, 'run-err')); }
      }
      if (run.truncated) { box.appendChild(element('p', 'run-note', WORDS.cut)); }
      summary.appendChild(box);
    }

    /* Put each case's text under its row, and the whole run's under the breakdown. */
    function draw() {
      var region = panel.querySelector('[' + PART + '="breakdown"]');
      if (!region) { return; }
      [].slice.call(region.querySelectorAll('[' + CASE + ']')).forEach(function (row) {
        var record = cases[row.getAttribute(CASE)];
        var box = record ? printed(record) : null;
        if (box) { row.appendChild(box); }
      });
      if (run) { wholeRun(region); }
    }

    return { add: add, draw: draw, clear: clear, passed: function () { return cases; } };
  }

  window.studyforge = window.studyforge || {};
  window.studyforge.practiceDetail = { collect: collect, parse: parse };
}());
