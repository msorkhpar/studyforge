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
from studyforge.render.markup import escape_attribute, inline
from studyforge.render.page import practice, quiz
from studyforge.render.pageassets import ASSET_DIR
from tests.studyforge.render.page.pages import sample_placement
from tests.studyforge.render.page.test_practice import QUIZ, SHIPPED, document, panel, section
from tests.studyforge.serve.routes.quizzing import (
    KEY_ATTRIBUTE,
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


#: ⭐ The opt-out: a plain quiz is drawn one question at a time unless its record says `page`, and
#: this module is about the all-on-one-page layout.
QUIZ_PAGE = {**QUIZ, "layout": "page"}


def markup(workspace=QUIZ_PAGE) -> str:
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


def key_block(said: str) -> dict:
    """The quiz's one key block, read back as the JSON it is."""
    found = re.findall(
        r'<script type="application/json" data-practice-part="key">(.*?)</script>', said, re.S
    )
    assert len(found) == 1, f"{len(found)} key blocks in one quiz"
    return json.loads(found[0])


def test_the_quiz_carries_its_own_key_in_one_data_block_and_no_option_carries_it():
    # ⭐ The key lives in the page it grades, in a script
    # local to it. ⛔ Only in that block: an option carries its id and words,
    # and neither its correctness nor its sentence — or a stylesheet or a screen
    # reader could say it before the reader chose.
    said = markup()
    assert key_block(said) == {
        question["id"]: {
            "key": next(o["id"] for o in question["options"] if o["correct"]),
            "says": {o["id"]: inline(o["says"]) for o in question["options"]},
        }
        for question in QUIZ["questions"]
    }
    outside = re.sub(r"<script type=\"application/json\".*?</script>", "", said, flags=re.S)
    for question in QUIZ["questions"]:
        for option in question["options"]:
            assert option["says"] not in outside, option["says"]
    assert "data-practice-correct" not in said and "data-practice-says" not in said


def test_a_sentence_can_never_close_the_key_block():
    # ⛔ The key block is JSON inside an HTML element: a sentence carrying
    # `</script>` would end the element and open whatever followed. ⭐ Written
    # as `\u` escapes, and read back as itself.
    hostile = "It ends </script><script>alert(1)</script> & starts <b>"
    record = json.loads(json.dumps(QUIZ_PAGE))
    record["questions"][0]["options"][0]["says"] = hostile
    said = markup(record)
    block = said[said.index('data-practice-part="key">') :]
    block = block[: block.index("</script>")]
    assert "<" not in block.split(">", 1)[1] and "&" not in block
    first = record["questions"][0]
    # ⭐ Read back, it is the sentence as the prose renderer makes it: escaped.
    assert key_block(said)[first["id"]]["says"][first["options"][0]["id"]] == inline(hostile)
    assert "<script>" not in inline(hostile)


def test_the_key_of_one_quiz_is_in_its_own_page_and_no_other_file_the_build_wrote(tmp_path):
    # ⛔ The key lives ONLY in the page it grades —
    # never in a shared asset, never in another page. Read on the BUILT prose
    # fixture, every file the build wrote. ⭐ Positive control in the same test:
    # every sentence IS in the quiz's own page, so an absence elsewhere is a
    # reading and not a needle nobody could find.
    root = quiz_corpus(tmp_path)
    texts = built_texts(root)
    page = page_of(root).relative_to(root).as_posix()
    assert "data-practice-quiz" in texts[page], "the quiz is not on the built page at all"
    for sentence in sentences():
        holders = sorted(
            path
            for path, text in texts.items()
            if sentence in text
            or escape_attribute(sentence) in text
            or json.dumps(sentence)[1:-1] in text
        )
        assert holders == [page], f"{sentence!r} is in {holders}"
    keyed = [path for path, text in texts.items() if KEY_ATTRIBUTE.search(text)]
    assert keyed == [], f"a key is spelled as an attribute in {keyed}"


def test_with_no_script_the_quiz_says_so_and_offers_no_check():
    # ⭐ A quiz is graded by the page's script, over `file://` and served alike.
    # With no script, the `offline` sentence ships showing and the controls ship
    # `hidden`; the script swaps them. ⛔ It names no server: none is needed.
    said = markup()
    assert '<p data-practice-part="controls" hidden>' in said
    offline = re.search(r'<p data-practice-part="offline">([^<]*)</p>', said)
    assert offline is not None, "the quiz does not say what it needs"
    assert "script" in offline.group(1)
    assert "server" not in offline.group(1)


def test_a_quiz_shows_no_run_no_submit_no_editor_and_no_disabled_one_either():
    # ⛔ A quiz has no file to name, no
    # command to run and no grader to submit to — ⚠️ **and a disabled control is
    # not the remedy**: the page never shows a control it cannot honour. ⭐ The negative control
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

#: ⛔ No JavaScript runs in this suite (the pinned image has no
#: engine), so what a text can establish is asserted here and the browser
#: reading is the visual harness's.
SCRIPT = ASSET_DIR / "practice-quiz.js"


def behaviour() -> str:
    """`practice-quiz.js` with its comments removed, so a claim is about the code."""
    return re.sub(r"/\*.*?\*/", "", SCRIPT.read_text(encoding="utf-8"), flags=re.DOTALL)


def test_the_quiz_is_graded_in_the_page_from_its_own_key_with_no_request():
    # ⭐ Nothing about a quiz is a server function. ⛔ So the
    # script asks no client and no origin, and makes no request of any kind.
    body = behaviour()
    assert "JSON.parse(block.textContent)" in body
    assert "part(quiz, 'key')" in body
    for word in ("studyforge.run", "studyforge.quiz", "fetch(", "XMLHttpRequest", "sendBeacon",
                 "/api", "available()"):  # fmt: skip
        assert word not in body, word


def test_a_passed_quiz_is_kept_in_the_readers_store_and_nothing_else_is():
    # ⭐ Clause 3: a quiz card keeps *passed* across a reload, held in the
    # browser — through the store's one writer, never by this file itself.
    body = behaviour()
    assert (
        "if (complete && store) { store.passQuiz(quiz.getAttribute('data-practice-quiz')); }"
        in body
    )
    for word in ("localStorage", "sessionStorage", "indexedDB", "document.cookie"):
        assert word not in body, word


def test_complete_is_every_question_answered_right_and_nothing_less():
    # ⛔ The rule `exercise.quiz.completes` states: no pass mark, no partial
    # credit. ⚠️ The count is said in every other case.
    body = behaviour()
    assert "var complete = questions.length > 0 && right === questions.length;" in body
    assert "var right = answer === entry.key;" in body
    assert "'{right}'" in body and "'{asked}'" in body


def test_an_unanswered_question_shows_nothing_and_the_chosen_options_sentence_shows():
    body = behaviour()
    assert "if (answer === undefined || !hasSaid) {" in body
    assert "entry.says[answer]" in body
    assert 'input[type="radio"]:checked' in body


def test_every_word_the_quiz_says_is_read_off_the_markup():
    # ⭐ The two-sided spelling every hook on this page has: a label
    # spelled in the script too would be a second place for it to drift.
    body = behaviour()
    for said in (
        "Right.",
        "Not this one.",
        "Choose an answer first.",
        "answered correctly",
        "not running",
    ):
        assert said not in body, said
    for template in ("practice-question.html", "practice-quiz.html"):
        assert templates.template(template).template != ""


def test_inline_code_in_a_stem_an_option_and_a_sentence_renders_as_code():
    # ⛔ The Java pilot's quiz showed "`switch`" with its backticks. ⭐ A stem, an
    # option and a sentence go through the prose's own inline renderer.
    record = json.loads(json.dumps(QUIZ_PAGE))
    first = record["questions"][0]
    first["stem"] = "Which types may a `switch` take?"
    first["options"][0]["text"] = "an `int` and its wrapper"
    first["options"][0]["says"] = "A `switch` takes `int`, never `long`."
    said = markup(record)
    assert "Which types may a <code>switch</code> take?" in said
    assert "an <code>int</code> and its wrapper" in said
    assert "`" not in said.split('data-practice-part="key">')[0]
    says = key_block(said)[first["id"]]["says"][first["options"][0]["id"]]
    assert says == "A <code>switch</code> takes <code>int</code>, never <code>long</code>."
