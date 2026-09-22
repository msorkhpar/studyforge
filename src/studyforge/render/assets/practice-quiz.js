/* The quiz: what a reader chose, whether it was right, and why it is what it is.

   ⛔ **NO SERVER, EVER — and that is the whole point of the shape** (spec §7 §7,
   `AX-05`). A quiz is graded with no compiler, no container, no network and no
   model: the key ships in the page and the rule is four lines of arithmetic, so
   the reading is IDENTICAL over `file://` and over a served origin (R8). ⭐ So
   this file does NOT ask `window.studyforge.run` whether an origin exists, and
   it must never be made to — a guard on the run client would make a quiz work
   only where a server happens to be, which is the one property this shape has
   that the code exercise does not.

   ⛔ **A quiz has no file, no command and no grader to submit to, so it renders
   no Run and no Submit — and not disabled ones** (`AX-05/3`, `SF-24`'s standing
   rule about a dead button). ⚠️ There is nothing here that hides such a control
   either: `render/page/practice.py` never emits one, which is the only place a
   control can be refused honestly.

   ⛔ **The key is IN the page and this file does not pretend otherwise.** The
   site is offline and the bundle is on the reader's disk, exactly as an offline
   workspace cannot hide its test file — claiming to hide either is the theatre
   R5 exists to prevent, and `exercise.quiz` says so first.

   ⛔ **Nothing is written to browser storage.** What a reader answered is the
   page's for as long as they are on it; a second, weaker record of *did this
   complete?* is exactly the second answer `practice.js` refuses to keep for a
   run. ⚠️ **So a reload clears the answers**, and that is a property rather than
   an oversight: recording a quiz's completion is a decision about the reader's
   own state and it belongs to the row that takes it, not to the panel.

   ⭐ **Every word this file says is read off the markup**, where Python put it —
   the same two-sided spelling every hook on this page has, because markup and
   script cannot import one another and the Python side is the single source for
   what is emitted (`W431`). */

(function () {
  'use strict';

  var QUIZ = 'section[data-practice-quiz]';
  var PART = 'data-practice-part';
  var QUESTION = 'data-practice-question';
  var OPTION = 'data-practice-option';
  var CORRECT = 'data-practice-correct';
  var SAYS = 'data-practice-says';
  var VERDICT = 'data-practice-verdict';

  /* Where each of this file's own sentences is kept. ⚠️ `right` is read off two
     different elements and means two different things — the question's *Right.*
     and the section's counting line — which is why it is asked for by element
     rather than looked up in one table. */
  var RIGHT = 'data-practice-right';
  var WRONG = 'data-practice-wrong';
  var COMPLETE = 'data-practice-complete';
  var BLANK = 'data-practice-blank';

  function part(root, name) {
    return root.querySelector('[' + PART + '="' + name + '"]');
  }

  function words(element, name) {
    return (element && element.getAttribute(name)) || '';
  }

  /* The option a reader chose, or `null`. ⚠️ Read off the DOM rather than
     remembered: the radios ARE the state, and a second copy of them would be a
     second answer to *what did they choose?*. */
  function chosen(question) {
    var picked = question.querySelector('input[type="radio"]:checked');
    return picked ? question.querySelector('[' + OPTION + '="' + picked.value + '"]') : null;
  }

  /* ⛔ **One question's reading, and it is TOTAL.** A question nobody answered
     is not correct — it is simply not answered, which is the same answer
     `exercise.quiz.grade` gives for a stored answer it does not recognise. */
  function read(question) {
    var picked = chosen(question);
    var says = part(question, 'says');
    var right = !!picked && picked.getAttribute(CORRECT) === 'true';
    if (!picked) {
      question.removeAttribute(VERDICT);
      if (says) { says.textContent = ''; says.hidden = true; }
      return { answered: false, correct: false };
    }
    question.setAttribute(VERDICT, right ? 'correct' : 'wrong');
    if (says) {
      /* ⭐ The sentence for whatever the reader chose, RIGHT OR WRONG. A page
         that showed one only for a wrong answer would teach half the material
         and would tell the reader which half by showing nothing. */
      says.textContent = words(says, right ? RIGHT : WRONG) + ' ' + picked.getAttribute(SAYS);
      says.hidden = false;
    }
    return { answered: true, correct: right };
  }

  function grade(quiz) {
    var questions = [].slice.call(quiz.querySelectorAll('[' + QUESTION + ']'));
    var status = part(quiz, 'status');
    var right = 0;
    var answered = 0;
    questions.forEach(function (question) {
      var reading = read(question);
      if (reading.answered) { answered += 1; }
      if (reading.correct) { right += 1; }
    });
    if (!status) { return; }
    if (!answered) {
      status.textContent = words(status, BLANK);
      return;
    }
    /* ⛔ **Complete is EVERY question answered correctly and nothing less**
       (`exercise.quiz.completes`), and the count is said in every other case so
       a reader is never told only that they are not finished. */
    status.textContent = right === questions.length && questions.length
      ? words(status, COMPLETE)
      : words(status, RIGHT).replace('{right}', right).replace('{asked}', questions.length);
  }

  /* ⭐ Re-graded as soon as a reader changes an answer, so the sentence under a
     question can never describe an option that is no longer chosen. */
  function wire(quiz) {
    var check = part(quiz, 'check');
    if (!check) { return; }
    var graded = false;
    check.addEventListener('click', function () { graded = true; grade(quiz); });
    quiz.addEventListener('change', function () { if (graded) { grade(quiz); } });
  }

  [].slice.call(document.querySelectorAll(QUIZ)).forEach(wire);
}());
