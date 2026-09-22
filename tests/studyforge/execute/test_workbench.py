"""Mirror of `src/studyforge/execute/workbench.py` (R12): one practice's windows and settings.

⛔ **Every claim here is a silence when it fails.** A URL built from the wrong
file opens a file; a `readonlyExclude` naming the wrong path leaves an editor
that works; a settings file written over somebody else's is a file that is
simply gone. ⭐ So each is asserted in BOTH directions, and the two that decide
the whole design — that the two windows differ, and that the test is left
read-only — are asserted against each other rather than against a constant.
"""

from __future__ import annotations

import json
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest

from studyforge.execute import Editor
from studyforge.execute.workbench import (
    AUTO_SAVE,
    CLOSED,
    EVERYTHING,
    HOT_EXIT,
    MAIN_KEY,
    MARKER,
    READONLY_EXCLUDE,
    READONLY_INCLUDE,
    SETTINGS_DIR,
    SETTINGS_FILE,
    TEST_KEY,
    WorkbenchRefused,
    authority,
    open_url,
    settings,
    write_settings,
)

#: The editor a reader has up: one origin, one folder, and the part of the
#: source root it holds. ⚠️ A made-up container path, for `test_editor.py`'s
#: reason — the real one is a home and R7's gate reads one as a leak.
EDITOR = Editor(origin="http://127.0.0.1:8443", folder="/w/sources", base="practice")

MAIN = "practice/bitmap/Bitmap.java"
TEST = "practice/bitmap/BitmapTest.java"

#: The same two, relative to the folder a window opens — which is what the
#: workbench resolves a `files.readonly*` pattern against.
INSIDE_MAIN = "bitmap/Bitmap.java"
INSIDE_TEST = "bitmap/BitmapTest.java"


def payload_of(url: str) -> list:
    """The `payload` a code-server URL carries, decoded."""
    return json.loads(parse_qs(urlsplit(url).query)["payload"][0])


# --- the URL, which is the ONLY thing that tells two windows apart -----------


def test_a_window_is_opened_by_its_own_url_naming_one_absolute_file():
    url = open_url(EDITOR, MAIN)
    assert url is not None
    parts = urlsplit(url)
    assert f"{parts.scheme}://{parts.netloc}" == EDITOR.origin
    assert parse_qs(parts.query)["folder"] == [EDITOR.folder]
    opened = f"vscode-remote://127.0.0.1:8443/w/sources/{INSIDE_MAIN}"
    assert payload_of(url) == [["openFile", opened]]


def test_the_two_windows_get_two_different_urls_naming_two_different_files():
    # ⛔ **THE property the whole URL design exists for.** An extension cannot
    # read its own window's query string and both windows share ONE workspace
    # settings file — so anything an extension opened it would open in BOTH,
    # and the window's own URL is the only discriminator there is. ⚠️ Asserted
    # as a DIFFERENCE between the two answers, never against a literal: a
    # composer that ignored its argument would satisfy a literal check on
    # either one alone and still show the same file twice.
    main, test = open_url(EDITOR, MAIN), open_url(EDITOR, TEST)
    assert main != test
    assert payload_of(main) != payload_of(test)
    assert payload_of(main)[0][1].endswith(INSIDE_MAIN)
    assert payload_of(test)[0][1].endswith(INSIDE_TEST)
    # ⭐ And they are two windows of ONE editor: same origin, same folder.
    assert urlsplit(main).netloc == urlsplit(test).netloc
    assert parse_qs(urlsplit(main).query)["folder"] == parse_qs(urlsplit(test).query)["folder"]


def test_the_remote_authority_is_the_origins_own_and_is_never_composed_twice():
    # ⚠️ Two spellings of one host and port is the defect where they differ by a
    # character, the window opens nothing, and nothing fails anywhere.
    assert authority(EDITOR) == "127.0.0.1:8443"
    other = Editor(origin="http://[::1]:9000", folder="/w", base="")
    assert authority(other) == "[::1]:9000"
    assert payload_of(open_url(other, "one.py"))[0][1] == "vscode-remote://[::1]:9000/w/one.py"


def test_a_file_the_editor_does_not_hold_is_no_url_at_all():
    # ⛔ Naming an unmounted path opens an empty, dirty buffer titled with the
    # file's own name — it looks exactly like a corrupted file and is not one.
    assert open_url(EDITOR, "docs/reading.md") is None
    assert open_url(EDITOR, "/etc/passwd") is None


# --- read-only is the EDITOR's job --------------------------------------------


def test_everything_is_read_only_and_the_practices_own_source_is_excluded_back_out():
    written = settings(INSIDE_MAIN, INSIDE_TEST)
    assert written[READONLY_INCLUDE] == {EVERYTHING: True}
    assert written[READONLY_EXCLUDE] == {INSIDE_MAIN: True}


def test_the_test_is_deliberately_left_read_only():
    # ⛔ **Deliberate, and it is the point of the second window.** The test is
    # the statement of what *done* means; a reader who can edit it can make it
    # say anything. ⚠️ Asserted against the exclusion the MAIN file gets, so it
    # cannot pass by excluding nothing at all.
    written = settings(INSIDE_MAIN, INSIDE_TEST)
    assert INSIDE_TEST not in written[READONLY_EXCLUDE]
    assert INSIDE_MAIN in written[READONLY_EXCLUDE]


def test_the_module_says_which_scope_can_lift_the_lock_it_writes():
    # ⛔ W433, and it is a MEASUREMENT rather than a caution. `files.readonlyExclude`
    # is an object setting and VS Code MERGES object settings across scopes, so a
    # USER-scope entry naming the test file is merged into the workspace value this
    # module writes and the test becomes writable. Measured in a real session:
    # {"Main.java": True} became {"MainTest.java": True, "Main.java": True} after one
    # ConfigurationTarget.Global write. ⚠️ No key here can prevent that — the editor
    # image's confinement of the command surface is what does — so the module has to
    # SAY so, or the next reader takes the lock for stronger than it is.
    from studyforge.execute import workbench

    said = workbench.__doc__
    assert "merge" in said.lower() and "ConfigurationTarget.Global" in said
    assert "W433" in said
    # ⛔ Named, never linked, and never imported: the toolchain is another
    # repository and this framework knows no path inside it (R1, R20).
    assert "code-server-toolchain" in said
    assert "code_server_toolchain" not in Path(workbench.__file__).read_text(encoding="utf-8")


def test_the_two_keys_the_lockdown_extension_declares_carry_the_two_paths():
    # ⭐ Workspace-relative, which is what the extension's manifest declares
    # them to be. ⚠️ Their REWRITE is the one signal inside the editor that the
    # practice moved; the extension reads neither value, because the URL names
    # the file.
    written = settings(INSIDE_MAIN, INSIDE_TEST)
    assert written[MAIN_KEY] == INSIDE_MAIN
    assert written[TEST_KEY] == INSIDE_TEST
    assert settings(INSIDE_MAIN, None)[TEST_KEY] == ""


def test_hot_exit_is_off_and_auto_save_is_on():
    # ⛔ **The subtle one.** Editor-restore state is per WORKSPACE, not per
    # window: with hot exit on, each window reopens what the other last had and
    # BOTH end up showing BOTH files — the two-window design undone by a
    # default. ⭐ Which makes auto-save a CORRECTNESS rule and not a
    # convenience: Run and Submit execute against the file ON DISK.
    written = settings(INSIDE_MAIN, INSIDE_TEST)
    assert written["files.hotExit"] == HOT_EXIT == "off"
    assert written["files.autoSave"] == AUTO_SAVE != "off"


def test_the_workbench_is_closed_around_the_one_file():
    # ⚠️ Asserted as the whole of `CLOSED` rather than key by key, so a surface
    # dropped from the set is a red test here and not a silent reopening.
    written = settings(INSIDE_MAIN, INSIDE_TEST)
    assert CLOSED and all(written[key] == value for key, value in CLOSED.items())
    # ⚠️ `commandCenter` joined this list on a USER REPORT, not on a review:
    # the title bar's search box stayed reachable through W432 and W433 because
    # no key in this set named it, and the reader used it (2026-09-22).
    for surface in (
        "activityBar",
        "statusBar",
        "showTabs",
        "menuBarVisibility",
        "minimap",
        "commandCenter",
        "layoutControl",
    ):
        assert any(surface in key for key in CLOSED), surface


def test_the_practice_file_does_not_scroll_past_its_last_line():
    # ⭐ The panel cannot be resized by the reader, so a viewport of blank space
    # below the closing brace is not a preference: it reads as more file.
    written = settings(INSIDE_MAIN, INSIDE_TEST)
    assert written["editor.scrollBeyondLastLine"] is False


def test_the_chat_pane_is_hidden_by_a_setting_and_the_explorer_is_not():
    # ⛔ W432, and it is the asymmetry that matters rather than the key. The
    # SECONDARY side bar is the chat pane and a setting names its default
    # visibility; the PRIMARY side bar is the Explorer and NO setting names its
    # visibility at all — it is workbench UI state, which is the whole reason
    # the lockdown extension exists. ⚠️ A future editor that hid the Explorer by
    # setting would make the second half of this test red, and that is the
    # intended way to find out.
    written = settings(INSIDE_MAIN, INSIDE_TEST)
    assert written["workbench.secondarySideBar.defaultVisibility"] == "hidden"
    assert not [key for key in CLOSED if "sideBar." in key and "secondary" not in key.lower()], (
        "a primary side bar visibility setting appeared; W432's belt can stop being only a belt"
    )


def test_nothing_here_claims_to_be_a_security_boundary():
    # ⛔ An iframe of an IDE with a shell is exactly as powerful as the process
    # behind it. The boundary is the container, the loopback bind and one exact
    # origin — and a docstring that said otherwise would be read by somebody
    # deciding how to run one.
    from studyforge.execute import workbench

    said = workbench.__doc__ or ""
    assert "NOT a security boundary" in said
    assert "The boundary is the container" in said


# --- written where the editor reads it ----------------------------------------


def settings_file(folder: Path) -> Path:
    return folder / SETTINGS_DIR / SETTINGS_FILE


def test_the_settings_are_written_into_the_folder_the_window_opens(tmp_path):
    written = write_settings(tmp_path, INSIDE_MAIN, INSIDE_TEST)
    assert written == settings_file(tmp_path)
    assert json.loads(written.read_text(encoding="utf-8")) == settings(INSIDE_MAIN, INSIDE_TEST)


def test_a_rewrite_replaces_this_frameworks_own_file_whole(tmp_path):
    # ⚠️ Rewritten on EVERY ask, because the exclusion names THIS practice's own
    # source: a reader who moved to another practice must not still be able to
    # edit the last one's file.
    write_settings(tmp_path, INSIDE_MAIN, INSIDE_TEST)
    write_settings(tmp_path, "other/Kata.java", None)
    held = json.loads(settings_file(tmp_path).read_text(encoding="utf-8"))
    assert held[READONLY_EXCLUDE] == {"other/Kata.java": True}
    assert INSIDE_MAIN not in held[READONLY_EXCLUDE]


def test_a_settings_file_this_framework_did_not_write_is_refused_and_not_touched(tmp_path):
    # ⛔ R3's spirit where this framework writes at all: a reader's own settings
    # are theirs. The refusal names the file; the file is left exactly as it was.
    settings_file(tmp_path).parent.mkdir(parents=True)
    mine = '{"editor.fontSize": 18}\n'
    settings_file(tmp_path).write_text(mine, encoding="utf-8")
    with pytest.raises(WorkbenchRefused) as refusal:
        write_settings(tmp_path, INSIDE_MAIN, INSIDE_TEST)
    assert SETTINGS_FILE in str(refusal.value) and MAIN_KEY in str(refusal.value)
    assert settings_file(tmp_path).read_text(encoding="utf-8") == mine


def test_something_that_is_not_json_at_all_is_refused_too(tmp_path):
    settings_file(tmp_path).parent.mkdir(parents=True)
    settings_file(tmp_path).write_text("not json", encoding="utf-8")
    with pytest.raises(WorkbenchRefused):
        write_settings(tmp_path, INSIDE_MAIN, INSIDE_TEST)


def test_a_settings_file_with_comments_in_it_is_read_and_not_choked_on(tmp_path):
    # ⚠️ A workbench settings file may legally carry `//` comments — the editor
    # image's own seed does — so the tell is looked for as TEXT. ⛔ A JSON parse
    # would raise on this file and refuse one this framework itself wrote.
    settings_file(tmp_path).parent.mkdir(parents=True)
    settings_file(tmp_path).write_text(
        f'{{\n  // written by the study server\n  {MARKER}: "old/One.java"\n}}\n',
        encoding="utf-8",
    )
    write_settings(tmp_path, INSIDE_MAIN, INSIDE_TEST)
    assert json.loads(settings_file(tmp_path).read_text(encoding="utf-8"))[MAIN_KEY] == INSIDE_MAIN


def test_the_marker_is_one_of_the_keys_this_module_itself_writes(tmp_path):
    # ⭐ Otherwise the guard would refuse this framework's OWN last write, and
    # the second ask for a practice would fail where the first succeeded.
    assert MARKER in json.dumps(settings(INSIDE_MAIN, INSIDE_TEST))
    write_settings(tmp_path, INSIDE_MAIN, INSIDE_TEST)
    write_settings(tmp_path, INSIDE_MAIN, INSIDE_TEST)


def test_nothing_is_left_beside_the_settings_file(tmp_path):
    # ⭐ Replaced atomically, so a workbench never reads half a settings file —
    # and the temporary it is replaced from does not survive the write.
    write_settings(tmp_path, INSIDE_MAIN, INSIDE_TEST)
    assert sorted(one.name for one in settings_file(tmp_path).parent.iterdir()) == [SETTINGS_FILE]


def test_a_folder_that_cannot_be_written_is_refused_saying_so(tmp_path):
    blocked = tmp_path / "read-only"
    blocked.mkdir()
    blocked.chmod(0o500)
    try:
        with pytest.raises(WorkbenchRefused) as refusal:
            write_settings(blocked, INSIDE_MAIN, INSIDE_TEST)
    finally:
        blocked.chmod(0o700)
    assert f"{SETTINGS_DIR}/{SETTINGS_FILE}" in str(refusal.value)
    # ⛔ And the message carries no absolute path: it runs into a serving
    # process's log (R7).
    assert str(tmp_path) not in str(refusal.value)
