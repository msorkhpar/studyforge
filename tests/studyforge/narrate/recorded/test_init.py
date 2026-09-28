"""Mirror of `src/studyforge/narrate/recorded/__init__.py` (R12): the record, without the pass."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

from studyforge.narrate import recorded, synth

REPO = Path(__file__).resolve().parents[4]


def test_everything_the_package_exports_is_reachable_by_that_name():
    for name in recorded.__all__:
        assert hasattr(recorded, name), name
    assert set(recorded.__all__) == {name for name in dir(recorded) if not name.startswith("_")} - {
        "location",
        "record",
        "studyforge",
    }


def test_synthesis_re_exports_every_name_as_the_same_object():
    # ⭐ A caller that synthesises still imports one package, and gets these.
    for name in recorded.__all__:
        if hasattr(synth, name):
            assert getattr(synth, name) is getattr(recorded, name), name
    for name in ("State", "StateError", "audio_dir", "read_state", "state_file", "located"):
        assert getattr(synth, name) is getattr(recorded, name), name


def test_reading_the_record_loads_no_synthesis():
    # ⛔ The reason the package exists: a build, a plan and the server read the
    # record, and none of them may load the pass, the client or the wire.
    probe = (
        "import sys; import studyforge.narrate.recorded; "
        "print(sorted(m for m in sys.modules if m.startswith('studyforge.narrate.')))"
    )
    loaded = subprocess.run(
        [sys.executable, "-c", probe],
        cwd=REPO,
        env={"PYTHONPATH": str(REPO / "src")},
        capture_output=True,
        text=True,
        check=True,
    ).stdout
    for gone in ("synth", "client", "wire"):
        assert f"'studyforge.narrate.{gone}" not in loaded, gone
