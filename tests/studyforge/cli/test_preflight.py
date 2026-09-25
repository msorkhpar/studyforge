"""Mirror of `src/studyforge/cli/preflight.py` (R12): the compose preflight's verb."""

from __future__ import annotations

import io

from studyforge.cli import VERBS
from studyforge.cli.preflight import CLEAN, main
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.studyforge.execute.test_preflight import corpus


def said(argv: list[str]) -> tuple[int, list[str]]:
    out = io.StringIO()
    code = main(argv, out)
    return code, out.getvalue().splitlines()


def test_it_is_the_registered_verb():
    assert VERBS["preflight"].run is main


def test_a_clean_instance_exits_0_and_says_so(tmp_path):
    assert said([str(corpus(tmp_path))]) == (OK, [CLEAN])


def test_each_bad_value_is_one_line_naming_its_key_and_the_exit_is_1(tmp_path):
    root = corpus(tmp_path, STUDYFORGE_SITE_PORT="18505", extra="STUDYFORGE_BIND=x\n")
    code, lines = said([str(root)])
    assert code == INVALID
    assert len(lines) == 2 and all(line.startswith("preflight ") for line in lines)
    assert "STUDYFORGE_SITE_PORT" in lines[0] and "STUDYFORGE_BIND" in lines[1]


def test_a_root_that_is_not_a_directory_is_unusable(tmp_path):
    assert said([str(tmp_path / "absent")])[0] == UNUSABLE
