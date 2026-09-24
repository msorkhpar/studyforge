/* The quiz: what a reader chose, and what the local study server said about it.

   ⛔ **THE KEY IS NOT IN THE PAGE, AND THIS FILE DOES NOT GRADE** — the user's
   ruling of 2026-09-23: *"a test with the correct answer residing on
   the server side. When user answers it will get validated and result will be
   returned to the user with explanation if needed"*. ⭐ So this file reads
   which option the reader chose, hands the choices to `window.studyforge.quiz`
   — which the SERVING PROCESS adds to a served page and a built page never
   names (R8, `W370`) — and shows what came back: right or wrong per question,
   the chosen option's sentence, the count, and whether the quiz is complete.
   ⛔ **The completion rule is the server's** (`exercise.quiz.completes`, applied
   once, in Python); this file shows `complete` and never re-derives it.

   ⚠️ **Superseded, and kept readable so it is not re-derived:** until that
   ruling this file graded in the page from a key every option carried, identically
   over `file://`, on the stance that an offline page cannot hide the key it grades
   with. The ruling removes the key from the page instead.

   ⭐ **Over `file://` the questions and the options still show** and a reader
   may still choose; the Check control stays `hidden` and the `offline`
   sentence stays showing, exactly as Run and Submit do in the code panel. ⛔
   Nothing is sent from a file page — there is no origin to send it to.

   ⛔ **A quiz has no file, no command and no grader to submit to, so it renders
   no Run and no Submit — and not disabled ones** (`AX-05/3`, `SF-24`'s standing
   rule about a dead button).

   ⛔ **Nothing is written to browser storage, and the server records nothing
   either.** What a reader answered is the page's for as long as they are on
   it; ⚠️ **so a reload clears the answers**, and recording a quiz's completion
   in the reader's own state is a decision for the row that takes it — never a
   run verdict, which a quiz does not produce.

   ⭐ **Every word this file says is read off the markup**, where Python put it —
   the same two-sided spelling every hook on this page has (`W431`). */

(function () {
  'use strict';

  var QUIZ = 'section[data-practice-quiz]';
  var PART = 'data-practice-part';
  var QUESTION = 'data-practice-question';
  var VERDICT = 'data-practice-verdict';

  /* Where each of this file's own sentences is kept. ⚠️ `right` is read off two
     different elements and means two different things — the question's *Right.*
     and the section's counting line — which is why it is asked for by element
     rather than looked up in one table. */
  var RIGHT = 'data-practice-right';
  var WRONG = 'data-practice-wrong';
  var COMPLETE = 'data-practice-complete';
  var BLANK = 'data-practice-blank';
  var CHECKING = 'data-practice-checking';
  var FAILED = 'data-practice-failed';

  function part(root, name) {
    return root.querySelector('[' + PART + '="' + name + '"]');
  }

  function words(element, name) {
    return (element && element.getAttribute(name)) || '';
  }

  /* What the reader chose, as `{question id: option id}`. ⚠️ Read off the DOM
     rather than remembered: the radios ARE the state, and a second copy of them
     would be a second answer to *what did they choose?*. */
  function chosen(quiz) {
    var answers = {};
    [].slice.call(quiz.querySelectorAll('[' + QUESTION + ']')).forEach(function (question) {
      var picked = question.querySelector('input[type="radio"]:checked');
      if (picked) { answers[question.getAttribute(QUESTION)] = picked.value; }
    });
    return answers;
  }

  /* One question's row of the server's verdict, drawn. ⭐ The sentence is the
     one for whatever the reader CHOSE, right or wrong — a page that showed one
     only for a wrong answer would teach half the material. ⛔ A question the
     verdict says nobody answered shows nothing. */
  function draw(question, row) {
    var says = part(question, 'says');
    if (!row || !row.answered) {
      question.removeAttribute(VERDICT);
      if (says) { says.textContent = ''; says.hidden = true; }
      return;
    }
    question.setAttribute(VERDICT, row.correct ? 'correct' : 'wrong');
    if (says) {
      says.textContent = words(says, row.correct ? RIGHT : WRONG) + ' ' + (row.says || '');
      says.hidden = false;
    }
  }

  function show(quiz, verdict) {
    var rows = {};
    (verdict.questions || []).forEach(function (row) { rows[row.id] = row; });
    [].slice.call(quiz.querySelectorAll('[' + QUESTION + ']')).forEach(function (question) {
      draw(question, rows[question.getAttribute(QUESTION)]);
    });
    var status = part(quiz, 'status');
    if (!status) { return; }
    /* ⛔ **Complete is the SERVER's word** and is EVERY question answered
       correctly; the count is said in every other case so a reader is never
       told only that they are not finished. */
    status.textContent = verdict.complete === true
      ? words(status, COMPLETE)
      : words(status, RIGHT).replace('{right}', verdict.right).replace('{asked}', verdict.asked);
  }

  function wire(quiz, client) {
    var check = part(quiz, 'check');
    var controls = part(quiz, 'controls');
    var offline = part(quiz, 'offline');
    var status = part(quiz, 'status');
    if (!check || !controls) { return; }
    if (offline) { offline.hidden = true; }
    controls.hidden = false;
    var graded = false;
    /* ⭐ Only the LATEST request may draw: a reader who changes an answer while
       the previous one is still being checked must never see the older verdict
       land on top of the newer choice. */
    var asked = 0;

    function grade() {
      var answers = chosen(quiz);
      var ticket = ++asked;
      if (!Object.keys(answers).length) {
        show(quiz, { questions: [], right: 0, asked: 0, complete: false });
        if (status) { status.textContent = words(status, BLANK); }
        return;
      }
      if (status) { status.textContent = words(status, CHECKING); }
      client.grade(quiz.getAttribute('data-corpus'), quiz.getAttribute('data-practice-quiz'), answers)
        .then(function (verdict) {
          if (ticket === asked) { show(quiz, verdict); }
        }, function () {
          if (ticket === asked && status) { status.textContent = words(status, FAILED); }
        });
    }

    /* ⭐ Re-graded as soon as a reader changes an answer, once they have asked
       once, so the sentence under a question can never describe an option that
       is no longer chosen. */
    check.addEventListener('click', function () { graded = true; grade(); });
    quiz.addEventListener('change', function () { if (graded) { grade(); } });
  }

  var client = window.studyforge && window.studyforge.quiz;
  if (!client || !client.available()) { return; }
  [].slice.call(document.querySelectorAll(QUIZ)).forEach(function (quiz) { wire(quiz, client); });
}());
