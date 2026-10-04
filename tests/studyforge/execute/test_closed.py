"""Mirror of `execute/closed.py` (R12): the settings that keep the editor to the practice."""

from __future__ import annotations

import json

from studyforge.execute import workbench
from studyforge.execute.closed import CLOSED


def test_the_closed_settings_hide_every_surface_that_leads_away_and_are_plain_json():
    assert CLOSED["workbench.statusBar.visible"] is False
    assert CLOSED["window.commandCenter"] is False
    assert CLOSED["workbench.editor.showTabs"] == "none"
    assert json.loads(json.dumps(CLOSED)) == CLOSED


def test_every_practice_settings_file_carries_them_whole():
    held = workbench.settings("main.py", "test_main.py")
    assert all(held[key] == value for key, value in CLOSED.items())
