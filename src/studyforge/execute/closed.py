"""The workbench's closed settings: every surface that leads away from the practice.

**What it does.** Holds `CLOSED`, the workspace settings that keep the editor to the practice's
own files: no menus, no side bars, no tabs, no command centre. `workbench.settings` merges it
into every practice's settings file. ⛔ These are settings and not commands, and they carry no
path, no origin and no corpus's word.
"""

from __future__ import annotations

#: The workbench, closed. ⛔ Every surface that is a way to end up somewhere the
#: lesson did not send the reader. ⚠️ These are settings and not commands: the
#: extension closes what is already open, and these stop it opening again.
#:
#: ⚠️ `workbench.secondarySideBar.defaultVisibility` is a belt only, and it is
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
    # the title bar, and no other key names it. ⚠️ It is a SECOND route to Go
    # to File, open even when the palette is confined.
    "window.commandCenter": False,
    "workbench.startupEditor": "none",
    "window.menuBarVisibility": "hidden",
    "breadcrumbs.enabled": False,
    "editor.minimap.enabled": False,
    # ⭐ A practice file ends where its last line ends. The default scrolls a
    # whole viewport of empty space past the closing brace, which reads as "the
    # file continues" in a panel the reader cannot resize.
    "editor.scrollBeyondLastLine": False,
    "explorer.openEditors.visible": 0,
    "workbench.tips.enabled": False,
}
