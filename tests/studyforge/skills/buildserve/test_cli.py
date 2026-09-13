"""Mirror of `src/studyforge/skills/buildserve/cli.py` (R12)."""

from __future__ import annotations

import io

import pytest

from studyforge.skills.buildserve.cli import PROG, build_parser, main
from studyforge.validate.cli import UNUSABLE


def test_the_parser_takes_a_root_an_out_and_three_optional_flags():
    parser = build_parser()
    assert parser.prog == PROG
    arguments = parser.parse_args(["corpus", "--out", "site"])
    assert (arguments.root, arguments.out) == ("corpus", "site")
    assert (arguments.voice, arguments.service, arguments.port) == (None, None, None)
    given = parser.parse_args(["c", "--out", "s", "--voice", "v", "--service", "u", "--port", "0"])
    assert (given.voice, given.service, given.port) == ("v", "u", 0)


def test_out_is_required_and_has_no_default():
    with pytest.raises(SystemExit) as refused:
        build_parser().parse_args(["corpus"])
    assert refused.value.code == UNUSABLE


def test_a_missing_root_stops_at_validate_and_names_what_was_asked_for(tmp_path):
    out = io.StringIO()
    code = main(["no-such-corpus", "--out", str(tmp_path)], out=out)
    said = out.getvalue()
    assert code == UNUSABLE
    assert "no-such-corpus: not a directory" in said
    assert said.splitlines()[-1] == f"step validate exit {UNUSABLE}"
    assert list(tmp_path.iterdir()) == []
