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
    assert "frames.frame(slots[name], current[name].url, TITLES[name])" in body
    assert "frames.reloadWhenBlocked(where.main.url)" in body
    editor = re.sub(r"/\*.*?\*/", "", (ASSET_DIR / "practice-editor.js").read_text(), flags=re.S)
    assert "window.studyforge.frames = { frame: frame, reloadWhenBlocked: reloadWhenBlocked };" in (
        editor
    )


def test_it_follows_the_practice_editor_in_the_bundle_which_is_what_lets_it_find_the_frames():
    parts = list(SCRIPT_PARTS)
    assert parts.index("practice-editor.js") < parts.index("code-links.js")


def test_a_link_opens_the_editor_only_once_the_editor_is_up_and_otherwise_is_followed():
    # ⛔ The plain view is W488's and is never broken: no editor, no answer,
    # an error — each follows the link.
    body = behaviour()
    assert body.index("run.editor(corpus).then") < body.index("document.addEventListener('click'")
    opening = body[body.index("function open(path, href)") :]
    assert "if (where) { draw(where); } else { fallback(); }" in opening
    assert "}, fallback);" in opening
    assert "if (href) { location.href = href; }" in body
    # ⭐ A cold instance reloads once for its frame policy, and the click is kept.
    assert "timing[0].type === 'reload' ? path : null" in body


def test_a_modified_click_is_left_to_the_browser():
    body = behaviour()
    assert "event.metaKey || event.ctrlKey || event.shiftKey || event.altKey" in body


def test_the_copy_sentence_replaces_the_plain_one_only_for_an_editor_that_is_up():
    body = behaviour()
    up = body[body.index("run.editor(corpus).then") :]
    assert up.index("if (!found) { return; }") < up.index("show(part('copy'), true);")


def test_it_never_claims_or_enforces_read_only():
    body = behaviour()
    for word in ("readonly", "readOnly", "read-only"):
        assert word not in body, word


def test_the_test_is_run_by_the_file_the_server_named_and_never_composed_here():
    body = behaviour()
    assert "run.codeTest(corpus, current.runs, function (line) {" in body
    assert "if (!current || !current.runs) { return; }" in body
