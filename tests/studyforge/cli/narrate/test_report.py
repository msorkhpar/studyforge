"""Mirror of `src/studyforge/cli/narrate/report.py` (R12)."""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.cli.narrate.report import NO_SERVICE, exit_code, lines
from studyforge.cli.narrate.stage import Narrated
from studyforge.narrate.client import Health
from studyforge.narrate.synth import Synthesis
from studyforge.validate.cli import UNUSABLE
from studyforge.validate.report import INVALID, OK

UP = Health(True, "the narration service answered", provides=3, chunk_chars=1800)
DOWN = Health(False, "the narration service did not answer (ConnectionRefusedError).")


def synthesis(written=(), failed=(), retryable=(), unsettled=(), fresh=()) -> Synthesis:
    return Synthesis(
        written=tuple(written),
        fresh=tuple(fresh),
        reasons={},
        failed=tuple(failed),
        retryable=tuple(retryable),
        unsettled=tuple(unsettled),
        recorded=bool(written),
    )


def test_an_absent_service_exits_two_and_is_named():
    narrated = Narrated(health=DOWN)
    printed = lines(narrated, "corpus")
    assert exit_code(narrated) == UNUSABLE
    assert f"refuse service  {NO_SERVICE}" in printed
    assert any(DOWN.detail in line for line in printed)


def test_a_clean_run_exits_zero():
    assert exit_code(Narrated(health=UP, units=(("u", synthesis(fresh=("a",))),))) == OK


@pytest.mark.parametrize(
    "moved",
    [
        {"failed": (("a", "not_synthesisable"),)},
        {"retryable": ("a",)},
        {"unsettled": ("a",)},
    ],
)
def test_anything_declared_and_not_produced_exits_one(moved):
    assert exit_code(Narrated(health=UP, units=(("u", synthesis(**moved)),))) == INVALID


def test_a_run_stopped_part_way_exits_one():
    narrated = Narrated(health=UP, stopped="the service went away")
    assert exit_code(narrated) == INVALID
    assert "stopped service  the service went away" in lines(narrated, "corpus")


def test_clip_paths_are_relative_to_the_corpus_root_and_sorted(tmp_path):
    root = tmp_path / "corpus"
    clips = [root / "b" / "audio" / "u-2.mp3", root / "a" / "audio" / "u-1.mp3"]
    printed = lines(Narrated(health=UP, units=(("u", synthesis(written=clips)),)), str(root))

    wrote = [line for line in printed if line.startswith("wrote ")]
    assert wrote == ["wrote a/audio/u-1.mp3", "wrote b/audio/u-2.mp3"]
    # ⚠️ The header and summary echo the root AS TYPED, as `studyforge build`
    # does; what this module composes — the clip paths — carries no directory.
    assert str(tmp_path) not in "\n".join(wrote)


def test_a_clip_outside_the_root_prints_only_its_name(tmp_path):
    clip = tmp_path / "elsewhere" / "u-1.mp3"
    printed = lines(Narrated(health=UP, units=(("u", synthesis(written=[clip])),)), "corpus")
    assert "wrote u-1.mp3" in printed


def test_the_summary_counts_written_and_fresh_clips():
    done = synthesis(written=[Path("corpus/a.mp3")], fresh=("b", "c"))
    printed = lines(Narrated(health=UP, units=(("u", done),)), "corpus")
    assert printed[-1] == (
        "narrated corpus  1 clip(s) written, 2 already synthesised under these conditions"
    )
