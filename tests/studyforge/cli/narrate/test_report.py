"""Mirror of `src/studyforge/cli/narrate/report.py` (R12)."""

from __future__ import annotations

from pathlib import Path

import pytest

from studyforge.cli.narrate.prune import Pruned
from studyforge.cli.narrate.report import (
    DEAD,
    NO_SERVICE,
    PARTIAL,
    REFUSED,
    exit_code,
    lines,
    prune_exit_code,
    prune_lines,
)
from studyforge.cli.narrate.stage import Narrated
from studyforge.narrate.answers import Health
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


# --------------------------------------------------------------------------
# ⛔ The dead-entry disclosure, and `--prune`'s own report
# --------------------------------------------------------------------------


@pytest.mark.parametrize("health", [UP, DOWN])
def test_the_dead_count_is_printed_on_every_run_zero_included(health):
    assert f"dead record  0 {DEAD}" in lines(Narrated(health=health), "corpus")
    printed = lines(Narrated(health=health, dead=("u.gone.b1",)), "corpus")
    assert f"dead record  1 {DEAD}" in printed


def test_a_partial_walk_is_named_and_a_whole_one_prints_no_such_line():
    assert not any(line.startswith("partial walk") for line in lines(Narrated(health=UP), "c"))
    printed = lines(Narrated(health=UP, unwalked=("a/unit-01", "a/unit-02")), "c")
    assert f"partial walk  {PARTIAL}: a/unit-01, a/unit-02" in printed


def test_a_refused_prune_names_the_units_and_exits_one():
    pruned = Pruned(unwalked=("a/unit-02",))
    assert prune_lines(pruned, "corpus") == ["prune corpus", f"refuse walk  {REFUSED}: a/unit-02"]
    assert prune_exit_code(pruned) == INVALID


def test_a_prune_that_held_an_entry_exits_one_and_a_clean_one_zero(tmp_path):
    root = tmp_path / "corpus"
    done = Pruned(deleted=(root / "a" / "audio" / "u.gone.b1-deadbeef.mp3",), forgotten=("x",))
    printed = prune_lines(done, str(root))
    assert "delete a/audio/u.gone.b1-deadbeef.mp3" in printed
    assert str(tmp_path) not in "\n".join(line for line in printed if line.startswith("delete"))
    assert printed[-1].endswith("1 clip(s) deleted, 1 record entries removed, 0 held")
    assert prune_exit_code(done) == OK
    assert prune_exit_code(Pruned(held=(("x", "why"),))) == INVALID


@pytest.mark.parametrize("health", [UP, DOWN])
def test_the_superseded_count_is_printed_on_every_run_zero_included(health):
    from studyforge.cli.narrate.report import SUPERSEDED

    assert f"superseded clips  0 {SUPERSEDED}" in lines(Narrated(health=health), "corpus")


def test_a_cleared_superseded_clip_is_named_in_the_prune_report():
    from studyforge.cli.narrate.report import prune_lines
    from studyforge.narrate.synth import Superseded

    cleared = (("u.s.b1", Superseded("u.s.b1-aaaaaaaa.mp3", "unit/audio")),)
    assert "forget u.s.b1  superseded u.s.b1-aaaaaaaa.mp3" in prune_lines(
        Pruned(cleared=cleared), "c"
    )


def test_the_absent_service_hint_names_the_clone_the_command_and_both_ways_to_point():
    for phrase in (
        "clone the studyforge-narrate-service repository",
        "https://github.com/<owner>/studyforge-narrate-service.git",
        "docker compose up -d --build",
        "--service",
        "STUDYFORGE_NARRATE_SERVICE",
    ):
        assert phrase in NO_SERVICE.replace("Clone the", "clone the")
