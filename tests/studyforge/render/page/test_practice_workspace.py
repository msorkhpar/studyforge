"""Mirror of `src/studyforge/render/assets/practice-workspace.js` (R12).

⚠️ **No JavaScript runs in this suite** (the pinned image has no engine), so
what a TEXT can establish is established here and the browser reading is the
visual harness's (`tests/visual/test_practice_workspace.py`). ⭐ What a text
can hold is exactly what keeps a reader's work: that nothing is moved, that the
page goes back to where it was, and that the status is asked of the reader's
own record.
"""

from __future__ import annotations

import re

from studyforge.render import templates
from studyforge.render.pageassets import ASSET_DIR, script

#: ⛔ The file this module mirrors, and the ONE place its name is spelled here.
SCRIPT = ASSET_DIR / "practice-workspace.js"
STYLE = ASSET_DIR / "practice-workspace.css"


def behaviour() -> str:
    """`practice-workspace.js` with its comments removed, so a claim is about the code."""
    return re.sub(r"/\*.*?\*/", "", SCRIPT.read_text(encoding="utf-8"), flags=re.DOTALL)


def test_it_is_in_the_pages_script():
    assert SCRIPT.read_text(encoding="utf-8") in script()


def test_nothing_is_moved_copied_or_rebuilt():
    # ⛔ An `iframe` MOVED TO ANOTHER PARENT RELOADS, taking the reader's work
    # with it. The workspace only hides, shows and marks what is already there.
    body = behaviour()
    for word in (
        "appendChild",
        "insertBefore",
        "replaceChild",
        "removeChild",
        ".append(",
        ".prepend(",
        ".before(",
        ".after(",
        "replaceWith",
        "cloneNode",
        "innerHTML",
        "outerHTML",
        "insertAdjacent",
        "createElement",
    ):
        assert word not in body, word


def test_it_names_no_api_no_origin_and_touches_no_frame():
    # ⛔ R8: the one seam is `window.studyforge.run`, and the frame is the
    # editor half's alone — this file says *opened* and *closed* and no more.
    body = behaviour()
    assert body.count("window.studyforge.run") == 1
    for word in ("/api", "127.0.0.1", "localhost", "fetch(", "iframe", "run.practice("):
        assert word not in body, word


def test_close_puts_the_page_back_where_it_was_in_one_step():
    # ⛔ `reset.css` makes every scroll smooth, and a glide is a page still
    # moving when the reader looks: the restore is `instant`, and the focus
    # given back to the card moves nothing.
    body = behaviour()
    closing = body[
        body.index("function close()") : body.index("practices.forEach(function (one, index)")
    ]
    assert "window.scrollTo({ top: was, left: 0, behavior: 'instant' });" in closing
    assert "one.link.focus({ preventScroll: true });" in closing
    assert closing.index("window.scrollTo(") < closing.index("one.link.focus(")
    # ⭐ Where the reader was is read on the FIRST open only: Next and Previous
    # move within the workspace, and the page under it has not moved.
    assert "if (current < 0) { was = window.pageYOffset || 0; }" in body


def test_escape_closes_and_is_read_on_the_document():
    body = behaviour()
    assert "var ESCAPE = 'Escape';" in body
    assert "document.addEventListener('keydown', function (event) {" in body
    assert "if (current >= 0 && event.key === ESCAPE) { close(); }" in body


def test_opening_one_closes_the_other_first_and_says_so_to_the_editor():
    # ⛔ One editor at most: the practice left is told it is closed BEFORE the
    # next is told it is opened, so its frame goes before another is asked for.
    body = behaviour()
    opening = body[body.index("function open(index)") : body.index("function close()")]
    assert opening.index("leave();") < opening.index("say(OPENED, one);")
    leaving = body[body.index("function leave()") : body.index("function open(index)")]
    assert "say(CLOSED, one);" in leaving
    assert "var OPENED = 'studyforge:practice-opened';" in body
    assert "var CLOSED = 'studyforge:practice-closed';" in body


def test_previous_and_next_are_hidden_at_the_ends_rather_than_dead():
    body = behaviour()
    assert "act('previous').hidden = index === 0;" in body
    assert "act('next').hidden = index === practices.length - 1;" in body


def test_the_status_is_asked_of_the_readers_record_and_painted_only_from_its_answer():
    # ⛔ The status is the reader's own record, never the page's: it is asked of
    # the served client, read again when a run settles, and a card whose answer
    # is not one is left saying nothing.
    body = behaviour()
    assert "run.practices(first.getAttribute(CARD_CORPUS), unit)" in body
    assert "if (!held) { return; }" in body
    assert "document.addEventListener(SETTLED, refresh);" in body
    assert "var asks = run && run.available() && run.practices;" in body
    assert "if (!asks) { return; }" in body


def test_what_it_selects_is_what_the_page_emits():
    # ⚠️ Spelled twice — here and in `render/page/practices.py`'s templates —
    # so each spelling is read against the markup it names.
    body = behaviour()
    shipped = "".join(
        templates.template(name).template
        for name in (
            "practices.html",
            "practice-card.html",
            "practice-state.html",
            "practice-workspace.html",
        )
    )
    for attribute in (
        "data-practices",
        "data-practice-card",
        "data-practice-key",
        'data-practices-part="open"',
        'data-practices-part="state"',
        "data-practice-state",
        "data-workspace",
        "data-workspace-part",
        "data-workspace-act",
    ):
        assert attribute in shipped, attribute
    assert "'section[data-practices]'" in body and "'div[data-workspace]'" in body


def test_the_workspace_layer_stands_over_every_other_raised_layer():
    # ⛔ The skip link is raised to 2 and the narration transport to 1: a
    # workspace below either is covered by the bar it was meant to cover.
    style = re.sub(r"/\*.*?\*/", "", STYLE.read_text(encoding="utf-8"), flags=re.DOTALL)
    shell = style[style.index("div[data-workspace] {") :]
    shell = shell[: shell.index("}")]
    assert "position: fixed;" in shell and "inset: 0;" in shell
    assert int(re.search(r"z-index: (\d+);", shell).group(1)) > 2
    assert "html[data-workspace-open] { overflow: hidden; }" in style
    # ⭐ At phone width the statement stacks over the editor.
    assert "@media (max-width: 40rem)" in style


def test_an_open_practice_is_named_in_the_address_and_opens_again_from_it():
    # ⚠️ A cold editor needs ONE reload (`practice-editor.js`), and it comes
    # after the reader opened a practice: the address is what brings them back
    # to it. ⛔ `replaceState`, so Back leaves the page as it always did.
    body = behaviour()
    assert "history.replaceState(state, '', location.pathname + location.search + hash);" in body
    assert "var state = Object.assign({}, history.state || {});" in body
    assert "state[WAS] = hash ? was : null;" in body
    assert "pushState" not in body
    opening = body[body.index("function open(index)") : body.index("function close()")]
    assert "address('#' + one.section.id);" in opening
    closing = body[
        body.index("function close()") : body.index("practices.forEach(function (one, index)")
    ]
    assert "address('');" in closing
    reopening = body[body.index("if (location.hash !== '#' + one.section.id) { return; }") :]
    # ⭐ Close then returns the reader to the card: `was` is set AFTER `open`,
    # which would otherwise keep the fragment's own scroll.
    assert reopening.index("open(index);") < reopening.index("was = ")
    # ⭐ And where the reader was, kept on the entry, wins over the card.
    assert reopening.index("var kept = history.state && history.state[WAS];") < reopening.index(
        "open(index);"
    )
    assert "was = typeof kept === 'number'" in reopening


def test_the_page_under_the_workspace_is_inert_while_it_is_up_and_only_then():
    # ⛔ A dialog whose Tab walks under its own cover is one a keyboard reader
    # is lost in. The page is made `inert` — no node moved — and exactly what
    # was marked is unmarked when the practice is left.
    body = behaviour()
    stilling = body[body.index("function still(one)") : body.index("function wake()")]
    assert "var kept = [shell, one.section, one.panel].filter(Boolean);" in stilling
    assert "child.inert = true;" in stilling and "stilled.push(child);" in stilling
    leaving = body[body.index("function leave()") : body.index("function open(index)")]
    assert "wake();" in leaving
    opening = body[body.index("function open(index)") : body.index("function close()")]
    assert "still(one);" in opening
    assert (
        'role="dialog" aria-modal="true"' in templates.template("practice-workspace.html").template
    )
