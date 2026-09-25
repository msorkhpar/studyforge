"""Mirror of `src/studyforge/render/assets/code-links.js` (R12): a lesson's code, in the editor.

⚠️ **No JavaScript runs in this suite** (the pinned image has no engine), so
what a TEXT can establish is established here and the browser reading is a live
one: that the file reaches the API only through the served client, reuses the
practice panel's frame rather than building one, and follows the link whenever
it cannot open the editor.
"""

from __future__ import annotations

import re

from studyforge.render.pageassets import ASSET_DIR, SCRIPT_PARTS

SCRIPT = ASSET_DIR / "code-links.js"


def behaviour() -> str:
    """`code-links.js` with its comments removed, so a claim is about the code."""
    return re.sub(r"/\*.*?\*/", "", SCRIPT.read_text(encoding="utf-8"), flags=re.DOTALL)


def test_it_names_no_api_no_origin_and_no_client_file():
    # ⛔ R8: a built text names none of them; the served client is the one seam.
    body = behaviour()
    assert body.count("window.studyforge.run") == 1
    for word in ("/api", "127.0.0.1", "localhost", "run-client", "docker", "fetch("):
        assert word not in body, word


def test_it_builds_no_frame_of_its_own_and_takes_the_practice_panel_s():
    # ⭐ One focus guard and one reload remedy, published by `practice-editor.js`.
    body = behaviour()
    assert "document.createElement('iframe')" not in body
    assert "frames.frame(slot(entry, name), where[name].url," in body
    assert "frames.reloadWhenBlocked(where.main.url)" in body
    editor = re.sub(r"/\*.*?\*/", "", (ASSET_DIR / "practice-editor.js").read_text(), flags=re.S)
    assert "window.studyforge.frames = { frame: frame, reloadWhenBlocked: reloadWhenBlocked };" in (
        editor
    )


def test_it_follows_the_practice_editor_in_the_bundle_which_is_what_lets_it_find_the_frames():
    parts = list(SCRIPT_PARTS)
    assert parts.index("practice-editor.js") < parts.index("code-links.js")


def test_an_example_is_wired_only_once_the_editor_is_up():
    # ⛔ Until then an entry is its lines and the built sentence: every link is followed.
    body = behaviour()
    up = body[body.index("run.editor(entries[0].corpus).then") :]
    assert up.index("if (!found) { return; }") < up.index("wire(entry);")
    assert "addEventListener('toggle'" in body[body.index("function wire(entry)") :]


def test_an_example_loads_only_when_it_is_expanded_and_closing_it_unloads_it():
    body = behaviour()
    assert (
        "if (entry.details.open) { load(entry); } else if (live === entry) { unload(entry); }"
        in (body)
    )
    unload = body[body.index("function unload(entry)") : body.index("function draw(")]
    assert "slot(entry, name).textContent = '';" in unload


def test_one_example_at_most_is_live_and_expanding_another_closes_the_first():
    load = behaviour().split("function load(entry)", 1)[1].split("function remember", 1)[0]
    assert "if (live) { var before = live; before.details.open = false; unload(before); }" in load
    assert "if (mine !== asked || live !== entry || !entry.details.open) { return; }" in load


def test_the_page_is_never_scrolled_to_an_example_and_a_reload_puts_it_back():
    body = behaviour()
    for word in ("scrollIntoView", ".focus("):
        assert word not in body, word
    # ⛔ The one move: back to where the reader was when a cold reload moved the page.
    assert body.count("scrollTo(") == 1
    assert "{ entry: index, x: window.scrollX, y: window.scrollY }" in body
    assert "requestAnimationFrame(function () { putBack(kept); });" in body


def test_a_modified_click_is_left_to_the_browser():
    body = behaviour()
    assert "event.metaKey || event.ctrlKey || event.shiftKey || event.altKey" in body


def test_the_copy_sentence_replaces_the_plain_one_only_for_an_editor_that_is_up():
    body = behaviour()
    up = body[body.index("run.editor(entries[0].corpus).then") :]
    assert up.index("if (!found) { return; }") < up.index("show(part(entry, 'copy'), true);")


def test_it_never_claims_or_enforces_read_only():
    body = behaviour()
    for word in ("readonly", "readOnly", "read-only"):
        assert word not in body, word


def test_the_test_is_run_by_the_file_the_server_named_and_never_composed_here():
    body = behaviour()
    assert "run.codeTest(entry.corpus, where.runs, function (line) {" in body
    assert "if (!where || !where.runs) { return; }" in body
