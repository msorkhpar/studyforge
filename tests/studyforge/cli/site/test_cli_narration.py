"""Mirror of `src/studyforge/cli/site/cli.py`'s narration half: `build --no-narration`.

⭐ And a build names every stale clip it plays, and every clip an earlier
narrated build left in its `--out`, and deletes neither.
"""

from __future__ import annotations

import io
import json

import pytest

from studyforge.cli.site.cli import SILENT, build_parser, main
from studyforge.cli.site.report import STALE, UNLINKED
from studyforge.validate.report import OK
from tests.studyforge.cli.narrate.plant import edit_one_paragraph, narrated
from tests.studyforge.generate.corpora import a_corpus, an_output
from tests.studyforge.generate.test_narration import PLAYER, narrate
from tests.studyforge.validate.test_narration import stale_by_join


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


# --------------------------------------------------------------------------
# ⭐ What a build says about clips it does not act on
# --------------------------------------------------------------------------


def _said(root, out, *flags):
    said = io.StringIO()
    assert main([str(root), "--out", str(out), *flags], out=said) == OK
    return said.getvalue().splitlines()


def _clips(out):
    return sorted(
        path.relative_to(out).as_posix()
        for path in out.rglob("*")
        if path.is_file() and path.parent.name == "audio"
    )


def test_a_bare_build_names_each_clip_that_plays_words_its_paragraph_no_longer_says(tmp_path):
    # ⛔ The bare verb names every stale clip rather than building without a word.
    root = narrated(tmp_path)
    assert [line for line in _said(root, an_output(tmp_path)) if line.startswith("stale ")] == []
    edit_one_paragraph(root)
    out = tmp_path / "again"
    out.mkdir()

    stale = [line for line in _said(root, out) if line.startswith("stale ")]

    assert len(stale) == len(stale_by_join(root)) == 1
    assert stale[0].endswith(STALE) and "studyforge validate" in stale[0]


def test_a_build_with_narration_off_names_each_clip_an_earlier_build_left_and_keeps_it(tmp_path):
    # ⛔ The clips stay, and the build says so. They are kept (R3).
    root = a_corpus(tmp_path, "depth1")
    narrate(root)
    out = an_output(tmp_path)
    _said(root, out)
    copied = _clips(out)
    assert copied, "the narrated build copied no clip, so there is nothing to leave"

    off = _said(root, out, "--no-narration")

    unlinked = [line for line in off if line.startswith("unlinked ")]
    assert [line.split()[1] for line in unlinked] == copied
    assert all(line.endswith(UNLINKED) for line in unlinked)
    assert _clips(out) == copied, "a build deleted a clip"


@pytest.mark.parametrize("where", ["fresh", "root"])
def test_a_build_with_narration_off_into_a_clean_out_or_the_root_names_nothing(tmp_path, where):
    root = a_corpus(tmp_path, "depth1")
    narrate(root)
    out = an_output(tmp_path) if where == "fresh" else root

    assert not [line for line in _said(root, out, "--no-narration") if "unlinked" in line]
