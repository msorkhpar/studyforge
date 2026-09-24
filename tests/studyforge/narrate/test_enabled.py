"""Mirror of `src/studyforge/narrate/enabled.py` (R12) — the one "narration is on" predicate."""

from __future__ import annotations

import pytest

from studyforge.narrate.enabled import narration_on


def test_a_run_nobody_asked_is_on(tmp_path):
    # ⭐ The behaviour every corpus had before narration was made optional.
    assert narration_on(tmp_path) is True


@pytest.mark.parametrize("asked", [True, False])
def test_the_runs_own_answer_wins_either_way(tmp_path, asked):
    assert narration_on(tmp_path, asked=asked) is asked


def test_the_run_is_keyword_only(tmp_path):
    # ⛔ A positional `False` would read as a root, not as an answer.
    with pytest.raises(TypeError):
        narration_on(tmp_path, False)  # type: ignore[misc]


def _declaring(root, narration):
    """A corpus root whose `corpus.json` records `narration` (`W460`)."""
    import json
    import shutil

    from tests.fixture_checks import FIXTURES

    shutil.copytree(FIXTURES / "depth1", root)
    manifest = root / "corpus.json"
    document = json.loads(manifest.read_text(encoding="utf-8"))
    manifest.write_text(json.dumps({**document, "corpus_api": 5, "narration": narration}))
    return root


@pytest.mark.parametrize(
    ("recorded", "asked", "on"),
    [(False, None, False), (True, None, True), (False, True, True), (True, False, False)],
)
def test_the_corpus_s_recorded_answer_decides_when_the_run_asked_nothing(
    tmp_path, recorded, asked, on
):
    # ⭐ `W460`: step 2 of the order — `corpus.json`'s `narration`.
    assert narration_on(_declaring(tmp_path / "c", recorded), asked=asked) is on


def test_a_manifest_that_says_nothing_or_cannot_be_read_is_on(tmp_path):
    (tmp_path / "corpus.json").write_text("{not json", encoding="utf-8")
    assert narration_on(tmp_path) is True
