"""Mirror of `src/studyforge/narrate/answers.py` (R12): the values, `place`, and no wire.

⭐ **`place` is exercised on a `Narration` built here, with no client**, because
writing clips needs no service. That it is reachable without one is `W223`'s seam.
"""

from __future__ import annotations

import ast
import inspect
from pathlib import Path

import pytest

from studyforge.address.address import Address
from studyforge.archive.scrub import PersonalDataLeak
from studyforge.corpus.placement.names import AUDIO_DIRNAME
from studyforge.corpus.placement.profile import profile_for
from studyforge.narrate import answers
from studyforge.narrate.answers import Artifact, Health, Narration, NarrationError, place
from studyforge.narrate.speakable.naming import clip_name
from studyforge.narrate.speakable.records import SpeakableError, SpeechUnit
from tests.support import imports_module

SOURCE = Path(inspect.getfile(answers))
AUDIO = b"ID3\x04\x00\x00\x00\x00\x00\x00mp3 bytes"


def unit(identifier: str, said: str) -> SpeechUnit:
    return SpeechUnit(
        id=identifier, speak=said, section="s", block_path=(0,), sub_index=None, kind="paragraph"
    )


def narration_of(spoken: SpeechUnit) -> Narration:
    """One produced clip for `spoken`, as a client would hand it back."""
    clip = Artifact(
        spoken.id, f"{clip_name(spoken)}.mp3", "audio/mpeg", AUDIO, "kokoro", "kokoro", "cached"
    )
    return Narration((clip,), (), (), "am_liam", "mp3", 3)


# --------------------------------------------------------------------------
# ⭐ Artifacts are placed THROUGH the policy — driven by both profiles
# --------------------------------------------------------------------------


@pytest.mark.parametrize("profile_name", ["tree", "sibling"])
def test_artifacts_are_placed_where_the_policy_says_and_nowhere_else(tmp_path, profile_name):
    spoken = unit("unit-01.1.b1", "A spoken paragraph.")
    locations = profile_for(profile_name).unit(
        Address(("java", "basics")), 1, "Meaningful Names", origin="doc/lesson.md"
    )
    into = tmp_path / locations.media_dir(AUDIO_DIRNAME)
    written = place(narration_of(spoken), into)
    # ⚠️ MEASURED: a writer that composed `parent / "audio"` for itself is a
    # NO-OP under `tree`, whose audio directory is literally `<unit>/audio` — so
    # only the `sibling` arm can discriminate that defect.
    assert written[0].parent == into
    assert written == (into / f"{clip_name(spoken)}.mp3",)
    assert written[0].read_bytes() == AUDIO


def test_the_two_profiles_put_the_same_clip_in_different_places(tmp_path):
    spoken = unit("unit-01.1.b1", "A spoken paragraph.")
    where = []
    for profile_name in ("tree", "sibling"):
        locations = profile_for(profile_name).unit(
            Address(("java",)), 1, "Meaningful Names", origin="doc/lesson.md"
        )
        root = tmp_path / profile_name
        where.append(place(narration_of(spoken), root / locations.media_dir(AUDIO_DIRNAME))[0])
    assert where[0].relative_to(tmp_path / "tree") != where[1].relative_to(tmp_path / "sibling")


def test_placing_leaves_no_partial_file_behind(tmp_path):
    spoken = unit("unit-01.1.b1", "A spoken paragraph.")
    place(narration_of(spoken), tmp_path / "audio")
    assert [item.name for item in (tmp_path / "audio").iterdir()] == [f"{clip_name(spoken)}.mp3"]


def test_place_has_no_default_destination():
    assert inspect.signature(place).parameters["into"].default is inspect.Parameter.empty


# --------------------------------------------------------------------------
# ⛔ Ruling 58, and what a Health says when nobody read a deployment
# --------------------------------------------------------------------------


def test_a_leak_is_not_translated_into_the_narration_error_family():
    assert not issubclass(PersonalDataLeak, NarrationError)
    assert not issubclass(SpeakableError, NarrationError)


def test_a_health_nobody_probed_claims_no_deployment_setting():
    health = Health(False, "the narration service did not answer")
    assert (health.provides, health.chunk_chars, health.engine_model) == (None, None, None)


# --------------------------------------------------------------------------
# ⛔ W223: this module is the side of the seam that loads no wire
# --------------------------------------------------------------------------


def test_the_module_imports_the_standard_library_and_the_speech_records_only():
    tree = ast.parse(SOURCE.read_text(encoding="utf-8"))
    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            imported.add(node.module)
        if isinstance(node, ast.Import):
            imported.update(alias.name for alias in node.names)
    assert imported == {
        "__future__",
        "collections.abc",
        "dataclasses",
        "pathlib",
        "typing",
        "studyforge.narrate.speakable.records",
    }


def test_the_module_imports_no_wire_no_client_and_no_placement_policy():
    for module in (
        "studyforge.narrate.wire",
        "studyforge.narrate.client",
        "studyforge.corpus.placement",
    ):
        assert not imports_module(SOURCE, module), module
