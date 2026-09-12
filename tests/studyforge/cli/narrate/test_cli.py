"""Mirror of `src/studyforge/cli/narrate/cli.py` (R12).

⛔ **Every case writes into a copy of a fixture under `tmp_path`.** The
service-backed cases swap the module's one transport for a recording one, so
the exit codes are asserted through the real entry point with no service.
"""

from __future__ import annotations

import io
import socket

import pytest

from studyforge.cli.narrate import cli
from studyforge.cli.narrate.cli import DEFAULT_FORMAT, DEFAULT_SERVICE, build_parser, main
from studyforge.cli.narrate.report import NO_SERVICE
from studyforge.narrate.synth import state_file
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK
from tests.studyforge.cli.narrate.service import (
    VOICE,
    FakeService,
    clip_ids,
    files,
    new_clips,
    speech_ids,
)
from tests.studyforge.generate.corpora import a_corpus


def invoke(*argv):
    out = io.StringIO()
    return main(list(argv), out=out), out.getvalue()


def dead_port() -> int:
    """A loopback port nothing is listening on."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as probe:
        probe.bind(("127.0.0.1", 0))
        return probe.getsockname()[1]


# --------------------------------------------------------------------------
# the interface
# --------------------------------------------------------------------------


def test_the_parser_takes_a_root_and_a_voice():
    parser = build_parser()
    assert parser.prog == "studyforge narrate"
    arguments = parser.parse_args(["corpus", "--voice", VOICE])
    assert (arguments.root, arguments.voice) == ("corpus", VOICE)
    assert (arguments.fmt, arguments.service) == (DEFAULT_FORMAT, DEFAULT_SERVICE)


def test_the_voice_is_required_and_has_no_default():
    with pytest.raises(SystemExit):
        build_parser().parse_args(["corpus"])


def test_the_default_service_is_loopback_only():
    assert DEFAULT_SERVICE.startswith("http://127.0.0.1:")


# --------------------------------------------------------------------------
# through the entry point
# --------------------------------------------------------------------------


def test_it_narrates_a_corpus_and_exits_zero(tmp_path, monkeypatch):
    root = a_corpus(tmp_path, "depth1")
    before = files(root)
    monkeypatch.setattr(cli, "over_http", FakeService())

    code, printed = invoke(str(root), "--voice", VOICE)

    assert code == OK, printed
    assert clip_ids(new_clips(root, before)) == speech_ids(root)
    assert len([line for line in printed.splitlines() if line.startswith("wrote ")]) == len(
        speech_ids(root)
    )


def test_a_rerun_through_the_entry_point_requests_nothing(tmp_path, monkeypatch):
    root = a_corpus(tmp_path, "depth1")
    monkeypatch.setattr(cli, "over_http", FakeService())
    invoke(str(root), "--voice", VOICE)
    again = FakeService()
    monkeypatch.setattr(cli, "over_http", again)

    code, _ = invoke(str(root), "--voice", VOICE)

    assert code == OK
    assert again.submitted == []


def test_a_segment_the_service_could_not_synthesise_exits_one(tmp_path, monkeypatch):
    root = a_corpus(tmp_path, "depth1")
    lost = speech_ids(root)[0]
    monkeypatch.setattr(cli, "over_http", FakeService(failing={lost}))

    code, printed = invoke(str(root), "--voice", VOICE)

    assert code == INVALID
    assert f"fail {lost}  not_synthesisable" in printed


def test_a_dead_port_is_a_named_refusal_exiting_two(tmp_path):
    # ⛔ The REAL transport against a port nobody listens on: `probe()` never
    # raises for absence, and nothing is written.
    root = a_corpus(tmp_path, "depth1")
    before = files(root)

    code, printed = invoke(
        str(root), "--voice", VOICE, "--service", f"http://127.0.0.1:{dead_port()}"
    )

    assert code == UNUSABLE
    assert f"refuse service  {NO_SERVICE}" in printed
    assert files(root) == before


def test_a_root_that_is_not_a_directory_exits_two(tmp_path):
    code, printed = invoke(str(tmp_path / "absent"), "--voice", VOICE)
    assert code == UNUSABLE
    assert "not a directory" in printed


def test_an_unreadable_corpus_exits_two_without_a_request(tmp_path, monkeypatch):
    root = a_corpus(tmp_path, "depth1")
    (root / "corpus.json").write_text("{", encoding="utf-8")
    service = FakeService()
    monkeypatch.setattr(cli, "over_http", service)

    code, printed = invoke(str(root), "--voice", VOICE)

    assert code == UNUSABLE
    assert "corpus.json" in printed
    assert str(tmp_path) not in printed
    assert service.sent == []


def test_an_unreadable_record_exits_two_without_a_request(tmp_path, monkeypatch):
    root = a_corpus(tmp_path, "depth1")
    record = state_file(root)
    record.parent.mkdir(parents=True, exist_ok=True)
    record.write_text("[]", encoding="utf-8")
    service = FakeService()
    monkeypatch.setattr(cli, "over_http", service)

    code, _ = invoke(str(root), "--voice", VOICE)

    assert code == UNUSABLE
    assert service.sent == []
