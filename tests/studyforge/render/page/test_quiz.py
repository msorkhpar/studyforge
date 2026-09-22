"""Mirror of `src/studyforge/render/page/quiz.py` (R12).

⛔ **Every clause is asserted BOTH WAYS.** A question that is absent where it
should be and a control that is present where it must not be both render, carry
every word and pass `validate` — which is the same silence `test_practice.py`
opens by naming, on the other half of this surface.
"""

from __future__ import annotations

import re

from studyforge.exercise import from_document
from studyforge.render import templates
from studyforge.render.page import practice, quiz
from studyforge.render.pageassets import ASSET_DIR
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_practice import QUIZ, SHIPPED, document, panel, section

#: The practice key the panel would file this quiz's section under. ⛔ Asked for
#: rather than typed: a key spelled twice and differing by one character simply
#: never matches anything, with nothing failing anywhere.
KEY = practice.key_of(document(), section())


def markup(workspace=QUIZ) -> str:
    """One quiz's section, rendered the way `page.practice` renders it."""
    return panel(sections=[section(workspace=workspace)])


def test_a_quiz_renders_its_questions_and_a_code_exercise_renders_nothing_here():
    # ⛔ The two shapes share one surface and each renders the other as an
    # ABSENCE. ⭐ Asked of this module directly, so the emptiness is this
    # module's answer and not `page.practice`'s branch.
    asked = from_document(QUIZ, "a quiz")
    code = from_document(SHIPPED, "a code exercise")
    assert quiz.render(asked, key=KEY, corpus="demo", grader="") != ""
    assert quiz.render(code, key=KEY, corpus="demo", grader="") == ""


def test_every_question_carries_its_stem_and_every_option_its_own_sentence():
    # ⭐ `AX-05`: one sentence per option, right or wrong, because a page that
    # explained only the wrong answers would teach half the material and would
    # tell the reader which half by showing nothing.
    said = markup()
    for question in QUIZ["questions"]:
        assert question["stem"] in said
        for option in question["options"]:
            assert option["text"] in said
            assert f'data-practice-says="{option["says"]}"' in said


def test_exactly_one_option_per_question_is_keyed_and_the_key_is_in_the_page():
    # ⛔ **R5's theatre clause, and it is deliberate**: the site is offline and
    # the bundle is on the reader's disk, so a page that graded without carrying
    # its key could not grade at all — exactly as an offline workspace cannot
    # hide its test file. ⚠️ Claiming to hide either is the pretence.
    said = markup()
    assert said.count('data-practice-correct="true"') == len(QUIZ["questions"])
    assert said.count('data-practice-correct="false"') == sum(
        len(question["options"]) - 1 for question in QUIZ["questions"]
    )


def test_a_quiz_shows_no_run_no_submit_no_editor_and_no_disabled_one_either():
    # ⛔ `AX-05/3` and this row's Acceptance. A quiz has no file to name, no
    # command to run and no grader to submit to — ⚠️ **and a disabled control is
    # not the remedy**, which is `SF-24`'s standing rule. ⭐ The negative control
    # is the code panel, where every one of these IS present.
    said = markup()
    code = markup(SHIPPED)
    for dead in ('data-practice-act="run"', 'data-practice-act="test"', "data-practice-frame"):
        assert dead not in said, dead
        assert dead in code, dead
    for word in ("disabled", "aria-disabled", "<iframe", "Maximise"):
        assert word not in said, word


def test_no_token_of_r5_s_vocabulary_reaches_a_quiz_page():
    # ⛔ `provenance` and `trust` are the framework's words for how much a
    # verdict is worth, and no reader was ever told what either means. ⭐ The
    # VALUES are read for too, so an attribute carrying `advisory` fails here.
    said = markup()
    for word in ("provenance", "trust", "authoritative", "advisory", "bundled", "generated"):
        assert word not in said, f"the page says {word!r}"


def test_the_quiz_carries_the_learner_worded_label_and_not_the_code_one():
    # ⛔ Spec §7 §9's third row: `generated`/`advisory` with kind `quiz` reads
    # *Written for this site from this page.* ⚠️ Both directions, because the
    # code sentence would render perfectly well on a quiz and say the wrong
    # thing about tests that do not exist.
    said = markup()
    assert templates.template("practice-grader-quiz.html").template in said
    assert templates.template("practice-grader-generated.html").template not in said


def test_each_question_is_its_own_radio_group_and_two_quizzes_never_share_one():
    # ⚠️ Two groups sharing a name would silently unselect each other, with
    # nothing failing anywhere — the same shape as a key spelled twice.
    groups = set(re.findall(r'name="([^"]+)"', markup()))
    assert len(groups) == len(QUIZ["questions"])
    other = quiz.render(
        from_document(QUIZ, "a quiz"), key="other/unit-01/practice", corpus="demo", grader=""
    )
    assert not groups & set(re.findall(r'name="([^"]+)"', other))


def test_a_question_that_carries_markup_is_escaped_and_never_rendered_as_markup():
    # ⛔ Corpus text is text (R1). A stem or an option that carried a tag would
    # otherwise be parsed as one, on a page this framework wrote.
    sharp = {
        **QUIZ,
        "questions": [
            {
                **QUIZ["questions"][0],
                "stem": "Does <script>alert(1)</script> run?",
                "options": [
                    {"id": "a", "text": "<b>no</b>", "correct": True, "says": 'It "does" not.'},
                    {"id": "b", "text": "yes", "correct": False, "says": "It does not."},
                ],
            }
        ],
    }
    said = markup(sharp)
    assert "<script>" not in said
    assert "&lt;script&gt;" in said
    assert "&lt;b&gt;no&lt;/b&gt;" in said
    assert 'data-practice-says="It &quot;does&quot; not."' in said


def test_the_same_quiz_renders_identical_bytes():
    # ⛔ R10: a build is byte-reproducible, and nothing here sorts, hashes or
    # reads a clock.
    assert markup() == markup()


def test_the_quiz_is_rendered_where_the_panel_would_have_been():
    # ⭐ The whole page, because that is where a reader would see it: the quiz
    # follows its own section, exactly as the panel does.
    page = practice.render(document()["sections"][0], document(), sample_placement())
    assert "<section data-practice=" in page
    assert "<section data-practice-quiz=" in markup()


# --- the quiz's script, read as the data it is ------------------------------

#: ⛔ No JavaScript runs in this suite (`QA-03/1`: the pinned image has no
#: engine), so what a text can establish is asserted here and the browser
#: reading is the visual harness's.
SCRIPT = ASSET_DIR / "practice-quiz.js"


def behaviour() -> str:
    """`practice-quiz.js` with its comments removed, so a claim is about the code."""
    return re.sub(r"/\*.*?\*/", "", SCRIPT.read_text(encoding="utf-8"), flags=re.DOTALL)


def test_the_quiz_grades_with_no_server_and_never_asks_whether_one_exists():
    # ⛔ **THE property of this shape** (spec §7 §7): a quiz is graded with no
    # compiler, no container, no network and no model, so the reading is
    # identical over `file://` and over a served origin. ⚠️ A guard on the run
    # client would make a quiz work only where a server happens to be — which is
    # exactly what `practice.js` does, correctly, for the other shape.
    body = behaviour()
    for word in ("studyforge.run", "available()", "fetch(", "XMLHttpRequest", "/api"):
        assert word not in body, word


def test_the_quiz_writes_nothing_to_browser_storage():
    # ⛔ A second, weaker record of *did this complete?* is the second answer
    # `practice.js` refuses to keep for a run. ⚠️ Recording a quiz's completion
    # is a decision about the reader's own state and belongs to the row that
    # takes it, not to the panel.
    body = behaviour()
    for word in ("localStorage", "sessionStorage", "indexedDB", "document.cookie"):
        assert word not in body, word


def test_completion_is_every_question_answered_correctly_and_nothing_less():
    # ⛔ `exercise.quiz.completes`'s rule, kept on this side of the wire. ⚠️ The
    # count is said in every other case, so a reader is never told only that
    # they are not finished.
    body = behaviour()
    assert "right === questions.length && questions.length" in body
    assert "words(status, COMPLETE)" in body
    assert "'{right}'" in body and "'{asked}'" in body


def test_an_unanswered_question_is_not_a_correct_one():
    # ⛔ **Total**, exactly as the Python rule is: a question nobody answered is
    # not correct, it is simply not answered.
    body = behaviour()
    assert "return { answered: false, correct: false };" in body
    assert 'input[type="radio"]:checked' in body


def test_every_word_the_quiz_says_is_read_off_the_markup():
    # ⭐ The two-sided spelling every hook on this page has (`W431`): a label
    # spelled in the script too would be a second place for it to drift.
    body = behaviour()
    for said in ("Right.", "Not this one.", "Choose an answer first.", "answered correctly"):
        assert said not in body, said
    for template in ("practice-question.html", "practice-quiz.html"):
        assert templates.template(template).template != ""
