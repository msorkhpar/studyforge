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
from tests.studyforge.render.page.pages import depth2_unit_01, sample_placement

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

#: `AX-05`'s shape: questions in place of a workspace. ⛔ Every workspace key is
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

#: `W357`'s other shape: a file nothing checks. ⛔ The grader half is written
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
    # ⛔ `W357`: a record may carry `main_path` and `run_command` alone, and
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


def test_an_ungraded_practice_claims_nothing_about_a_grader():
    # ⚠️ Not a third sentence: the page offers no Submit, which says it without
    # a claim about a grader that does not exist.
    assert 'data-practice-part="grader"' not in panel(sections=[section(workspace=UNGRADED)])
    assert 'data-practice-part="grader"' in panel()


@pytest.mark.parametrize("workspace", [SHIPPED, GENERATED, UNGRADED])
def test_neither_r5_key_ever_reaches_the_page(workspace):
    # ⛔ The register's note, asserted: `provenance` and `trust` are the
    # framework's vocabulary for how much a verdict is worth, and no reader was
    # told what either word means. ⭐ Both the keys and their VALUES are read
    # for, so an attribute carrying `advisory` fails here too.
    markup = panel(sections=[section(workspace=workspace)])
    for word in ("provenance", "trust", "authoritative", "advisory", "bundled", "generated"):
        assert word not in markup, f"the page says {word!r}"


def test_the_practice_key_is_the_one_progress_would_mint():
    # ⛔ Asked for, never composed (`SF-21/4`): the string the run route parses
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
    # failure is named here first (`W370`). The client is added by the SERVING
    # process and a built page must name none of it.
    markup = panel()
    assert "/api" not in markup
    assert "client.js" not in markup
    assert "127.0.0.1" not in markup and "localhost" not in markup


def test_every_control_is_a_real_button_and_the_output_is_reachable_by_keyboard():
    # ⛔ Keyboard accessibility is in this row's acceptance, not a follow-up. A
    # styled `div` is not in the tab order, takes no Enter or Space and is
    # announced as nothing; a scrolling region with no `tabindex` cannot be
    # scrolled without a mouse.
    markup = panel()
    acts = re.findall(r"<(\w+)[^>]*data-practice-act=", markup)
    tabs = re.findall(r"<(\w+)[^>]*data-practice-tab=", markup)
    assert acts and set(acts) == {"button"}
    # ⭐ `W429`: the two window tabs are controls too, and they are held to the
    # same rule rather than exempted from it — a tab that was a styled `div`
    # would be announced as nothing in a `role="tablist"` that promises tabs.
    assert tabs and set(tabs) == {"button"}
    assert markup.count('type="button"') == len(acts) + len(tabs)
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
    # ⭐ `W429`: the reader's own file and the test that judges it, as two tabs
    # over two frames of ONE editor — never a split pane, which halves the
    # width of both. ⛔ Hidden in the built page: there is no editor to show
    # until a served origin says there is one.
    markup = panel()
    assert re.search(r'<div data-practice-part="tabs" role="tablist"[^>]*hidden', markup)
    assert re.search(r'<button[^>]*data-practice-tab="main"[^>]*aria-selected="true"', markup)
    assert re.search(r'<button[^>]*data-practice-tab="test"[^>]*aria-selected="false"', markup)
    assert re.search(r'<div data-practice-frame="main" hidden></div>', markup)
    assert re.search(r'<div data-practice-frame="test" hidden></div>', markup)


def test_the_tests_tab_is_emitted_only_where_the_record_names_a_test():
    # ⛔ Both directions, because each is a silence: a tab over a test that does
    # not exist opens an empty buffer, and a missing tab hides the statement of
    # what *done* means. ⚠️ The FRAME slot stays either way — it is the panel's
    # markup, and `practice.js` shows it only for a window it was given.
    assert 'data-practice-tab="test"' in panel()
    assert 'data-practice-tab="test"' not in panel(sections=[section(workspace=UNGRADED)])
    assert 'data-practice-tab="main"' in panel(sections=[section(workspace=UNGRADED)])


def test_a_quiz_renders_no_panel_at_all_no_frame_no_run_and_no_submit():
    # ⛔ `AX-05` and `W429`, clause 4. A quiz carries QUESTIONS in place of a
    # workspace: no file to name, nothing to open in an editor, no command to
    # Run and no grader to Submit to. ⭐ The two shapes share this one surface
    # and one of them renders with NO FRAME AT ALL — as an absence, never as
    # controls a reader may not use. ⚠️ Asserted both ways against the very
    # same section, so it cannot pass by rendering nothing for everything.
    assert panel(sections=[section(workspace=QUIZ)]) == ""
    assert panel(sections=[section(workspace=SHIPPED)]) != ""


def test_the_editor_slot_says_it_is_not_running_and_how_to_start_it():
    # ⛔ The honesty requirement: an IDE with a shell is not started because
    # somebody opened a reading page, and a panel that rendered blank would look
    # broken instead of saying so.
    note = panel().split('data-practice-part="no-editor"')[1]
    assert "not running" in note
    assert "code-server-toolchain" in note


# --- the panel's script, read as the data it is (`W416`) --------------------

#: ⛔ No JavaScript runs in this suite (`QA-03/1`: the pinned image has no
#: engine), so what a text can establish about the panel's script is asserted
#: here and the browser reading is `QA-02`'s (`SF-24/5`).
SCRIPT = ASSET_DIR / "practice.js"


def behaviour() -> str:
    """`practice.js` with its comments removed, so a claim is about the code."""
    return re.sub(r"/\*.*?\*/", "", SCRIPT.read_text(encoding="utf-8"), flags=re.DOTALL)


def test_the_editor_slot_is_filled_from_the_served_client_and_from_nowhere_else():
    # ⭐ The seam `W416` drew and `W429` kept: the panel reads
    # `studyforge.run` — the same object it already runs and stops through —
    # and fills the slot the panel already ships. ⛔ It asks for ONE PRACTICE's
    # windows, not for the corpus's folder: a folder cannot say which of two
    # windows shows which file.
    body = behaviour()
    assert "run.practice(corpus, key)" in body
    assert body.count("window.studyforge.run") == 1


def test_an_older_client_that_publishes_no_editor_leaves_run_and_submit_working():
    # ⚠️ A site BUILT by one version may be SERVED by another, and the client is
    # the serving process's — so the panel asks whether the function is there
    # rather than assuming it, and Run and Submit survive an older one.
    body = behaviour()
    assert "if (run.practice) {" in body
    assert body.index("if (run.practice) {") < body.index("run.practice(corpus, key)")


def test_a_frame_is_added_only_for_an_editor_the_server_says_is_up():
    body = behaviour()
    filling = body[body.index("run.practice(corpus, key)") :]
    assert "if (where && where.main && where.main.url) { windows(panel, where); }" in filling
    assert filling.index("where.main.url") < filling.index("windows(panel, where)")


def test_the_two_frames_are_built_from_urls_the_server_answered_and_from_nothing_else():
    # ⛔ R8: a built page names no origin, no port and no path inside anybody's
    # container. ⭐ **The whole URL arrives at serve time** — this file composes
    # no part of it, which is stronger than `W416`'s encoded folder was.
    body = behaviour()
    assert "built.src = url;" in body
    for word in ("?folder=", "payload=", "openFile", "vscode-remote", "encodeURIComponent"):
        assert word not in body, word
    assert "127.0.0.1" not in body and "localhost" not in body and "http://" not in body


def test_the_two_frames_take_two_different_urls_and_neither_is_the_other_s():
    # ⛔ **THE property the whole URL design exists for.** One window shows the
    # reader's file and the other shows the test, and the ONLY thing that can
    # tell two windows of one code-server apart is each window's own URL — an
    # extension cannot read its own window's query string, and both windows
    # share one workspace settings file. ⚠️ So a panel that built both frames
    # from ONE url would look entirely correct and show the same file twice.
    body = behaviour()
    built = re.findall(r"frame\(slots\.(\w+), (where\.\w+\.url), TITLES\.(\w+)\)", body)
    assert sorted(built) == [
        ("main", "where.main.url", "main"),
        ("test", "where.test.url", "test"),
    ], built


def test_the_tests_frame_is_built_lazily_on_the_first_click_of_its_tab():
    # ⭐ A second workbench is a second language server. A reader who never
    # opens the tests never pays for one — so the test frame is built inside
    # `select`, behind the once-only latch, and never beside the main one.
    #
    # ⛔ **The COUNT is the half that measures anything, and it is here because
    # the first version of this case did not have it.** Asserting only that the
    # lazy call is inside `select` is satisfied by a build that ALSO builds the
    # frame eagerly beside the main one — measured: that exact plant left this
    # case GREEN, which is a plant that observed nothing.
    body = behaviour()
    region = body[body.index("function windows(panel, where)") : body.index("function wire(")]
    assert region.count("frame(slots.test") == 1
    assert region.count("frame(slots.main") == 1
    selecting = region[region.index("function select(name)") : region.index("frame(slots.main")]
    assert "if (name === 'test' && !lazy && tested)" in selecting
    assert "lazy = true;" in selecting
    assert "frame(slots.test" in selecting
    # ⛔ And the main frame is built OUTSIDE `select`, at once: the reader's own
    # file is what the panel is for.
    assert "frame(slots.main" not in selecting


def test_the_sentence_stands_until_a_frame_replaces_it():
    body = behaviour()
    filling = body[body.index("function windows(panel, where)") :]
    assert "show(part(panel, 'no-editor'), false)" in filling
    assert filling.index("frame(slots.main") < filling.index("'no-editor'")


def test_the_tablist_is_shown_only_where_there_are_two_windows_to_choose_between():
    # ⚠️ `W357`'s shape: a record may name a file and no test. One tab is no
    # choice, and a tab over a file the material does not have is a dead
    # control — the same honesty that offers no Submit there.
    body = behaviour()
    assert "show(part(panel, 'tabs'), tested);" in body
    assert "var tested = !!(where.test && where.test.url);" in body


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
    assert "Work on this practice" not in outline


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


# --- ⛔ `W430`: the ONE reload a genuinely cold instance's first page needs ---
#
# ⛔ **No JavaScript runs in this suite** (`QA-03/1`), so what a TEXT can
# establish about the reload is established here and the browser reading is the
# visual harness's. ⭐ What a text can establish is exactly the thing that makes
# an automatic reload safe or catastrophic: that each of its guards is in front
# of it, and that there is only one `location.reload()` to guard.


def test_the_page_reloads_only_when_the_browser_says_the_frame_was_blocked():
    # ⭐ Asked rather than guessed at: a `securitypolicyviolation` naming
    # `frame-src` is the browser STATING that the editor's frame was refused,
    # and a reload without one would be a reload on a hunch.
    body = behaviour()
    assert body.count("location.reload()") == 1
    assert body.count("securitypolicyviolation") == 1
    assert body.index("securitypolicyviolation") < body.index("location.reload()")
    assert "indexOf(FRAME_SRC) !== 0" in body
    assert body.index("indexOf(FRAME_SRC) !== 0") < body.index("location.reload()")


def test_every_guard_that_stops_the_reload_repeating_stands_in_front_of_it():
    # ⛔ **Each of these closes a real loop, and a text can read that they are
    # all EARLIER than the reload.** The navigation must not itself be a reload,
    # so the remedy costs at most one; the editor's host must be this page's,
    # because a policy withholds an editor from another spelling of the same
    # machine on purpose and no reload would ever change that; and the blocked
    # URI must be the editor's, so an unrelated violation reloads nothing.
    body = behaviour()
    guards = (
        "timing[0].type === 'reload'",
        "String(location.hostname || '').toLowerCase()",
        "hostOf(event.blockedURI) !== editor",
    )
    reload_at = body.index("location.reload()")
    for guard in guards:
        assert guard in body, guard
        assert body.index(guard) < reload_at, guard


def test_a_browser_with_no_navigation_timing_is_never_reloaded():
    # ⚠️ **Failing closed is a frame that does not load; failing open is a page
    # that reloads for ever.** So an empty timing list returns, rather than
    # being read as *not a reload*.
    body = behaviour()
    assert "!timing.length ||" in body
    assert "getEntriesByType('navigation')" in body
    assert body.index("!timing.length ||") < body.index("location.reload()")


def test_the_listener_is_installed_before_the_frame_that_raises_the_violation():
    # ⛔ A listener added AFTER the frame would miss the only event it exists
    # for, and nothing anywhere would fail.
    body = behaviour()
    assert body.index("reloadWhenBlocked(where.main.url)") < body.index("frame(slots.main")
