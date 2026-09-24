"""Mirror of `src/studyforge/skills/buildserve/run.py`'s `W460` half: the user's answer.

⭐ **The user's ruling, 2026-09-23:** *"while serving or even while caputring the
matterial skills should ask if user is interested in the narrition or not"*.
Read over a served site with clips on disk: off serves no clip, prints no
`partial` narration state and says once what it chose; on, the positive control,
serves every clip its pages name.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from urllib.parse import quote

import pytest

from studyforge.skills.buildserve.states import NARRATION_OFF, VOICE_UNHEARD
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import OK
from tests.studyforge.cli.narrate.service import VOICE
from tests.studyforge.generate.test_narration import PLAYER, narrate
from tests.studyforge.serve.serving import fetch
from tests.studyforge.skills.buildserve.running import (
    audio_references,
    copied,
    directory,
    partials,
    run_once,
    skill_running,
    steps,
)


def clips(root: Path) -> dict[str, str]:
    return {
        path.relative_to(root).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(root.rglob("*.mp3"))
    }


def silenced(root: Path) -> Path:
    manifest = root / "corpus.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    document.update(corpus_api=5, narration=False)
    manifest.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    return root


@pytest.mark.parametrize("how", ["flag", "corpus.json"])
def test_off_serves_the_floor_with_no_narration_state_and_touches_no_clip(tmp_path, how):
    root = copied("depth1", tmp_path)
    assert narrate(root)
    before = clips(root)
    options = {"narration": False} if how == "flag" else {}
    if how == "corpus.json":
        silenced(root)
    out = directory(tmp_path)

    with skill_running(root, out, **options) as running:
        pages = [page for page in out.rglob("*.unit.html")]
        bodies = [fetch(running.server, "/" + quote(str(p.relative_to(out))))[2] for p in pages]
    said = running.said()

    assert running.code == [OK], said
    assert partials(said) == ["exercises"], "narration off was reported as short"
    assert NARRATION_OFF in said
    assert pages and all(PLAYER.encode() not in body for body in bodies)
    assert audio_references(out) == []
    assert clips(root) == before


def test_on_is_the_positive_control_and_serves_every_clip(tmp_path):
    root = silenced(copied("depth1", tmp_path))
    assert narrate(root)
    out = directory(tmp_path)

    with skill_running(root, out, narration=True) as running:
        named = audio_references(out)
        answers = [fetch(running.server, "/" + quote(clip))[0] for clip in named]
    said = running.said()

    assert running.code == [OK], said
    assert NARRATION_OFF not in said
    assert named and set(answers) == {200}


def test_a_voice_with_narration_off_is_refused_before_anything_runs(tmp_path):
    root, out = copied("depth1", tmp_path), directory(tmp_path)

    code, said = run_once(root, out, voice=VOICE, narration=False)

    assert code == UNUSABLE
    assert VOICE_UNHEARD in said
    assert steps(said) == ["step validate exit 0"]
    assert not any(out.iterdir())
