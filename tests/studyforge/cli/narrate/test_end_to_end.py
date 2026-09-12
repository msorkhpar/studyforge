"""⛔ `SF-42`'s end-to-end leg: a `FND-04` corpus narrated against a RUNNING `narrate-service`.

⭐ **The leg `M3` is missing.** It is asserted as a READING OF THE DISK — clip
files under the copied corpus that were not there before, one per speech unit,
each carrying MPEG audio bytes — and the re-run as a reading of the TRANSPORT.

## ⛔ Where it runs, and why a skip here is LOUD

⚠️ **The pinned dev image runs with `network_mode: "none"`**
(`docker/dev/compose.yaml`), so no service is reachable from inside it and this
leg is a HOST reading. ⛔ **Unset `STUDYFORGE_NARRATION_SERVICE` and every case
SKIPS with a reason that says it DID NOT RUN** — `pytest -ra` prints it.
⭐ **Set it and the service must answer**: an unreachable URL fails the case,
it never skips, so a person who asked for the leg cannot receive a silent pass.

Placeholder prose only: the text sent is the fixture corpus's, nothing else.
"""

from __future__ import annotations

import io
import os

import pytest

from studyforge.cli.narrate import cli
from studyforge.cli.narrate.cli import main
from studyforge.narrate.client import over_http
from studyforge.validate.report import OK
from tests.studyforge.cli.narrate.service import (
    HEALTH,
    VOICE,
    Recording,
    clip_ids,
    files,
    new_clips,
    speech_ids,
)
from tests.studyforge.generate.corpora import BOTH, a_corpus

VARIABLE = "STUDYFORGE_NARRATION_SERVICE"


def service_url() -> str:
    url = os.environ.get(VARIABLE, "").strip()
    if not url:
        pytest.skip(
            f"SF-42 end-to-end narration DID NOT RUN: set {VARIABLE} to a running "
            f"narrate-service's URL (a host reading; the pinned image has no network)"
        )
    return url


def is_mpeg_audio(data: bytes) -> bool:
    """An ID3v2 tag or an MPEG frame sync — the bytes a real engine answers with."""
    return data[:3] == b"ID3" or (len(data) > 1 and data[0] == 0xFF and data[1] & 0xE0 == 0xE0)


@pytest.mark.parametrize("name", BOTH)
def test_a_fixture_corpus_is_narrated_end_to_end_and_its_clips_are_on_disk(
    tmp_path, monkeypatch, capsys, name
):
    url = service_url()
    root = a_corpus(tmp_path, name)
    before = files(root)
    out = io.StringIO()
    monkeypatch.setattr(cli, "over_http", Recording(over_http))

    code = main([str(root), "--voice", VOICE, "--service", url], out=out)

    assert code == OK, out.getvalue()
    clips = new_clips(root, before)
    expected = speech_ids(root)
    assert expected, f"{name} declares no speech; the reading would be vacuous"
    assert clip_ids(clips) == expected
    assert all(is_mpeg_audio(clip.read_bytes()) for clip in clips)

    settled = files(root)
    again = Recording(over_http)
    monkeypatch.setattr(cli, "over_http", again)
    code = main([str(root), "--voice", VOICE, "--service", url], out=io.StringIO())

    assert code == OK
    assert again.submitted == []
    assert again.requests == [HEALTH]
    assert files(root) == settled
    with capsys.disabled():
        reading = f"{len(clips)} clip file(s) on disk, {len(expected)} speech unit(s)"
        print(f"\nSF-42 end-to-end [{name}]: {reading}")
