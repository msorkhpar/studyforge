/* The quiz: what a reader chose, whether it was right, and why — graded in the page.

   ⭐ **A quiz's answers live in the page, in a
   script local to that page, and nothing about a quiz is a server function.**
   This reverses the ruling that kept the key on the local study server. ⭐ So
   each quiz section carries its OWN key, as a JSON data block
   (`<script type="application/json" data-practice-part="key">`, written by
   `render/page/quiz.py`), and this file — shared by every page, and holding no
   answer — reads it and grades in the browser. ⛔ **No request is made to
   answer a quiz**, so the reading is the same over `file://` and served (R8).

   ⭐ **The rule, in full**: a question is right when the chosen option is its
   key; the chosen option's sentence is shown, right or wrong; and the quiz is
   complete only when EVERY question is answered right — no pass mark, no
   partial credit. ⚠️ A wrong answer shows its own sentence and never names
   the key: a reader told why their choice fails can try again.

   ⭐ **A complete quiz is recorded as passed in the reader's own browser store**
   (`study-progress.js`, where "Mark as read" keeps its marks), so its card reads
   *passed* after a reload. ⛔ Never on the server, and never as a run's pass.
   ⚠️ The answers themselves are not kept: a reload clears the choices, and the
   pass stays.

   ⭐ **The 2026-11 redesign adds three things and removes none**: the "N of M
   answered" line, kept up to date as options are chosen; the chosen option's
   own mark after Check (an icon the stylesheet draws, and the verdict's word);
   and Reset, offered once the quiz is checked, which clears the page and never
   the reader's recorded pass.

   ⛔ **A quiz has no file, no command and no grader to submit to, so it renders
   no Run and no Submit — and not disabled ones.** With no script at all, the
   Check control stays hidden and the page says why.

   ⭐ **Every word this file says is read off the markup**, where Python put it —
   the same two-sided spelling every hook on this page has. */

(function () {
  'use strict';

  var QUIZ = 'section[data-practice-quiz]';
  var PART = 'data-practice-part';
  var QUESTION = 'data-practice-question';
  var VERDICT = 'data-practice-verdict';

  /* What a quiz says when it is graded, raised on its section, so the card over
     it reads the reader's record again (`practice-workspace.js`). */
  var SETTLED = 'studyforge:practice-settled';

  /* Where each of this file's own sentences is kept. ⚠️ `right` is read off two
     different elements and means two different things — the question's *Right.*
     and the section's counting line. */
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

  /* This quiz's key, or null where the block is missing or is not one. ⛔ A
     quiz with no key cannot be graded, and says nothing rather than guess. */
  function keyOf(quiz) {
    var block = part(quiz, 'key');
    if (!block) { return null; }
    try {
      var key = JSON.parse(block.textContent);
      return key && typeof key === 'object' && !Array.isArray(key) ? key : null;
    } catch (error) {
      return null;
    }
  }

  /* What the reader chose, as `{question id: option id}`. ⚠️ Read off the DOM:
     the radios ARE the state. */
  function chosen(quiz) {
    var answers = {};
    [].slice.call(quiz.querySelectorAll('[' + QUESTION + ']')).forEach(function (question) {
      var picked = question.querySelector('input[type="radio"]:checked');
      if (picked) { answers[question.getAttribute(QUESTION)] = picked.value; }
    });
    return answers;
  }

  /* The chosen option's own mark: an icon (drawn by `practice-quiz.css`) and the verdict's
     word, inside the option's label so it is read with it. ⭐ The 2026-11 redesign: a status
     colour is never the only signal, so the card that turns green or red also says so in words.
     ⛔ Only the CHOSEN option is marked, never the key (see the rule above). */
  function unmark(question) {
    [].slice.call(question.querySelectorAll('[' + PART + '="mark"]')).forEach(function (mark) {
      mark.parentNode.removeChild(mark);
    });
  }

  function markChosen(question, said) {
    var picked = question.querySelector('input[type="radio"]:checked');
    var label = picked && picked.closest('label');
    if (!label) { return; }
    var mark = document.createElement('span');
    mark.setAttribute(PART, 'mark');
    mark.textContent = said.replace(/\.$/, '');
    label.appendChild(mark);
  }

  /* One question graded and drawn; answers whether it is right. ⭐ The sentence
     is the one for whatever the reader CHOSE, right or wrong. */
  function draw(question, entry, answer) {
    var says = part(question, 'says');
    var hasSaid = entry && entry.says && Object.prototype.hasOwnProperty.call(entry.says, answer);
    unmark(question);
    if (answer === undefined || !hasSaid) {
      question.removeAttribute(VERDICT);
      if (says) { says.textContent = ''; says.hidden = true; }
      return false;
    }
    var right = answer === entry.key;
    question.setAttribute(VERDICT, right ? 'correct' : 'wrong');
    markChosen(question, words(says, right ? RIGHT : WRONG));
    if (says) {
      /* ⚠️ The sentence is markup the BUILD rendered (`markup.inline`: escaped,
         its inline code as code); the verdict's own word stays text. */
      var word = document.createElement('strong');
      word.textContent = words(says, right ? RIGHT : WRONG);
      says.textContent = '';
      says.appendChild(word);
      says.appendChild(document.createTextNode(' '));
      says.insertAdjacentHTML('beforeend', entry.says[answer]);
      says.hidden = false;
    }
    return right;
  }

  function grade(quiz, key) {
    var answers = chosen(quiz);
    var status = part(quiz, 'status');
    var questions = [].slice.call(quiz.querySelectorAll('[' + QUESTION + ']'));
    var right = 0;
    questions.forEach(function (question) {
      var id = question.getAttribute(QUESTION);
      if (draw(question, key[id], answers[id])) { right += 1; }
    });
    /* ⛔ Complete is EVERY question answered right, and nothing less. */
    var complete = questions.length > 0 && right === questions.length;
    if (status) {
      status.textContent = !Object.keys(answers).length ? words(status, BLANK)
        : complete ? words(status, COMPLETE)
          : words(status, RIGHT).replace('{right}', right).replace('{asked}', questions.length);
    }
    var store = window.studyforge && window.studyforge.progress;
    if (complete && store) { store.passQuiz(quiz.getAttribute('data-practice-quiz')); }
    quiz.dispatchEvent(new CustomEvent(SETTLED, { bubbles: true }));
  }

  /* "N of M answered", counted off the radios as the reader chooses. ⭐ The 2026-11 redesign:
     the reader sees how far through the check they are before they ask for a verdict. */
  function count(quiz) {
    var line = part(quiz, 'count');
    if (!line) { return; }
    var asked = quiz.querySelectorAll('[' + QUESTION + ']').length;
    line.textContent = words(line, 'data-practice-count')
      .replace('{answered}', Object.keys(chosen(quiz)).length).replace('{asked}', asked);
    line.hidden = false;
  }

  /* Back to the quiz as it was opened: no choice, no verdict, no sentence. ⛔ A pass already
     recorded stays recorded: Reset clears the page, never the reader's record. */
  function reset(quiz) {
    [].slice.call(quiz.querySelectorAll('input[type="radio"]:checked')).forEach(function (input) {
      input.checked = false;
    });
    [].slice.call(quiz.querySelectorAll('[' + QUESTION + ']')).forEach(function (question) {
      draw(question, null, undefined);
    });
    var status = part(quiz, 'status');
    if (status) { status.textContent = ''; }
    count(quiz);
  }

  function wire(quiz) {
    var key = keyOf(quiz);
    var check = part(quiz, 'check');
    var again = part(quiz, 'reset');
    var controls = part(quiz, 'controls');
    var offline = part(quiz, 'offline');
    if (!key || !check || !controls) { return; }
    if (offline) { offline.hidden = true; }
    controls.hidden = false;
    count(quiz);
    var graded = false;
    /* ⭐ Re-graded as soon as a reader changes an answer, once they have asked
       once, so the sentence under a question can never describe an option that
       is no longer chosen. */
    check.addEventListener('click', function () {
      graded = true;
      grade(quiz, key);
      if (again) { again.hidden = false; }
    });
    quiz.addEventListener('change', function () {
      count(quiz);
      if (graded) { grade(quiz, key); }
    });
    if (again) {
      again.addEventListener('click', function () {
        graded = false;
        again.hidden = true;
        reset(quiz);
        quiz.focus();
      });
    }
  }

  [].slice.call(document.querySelectorAll(QUIZ)).forEach(wire);
}());
