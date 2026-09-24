"""Mirror of `src/studyforge/cli/site/cli.py`'s `W460` half: `build --no-narration`."""

from __future__ import annotations

import io
import json

import pytest

from studyforge.cli.site.cli import SILENT, build_parser, main
from studyforge.validate.report import OK
from tests.studyforge.generate.corpora import a_corpus, an_output
from tests.studyforge.generate.test_narration import PLAYER, narrate


def test_the_flag_is_optional_both_ways_and_absent_means_the_corpus_decides():
    parser = build_parser()
    assert parser.parse_args(["r", "--out", "o"]).narration is None
    assert parser.parse_args(["r", "--out", "o", "--no-narration"]).narration is False
    assert parser.parse_args(["r", "--out", "o", "--narration"]).narration is True


@pytest.mark.parametrize(
    ("declared", "flags", "silent"),
    [
        (None, [], False),
        (None, ["--no-narration"], True),
        (False, [], True),
        (False, ["--narration"], False),
    ],
)
def test_the_build_says_narration_is_off_exactly_when_it_is(tmp_path, declared, flags, silent):
    root = a_corpus(tmp_path, "depth1")
    narrate(root)
    if declared is not None:
        manifest = root / "corpus.json"
        document = json.loads(manifest.read_text(encoding="utf-8"))
        manifest.write_text(json.dumps({**document, "corpus_api": 5, "narration": declared}))
    out, said = an_output(tmp_path), io.StringIO()

    assert main([str(root), "--out", str(out), *flags], out=said) == OK

    assert (SILENT in said.getvalue()) is silent
    played = any(PLAYER in page.read_text("utf-8") for page in out.rglob("*.unit.html"))
    assert played is not silent
