"""Mirror of `src/studyforge/generate/narration.py`'s optional half: narration is optional.

⭐ A corpus may be read without voices, even when clips were generated.

What is proved here, through the build, over both framework fixture corpora with a
record and a clip per speech unit on disk:

- off, from `corpus.json` or from a run's override, builds **the reading floor
  byte for byte** — the pages a corpus with no record at all gets;
- off copies no clip and **touches none**: every clip and the record keep their
  bytes, and nothing is deleted (R3);
- on again plays the same clips, with no re-synthesis;
- off never opens the record, so a record it will not voice cannot stop it.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

import pytest

from studyforge.corpus.placement import AUDIO_DIRNAME
from studyforge.generate import BuildError, write_site
from studyforge.generate.declarations import read_corpus
from studyforge.generate.narration import SILENCED, narrated, voiced
from studyforge.narrate.synth import state_file
from tests.studyforge.generate.corpora import BOTH, a_corpus, an_output
from tests.studyforge.generate.test_narration import PLAYER, narrate, not_quiet, unit_pages
from tests.support import repository_root


def silence(root: Path, *, narration: bool = False) -> None:
    """Record the author's answer in `corpus.json`, at the version that reads it."""
    path = root / "corpus.json"
    document = json.loads(path.read_text(encoding="utf-8"))
    document.update(corpus_api=5, narration=narration)
    path.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")


def digests(paths: list[Path]) -> dict[Path, str]:
    """Every file's sha256, so "untouched" is a comparison and not a promise."""
    return {path: hashlib.sha256(path.read_bytes()).hexdigest() for path in sorted(paths)}


def pages(root: Path) -> dict[str, bytes]:
    """Every page a build wrote under `root`, by its path relative to it."""
    found = {str(path.relative_to(root)): path.read_bytes() for path in root.rglob("*.html")}
    assert found, "no page was built, so every comparison below would pass over nothing"
    return found


def clips_under(root: Path) -> list[Path]:
    """Every file inside a narration audio directory under `root`."""
    return [path for path in root.rglob("*") if path.is_file() and AUDIO_DIRNAME in path.parts[:-1]]


@pytest.mark.parametrize("name", BOTH)
@pytest.mark.parametrize("how", ["corpus.json", "override"])
def test_off_builds_the_reading_floor_byte_for_byte(tmp_path, name, how):
    floor = a_corpus(tmp_path / "floor", name)
    voiced_root = a_corpus(tmp_path / "voiced", name)
    assert narrate(voiced_root)
    if how == "corpus.json":
        silence(voiced_root)
        silence(floor)
        write_site(voiced_root, voiced_root)
    else:
        write_site(voiced_root, voiced_root, narration=False)
    write_site(floor, floor)

    for path, body in unit_pages(voiced_root).items():
        assert not_quiet(body) == [], f"{path.name} carries narration while off"
    assert pages(voiced_root) == pages(floor)


@pytest.mark.parametrize("name", BOTH)
def test_off_touches_no_clip_and_no_record_and_on_plays_them_again(tmp_path, name):
    root = a_corpus(tmp_path, name)
    placed = narrate(root)
    before = digests([*placed, state_file(root)])

    write_site(root, root, narration=False)
    assert digests([*placed, state_file(root)]) == before
    assert all(PLAYER not in body for body in unit_pages(root).values())

    write_site(root, root, narration=True)
    assert digests([*placed, state_file(root)]) == before
    assert any(PLAYER in body for body in unit_pages(root).values())


@pytest.mark.parametrize("name", BOTH)
def test_off_into_another_directory_copies_no_clip(tmp_path, name):
    root = a_corpus(tmp_path, name)
    assert narrate(root)
    out = an_output(tmp_path)

    written = write_site(root, out, narration=False)

    assert [path for path in written.media if AUDIO_DIRNAME in path.parts] == []
    assert clips_under(out) == []
    # ⛔ No clip is reported missing either: off promises nothing to go missing.
    assert [path for path in written.missing if AUDIO_DIRNAME in path.parts] == []


def test_the_override_turns_a_corpus_the_author_silenced_back_on(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    assert narrate(root)
    silence(root)

    write_site(root, root, narration=True)

    assert any(PLAYER in body for body in unit_pages(root).values())


def test_off_never_opens_the_record_so_a_broken_one_cannot_stop_it(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    narrate(root)
    state_file(root).write_text("{not json", encoding="utf-8")

    write_site(root, root, narration=False)
    with pytest.raises(BuildError, match="narration record"):
        write_site(root, root)


def test_the_gate_answers_the_record_s_own_absent_state(tmp_path):
    root = a_corpus(tmp_path, "depth1")
    narrate(root)
    corpus = read_corpus(root)

    assert corpus.narration is True
    assert narrated(corpus).present
    assert narrated(voiced(corpus, False)) is SILENCED
    assert voiced(corpus, None) is corpus


def test_a_manifest_that_says_nothing_keeps_the_voice_it_always_had(tmp_path):
    # ⭐ "Existing corpora keep narration if they have a record": absent is on.
    root = a_corpus(tmp_path, "depth2")
    assert "narration" not in (root / "corpus.json").read_text(encoding="utf-8")
    narrate(root)

    write_site(root, root)

    assert any(PLAYER in body for body in unit_pages(root).values())


def test_no_pass_reads_the_record_around_the_one_gate():
    # ⛔ `narrated` is the ONE gate: a pass that called `recorded` itself would
    # voice a corpus its author turned off, with every test above still green
    # for the passes that did not.
    package = repository_root() / "src" / "studyforge" / "generate"
    callers = sorted(
        path.name
        for path in package.glob("*.py")
        if "recorded(" in path.read_text(encoding="utf-8") and path.name != "narration.py"
    )
    assert callers == []
