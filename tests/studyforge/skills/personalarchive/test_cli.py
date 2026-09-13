"""Mirror of `src/studyforge/skills/personalarchive/cli.py` (R12): `--for` has no default."""

from __future__ import annotations

import io

import pytest

from studyforge.skills.personalarchive.cli import build_parser, main
from studyforge.skills.personalarchive.layout import KINDS
from tests.studyforge.skills.personalarchive.archiving import TIMES, entry, machine, run


def test_export_without_a_choice_of_who_it_is_for_is_a_usage_error(tmp_path, capsys):
    with pytest.raises(SystemExit) as stopped:
        build_parser().parse_args(["export", str(tmp_path), str(tmp_path / "x.zip")])
    assert stopped.value.code == 2
    assert "--for" in capsys.readouterr().err


def test_the_choice_is_exactly_owner_or_sharing_and_has_no_default():
    export = build_parser()._subparsers._group_actions[0].choices["export"]
    kind = next(action for action in export._actions if action.dest == "kind")
    assert (kind.required, kind.default, tuple(kind.choices)) == (True, None, KINDS)
    with pytest.raises(SystemExit):
        build_parser().parse_args(["export", "a", "b", "--for", "everyone"])


def test_main_exports_and_imports_through_the_functions_that_do_it(tmp_path):
    first = machine(tmp_path, "a")
    run(first, passed=True, when=TIMES["t1"])
    archive = tmp_path / "mine.zip"
    out = io.StringIO()
    assert main(["export", str(first), str(archive), "--for", "owner"], out) == 0
    second = machine(tmp_path, "b", corpus=False)
    assert main(["import", str(archive), str(second)], out) == 0
    assert entry(second) == entry(first)
    assert "export owner exit 0" in out.getvalue() and "import exit 0" in out.getvalue()
