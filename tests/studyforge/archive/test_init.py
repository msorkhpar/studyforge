"""Mirror of `src/studyforge/archive/__init__.py` (R12)."""

from __future__ import annotations

import re

from studyforge import archive
from tests.support import assert_package_contract, repository_root


def test_states_its_contract():
    assert_package_contract(archive, "studyforge.archive")


def test_the_raw_html_figure_is_the_one_spec_c3_measured():
    # ⛔ The docstring once kept a count spec §1's C3 retracted: markup quoted inside a
    # fence was read as raw HTML. The figure it states is C3's table row, never a copy
    # that can drift from it.
    spec = repository_root().joinpath("docs", "specs", "2026-09-08-studyforge-v1-design.md")
    row = next(
        line
        for line in spec.read_text(encoding="utf-8").splitlines()
        if line.startswith("| raw HTML |")
    )
    measured = re.search(r"(\d+) of (\d+)", row)
    stated = re.search(
        r"raw HTML appears in (\d+) (?:of (\d+) )?files", " ".join(archive.__doc__.split())
    )
    assert measured and stated, "the spec's C3 row or the docstring's figure no longer reads"
    assert stated.groups() == measured.groups()
