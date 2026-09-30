"""Mirror of `src/studyforge/skills/execution/standalone/__init__.py` (R12): its surface."""

from __future__ import annotations

from studyforge.skills.execution import standalone


def test_every_name_on_the_surface_resolves():
    for name in standalone.__all__:
        assert getattr(standalone, name) is not None, name


def test_the_surface_offers_the_step_and_its_readings():
    assert {"release", "served", "classify", "tracked", "table", "Run", "MANIFEST"} <= set(
        standalone.__all__
    )
    assert standalone.MANIFEST == ".studyforge/release.json"


def test_the_surface_offers_the_thin_export_s_lock():
    assert {"Bases", "BasesRefused", "read_bases"} <= set(standalone.__all__)
