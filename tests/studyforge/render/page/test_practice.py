"""Mirror of `src/studyforge/render/page/practice.py` (R12).

⛔ **Every clause is asserted BOTH WAYS**, because every one of them is a
silence when it fails: a panel that is absent where it should be and a panel
that is present where it should not be both render, carry every word, and pass
`validate`.
"""

from __future__ import annotations

import re

import pytest

from studyforge.progress import practice_key
from studyforge.render import templates
from studyforge.render.page import anchors, practice, render
from studyforge.render.page.errors import PageError
from studyforge.render.pageassets import ASSET_DIR
from studyforge.unit.errors import ContentError
from studyforge.unit.trust import PROVENANCE, TRUST, check_test_record
from tests.studyforge.render.page.pages import depth2_unit_01, sample_placement
from tests.support import repository_root


def _legal_pairs() -> set[tuple[str, str]]:
    """Every `(provenance, trust)` pair R5 admits, asked of `unit.trust` itself."""
    legal = set()
    for provenance in PROVENANCE:
        for trust in TRUST:
            try:
                legal.add(check_test_record(provenance, trust))
            except ContentError:
                continue
    return legal


LEGAL_PAIRS = _legal_pairs()


def spec_label_rows() -> dict[str, str]:
    """The spec's §7 §9 table: `{record cell: the bold sentence}`, one per row."""
    spec = next((repository_root() / "docs" / "specs").glob("*-design.md"))
    text = spec.read_text(encoding="utf-8")
    start = text.index("| the record says | the page says |")
    rows = {}
    for line in text[start:].splitlines()[2:]:
        if not line.startswith("|"):
            break
        record, says = (cell.strip() for cell in line.strip("|").split("|"))
        rows[record] = re.fullmatch(r"\*\*(.+)\*\*", says).group(1)
    return rows


#: A graded record: a file, how it runs, and the material's own grader.
SHIPPED = {
    "main_path": "practice/one/src/Greeter.java",
    "test_path": "practice/one/src/GreeterTest.java",
    "run_command": ["mvn", "-q", "compile"],
    "test_command": ["mvn", "-q", "test"],
    "provenance": "bundled",
    "trust": "authoritative",
}

#: The same shape with a grader this project generated (R5). ⛔ `generated` may
#: never be `authoritative`, which `unit.trust` refuses — so this is what an
#: advisory grader looks like on disk.
GENERATED = {**SHIPPED, "provenance": "generated", "trust": "advisory"}

#: A grader that shipped with the material and was never derived through the
#: two gates: it claims no authority, and it was not written for this site.
BUNDLED = {**SHIPPED, "trust": "advisory"}

#: A grader somebody wrote by hand for this practice: neither the material's
#: nor one this site authored and proved, so it gets neither sentence.
USER = {**SHIPPED, "provenance": "user", "trust": "advisory"}

#: A quiz: questions in place of a workspace. ⛔ Every workspace key is
#: refused on it, which is why it carries none of them.
QUIZ = {
    "kind": "quiz",
    "questions": [
        {
            "id": "q-1",
            "stem": "What does a class declaration open?",
            "options": [
                {"id": "a", "text": "A type", "correct": True, "says": "The page says so."},
                {"id": "b", "text": "A file", "correct": False, "says": "A file holds one."},
            ],
            "origin": {"path": "basics/01.md", "section": "What a class is"},
        }
    ],
}

#: The other shape: a file nothing checks. ⛔ The grader half is written
#: whole or not at all, so an ungraded record is exactly these two keys.
UNGRADED = {"main_path": "kata/greet.py", "run_command": ["python3", "kata/greet.py"]}


def document(**over):
    """A served unit document with one practice section, overridable."""
    base = {
        "address": ["basics"],
        "unit": 3,
        "variant": "java",
        "title": "A unit",
        "sections": [section()],
    }
    return {**base, **over}


def section(*, workspace=SHIPPED, kind="practice", key="practice-java"):
    """One served section, as `unit.builder.parts.section` writes it."""
    return {
        "key": key,
        "kind": kind,
        "heading": "Practice",
        "blocks": [{"type": "para", "text": "Do the thing."}],
        "video": None,
        "workspace": workspace,
        "attachments": [],
    }


def panel(**over):
    """The panel for one section of the default document."""
    unit = document(**over)
    return practice.render(unit["sections"][0], unit, sample_placement())


def test_a_graded_practice_gets_a_panel_and_a_lesson_gets_none():
    # ⛔ The two directions of the same question. A lesson with a workspace is
    # not a thing the archive can produce — `exercise.of` refuses an `exercise`
    # on a lesson — but the renderer is not the place that argument is made, so
    # it asks the section's own kind.
    assert "<section data-practice=" in panel()
    assert practice.render(section(kind="lesson"), document(), sample_placement()) == ""


def test_a_practice_with_no_workspace_shows_no_control_at_all():
    # ⛔ The row's own rule: a dead button is a promise the page cannot keep, so
    # a reading-only unit gets no affordance rather than a disabled one.
    empty = panel(sections=[section(workspace=None)])
    assert empty == ""
    assert "data-practice-act" not in empty
    # ⭐ The negative control, run negatively: the same section WITH a workspace
    # does carry the controls, so the emptiness above is the workspace and not
    # the harness.
    assert "data-practice-act" in panel()


def test_a_unit_whose_every_section_is_a_lesson_renders_no_panel_anywhere():
    # ⭐ Read at the whole page rather than at the region, because that is where
    # a reader would see it: the reading floor is a complete product (C5).
    page = render(document(sections=[section(kind="lesson", workspace=None)]), sample_placement())
    assert b"data-practice" not in page
    assert b"data-practice" in render(document(), sample_placement())


def test_submit_is_offered_only_where_the_workspace_names_a_test():
    # ⛔ A record may carry `main_path` and `run_command` alone, and
    # `serve.routes.run` answers `409` for the mode it does not name.
    graded = panel()
    assert 'data-practice-act="run"' in graded
    assert 'data-practice-act="test"' in graded
    ungraded = panel(sections=[section(workspace=UNGRADED)])
    assert 'data-practice-act="run"' in ungraded
    assert 'data-practice-act="test"' not in ungraded


def test_the_material_s_own_grader_and_a_generated_one_read_differently():
    # ⛔ R5, at the only place a reader can see it. The two sentences must not
    # be the same sentence, or the label is decoration.
    shipped = panel()
    generated = panel(sections=[section(workspace=GENERATED)])
    assert templates.template("practice-grader-shipped.html").template in shipped
    assert templates.template("practice-grader-generated.html").template in generated
    assert shipped != generated


#: Every record the page can be handed, by the label it is owed.
EVERY_LABEL = (
    ("shipped", SHIPPED),
    ("bundled", BUNDLED),
    ("user", USER),
    ("generated", GENERATED),
    ("quiz", QUIZ),
    ("none", UNGRADED),
)


def test_each_label_case_renders_its_own_stated_sentence():
    # ⛔ Spec §7 §9 read as the table it is: one record per row, one sentence
    # per record, and every one of them different from every other. ⭐ The
    # ungraded case says *nothing here checks your answer* rather than saying
    # nothing — a label is never omitted because it is unflattering.
    said = {}
    for name, workspace in EVERY_LABEL:
        markup = panel(sections=[section(workspace=workspace)])
        wanted = templates.template(f"practice-grader-{name}.html").template
        assert wanted in markup, name
        said[name] = wanted
    assert set(said) == set(practice.GRADER_TEMPLATES)
    assert len(set(said.values())) == len(said), "two labels are the same sentence"
    assert 'data-practice-part="grader"' in panel(sections=[section(workspace=UNGRADED)])


def test_a_grader_written_by_hand_is_not_told_it_was_proven():
    # ⛔ The generated sentence says its tests were proven against a worked
    # solution. Nothing proves a grader somebody wrote by hand, so it must not
    # borrow that sentence, nor the material's own.
    markup = panel(sections=[section(workspace=USER)])
    assert templates.template("practice-grader-user.html").template in markup
    for other in ("generated", "shipped", "bundled"):
        assert templates.template(f"practice-grader-{other}.html").template not in markup
    assert "proven against" not in markup


@pytest.mark.parametrize("pair", sorted(LEGAL_PAIRS), ids="-".join)
def test_every_legal_record_renders_a_label_the_spec_table_states(pair):
    # ⭐ Every combination `unit.trust` admits, for a code practice, renders one
    # of the page's sentences, and the spec's §7 §9 table has a row for that
    # combination saying exactly that sentence.
    provenance, trust = pair
    workspace = {**SHIPPED, "provenance": provenance, "trust": trust}
    exercise = practice._exercise(workspace)
    sentence = templates.template(practice.GRADER_TEMPLATES[practice.label_of(exercise)]).template
    rows = spec_label_rows()
    cells = [f"`{provenance}` · `{trust}`", f"`{provenance}` · `{trust}`, kind `code`"]
    found = [rows[cell] for cell in cells if cell in rows]
    assert len(found) == 1, pair
    assert found[0] in sentence, pair


def test_the_spec_table_states_every_sentence_the_page_renders():
    # ⭐ The other direction: no template says a sentence the table does not.
    stated = set(spec_label_rows().values())
    for name in practice.GRADER_TEMPLATES:
        body = templates.template(f"practice-grader-{name}.html").template
        assert any(sentence in body for sentence in stated), name


@pytest.mark.parametrize("workspace", [SHIPPED, BUNDLED, USER, GENERATED, UNGRADED])
def test_neither_r5_key_ever_reaches_the_page(workspace):
    # ⛔ `provenance` and `trust` are the framework's vocabulary for how much a
    # verdict is worth, and no reader is told what either word means. ⭐ Both
    # the keys and their VALUES are read for, so an attribute carrying
    # `advisory` fails here too.
    markup = panel(sections=[section(workspace=workspace)])
    for word in ("provenance", "trust", "authoritative", "advisory", "bundled", "generated"):
        assert word not in markup, f"the page says {word!r}"


def test_the_practice_key_is_the_one_progress_would_mint():
    # ⛔ Asked for, never composed: the string the run route parses
    # back and the store records under. Compared against `progress`'s own
    # composer rather than against a literal, so a change there is a red test
    # here rather than a key that matches nothing.
    from studyforge.address import Address

    wanted = practice_key(Address(("basics",)), 3, "practice-java")
    assert f'data-practice="{wanted}"' in panel()


def test_a_key_the_document_cannot_mint_is_refused_rather_than_invented():
    # ⚠️ A section key that is not a slug would otherwise become a key nothing
    # else will ever produce, with nothing failing anywhere.
    with pytest.raises(PageError):
        panel(sections=[section(key="not a slug")])
    with pytest.raises(PageError):
        panel(unit=0)
    # ⭐ The negative control: the same call with a usable ordinal and key works.
    assert panel(unit=1)


def test_a_workspace_the_record_refuses_is_a_page_error_and_not_a_half_panel():
    # ⛔ A grader written in part is refused by `exercise`, and a renderer that
    # swallowed that would draw a Submit with no command behind it.
    half = {key: value for key, value in SHIPPED.items() if key != "test_command"}
    with pytest.raises(PageError):
        panel(sections=[section(workspace=half)])


def test_the_panel_names_no_api_no_origin_and_no_client_file():
    # ⛔ R8's floor, at the renderer rather than over a built site, so the
    # failure is named here first. The client is added by the SERVING
    # process and a built page must name none of it.
    markup = panel()
    assert "/api" not in markup
    assert "client.js" not in markup
    assert "127.0.0.1" not in markup and "localhost" not in markup


def test_every_control_is_a_real_button_and_the_output_is_reachable_by_keyboard():
    # ⛔ Keyboard accessibility is part of the panel, not a follow-up. A
    # styled `div` is not in the tab order, takes no Enter or Space and is
    # announced as nothing; a scrolling region with no `tabindex` cannot be
    # scrolled without a mouse.
    markup = panel()
    acts = re.findall(r"<(\w+)[^>]*data-practice-act=", markup)
    tabs = re.findall(r"<(\w+)[^>]*data-practice-tab=", markup)
    assert acts and set(acts) == {"button"}
    # ⭐ The two window tabs are controls too, and they are held to the
    # same rule rather than exempted from it — a tab that was a styled `div`
    # would be announced as nothing in a `role="tablist"` that promises tabs.
    assert tabs and set(tabs) == {"button"}
    # ⛔ **Counted over every `<button>` the panel emits**, so a control that is
    # neither an act nor a tab is held to the rule too.
    buttons = re.findall(r"<button\b[^>]*>", markup)
    assert len(buttons) == len(acts) + len(tabs)
    assert markup.count('type="button"') == len(buttons)
    assert re.search(r'<pre[^>]*data-practice-part="output"[^>]*tabindex="0"', markup)
    assert 'role="status"' in markup and 'aria-live="polite"' in markup


def test_the_controls_and_the_editor_ship_hidden_and_the_offline_note_does_not():
    # ⛔ The `file://` floor is the BASELINE, not a fallback: with no origin
    # there is nothing to run, so the page shows the sentence saying so and no
    # control at all. ⭐ `practice.js` swaps them once the client answers.
    markup = panel()
    assert re.search(r'<p data-practice-part="controls" hidden', markup)
    assert re.search(r'<div data-practice-part="editor" hidden', markup)
    assert re.search(r'<p data-practice-part="offline">', markup)


def test_the_two_tabs_ship_hidden_and_name_the_two_windows():
    # ⭐ The reader's own file and the test that judges it, as two tabs
    # over two windows of ONE editor — never a split pane, which halves the
    # width of both. ⛔ Hidden in the built page: there is no editor to show
    # until a served origin says there is one.
    markup = panel()
    assert re.search(r'<div data-practice-part="tabs" role="tablist"[^>]*hidden', markup)
    assert re.search(r'<button[^>]*data-practice-tab="main"[^>]*aria-selected="true"', markup)
    assert re.search(r'<button[^>]*data-practice-tab="test"[^>]*aria-selected="false"', markup)
    # ⛔ ONE frame slot: the two windows take turns in one frame, so a page
    # never holds more than one editor.
    assert markup.count("data-practice-frame=") == 1
    assert re.search(r'<div data-practice-frame="main" hidden></div>', markup)


def test_the_tests_tab_is_emitted_only_where_the_record_names_a_test():
    # ⛔ Both directions, because each is a silence: a tab over a test that does
    # not exist opens an empty buffer, and a missing tab hides the statement of
    # what *done* means. ⚠️ The FRAME slot stays either way — it is the panel's
    # markup, and `practice.js` shows it only for a window it was given.
    assert 'data-practice-tab="test"' in panel()
    assert 'data-practice-tab="test"' not in panel(sections=[section(workspace=UNGRADED)])
    assert 'data-practice-tab="main"' in panel(sections=[section(workspace=UNGRADED)])


def test_a_quiz_shows_its_questions_and_no_run_affordance_at_all():
    # ⛔ A quiz carries QUESTIONS in place of
    # a workspace: no file to name, nothing to open in an editor, no command to
    # Run and no grader to Submit to — ⚠️ **and not disabled ones**, which is
    # this module's standing rule about a dead button. ⭐ Asserted both ways
    # against the very same section, so it cannot pass by rendering nothing for
    # everything.
    quiz = panel(sections=[section(workspace=QUIZ)])
    code = panel(sections=[section(workspace=SHIPPED)])
    assert "data-practice-question=" in quiz
    for dead in ("data-practice-act", "data-practice-frame", "data-practice-tab", "<iframe"):
        assert dead not in quiz, dead
        assert dead in code or dead == "<iframe", dead
    # ⛔ And the panel's own attribute is NOT on it: a quiz is its own section,
    # so nothing keyed on `data-practice` — the run, the output —
    # can reach it by accident.
    assert "<section data-practice=" not in quiz
    assert "<section data-practice=" in code


def test_the_editor_slot_says_it_is_not_running_and_how_to_start_it():
    # ⛔ The honesty requirement: an IDE with a shell is not started because
    # somebody opened a reading page, and a panel that rendered blank would look
    # broken instead of saying so.
    note = panel().split('data-practice-part="no-editor"')[1]
    assert "not running" in note
    # ⭐ How to start it is the corpus's own command, never a README.
    assert 'the one command under "Bring it up" in this corpus\'s EXECUTION.md' in note
    assert "README" not in note.split("</p>")[0]


# --- the panel's script, read as the data it is --------------------

#: ⛔ No JavaScript runs in this suite (the pinned image has no engine),
#: so what a text can establish about the panel's script is asserted here
#: and the browser reading is the visual harness's.
SCRIPT = ASSET_DIR / "practice.js"


def behaviour() -> str:
    """`practice.js` with its comments removed, so a claim is about the code."""
    return re.sub(r"/\*.*?\*/", "", SCRIPT.read_text(encoding="utf-8"), flags=re.DOTALL)


def test_the_panel_never_claims_or_enforces_read_only():
    # ⛔ Read-only is the EDITOR's, out of the workspace settings the server
    # writes. A guard here would be a second, weaker copy of a rule the editor
    # already keeps — and a *claim* here would be a promise this file cannot
    # keep, since nothing in the page can stop a keystroke in an iframe.
    body = behaviour()
    for word in ("readonly", "readOnly", "read-only"):
        assert word not in body, word


def test_the_panel_starts_no_editor_and_names_no_container():
    # ⛔ An IDE with a shell is not started because somebody opened a reading
    # page (§8.3, and this panel's own honesty rule).
    body = behaviour()
    for word in ("docker", "fetch(", "XMLHttpRequest", "studyforge-", "compose"):
        assert word not in body, word


def test_the_panel_follows_the_section_it_belongs_to():
    # ⚠️ A unit may carry several practices: a panel that did not follow its own
    # statement would leave a reader with two statements and then two sets of
    # controls, with nothing saying which is which.
    page = render(
        document(sections=[section(key="practice-a"), section(key="practice-b")]),
        sample_placement(),
    ).decode("utf-8")
    order = re.findall(r'data-(?:section|practice)="(practice-[ab]|[^"]*practice-[ab])"', page)
    assert [name.rsplit("/", 1)[-1] for name in order] == [
        "practice-a",
        "practice-a",
        "practice-b",
        "practice-b",
    ]


def test_the_panel_is_outside_the_section_so_it_is_not_in_the_outline():
    # ⭐ The shape the narrated deck already has: the statement is the material
    # and belongs to the material; the controls are this framework's. ⛔ And the
    # consequence a reader sees: the panel is not a place the outline sends them.
    unit = document()
    page = render(unit, sample_placement()).decode("utf-8")
    assert "</section>\n<section data-practice=" in page
    opened = page.index('<section id="')
    assert page.index("</section>\n<section data-practice=") > opened
    assert "data-practice=" not in page[opened : page.index("</section>", opened)]
    # ⭐ Read on the fixture, whose material carries headings, because an outline
    # over a document with none is empty and would assert nothing.
    outline = anchors.outline(depth2_unit_01().document)
    assert outline
    assert "data-practice=" not in outline
    assert "Problem statement" not in outline


def test_the_same_document_renders_identical_bytes(tmp_path):
    # ⛔ R10, through the region that was just added: no clock, no set iteration,
    # no directory enumeration.
    del tmp_path
    assert render(document(), sample_placement()) == render(document(), sample_placement())


def test_a_real_fixture_unit_carries_the_panel_its_archive_declares():
    # ⭐ Read against a fixture a build produced rather than a hand-made dict, so
    # the record shape this renderer reads is the one `unit.builder` writes.
    case = depth2_unit_01()
    page = case.render().decode("utf-8")
    assert "<section data-practice=" in page
    assert 'data-corpus="depth2-demo"' in page
