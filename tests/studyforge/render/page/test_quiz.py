"""Mirror of `src/studyforge/render/page/quiz.py` (R12).

⛔ **Every clause is asserted BOTH WAYS.** A question that is absent where it
should be and a control that is present where it must not be both render, carry
every word and pass `validate` — which is the same silence `test_practice.py`
opens by naming, on the other half of this surface.
"""

from __future__ import annotations

import json
import re

from studyforge.exercise import from_document
from studyforge.render import templates
from studyforge.render.markup import escape_attribute
from studyforge.render.page import practice, quiz
from studyforge.render.pageassets import ASSET_DIR
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_practice import QUIZ, SHIPPED, document, panel, section
from tests.studyforge.serve.routes.quizzing import (
    KEY_ATTRIBUTE,
    PRACTICE_DOCUMENT,
    built_texts,
    page_of,
    quiz_corpus,
    sentences,
)

#: The key as a JSON island would spell it.
JSON_KEY = re.compile(r'"correct"\s*:')

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


def test_every_question_carries_its_stem_and_every_option_its_words():
    # ⭐ The reader can read and choose every option, over `file://` too.
    said = markup()
    for question in QUIZ["questions"]:
        assert question["stem"] in said
        for option in question["options"]:
            assert option["text"] in said
            assert f'data-practice-option="{option["id"]}"' in said


def test_no_option_carries_the_key_or_its_sentence():
    # ⛔ `W451`, the user's ruling of 2026-09-23: the correct answer resides on
    # the SERVER. ⭐ Every sentence and every spelling of the key is read for,
    # escaped and raw, because either one on the page tells a reader which
    # option is right before they choose. ⚠️ The positive control — the same
    # needles FOUND in the record this page was rendered from — is what makes
    # an absence here a reading rather than a typo in the needle.
    said = markup()
    record = json.dumps(QUIZ)
    for question in QUIZ["questions"]:
        for option in question["options"]:
            assert option["says"] in record
            assert option["says"] not in said, option["says"]
            assert escape_attribute(option["says"]) not in said, option["says"]
    for spelling in ("correct", "data-practice-says"):
        assert spelling not in said.replace("answered correctly", ""), spelling


def test_no_built_page_or_asset_carries_a_key_or_a_sentence(tmp_path):
    # ⛔ `W451`'s first clause, read on the BUILT prose fixture — every page and
    # every asset the build wrote, because a key that leaked into a script, a
    # stylesheet or a JSON island is missed by a reading of one page's markup.
    # ⭐ Positive control, in the same test: every needle IS in the practice
    # document on disk, which is where the server reads it — so an absence below
    # is a reading and not a needle nobody could find.
    root = quiz_corpus(tmp_path)
    texts = built_texts(root)
    page = page_of(root).relative_to(root).as_posix()
    assert "data-practice-quiz" in texts[page], "the quiz is not on the built page at all"
    record = (root / PRACTICE_DOCUMENT).read_text(encoding="utf-8")
    assert '"correct": true' in record
    for sentence in sentences():
        assert sentence in record, sentence
        leaked = [
            path
            for path, text in texts.items()
            if sentence in text or escape_attribute(sentence) in text
        ]
        assert leaked == [], f"{sentence!r} is in {leaked}"
    # ⚠️ `"correct":` and never `"correct"`: the stylesheet's own
    # `[data-practice-verdict="correct"]` is the SERVER's verdict drawn, not a key.
    keyed = [
        path for path, text in texts.items() if KEY_ATTRIBUTE.search(text) or JSON_KEY.search(text)
    ]
    assert keyed == [], f"a key is spelled in {keyed}"


def test_over_a_file_the_quiz_says_it_needs_the_study_server_and_offers_no_check():
    # ⭐ `W451`'s register default: the mechanism Run and Submit use — the
    # `offline` sentence ships showing and the controls ship `hidden`, and only
    # a served client unhides them. ⛔ The wording is the panel's own, so a
    # reader is told the same thing about both shapes.
    said = markup()
    assert '<p data-practice-part="controls" hidden>' in said
    offline = re.search(r'<p data-practice-part="offline">([^<]*)</p>', said)
    assert offline is not None, "the quiz does not say what a file page cannot do"
    panel_words = templates.template("practice-panel.html").template
    for shared in ("need", "the local study server. This page was opened as a file"):
        assert shared in offline.group(1) and shared in panel_words, shared


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


def test_the_quiz_is_graded_by_the_served_client_and_never_by_the_page():
    # ⛔ `W451` (spec §7 §7, amended 2026-09-23): the page holds no key, so it
    # cannot grade — it asks `window.studyforge.quiz`, which only a SERVING
    # process adds to a page, and only where that client says an origin can
    # answer. ⚠️ It names no API and fetches nothing itself: R8's floor reads a
    # built page that names the API as a defect, and the client is the one file
    # that may.
    body = behaviour()
    assert "window.studyforge.quiz" in body
    assert "client.available()" in body
    assert "client.grade(" in body
    for word in ("studyforge.run", "fetch(", "XMLHttpRequest", "/api", "-correct", "-says"):
        assert word not in body, word


def test_the_quiz_writes_nothing_to_browser_storage():
    # ⛔ A second, weaker record of *did this complete?* is the second answer
    # `practice.js` refuses to keep for a run. ⚠️ Recording a quiz's completion
    # is a decision about the reader's own state and belongs to the row that
    # takes it, not to the panel.
    body = behaviour()
    for word in ("localStorage", "sessionStorage", "indexedDB", "document.cookie"):
        assert word not in body, word


def test_completion_is_the_servers_word_and_the_page_never_re_derives_it():
    # ⛔ `exercise.quiz.completes` is applied ONCE, in Python, by the route; the
    # page shows `complete` and never adds verdicts up itself — a second
    # spelling of the rule in a file that cannot import the first. ⚠️ The count
    # is said in every other case, so a reader is never told only that they are
    # not finished.
    body = behaviour()
    assert "verdict.complete === true" in body
    assert "words(status, COMPLETE)" in body
    assert "'{right}'" in body and "'{asked}'" in body
    assert "questions.length" not in body


def test_an_unanswered_question_shows_nothing_and_only_the_latest_answer_draws():
    # ⛔ A question the verdict says nobody answered shows no sentence; and a
    # verdict for answers the reader has since changed never lands on the page.
    body = behaviour()
    assert "!row || !row.answered" in body
    assert 'input[type="radio"]:checked' in body
    assert "ticket === asked" in body


def test_every_word_the_quiz_says_is_read_off_the_markup():
    # ⭐ The two-sided spelling every hook on this page has (`W431`): a label
    # spelled in the script too would be a second place for it to drift.
    body = behaviour()
    for said in (
        "Right.",
        "Not this one.",
        "Choose an answer first.",
        "answered correctly",
        "Checking",
        "did not check",
        "study server",
    ):
        assert said not in body, said
    for template in ("practice-question.html", "practice-quiz.html"):
        assert templates.template(template).template != ""
