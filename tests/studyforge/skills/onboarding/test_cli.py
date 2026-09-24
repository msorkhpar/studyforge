"""Mirror of `src/studyforge/skills/onboarding/cli.py` (R12).

⛔ **This is the instrument the reader's document points at**, so every
clause here is against a corpus whose state the test MADE — ingested, then
narrated through the recording fake — rather than against a `Standing` somebody
typed. ⭐ **Both exit codes are asserted**, and so is the one property the whole
row rests on: the answer moves when the corpus does, with nothing regenerated.
"""

from __future__ import annotations

import shutil

import pytest

from studyforge.cli.narrate.stage import narrate_corpus
from studyforge.corpus.manifest import MANIFEST_FILENAME
from studyforge.exitcodes import UNUSABLE
from studyforge.narrate.client import NarrateClient
from studyforge.narrate.synth import state_file
from studyforge.skills.onboarding.cli import build_parser, main
from tests.studyforge.cli.narrate.service import BASE, FMT, VOICE, FakeService
from tests.studyforge.generate.corpora import a_corpus


def _narrate(root):
    client = NarrateClient(BASE, voice=VOICE, fmt=FMT, transport=FakeService())
    narrate_corpus(root, client, voice=VOICE, fmt=FMT)


def test_it_reads_one_corpus_root_and_says_so_in_its_own_interface():
    # ⭐ The interface a document prints, read off the parser rather than retyped.
    parser = build_parser()

    assert parser.prog == "python3 -m studyforge.skills.onboarding"
    assert vars(parser.parse_args(["somewhere"])) == {"root": "somewhere"}
    with pytest.raises(SystemExit):
        parser.parse_args([])


def test_an_ingested_corpus_is_reported_figure_by_figure_and_exits_zero(tmp_path, capsys):
    root = a_corpus(tmp_path, "depth1")

    code = main([str(root)])

    said = capsys.readouterr().out
    assert code == 0
    assert "- units: " in said and "with material" in said
    assert "- narrated: 0 of" in said and "there is no narration record yet" in said


def test_the_answer_moves_when_the_corpus_does_with_nothing_regenerated(tmp_path, capsys):
    # ⛔ THE ROW. The command is the same command, the corpus is the same corpus,
    # and nothing between the two readings rewrote a document: only `narrate` ran.
    root = a_corpus(tmp_path, "depth1")
    assert main([str(root)]) == 0
    before = capsys.readouterr().out

    _narrate(root)
    assert main([str(root)]) == 0
    after = capsys.readouterr().out

    assert "there is no narration record yet" in before
    assert "- narrated: 0 of" in before
    assert "there is no narration record yet" not in after
    assert "- narrated: 0 of" not in after
    assert before != after


def test_a_corpus_with_no_archive_is_an_answer_rather_than_a_failure(tmp_path, capsys):
    # ⭐ Exit 0: *nothing has been ingested* is a reading, and the reader's
    # document prints this line before ingest as well as after.
    root = a_corpus(tmp_path, "depth1")
    shutil.rmtree(root / "archive")

    code = main([str(root)])

    assert (code, "Nothing has been ingested" in capsys.readouterr().out) == (0, True)


def test_a_root_that_is_not_a_corpus_is_unusable_and_names_no_path(tmp_path, capsys):
    code = main([str(tmp_path)])

    said = capsys.readouterr().out
    assert code == UNUSABLE
    assert MANIFEST_FILENAME in said
    assert str(tmp_path) not in said and "/home/" not in said


def test_a_corpus_the_build_refuses_is_unusable_and_still_prints_why(tmp_path, capsys):
    # ⛔ Both ways against the clause above: a reading was attempted and failed,
    # and a reader who cannot see the refusal is left with an exit code alone.
    root = a_corpus(tmp_path, "depth1")
    state_file(root).parent.mkdir(parents=True, exist_ok=True)
    state_file(root).write_text("{not json", encoding="utf-8")

    code = main([str(root)])

    said = capsys.readouterr().out
    assert code == UNUSABLE
    assert "Not known" in said and "narration record" in said
    assert str(tmp_path) not in said and "/home/" not in said
