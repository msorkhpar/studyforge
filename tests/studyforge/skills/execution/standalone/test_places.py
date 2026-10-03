"""Mirror of `src/studyforge/skills/execution/standalone/places.py` (R12)."""

from __future__ import annotations

from studyforge.execute import instance
from studyforge.skills.execution.standalone import places
from tests.studyforge.skills.execution import contracts


def test_the_ports_are_the_defaults_for_a_course_that_recorded_none(tmp_path):
    site, editor = places.ports(tmp_path, contracts.editor_contract()["editor"])
    assert site == instance.DEFAULT_SITE_PORT
    assert editor > 0 and editor != site


def test_the_ports_are_the_ones_the_course_recorded(tmp_path):
    file = tmp_path / instance.INSTANCE_FILE
    file.parent.mkdir(parents=True)
    file.write_text(f"{instance.SITE_PORT}=19001\n{instance.EDITOR_PORT}=19002\n", encoding="utf-8")
    assert places.ports(tmp_path, contracts.editor_contract()["editor"]) == (19001, 19002)
