r"""The editor's workbench for ONE practice: which file each window opens, and what it may edit.

**What it does.** Two things, and they are two because only one of them can
tell the two windows apart:

- `open_url(editor, path)` — the URL that opens ONE file in a code-server
  window, or `None` for a path that editor does not hold;
- `settings(main, test)` and `write_settings(folder, main, test)` — the
  workspace settings a practice gets: everything read-only with the reader's
  own file excluded back out, the workbench closed, and the two keys the
  lockdown extension declares.

**How you use it.** `serve.routes.runs` calls both when a page asks for a
practice's editor: the settings are written into the opened folder, and the two
URLs are answered.

**Depends on.** `editor` for where an editor is and what it holds, `json`,
`os` and `pathlib`. No `subprocess` — nothing here starts anything.

## ⛔ The window's own URL is the ONLY thing that can tell two windows apart

⭐ **A practice is shown in TWO windows of ONE editor** — the file the reader
writes in one, the test that judges it in the other — and which file a window
shows is decided by **that window's own URL**:

    <origin>/?folder=<folder>&payload=[["openFile","vscode-remote://<authority><path>"]]

⛔ **Nothing else can do it, and this is a property rather than a preference.**
An extension cannot read its own window's query string, and both windows share
ONE workspace settings file — so anything an extension opened, it would open in
BOTH. ⚠️ The authority is the editor's own host and port, which is the origin's;
it is read off the origin rather than composed again here.

⛔ **A path this editor does not hold is answered as NOTHING, never as a URL.**
A code-server URL naming a file that is not mounted opens an **empty, dirty
buffer titled with the file's own name**, and the workbench then offers to save
it — it looks exactly like a corrupted file and is not one.

## ⛔ Read-only is the EDITOR's job, and the page neither claims nor enforces it

⭐ **Everything read-only, the practice's own source excluded back out:**

    "files.readonlyInclude": {"**/*": true}
    "files.readonlyExclude": {"<the practice's own source>": true}

⛔ **The test is DELIBERATELY NOT excluded.** It is the statement of what *done*
means, and a reader who can edit it can make it say anything. ⚠️ **A guard
written into the page would be a second, weaker copy of a rule the editor
already keeps**, so the page has none: it does not claim read-only and does not
attempt to enforce it.

⛔ **AND THE LOCK IS ONLY AS STRONG AS THE EDITOR'S CONFINEMENT — which is not
this module's, and is not a detail** (`W433`). ⚠️ `files.readonlyExclude` is an
**object** setting, and VS Code **merges** object settings across scopes, so a
USER-scope entry is merged INTO the workspace value written here rather than
being shadowed by it. ⭐ **Measured, in a real session on code-server 4.137.0:**
the workspace value `{"Main.java": True}` became
`{"MainTest.java": True, "Main.java": True}` after one
`ConfigurationTarget.Global` write, and the editor's own user settings file
carried it. ⛔ **So a reader who can reach the settings editor can make the test
that judges them writable, and NO key this module writes can prevent it.**

⭐ **What prevents it is the editor image's workbench lockdown**, which confines
the command surface so neither the settings editor nor the settings JSON can be
opened from inside a practice frame — ⛔ **`code-server-toolchain`, named and
not linked (R20), and the image is tagged only after a headless browser has
pressed those keys at a real session and seen nothing open.** ⚠️ **A consumer
serving this framework from an editor image WITHOUT that confinement has a
read-only lock a reader can lift**, and that is a property of the image rather
than of these settings.

## ⛔ `files.hotExit` is `off`, and it is the subtle one

⚠️ **Editor-restore state is per WORKSPACE, not per window.** With hot exit on,
each window reopens what the other last had, and **both windows end up showing
both files** — which is the whole two-window design undone by a default.

⭐ **Which makes `files.autoSave` a CORRECTNESS rule rather than a
convenience:** Run and Submit execute the practice's command against the file
ON DISK, so an unsaved edit is one the reader will watch their own tests
ignore — and they will believe the tests.

## ⛔ This is NOT a security boundary

An iframe of an IDE with a shell is exactly as powerful as the process behind
it. ⭐ **The boundary is the container, the loopback bind and one exact
origin.** What is here removes the ways *in* — it does not remove the
possibility, and nothing below should ever be read as if it did.

## ⛔ Written where the editor reads it, and never over somebody else's file

⭐ The settings of the folder a window opens are `.vscode/settings.json` inside
that folder, so that is where they are written — on the host side of the
editor's own bind mount. ⛔ **A file already there that this framework did not
write is never overwritten**: the write refuses, naming the file, and the
reader is told the editor could not be prepared rather than losing a settings
file they wrote. ⚠️ The tell is `MARKER`, one of the two keys the lockdown
extension contributes, which nothing else has a reason to write — looked for as
TEXT, because a workbench settings file may legally carry comments and a JSON
parse would raise on an ordinary one.

⭐ **Replaced whole, atomically**: a temporary file beside it and one `replace`,
so a reader's workbench never reads half a settings file.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from urllib.parse import quote

from studyforge.execute.editor import Editor

#: The directory a folder's own settings live in, and the file. ⛔ The
#: workbench's names, not this framework's, so neither is a choice.
SETTINGS_DIR = ".vscode"
SETTINGS_FILE = "settings.json"

#: The scheme a code-server window opens a file over. ⚠️ Not `file:`: the
#: workbench is remote to the browser and addresses its own disk this way.
REMOTE = "vscode-remote"

#: The query key that names the folder, and the one that carries acts to
#: perform once the workbench has started.
FOLDER = "folder"
PAYLOAD = "payload"
OPEN_FILE = "openFile"

#: The section the lockdown extension declares, and the two keys in it. ⭐ A
#: rewrite of this section is the ONE signal in the editor that the practice
#: moved; the extension reads neither value, because the URL names the file.
SECTION = "studyforge.practice"
MAIN_KEY = f"{SECTION}.main"
TEST_KEY = f"{SECTION}.test"

#: What says a settings file is this framework's to replace, looked for as
#: TEXT. ⛔ Absence is a file somebody else wrote, and it is refused rather than
#: overwritten. ⚠️ **Deliberately not a decode.** A workbench settings file may
#: legally carry `//` comments — the editor image's own seed does — so a JSON
#: parse would raise on a perfectly ordinary one and this framework would then
#: refuse a file it might as well have read. ⭐ And a module that decodes a
#: document owes the personal-data gate a call (R7, W7); this one reads nothing
#: OUT of that file, so not decoding it is the honest shape as well as the
#: robust one.
MARKER = f'"{MAIN_KEY}"'

#: Everything read-only, and what is excluded back out.
READONLY_INCLUDE = "files.readonlyInclude"
READONLY_EXCLUDE = "files.readonlyExclude"
EVERYTHING = "**/*"

#: The workbench, closed. ⛔ Every surface that is a way to end up somewhere the
#: lesson did not send the reader. ⚠️ These are settings and not commands: the
#: extension closes what is already open, and these stop it opening again.
#:
#: ⚠️ `workbench.secondarySideBar.defaultVisibility` is `W432`'s belt and it is
#: NOT the fix. The secondary side bar is the chat pane, and it is the ONE of
#: the two surfaces a reader saw that a setting can reach at all — the PRIMARY
#: side bar's visibility is workbench UI STATE and no setting names it, which
#: is why the lockdown extension exists. ⛔ So a window whose extension never
#: activates still shows the Explorer, and this key hides one of the two
#: symptoms rather than the cause. The cause is the editor image's
#: `--disable-workspace-trust` and the extension's own
#: `capabilities.untrustedWorkspaces` (`code-server-toolchain`), and neither
#: lives here.
CLOSED: dict[str, object] = {
    "workbench.secondarySideBar.defaultVisibility": "hidden",
    "workbench.activityBar.location": "hidden",
    "workbench.statusBar.visible": False,
    "workbench.editor.showTabs": "none",
    "workbench.editor.editorActionsLocation": "hidden",
    "workbench.layoutControl.enabled": False,
    # ⛔ The command centre is the "sources" box and the back/forward arrows in
    # the title bar, and it survived every round of this lockdown because no
    # other key names it. ⚠️ A reader reported reaching it (2026-09-22) after
    # the palette had already been confined: it is a SECOND route to Go to File.
    "window.commandCenter": False,
    "workbench.startupEditor": "none",
    "window.menuBarVisibility": "hidden",
    "breadcrumbs.enabled": False,
    "editor.minimap.enabled": False,
    # ⭐ A practice file ends where its last line ends. The default scrolls a
    # whole viewport of empty space past the closing brace, which reads as "the
    # file continues" in a panel the reader cannot resize (user, 2026-09-22).
    "editor.scrollBeyondLastLine": False,
    "explorer.openEditors.visible": 0,
    "workbench.tips.enabled": False,
}

#: ⛔ `off`, and the reason is in this module's docstring: restore state is per
#: WORKSPACE, so hot exit makes each window reopen what the other last had.
HOT_EXIT = "off"

#: ⭐ A correctness rule: a run executes the file on DISK.
AUTO_SAVE = "afterDelay"


class WorkbenchRefused(Exception):
    """The practice's workspace could not be prepared, saying which file and why."""


def open_url(editor: Editor, path: str) -> str | None:
    """Return the URL that opens `path` in one window, or `None` for a path not held.

    `path` is relative to the source root — a practice's `main_path` or
    `test_path`. ⛔ The folder is the editor's own, discovered rather than
    composed, and the file is absolute inside the container.
    """
    inside = editor.file(path)
    if inside is None:
        return None
    # ⚠️ Compact separators: this is a query-string value, and a space in it
    # becomes three characters once quoted, in a URL a reader may see.
    payload = json.dumps(
        [[OPEN_FILE, f"{REMOTE}://{authority(editor)}{inside}"]], separators=(",", ":")
    )
    return (
        f"{editor.origin}/?{FOLDER}={quote(editor.folder, safe='')}"
        f"&{PAYLOAD}={quote(payload, safe='')}"
    )


def authority(editor: Editor) -> str:
    """Return the host and port a `vscode-remote` URL is addressed to.

    ⭐ Read off the origin the probe discovered, never composed a second time:
    two spellings of one host and port is the defect where they differ by a
    character and the window opens nothing, with nothing failing anywhere.
    """
    _, _, rest = editor.origin.partition("://")
    return rest.rstrip("/")


def settings(main: str, test: str | None) -> dict[str, object]:
    """Return the workspace settings for one practice, as the decoded object.

    `main` and `test` are relative to the OPENED FOLDER — what
    `Editor.inside` answers — because that is what the workbench resolves a
    `files.readonly*` pattern against and what the lockdown extension's two
    keys are declared to carry.
    """
    return {
        MAIN_KEY: main,
        TEST_KEY: test or "",
        READONLY_INCLUDE: {EVERYTHING: True},
        READONLY_EXCLUDE: {main: True},
        "files.hotExit": HOT_EXIT,
        "files.autoSave": AUTO_SAVE,
        **CLOSED,
    }


def write_settings(folder: Path, main: str, test: str | None) -> Path:
    """Write one practice's workspace settings into `folder`, and return the file.

    `folder` is the HOST side of the editor's bind mount. Raises
    `WorkbenchRefused` when the file there is not this framework's, or when it
    cannot be written.
    """
    target = Path(folder) / SETTINGS_DIR / SETTINGS_FILE
    _require_ours(target)
    body = json.dumps(settings(main, test), indent=2, sort_keys=True) + "\n"
    temporary = target.with_name(f"{target.name}.studyforge")
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        temporary.write_text(body, encoding="utf-8")
        os.replace(temporary, target)
    except OSError as error:
        raise WorkbenchRefused(
            f"this practice's workspace settings could not be written to "
            f"{SETTINGS_DIR}/{SETTINGS_FILE}: {error.strerror or error.__class__.__name__}"
        ) from None
    return target


def _require_ours(target: Path) -> None:
    """Refuse a settings file this framework did not write, rather than replace it."""
    try:
        existing = target.read_text(encoding="utf-8")
    except FileNotFoundError:
        return
    except OSError as error:
        raise WorkbenchRefused(
            f"this practice's workspace settings could not be read at "
            f"{SETTINGS_DIR}/{SETTINGS_FILE}: {error.strerror or error.__class__.__name__}"
        ) from None
    if MARKER not in existing:
        raise WorkbenchRefused(
            f"{SETTINGS_DIR}/{SETTINGS_FILE} in the editor's folder was not written by "
            f"this framework — it carries no {MARKER} key — and it is not overwritten"
        )
