"""Mirror of `src/studyforge/render/assets/practice-editor.js` (R12).

⛔ **Its own module, as `practice-editor.js` is its own file** (R11): the two
editor windows, their tablist, and the one reload a cold instance needs.

⚠️ **No JavaScript runs in this suite** (the pinned image has no
engine), so what a TEXT can establish about the editor half is established here
and the browser reading is the visual harness's. ⭐ What a text can establish is
exactly what makes an automatic reload safe rather than catastrophic: that each
of its guards stands in front of it, and that there is one reload to guard.
"""

from __future__ import annotations

import re

from studyforge.render.pageassets import ASSET_DIR

#: ⛔ The file this module mirrors, and the ONE place its name is spelled here.
SCRIPT = ASSET_DIR / "practice-editor.js"


def behaviour() -> str:
    """`practice-editor.js` with its comments removed, so a claim is about the code."""
    return re.sub(r"/\*.*?\*/", "", SCRIPT.read_text(encoding="utf-8"), flags=re.DOTALL)


def test_the_editor_half_names_no_api_no_origin_and_no_client_file():
    # ⛔ R8, on the second file as on the first: a built text that
    # named the API, the serving origin or the client would be a defect the
    # floor reads. ⭐ `window.studyforge.run` is the one seam, exactly once.
    body = behaviour()
    assert body.count("window.studyforge.run") == 1
    for word in ("/api", "127.0.0.1", "localhost", "run-client", "docker", "fetch("):
        assert word not in body, word


def test_the_editor_half_never_claims_or_enforces_read_only():
    # ⛔ Read-only is the EDITOR's, out of the workspace settings the server
    # writes. A guard here would be a second, weaker copy of a rule the editor
    # already keeps — and a *claim* here would be a promise this file cannot
    # keep, since nothing in the page can stop a keystroke in an iframe.
    body = behaviour()
    for word in ("readonly", "readOnly", "read-only"):
        assert word not in body, word


def test_the_editor_slot_is_filled_from_the_served_client_and_from_nowhere_else():
    # ⭐ The seam: the panel reads
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
    assert "|| !run.practice) { return; }" in body
    assert body.index("|| !run.practice) { return; }") < body.index("run.practice(corpus, key)")


def test_a_frame_is_added_only_for_an_editor_the_server_says_is_up():
    body = behaviour()
    filling = body[body.index("run.practice(corpus, key)") :]
    assert "if (where && where.main && where.main.url) { windows(panel, where); }" in filling
    assert filling.index("where.main.url") < filling.index("windows(panel, where)")


def test_the_two_frames_are_built_from_urls_the_server_answered_and_from_nothing_else():
    # ⛔ R8: a built page names no origin, no port and no path inside anybody's
    # container. ⭐ **The whole URL arrives at serve time** — this file composes
    # no part of it.
    body = behaviour()
    assert "built.src = url;" in body
    for word in ("?folder=", "payload=", "openFile", "vscode-remote", "encodeURIComponent"):
        assert word not in body, word
    assert "127.0.0.1" not in body and "localhost" not in body and "http://" not in body


def test_each_window_is_shown_from_its_own_url_and_neither_is_the_other_s():
    # ⛔ **THE property the whole URL design exists for.** One window shows the
    # reader's file and the other shows the test, and the ONLY thing that can
    # tell two windows of one code-server apart is each window's own URL — an
    # extension cannot read its own window's query string, and both windows
    # share one workspace settings file. ⚠️ So a panel that showed both tabs
    # from ONE url would look entirely correct and show the same file twice.
    body = behaviour()
    selecting = body[
        body.index("function select(name)") : body.index("function select(name)") + 600
    ]
    assert "var url = where[name].url;" in selecting
    assert "frame(slot, url, TITLES[name]);" in selecting
    assert "built.src = url;" in selecting


def test_one_practice_holds_one_frame_and_a_tab_changes_what_it_shows():
    # ⛔ The user's ruling: **one editor at most**. A second workbench is a
    # second language server, so the Tests tab does not build a second frame
    # beside the reader's file: it points the ONE frame at the test's window.
    #
    # ⛔ **The COUNT is the half that checks anything**: one call that builds a
    # frame in the whole of `windows`, behind the latch that says none is built.
    body = behaviour()
    region = body[body.index("function windows(panel, where)") : body.index("var asking = 0;")]
    assert region.count("frame(") == 1
    assert "if (!built) {" in region
    assert region.index("if (!built) {") < region.index("frame(")
    assert "slots.test" not in region


def test_the_sentence_stands_until_a_frame_replaces_it():
    body = behaviour()
    filling = body[body.index("function windows(panel, where)") :]
    assert "show(part(panel, 'no-editor'), false)" in filling
    assert filling.index("select('main')") < filling.index("'no-editor'")


def test_nothing_is_asked_until_a_practice_is_opened_and_its_frame_goes_when_it_closes():
    # ⭐ The user's ruling: **no editor loads until a practice is opened**. The
    # one place the server is asked for a practice's windows is `open`, and the
    # one caller of `open` is the workspace's `studyforge:practice-opened`.
    body = behaviour()
    assert body.count("run.practice(corpus, key)") == 1
    assert body.count("open(event.target, run)") == 1
    assert "document.addEventListener(OPENED, function (event) {" in body
    assert "document.addEventListener(CLOSED, function (event) {" in body
    assert "var OPENED = 'studyforge:practice-opened';" in body
    assert "var CLOSED = 'studyforge:practice-closed';" in body
    # ⛔ No ask on load: nothing calls `open` or `windows` outside a listener.
    tail = body[body.index("window.studyforge.frames = {") :]
    assert tail.count("open(") == 1 and "windows(" not in tail
    # ⛔ Closing empties the slot and puts the sentence back.
    closing = body[body.index("function close(panel)") : body.index("window.studyforge.frames")]
    assert "slot.removeChild(slot.firstChild)" in closing
    assert "show(part(panel, 'no-editor'), true);" in closing


def test_an_answer_that_arrives_after_the_reader_moved_on_builds_nothing():
    # ⚠️ The ask is a round trip: a reader who closes, or opens the next
    # practice, before it answers must not get a frame in a panel no one sees.
    body = behaviour()
    opening = body[body.index("function open(panel, run)") : body.index("function close(panel)")]
    assert "if (mine !== asking || !panel.hasAttribute(OPEN)) { return; }" in opening
    assert opening.index("!panel.hasAttribute(OPEN)") < opening.index("windows(panel, where)")
    assert "asking += 1;" in body[body.index("function close(panel)") :]


def test_the_tablist_is_shown_only_where_there_are_two_windows_to_choose_between():
    # ⚠️ A record may name a file and no test. One tab is no
    # choice, and a tab over a file the material does not have is a dead
    # control — the same honesty that offers no Submit there.
    body = behaviour()
    assert "show(part(panel, 'tabs'), tested);" in body
    assert "var tested = !!(where.test && where.test.url);" in body


# --- ⛔ The ONE reload a genuinely cold instance's first page needs ---
#
# ⛔ **No JavaScript runs in this suite**, so what a TEXT can
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
    assert body.index("reloadWhenBlocked(where.main.url)") < body.index("select('main');")


# ⛔ A frame never keeps focus the reader did not give it, and the
# page never moves on its own. ⭐ The browser reading is
# `tests/visual/test_practice_focus.py`; what a TEXT can hold is the part of the
# guard that harness cannot stage (see that module's docstring) and the orders
# that make the whole of it work.


def test_every_frame_is_held_before_it_is_added_to_the_page():
    # ⛔ The workbench takes focus as soon as it loads; a frame added first and
    # watched second is one whose first steal nobody answers.
    body = behaviour()
    built = body[body.index("function frame(slot, url, title)") :]
    assert built.index("held(built);") < built.index("slot.appendChild(built);")


def test_a_steal_that_raises_no_blur_is_still_seen():
    # ⛔ **The route the visual harness cannot stage**: a frame taking focus
    # from another frame, or while the browser window is not focused, raises
    # no `blur` on the page, and the page would still glide to the editor. ⭐ So the page reads
    # `activeElement` on an interval
    # from the moment its first frame is built, and never stops.
    body = behaviour()
    install = body[body.index("function install()") : body.index("return function (built)")]
    assert "setInterval(tick, WATCH_EVERY);" in install
    assert "clearInterval" not in body
    assert "window.addEventListener('blur'" in install


def test_focus_is_given_back_one_task_later_and_never_inside_the_blur():
    # ⚠️ A focus moved inside the `blur` — or in a microtask, which is still
    # inside it — is ignored, and the page glides to the editor.
    body = behaviour()
    refuse = body[body.index("function refuse(at)") : body.index("function arrived(at)")]
    assert "setTimeout(function () {" in refuse
    assert "queueMicrotask" not in body
    assert "preventScroll: true" in refuse


def test_only_the_readers_hand_gives_a_frame_focus():
    # ⭐ The pointer over THAT frame with the page's user activation, or a Tab
    # pressed on the page just before — never a timer and never a default.
    body = behaviour()
    given = body[body.index("function given(built)") : body.index("function stay(at, again)")]
    assert "navigator.userActivation" in given
    assert "(pointed === built && active) || Date.now() - tabbed < TAB_GRACE" in given
    assert "built.addEventListener('pointerenter'" in body
    assert "if (event.key === 'Tab') { tabbed = Date.now(); }" in body
