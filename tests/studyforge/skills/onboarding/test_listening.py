"""Mirror of `src/studyforge/skills/onboarding/listening.py` (R12): the guide's narration section.

- ⭐ a voiced corpus is told narration is optional and the site complete without it;
- ⭐ one that does not commit its clips is given both restore commands, by the
  paths `narrate.release` names, in prose and never in a fence (a fenced line
  is run as written from a fresh clone, and a restore reaches a release host);
- a corpus that commits its clips is told a clone carries them;
- a corpus that is not narrated is told so, and offered no restore.
"""

from __future__ import annotations

from studyforge.narrate.release import RESTORE_PS1, RESTORE_SH
from studyforge.skills.onboarding.listening import narration_section
from tests.studyforge.skills.onboarding.test_artifacts import _document, _manifest


def test_a_voiced_corpus_that_does_not_commit_its_clips_is_given_both_restores():
    text = "\n".join(narration_section(_manifest(media={"commit": "never"})))

    assert "Narration is optional: the site is complete without it." in text
    assert f"`sh {RESTORE_SH}`" in text
    assert f"`powershell -File {RESTORE_PS1}`" in text
    assert "GITHUB_TOKEN" in text


def test_the_restore_is_never_a_fenced_line():
    document = _document(_manifest(media={"commit": "never"}))
    fences = document.split("```")[1::2]

    assert RESTORE_SH in document
    assert not [fence for fence in fences if "restore" in fence]


def test_a_corpus_that_commits_its_clips_is_told_a_clone_carries_them():
    text = "\n".join(narration_section(_manifest()))

    assert "a clone carries them" in text
    assert RESTORE_SH not in text


def test_a_corpus_that_is_not_narrated_is_told_so_and_offered_no_restore():
    text = "\n".join(narration_section(_manifest(narration=False, media={"commit": "never"})))

    assert "not narrated" in text
    assert "complete without a voice" in text
    assert RESTORE_SH not in text


def test_the_section_is_in_the_reader_document():
    manifest = _manifest(media={"commit": "never"})
    assert "\n".join(narration_section(manifest)) in _document(manifest)
